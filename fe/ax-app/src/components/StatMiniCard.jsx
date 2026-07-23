export default function StatMiniCard({ label, value, unit, labelColor }) {
  return (
    <div className="flex flex-col gap-1 px-5 py-4 bg-white rounded-xl border border-gray-100">
      <span className="text-[14px] font-medium uppercase tracking-wide" style={{ color: labelColor ?? "#6b7280" }}>{label}</span>
      <div className="flex items-baseline gap-1 mt-1">
        <span className="text-[22px] font-bold leading-none" style={{ color: labelColor ?? "#111827" }}>{value}</span>
        {unit && <span className="text-[15px]" style={{ color: labelColor ? `${labelColor}99` : "#6b7280" }}>{unit}</span>}
      </div>
    </div>
  );
}
