export default function SemiBg() {
  const cx = 500, cy = 500, R = 420;
  const dieSize = 42;

  const hLines = [];
  const vLines = [];
  for (let y = cy - R; y <= cy + R; y += dieSize) {
    hLines.push(<line key={`h${y}`} x1={cx - R} y1={y} x2={cx + R} y2={y} stroke="#1a56db" strokeWidth="0.5" />);
  }
  for (let x = cx - R; x <= cx + R; x += dieSize) {
    vLines.push(<line key={`v${x}`} x1={x} y1={cy - R} x2={x} y2={cy + R} stroke="#1a56db" strokeWidth="0.5" />);
  }

  const rings = [0.96, 0.82, 0.65, 0.46, 0.28];

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none select-none">
      <svg
        className="absolute"
        style={{ top: "50%", left: "50%", transform: "translate(-50%, -50%)", width: "min(110vw, 110vh)", height: "min(110vw, 110vh)" }}
        viewBox="0 0 1000 1000"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
      >
        <defs>
          <clipPath id="waferClip">
            <circle cx={cx} cy={cy} r={R} />
          </clipPath>
          <radialGradient id="waferFill" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#dbeafe" stopOpacity="0.18" />
            <stop offset="60%" stopColor="#e0e7ff" stopOpacity="0.10" />
            <stop offset="100%" stopColor="#c7d2fe" stopOpacity="0.04" />
          </radialGradient>
          <radialGradient id="sheen" cx="38%" cy="32%" r="55%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
          </radialGradient>
        </defs>

        <circle cx={cx} cy={cy} r={R} fill="url(#waferFill)" />
        <circle cx={cx} cy={cy} r={R} fill="url(#sheen)" />

        <g clipPath="url(#waferClip)" opacity="0.18">
          {hLines}
          {vLines}
        </g>

        {rings.map((f, i) => (
          <circle
            key={i}
            cx={cx} cy={cy} r={R * f}
            fill="none"
            stroke="#1a56db"
            strokeWidth={i === 0 ? "0.6" : "0.4"}
            strokeDasharray={i > 0 ? "4 6" : "none"}
            opacity="0.12"
          />
        ))}

        <circle cx={cx} cy={cy + R} r={14} fill="#f0f2f6" />
        <circle cx={cx} cy={cy} r={R} stroke="#1a56db" strokeWidth="1.2" opacity="0.2" />

        <line x1={cx - 24} y1={cy} x2={cx + 24} y2={cy} stroke="#1a56db" strokeWidth="0.8" opacity="0.2" />
        <line x1={cx} y1={cy - 24} x2={cx} y2={cy + 24} stroke="#1a56db" strokeWidth="0.8" opacity="0.2" />
        <circle cx={cx} cy={cy} r={4} fill="#1a56db" opacity="0.15" />

        <line x1={cx - R} y1={cy + R + 24} x2={cx + R} y2={cy + R + 24} stroke="#1a56db" strokeWidth="0.6" opacity="0.14" />
        <line x1={cx - R} y1={cy + R + 18} x2={cx - R} y2={cy + R + 30} stroke="#1a56db" strokeWidth="0.6" opacity="0.14" />
        <line x1={cx + R} y1={cy + R + 18} x2={cx + R} y2={cy + R + 30} stroke="#1a56db" strokeWidth="0.6" opacity="0.14" />
        <text x={cx} y={cy + R + 42} textAnchor="middle" fontSize="11" fill="#1a56db" opacity="0.2" fontFamily="DM Mono, monospace" letterSpacing="2">Φ 300mm</text>

        <text x={cx + R + 14} y={cy + 4} fontSize="10" fill="#1a56db" opacity="0.18" fontFamily="DM Mono, monospace">0°</text>
        <text x={cx - 16} y={cy - R - 12} fontSize="10" fill="#1a56db" opacity="0.18" fontFamily="DM Mono, monospace" textAnchor="middle">90°</text>
      </svg>
    </div>
  );
}
