export default function StatMiniCard({ icon: Icon, iconBg, iconColor, label, value, unit, progress, progressColor }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5">
      <div className="flex items-center gap-2.5 mb-4">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: iconBg }}>
          <Icon size={16} style={{ color: iconColor }} />
        </div>
        <span className="text-[13px] text-gray-500 truncate">{label}</span>
      </div>
      <div className="flex items-baseline gap-1 mb-3">
        <span className="text-[26px] font-bold text-gray-900 leading-none">{value}</span>
        {unit && <span className="text-gray-400 text-[13px]">{unit}</span>}
      </div>
      <div className="h-1.5 rounded-full bg-gray-100 overflow-hidden">
        <div className="h-full rounded-full" style={{ width: `${Math.min(Math.max(progress, 2), 100)}%`, background: progressColor }} />
      </div>
    </div>
  );
}
