"""
diagnosis_service.py — 모델 추론 + Grad-CAM + 원인공정 추론 통합 서비스 계층.
서버 시작 시 1회만 인스턴스화해 요청마다 재사용.
threading.Lock으로 동시 요청 시 hook 상태 섞임을 방지.
"""
import base64
import io
import json
import os
import threading

import numpy as np
import torch
import torch.nn.functional as F
import cv2
from PIL import Image

# server.py가 sys.path에 ai/hs 경로를 추가한 뒤 이 모듈을 임포트하는 것을 전제로 함.
from hs.model import ResNet9
from hs.data_utils import resize_for_dl, validate_wafer_array
from hs.dataset import WaferDataset
import hs.config as config
import process_attribution


class DiagnosisService:
    def __init__(
        self,
        weights_path: str | None = None,
        label_mapping_path: str | None = None,
        min_confidence: float = 0.4,
    ):
        hero_dir = os.path.dirname(os.path.abspath(__file__))
        hs_dir = os.path.join(hero_dir, "..", "hs")

        if weights_path is None:
            weights_path = os.path.join(hs_dir, config.MODEL_SAVE_PATH)
        if label_mapping_path is None:
            label_mapping_path = os.path.join(hs_dir, "label_mapping.json")

        with open(label_mapping_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # label_mapping.json 포맷 자동 감지
        # {"Center": 0, ...} (class_name→id) 또는 {"0": "Center", ...} (id_str→class_name)
        first_val = next(iter(raw.values()))
        if isinstance(first_val, int):
            # {"Center": 0, "Donut": 1, ...}
            self.id_to_name: dict[int, str] = {v: k for k, v in raw.items()}
            self.name_to_id: dict[str, int] = {k: v for k, v in raw.items()}
        else:
            # {"0": "Center", "1": "Donut", ...}
            self.id_to_name = {int(k): v for k, v in raw.items()}
            self.name_to_id = {v: int(k) for k, v in raw.items()}

        self.num_classes = len(self.id_to_name)
        self.min_confidence = min_confidence

        # label_mapping 클래스명과 PRIOR 키 일치 검증 — 불일치 시 서버 시작 중단
        label_names = set(self.id_to_name.values())
        prior_names = set(process_attribution.PRIOR.keys())
        if label_names != prior_names:
            missing_in_prior = label_names - prior_names
            missing_in_label = prior_names - label_names
            raise RuntimeError(
                f"[설정 오류] label_mapping.json과 process_attribution.PRIOR 불일치.\n"
                f"  PRIOR에 없는 클래스: {missing_in_prior}\n"
                f"  label_mapping에 없는 PRIOR 클래스: {missing_in_label}\n"
                f"두 파일의 클래스명을 맞춘 뒤 다시 시작하세요."
            )

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = ResNet9(self.num_classes).to(self.device)
        self.model.load_state_dict(torch.load(weights_path, map_location=self.device))
        self.model.eval()

        # Grad-CAM 타겟: res2 (AdaptiveAvgPool 직전 마지막 잔차 블록)
        self._target_layer = self.model.res2
        self._activations: torch.Tensor | None = None
        self._gradients: torch.Tensor | None = None
        self._target_layer.register_forward_hook(self._save_activation)
        self._target_layer.register_full_backward_hook(self._save_gradient)

        # 동시 요청 시 hook 상태(_activations/_gradients)가 섞이는 것을 방지
        self._lock = threading.Lock()

    def _save_activation(self, module, input, output):
        self._activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self._gradients = grad_output[0].detach()

    def _preprocess(self, raw_arr: np.ndarray):
        validate_wafer_array(raw_arr, source="uploaded_image")
        resized = resize_for_dl(raw_arr)
        X = np.expand_dims(np.stack([resized]), axis=-1)
        y_dummy = np.array([0])
        x_tensor = WaferDataset(X, y_dummy).X.to(self.device)
        return resized, x_tensor

    def _make_overlay_png_base64(self, base_img_01: np.ndarray, cam: np.ndarray, alpha: float = 0.45) -> str:
        heatmap = _jet_colormap(cam)
        base_rgb = np.stack([base_img_01] * 3, axis=-1)
        blended = np.clip(alpha * heatmap + (1 - alpha) * base_rgb, 0, 1)
        img = Image.fromarray((blended * 255).astype(np.uint8))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("ascii")

    def diagnose(self, raw_arr: np.ndarray, top_k: int = 3, top_k_process: int = 3) -> dict:
        """
        raw_arr: (H,W) ndarray, 값 0/1/2 (팔레트 PNG를 np.array()로 읽은 것).
        반환:
          predictions          — [{class_id, class_name, confidence, image_id}] top-k
          predicted_class      — top-1 클래스 이름
          confidence           — top-1 확률
          softmax              — {class_name: prob} 전체
          low_confidence       — 확신 낮음 여부 (프론트 배지용)
          gradcam_overlay_png_base64 — base64 PNG 문자열
          process_candidates   — [{process, sub_processes, weight, evidence_type, citations, note}]
        """
        with self._lock:  # forward → backward → hook값 읽기 전체를 한 요청씩 직렬화
            resized, x_tensor = self._preprocess(raw_arr)
            x_tensor = x_tensor.clone().detach().requires_grad_(True)

            logits = self.model(x_tensor)
            probs = torch.softmax(logits, dim=1)[0]
            pred_idx = int(probs.argmax().item())
            confidence = float(probs[pred_idx].item())

            # Grad-CAM: top-1 클래스 기준 (원인공정 추론과 동일 클래스 가리키도록)
            self.model.zero_grad()
            logits[0, pred_idx].backward()

            weights = self._gradients.mean(dim=(2, 3), keepdim=True)
            cam = F.relu((weights * self._activations).sum(dim=1, keepdim=True))
            cam = cam[0, 0].cpu().numpy()
            if cam.max() > 0:
                cam /= cam.max()
            cam_resized = cv2.resize(
                cam,
                (resized.shape[1], resized.shape[0]),
                interpolation=cv2.INTER_LINEAR,
            )

            base_img_01 = resized.astype(np.float32) / 2.0
            overlay_b64 = self._make_overlay_png_base64(base_img_01, cam_resized)

            probs_np = probs.detach().cpu().numpy()

        pred_name = self.id_to_name[pred_idx]
        softmax_dict = {
            self.id_to_name[i]: round(float(probs_np[i]), 4)
            for i in range(self.num_classes)
        }

        sorted_by_prob = sorted(softmax_dict.items(), key=lambda x: x[1], reverse=True)[:top_k]
        predictions = [
            {
                "class_id": self.name_to_id[name],
                "class_name": name,
                "confidence": round(prob, 4),
                "image_id": "",
            }
            for name, prob in sorted_by_prob
        ]

        low_confidence = confidence < self.min_confidence
        process_candidates = process_attribution.process_given_pattern(pred_name)[:top_k_process]

        return {
            "predictions": predictions,
            "predicted_class": pred_name,
            "confidence": round(confidence, 4),
            "softmax": softmax_dict,
            "low_confidence": low_confidence,
            "gradcam_overlay_png_base64": overlay_b64,
            "process_candidates": process_candidates,
        }


def _jet_colormap(cam_01: np.ndarray) -> np.ndarray:
    """jet 컬러맵 적용 — matplotlib 없이 cv2만으로 처리 (0~1 → (H,W,3) 0~1)."""
    cam_uint8 = (np.clip(cam_01, 0, 1) * 255).astype(np.uint8)
    colored_bgr = cv2.applyColorMap(cam_uint8, cv2.COLORMAP_JET)
    return colored_bgr[:, :, ::-1].astype(np.float32) / 255.0
