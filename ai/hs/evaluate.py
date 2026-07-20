"""
학습/검증 곡선 저장, 최종 테스트 평가(confusion matrix, precision/recall/F1),
none 오분류 분석 및 시각화.
학습 결과와 테스트 결과를 계산하고 그래프로 저장한다.
"""
import warnings

import numpy as np
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import config
from data_utils import compute_density

# 한글 폰트 설정 (Windows 기준 맑은 고딕) + 경고 억제
# -> 이 모듈을 import하는 어떤 스크립트(main.py, test_only.py 등)에서든 항상 적용되도록
#    evaluate.py 쪽에 둠 (예전엔 main.py에만 있어서 test_only.py에서 빠져있었음)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
warnings.filterwarnings('ignore', message='Glyph .* missing from font')


def save_training_curves(history, best_epoch, epochs, path=config.TRAINING_CURVES_PATH):
    print("\n=== 10. 학습/검증 곡선 저장 ===")
    # Early Stopping으로 중간에 멈추면 history가 epochs보다 짧을 수 있음 -> 실제 길이 기준으로 그림
    actual_epochs = len(history['train_loss'])
    epochs_range = range(1, actual_epochs + 1)

    has_f1 = 'val_macro_f1' in history
    fig, axes = plt.subplots(1, 3 if has_f1 else 2, figsize=(21 if has_f1 else 14, 5))

    axes[0].plot(epochs_range, history['train_loss'], label='Train Loss', marker='o')
    axes[0].plot(epochs_range, history['val_loss'], label='Val Loss', marker='s')
    axes[0].axvline(x=best_epoch, color='green', linestyle='--', alpha=0.7,
                     label=f'Best Epoch ({best_epoch})')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Train vs Val Loss')
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot(epochs_range, history['train_acc'], label='Train Acc', marker='o')
    axes[1].plot(epochs_range, history['val_acc'], label='Val Acc', marker='s')
    axes[1].axvline(x=best_epoch, color='green', linestyle='--', alpha=0.7,
                     label=f'Best Epoch ({best_epoch})')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title('Train vs Val Accuracy')
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    if has_f1:
        axes[2].plot(epochs_range, history['val_macro_f1'], label='Val Macro F1', marker='^', color='darkorange')
        axes[2].axvline(x=best_epoch, color='green', linestyle='--', alpha=0.7,
                         label=f'Best Epoch ({best_epoch})')
        axes[2].set_xlabel('Epoch')
        axes[2].set_ylabel('Macro F1')
        axes[2].set_title('Val Macro F1 (best_epoch 선정 기준)')
        axes[2].legend()
        axes[2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(path, dpi=100)
    plt.close()
    print(f"-> {path} 저장 완료")


def run_test_inference(model, test_loader, device):
    """test set 전체에 대해 예측 실행 -> (all_preds, all_labels)"""
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for xb, yb in test_loader:
            xb = xb.to(device)
            out = model(xb)
            pred = out.argmax(dim=1).cpu().numpy()
            all_preds.extend(pred)
            all_labels.extend(yb.numpy())
    return np.array(all_preds), np.array(all_labels)


def compute_confusion_and_metrics(all_preds, all_labels, num_classes, reverse_label_mapping):
    print("\n=== 11. 최종 테스트 평가 (test set, 최초 접촉) ===")
    conf_matrix = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(all_labels, all_preds):
        conf_matrix[t, p] += 1

    print("Confusion Matrix (행: 실제, 열: 예측)")
    print(conf_matrix)

    per_class_precision = np.zeros(num_classes)
    per_class_recall = np.zeros(num_classes)
    per_class_f1 = np.zeros(num_classes)

    print(f"\n{'클래스':<12}{'Precision':<12}{'Recall':<12}{'F1':<12}")
    for c in range(num_classes):
        tp = conf_matrix[c, c]
        fp = conf_matrix[:, c].sum() - tp
        fn = conf_matrix[c, :].sum() - tp
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        per_class_precision[c] = precision
        per_class_recall[c] = recall
        per_class_f1[c] = f1
        print(f"{reverse_label_mapping[c]:<12}{precision:<12.4f}{recall:<12.4f}{f1:<12.4f}")

    overall_acc = (all_preds == all_labels).mean()
    macro_f1 = per_class_f1.mean()
    print(f"\n전체 정확도(micro): {overall_acc:.4f}")
    print(f"Macro F1 (클래스별 단순 평균, 다수 클래스 가중치 없음): {macro_f1:.4f}")

    return conf_matrix, per_class_precision, per_class_recall, per_class_f1, overall_acc, macro_f1


def analyze_none_misclassification(all_preds, all_labels, test_df, label_mapping, none_idx,
                                     path=config.MISCLASSIFIED_SAMPLES_PATH):
    print("\n=== 11-1. none 오분류 샘플 확인 ===")
    target_confusions = config.TARGET_CONFUSIONS
    none_true_mask = (all_labels == none_idx)

    fig, axes = plt.subplots(len(target_confusions), 6, figsize=(18, 9))
    for row, target_name in enumerate(target_confusions):
        target_class_idx = label_mapping[target_name]
        mis_mask = none_true_mask & (all_preds == target_class_idx)
        mis_indices = np.where(mis_mask)[0]
        print(f"-> none을 {target_name}(으)로 오분류: {len(mis_indices)}건")

        n_show = min(6, len(mis_indices))
        for col in range(6):
            ax = axes[row, col]
            if col < n_show:
                idx = mis_indices[col]
                img = test_df.iloc[idx]['waferMap_resized']
                ax.imshow(img, cmap='inferno')
                ax.set_title(f"실제:none\n예측:{target_name}", fontsize=9)
            ax.axis('off')

    plt.suptitle('none이 오분류된 실제 웨이퍼 이미지 (각 행: 오분류 대상 클래스)', fontsize=13)
    plt.tight_layout()
    plt.savefig(path, dpi=100)
    plt.close()
    print(f"-> {path} 저장 완료")

    return none_true_mask


def analyze_none_density(all_preds, none_true_mask, test_df, label_mapping,
                          path=config.DENSITY_COMPARISON_PATH):
    """none 오분류 vs 정분류 샘플의 불량 다이 밀도 비교 (라벨 경계 사례 가설 검증)"""
    print("\n=== 12-2. none 오분류 vs 정분류 밀도 비교 ===")
    target_confusions = config.TARGET_CONFUSIONS
    none_idx = label_mapping['none']

    misclassified_idx = np.where(
        none_true_mask & np.isin(all_preds, [label_mapping[t] for t in target_confusions])
    )[0]
    correct_idx = np.where(none_true_mask & (all_preds == none_idx))[0]

    mis_density = np.array([compute_density(test_df.iloc[i]['waferMap_resized']) for i in misclassified_idx])
    correct_density = np.array([compute_density(test_df.iloc[i]['waferMap_resized']) for i in correct_idx])

    if len(mis_density) == 0 or len(correct_density) == 0:
        print(f"-> 오분류 {len(mis_density)}개 / 정분류 {len(correct_density)}개 -> "
              f"표본 부족으로 밀도 비교 스킵 (테스트셋이 작을 때 정상적으로 발생 가능)")
        return

    print(f"-> 오분류된 none 샘플 ({len(mis_density)}개): 평균 밀도 {mis_density.mean():.4f}, 중앙값 {np.median(mis_density):.4f}")
    print(f"-> 정분류된 none 샘플 ({len(correct_density)}개): 평균 밀도 {correct_density.mean():.4f}, 중앙값 {np.median(correct_density):.4f}")
    print(f"-> 배율: 오분류 그룹이 정분류 그룹보다 평균 밀도 {mis_density.mean() / (correct_density.mean() + 1e-9):.2f}배")

    try:
        from scipy import stats
        stat, pvalue = stats.mannwhitneyu(mis_density, correct_density, alternative='greater')
        print(f"-> Mann-Whitney U 검정 (오분류 밀도 > 정분류 밀도): p-value={pvalue:.6f}")
        print("   (p < 0.05면 두 그룹 밀도 차이가 통계적으로 유의미 -> 라벨 경계 사례 가설 뒷받침)")
    except ImportError:
        print("-> scipy 미설치로 통계 검정은 생략, 평균/중앙값 비교로만 판단")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot([correct_density, mis_density], tick_labels=['정분류 (none)', '오분류 (none->Loc/Scratch/Edge-Loc)'])
    ax.set_ylabel('불량 다이 밀도')
    ax.set_title('none 샘플 밀도 비교: 정분류 vs 오분류')
    ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(path, dpi=100)
    plt.close()
    print(f"-> {path} 저장 완료")


def save_evaluation_plots(conf_matrix, per_class_precision, per_class_recall, per_class_f1,
                           num_classes, reverse_label_mapping, path=config.TEST_EVALUATION_PATH):
    """컨퓨전 매트릭스 히트맵 + 클래스별 지표 바 차트"""
    print("\n=== 12. 평가 그래프 저장 ===")
    class_names = [reverse_label_mapping[c] for c in range(num_classes)]
    conf_matrix_norm = conf_matrix.astype(float) / conf_matrix.sum(axis=1, keepdims=True)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    im = axes[0].imshow(conf_matrix_norm, cmap='Blues', vmin=0, vmax=1)
    axes[0].set_xticks(range(num_classes))
    axes[0].set_yticks(range(num_classes))
    axes[0].set_xticklabels(class_names, rotation=45, ha='right')
    axes[0].set_yticklabels(class_names)
    axes[0].set_xlabel('예측 라벨')
    axes[0].set_ylabel('실제 라벨')
    axes[0].set_title('Confusion Matrix (행 기준 정규화)')
    for i in range(num_classes):
        for j in range(num_classes):
            val = conf_matrix_norm[i, j]
            color = 'white' if val > 0.5 else 'black'
            axes[0].text(j, i, f"{val:.2f}", ha='center', va='center', color=color, fontsize=8)
    fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)

    x_pos = np.arange(num_classes)
    width = 0.25
    axes[1].bar(x_pos - width, per_class_precision, width, label='Precision')
    axes[1].bar(x_pos, per_class_recall, width, label='Recall')
    axes[1].bar(x_pos + width, per_class_f1, width, label='F1')
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(class_names, rotation=45, ha='right')
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title('클래스별 Precision / Recall / F1')
    axes[1].legend()
    axes[1].grid(alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(path, dpi=100)
    plt.close()
    print(f"-> {path} 저장 완료")