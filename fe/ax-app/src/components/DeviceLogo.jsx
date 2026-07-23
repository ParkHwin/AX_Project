export default function DeviceLogo({ className, dark = false }) {
  const ink = dark ? "#ffffff" : "#0f1923";
  const bg  = dark ? "#0f172a" : "white";
  return (
    <svg viewBox="-2 0 213 52" className={className} xmlns="http://www.w3.org/2000/svg" fill="none">
      <path d="M0 4h12c14 0 22 9 22 22s-8 22-22 22H0V4z" fill={ink} />
      <path d="M10 13h2c8 0 13 5 13 13s-5 13-13 13h-2V13z" fill={bg} />
      <rect x="40" y="4" width="28" height="9" fill={ink} />
      <rect x="40" y="4" width="9" height="44" fill={ink} />
      <rect x="40" y="39" width="28" height="9" fill={ink} />
      <rect x="40" y="21" width="22" height="9" fill="#38bdf8" />
      <polygon points="74,4 85,4 95,36 105,4 118,4 101,48 89,48" fill={ink} />
      <rect x="124" y="4" width="10" height="44" fill={ink} />
      <path d="M140 26c0-13 9-23 21-23 7 0 13 3 17 8l-7 7c-3-3-6-5-10-5-7 0-12 6-12 13s5 13 12 13c4 0 7-2 10-5l7 7c-4 5-10 8-17 8-12 0-21-10-21-23z" fill={ink} />
      <rect x="181" y="4" width="28" height="9" fill={ink} />
      <rect x="181" y="4" width="9" height="44" fill={ink} />
      <rect x="181" y="39" width="28" height="9" fill={ink} />
      <rect x="181" y="21" width="22" height="9" fill="#38bdf8" />
    </svg>
  );
}
