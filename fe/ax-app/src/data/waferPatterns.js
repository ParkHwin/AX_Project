export const DEFECT_CLASSES = [
  { key: "Center", color: "#ef4444", description: "중앙부에 결함이 집중되는 패턴" },
  { key: "Donut", color: "#f97316", description: "중심 주변에 도넛 형태로 결함이 분포하는 패턴" },
  { key: "Edge-Loc", color: "#eab308", description: "가장자리 한 지점에 결함이 국소적으로 몰리는 패턴" },
  { key: "Edge-Ring", color: "#8b5cf6", description: "최외곽 테두리 전체에 결함이 형성되는 패턴" },
  { key: "Loc", color: "#06b6d4", description: "내부 특정 영역에 결함이 국소적으로 몰리는 패턴" },
  { key: "Near-full", color: "#dc2626", description: "웨이퍼 전면에 걸쳐 결함이 발생하는 심각한 패턴" },
  { key: "Random", color: "#a855f7", description: "규칙 없이 결함이 무작위로 분포하는 패턴" },
  { key: "Scratch", color: "#f43f5e", description: "긁힘 형태로 결함이 선형으로 이어지는 패턴" },
  { key: "none", color: "#10b981", description: "특이 패턴이 없는 정상 웨이퍼" },
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

// Deterministic pseudo-random in [0,1) so the generated wafer pattern is stable across re-renders.
function noise(i, j) {
  const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453;
  return x - Math.floor(x);
}

export function generateWaferDies(patternKey, gridN = 23) {
  const dies = [];
  const half = (gridN - 1) / 2;

  for (let i = 0; i < gridN; i++) {
    for (let j = 0; j < gridN; j++) {
      const nx = (i - half) / half;
      const ny = (j - half) / half;
      const dist = Math.sqrt(nx * nx + ny * ny);
      if (dist > 1.04) continue;

      const n = noise(i, j);
      const angle = Math.atan2(ny, nx);
      let fail = n < 0.03;

      switch (patternKey) {
        case "Center":
          if (dist < 0.32) fail = n < 0.85;
          break;
        case "Donut":
          if (dist > 0.42 && dist < 0.68) fail = n < 0.8;
          break;
        case "Edge-Loc":
          if (dist > 0.72 && angle > -0.9 && angle < 0.3) fail = n < 0.85;
          break;
        case "Edge-Ring":
          if (dist > 0.86) fail = n < 0.88;
          break;
        case "Loc":
          if (dist > 0.25 && dist < 0.55 && angle > 0.3 && angle < 1.6) fail = n < 0.85;
          break;
        case "Near-full":
          fail = n < 0.82;
          break;
        case "Random":
          fail = n < 0.32;
          break;
        case "Scratch": {
          const theta = 0.7;
          const proj = nx * Math.sin(theta) - ny * Math.cos(theta);
          if (Math.abs(proj) < 0.09) fail = n < 0.8;
          break;
        }
        case "none":
        default:
          break;
      }

      dies.push({ i, j, nx, ny, fail });
    }
  }

  return dies;
}

export function classifyWafer() {
  const topClass = pickWeightedClass();
  const probabilities = buildProbabilities(topClass);
  const topColor = CLASS_COLOR[topClass];
  const isFail = topClass !== "none";

  const dies = generateWaferDies(topClass);
  const totalDies = dies.length;
  const failDies = dies.filter((d) => d.fail).length;
  const yieldPct = (((totalDies - failDies) / totalDies) * 100).toFixed(1);
  const sortedProbs = [...probabilities].sort((a, b) => b.prob - a.prob);
  const runnerUp = sortedProbs[1];

  return { topClass, topColor, isFail, totalDies, failDies, yieldPct, sortedProbs, runnerUp };
}
