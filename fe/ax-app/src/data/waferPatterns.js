export const DEFECT_CLASSES = [
  {
    key: "Center",
    color: "#ef4444",
    description: "중앙부에 결함이 집중되는 패턴",
    cause: "박막 증착(thin film deposition) 단계의 문제",
    reference: "Wang, Kuo & Bensmail (2006), IIE Transactions; PMC10272367; Chen et al. (2023)",
    reliability: "저널논문, 여러 문헌 교차확인",
    subtypes: [
      { label: "완전 대칭 방사형 (center-high)", detail: "RF 정재파 효과 — VHF 30 MHz 이상 대역" },
      { label: "좌우 비대칭", detail: "구형 챔버의 터보펌프 측면 배치" },
    ],
    subtypeNote: "Semiconductor Digest 기고, US Patent 9385021 — 업계매체·특허 (저널논문보다 신뢰도 낮음)",
  },
  {
    key: "Donut",
    color: "#f97316",
    description: "중심 주변에 도넛 형태로 결함이 분포하는 패턴",
    cause: "용해된 포토레지스트가 웨이퍼 표면에 재증착",
    reference: "Chen et al. (2023), Expert Systems with Applications",
    reliability: "저널논문 1건 (원출처 표기 없음)",
  },
  {
    key: "Edge-Loc",
    color: "#eab308",
    description: "가장자리 한 지점에 결함이 국소적으로 몰리는 패턴",
    cause: "확산(diffusion) 공정 중 불균일한 가열",
    reference: "Hansen, Nair & Friedman (1997)",
    reliability: "원 저자 직접 인용, 다수 문헌 교차확인",
  },
  {
    key: "Edge-Ring",
    color: "#8b5cf6",
    description: "최외곽 테두리 전체에 결함이 형성되는 패턴",
    cause: "비정상적인 에칭(etching) 작업",
    reference: "Chen et al. (2023); Wang et al. (2019) 계열",
    reliability: "저널논문, 여러 문헌 교차확인",
  },
  {
    key: "Loc",
    color: "#06b6d4",
    description: "내부 특정 영역에 결함이 국소적으로 몰리는 패턴",
    cause: "특정 기계의 과도한 진동",
    reference: "Hansen & Thyregod (1998)",
    reliability: "원 저자 직접 인용",
  },
  {
    key: "Near-full",
    color: "#dc2626",
    description: "웨이퍼 전면에 걸쳐 결함이 발생하는 심각한 패턴",
    cause: "웨이퍼 수령 불량 (대부분 다이 불량)",
    reference: "Chen et al. (2023), Expert Systems with Applications",
    reliability: "저널논문 1건 (원출처 표기 없음)",
  },
  {
    key: "Random",
    color: "#a855f7",
    description: "규칙 없이 결함이 무작위로 분포하는 패턴",
    cause: "공기 중 입자 등 환경 요인 — 특정 공정 결함이 아님",
    reference: "Yuan, Kuo & Bae (2011), IEEE Trans. Semicond. Manuf.",
    reliability: "원 저자 직접 인용",
  },
  {
    key: "Scratch",
    color: "#f43f5e",
    description: "긁힘 형태로 결함이 선형으로 이어지는 패턴",
    cause: "운송·취급 중 인적 오류 또는 CMP 단계 결함",
    reference: "Chen et al. (2023), Expert Systems with Applications",
    reliability: "저널논문 1건",
    subtypes: [
      { label: "구불구불·불규칙", detail: "사람 취급 오류" },
      { label: "직선·호 반복", detail: "로봇" },
      { label: "고립된 긴 스크래치 + 혜성꼬리", detail: "CMP 슬러리" },
      { label: "호형 + 패드 회전방향 추종", detail: "CMP 패드" },
    ],
    subtypeNote: "SemiEngineering, JEES — 업계 기술문서 (동료심사 아님)",
  },
  {
    key: "none",
    color: "#10b981",
    description: "특이 패턴이 없는 정상 웨이퍼",
    cause: null,
    reference: null,
    reliability: null,
  },
];

export const CLASS_COLOR = Object.fromEntries(DEFECT_CLASSES.map((c) => [c.key, c.color]));

// Relative sampling weights modeled after the real-world class distribution of the
// WM-811K wafer map dataset (most wafers are normal; some defect patterns are rarer than others).
const CLASS_WEIGHTS = {
  none: 147431,
  "Edge-Ring": 9680,
  "Edge-Loc": 5189,
  Center: 4294,
  Loc: 3593,
  Scratch: 1193,
  Random: 866,
  Donut: 555,
  "Near-full": 149,
};

function pickWeightedClass() {
  const entries = Object.entries(CLASS_WEIGHTS);
  const total = entries.reduce((sum, [, w]) => sum + w, 0);
  let r = Math.random() * total;
  for (const [key, w] of entries) {
    if (r < w) return key;
    r -= w;
  }
  return entries[entries.length - 1][0];
}

function randomInRange(min, max) {
  return min + Math.random() * (max - min);
}

function buildProbabilities(topClass) {
  const topProb = topClass === "none" ? randomInRange(92, 99.2) : randomInRange(62, 96);
  const others = DEFECT_CLASSES.map((c) => c.key).filter((k) => k !== topClass);
  const remaining = 100 - topProb;
  const shares = others.map(() => Math.random());
  const shareTotal = shares.reduce((a, b) => a + b, 0);

  const probabilities = [
    { key: topClass, prob: Math.round(topProb * 10) / 10 },
    ...others.map((key, i) => ({ key, prob: Math.round(((shares[i] / shareTotal) * remaining) * 10) / 10 })),
  ];

  // Nudge the smallest non-top entry so the total lands exactly on 100.0.
  const drift = Math.round((100 - probabilities.reduce((a, p) => a + p.prob, 0)) * 10) / 10;
  const smallest = [...probabilities].filter((p) => p.key !== topClass).sort((a, b) => a.prob - b.prob)[0];
  return probabilities.map((p) => (p.key === smallest.key ? { ...p, prob: Math.max(Math.round((p.prob + drift) * 10) / 10, 0.1) } : p));
}

export function classifyWafer() {
  const topClass = pickWeightedClass();
  const probabilities = buildProbabilities(topClass);
  const topColor = CLASS_COLOR[topClass];
  const isFail = topClass !== "none";

  const sortedProbs = [...probabilities].sort((a, b) => b.prob - a.prob);
  const runnerUp = sortedProbs[1];

  return { topClass, topColor, isFail, sortedProbs, runnerUp };
}
