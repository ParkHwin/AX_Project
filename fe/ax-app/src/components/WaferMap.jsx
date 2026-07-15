import { generateWaferDies } from "../data/waferPatterns.js";

export default function WaferMap({ pattern = "none", failColor = "#ef4444" }) {
  const cx = 130, cy = 130, r = 112;
  const gridN = 23;
  const dieSize = (r * 2) / gridN;

  const dies = generateWaferDies(pattern, gridN);

  return (
    <svg viewBox="0 0 260 260" className="w-full h-full">
      <defs>
        <radialGradient id="wg" cx="40%" cy="35%">
          <stop offset="0%" stopColor="#f8fafc" />
          <stop offset="70%" stopColor="#f1f5f9" />
          <stop offset="100%" stopColor="#e2e8f0" />
        </radialGradient>
        <clipPath id="wc"><circle cx={cx} cy={cy} r={r} /></clipPath>
      </defs>
      <circle cx={cx} cy={cy} r={r} fill="url(#wg)" />

      <g clipPath="url(#wc)">
        {dies.map((d) => (
          <rect
            key={`${d.i}-${d.j}`}
            x={cx + d.nx * r - dieSize / 2 + 0.5}
            y={cy + d.ny * r - dieSize / 2 + 0.5}
            width={Math.max(dieSize - 1, 1)}
            height={Math.max(dieSize - 1, 1)}
            fill={d.fail ? failColor : "#7fa8d9"}
            opacity={d.fail ? 0.92 : 0.55}
          />
        ))}
      </g>

      {[0.88, 0.66, 0.42].map((f, i) => (
        <circle key={i} cx={cx} cy={cy} r={r * f} fill="none" stroke="#c8d4e0" strokeWidth="0.5" strokeDasharray="3 3" />
      ))}
      <circle cx={cx} cy={cy + r} r={7} fill="#f5f6f8" />
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#94a3b8" strokeWidth="1.5" />
      <line x1={cx - 9} y1={cy} x2={cx + 9} y2={cy} stroke="#94a3b8" strokeWidth="0.7" />
      <line x1={cx} y1={cy - 9} x2={cx} y2={cy + 9} stroke="#94a3b8" strokeWidth="0.7" />
      <circle cx={cx} cy={cy} r={2} fill="#94a3b8" />
    </svg>
  );
}
