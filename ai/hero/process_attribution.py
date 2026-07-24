"""
process_attribution.py
결함 클래스별 원인공정 후보 목록.

evidence_type:
  LIT  — 학술 문헌에서 직접 근거를 확인한 항목
  EXP  — 문헌 방향성 참고 또는 공정 전문가 경험칙 기반 추정
         (화면에 "추정치"로 명시 권장)
"""

PRIOR: dict[str, list[dict]] = {
    "Center": [
        {
            "process": "박막 증착 (Deposition)",
            "sub_processes": [
                "CVD 챔버 온도 불균일",
                "스퍼터링 타겟 수명 저하",
                "가스 유량 편차",
            ],
            "weight": 0.90,
            "evidence_type": "LIT",
            "citations": ["Yu & Lu, 2016", "Shin et al., 2024"],
            "note": None,
        },
        {
            "process": "증착 후 세정 (Post-Deposition Clean)",
            "sub_processes": [
                "중심부 잔류 파티클",
                "화학약품 농도 편차",
            ],
            "weight": 0.10,
            "evidence_type": "EXP",
            "citations": [],
            "note": "추정치 — 문헌 직접 근거 없음",
        },
    ],
    "Scratch": [
        {
            "process": "웨이퍼 반송 (Handling/Transport)",
            "sub_processes": [
                "로봇 암 정렬 오차",
                "카세트 슬롯 마모",
                "진공 흡착 불량",
            ],
            "weight": 0.60,
            "evidence_type": "LIT",
            "citations": ["Yu & Lu, 2016", "Shin et al., 2024"],
            "note": None,
        },
        {
            "process": "평탄화 (CMP)",
            "sub_processes": [
                "슬러리 입자 크기 편차",
                "패드 컨디셔닝 불량",
                "다운포스 과부하",
            ],
            "weight": 0.40,
            "evidence_type": "LIT",
            "citations": ["Yu & Lu, 2016"],
            "note": None,
        },
    ],
    "Edge-Ring": [
        {
            "process": "식각 (Etch)",
            "sub_processes": [
                "플라즈마 엣지 집중",
                "척 정전기 분포 이상",
                "가스 링 노즐 막힘",
            ],
            "weight": 0.50,
            "evidence_type": "LIT",
            "citations": ["Yu & Lu, 2016"],
            "note": "⚠ 문헌 간 이견: 구세대 문헌 기준. 최신 문헌(Shin et al., 2024)은 RTP 온도 이상을 원인으로 봄",
        },
        {
            "process": "급속열처리 (RTP)",
            "sub_processes": [
                "엣지 램프 온도 편차",
                "웨이퍼 회전 불균일",
                "챔버 벽면 방사율 차이",
            ],
            "weight": 0.50,
            "evidence_type": "LIT",
            "citations": ["Shin et al., 2024"],
            "note": "⚠ 문헌 간 이견: 최신 문헌 기준. 구세대 문헌(Yu & Lu, 2016)은 식각 이상을 원인으로 봄",
        },
    ],
    "Donut": [
        {
            "process": "세정/현상 (Clean/Develop)",
            "sub_processes": [
                "포토레지스트 잔여물 재부착",
                "현상액 온도 불균일",
                "린스 불충분",
            ],
            "weight": 0.90,
            "evidence_type": "LIT",
            "citations": ["Shin et al., 2024"],
            "note": None,
        },
        {
            "process": "도포 (Coating)",
            "sub_processes": [
                "스핀 코팅 회전수 이상",
                "레지스트 점도 편차",
            ],
            "weight": 0.10,
            "evidence_type": "EXP",
            "citations": [],
            "note": "추정치 — 문헌 직접 근거 없음",
        },
    ],
    "Edge-Loc": [
        {
            "process": "확산 (Diffusion)",
            "sub_processes": [
                "가열 불균일 (엣지 집중)",
                "엣지 배제 영역 설정 오류",
            ],
            "weight": 0.60,
            "evidence_type": "LIT",
            "citations": ["Hansen, Nair & Friedman, 1997", "Shin et al., 2024"],
            "note": None,
        },
        {
            "process": "로드락 (Load-lock)",
            "sub_processes": [
                "밸브 불순물 유입",
                "압력 전환 충격",
            ],
            "weight": 0.40,
            "evidence_type": "LIT",
            "citations": ["Hansen, Nair & Friedman, 1997"],
            "note": None,
        },
    ],
    "Loc": [
        {
            "process": "진공 설비 (Vacuum Equipment)",
            "sub_processes": [
                "슬릿밸브 누출",
                "펌프 이상",
                "설비 진동",
            ],
            "weight": 0.90,
            "evidence_type": "LIT",
            "citations": ["Hansen & Thyregod, 1998", "Shin et al., 2024"],
            "note": None,
        },
        {
            "process": "챔버 오염 (Chamber Contamination)",
            "sub_processes": [
                "파티클 낙하",
                "챔버 내벽 박리",
            ],
            "weight": 0.10,
            "evidence_type": "EXP",
            "citations": [],
            "note": "추정치 — 문헌 직접 근거 없음",
        },
    ],
    "Near-full": [
        {
            "process": "이온주입 (Ion Implant)",
            "sub_processes": [
                "플라즈마 전자 과충전",
                "포토레지스트 파열",
                "빔 전류 과부하",
            ],
            "weight": 0.90,
            "evidence_type": "LIT",
            "citations": ["Shin et al., 2024"],
            "note": None,
        },
        {
            "process": "포토레지스트 도포 (PR Coating)",
            "sub_processes": [
                "PR 두께 과부족",
                "경화 불완전",
            ],
            "weight": 0.10,
            "evidence_type": "EXP",
            "citations": [],
            "note": "추정치 — 문헌 직접 근거 없음",
        },
    ],
    "Random": [
        {
            "process": "가스/유체 분출 (Gas/Fluid Ejection)",
            "sub_processes": [
                "진공 불안정",
                "가스 라인 이상",
                "파티클 오염",
            ],
            "weight": 0.70,
            "evidence_type": "EXP",
            "citations": ["Shin et al., 2024 (방향성 참고)"],
            "note": "⚠ 추정치 — 단일 원인 특정 불가. 복합 요인으로 추정 (Shin et al., 2024)",
        },
        {
            "process": "공정 간 오염 (Cross-contamination)",
            "sub_processes": [
                "이전 공정 잔류물",
                "설비 간 오염",
            ],
            "weight": 0.30,
            "evidence_type": "EXP",
            "citations": [],
            "note": "추정치 — 문헌 직접 근거 없음",
        },
    ],
    "none": [],  # 정상 웨이퍼 — 원인공정 개념 해당 없음
}


def process_given_pattern(class_name: str) -> list[dict]:
    """class_name에 해당하는 원인공정 후보를 weight 내림차순으로 반환."""
    candidates = PRIOR.get(class_name, [])
    return sorted(candidates, key=lambda x: x["weight"], reverse=True)
