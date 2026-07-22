import { Home, BarChart2, Layers, LogOut } from "lucide-react";
import DeviceLogo from "./DeviceLogo.jsx";

export default function Sidebar({ active, onNavigate, onLogout, session }) {
  const navItems = [
    { id: "dashboard", icon: Home, label: "대시보드" },
    { id: "results", icon: BarChart2, label: "분석 결과" },
    { id: "history", icon: Layers, label: "검사 이력" },
  ];

  const initial = (session.name || session.email || "?").slice(0, 1);

  return (
    <aside className="w-64 flex-shrink-0 flex flex-col bg-white border-r border-gray-100">
      <div className="px-6 py-6">
        <DeviceLogo className="h-8 w-auto" />
        <div className="mt-1.5 text-[11px] text-gray-400 tracking-wide">
          Wafer Inspection AI
        </div>
      </div>

      <nav className="flex-1 px-4 py-2 space-y-1">
        {navItems.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={`w-full flex items-center gap-3 pl-3.5 pr-3 py-2.5 text-[13px] rounded-lg border-l-[3px] transition-all ${
              active === id
                ? "border-blue-500 text-blue-600 font-semibold bg-blue-50/60"
                : "border-transparent text-gray-500 hover:text-gray-800 hover:bg-gray-50"
            }`}
          >
            <Icon size={16} strokeWidth={1.8} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="px-4 py-4">
        <div className="bg-blue-50/70 border border-blue-100 rounded-2xl p-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-white border border-blue-200 flex items-center justify-center text-blue-600 text-[13px] font-bold flex-shrink-0">
            {initial}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-gray-800 text-[13px] font-medium truncate">
              {session.name || session.email}
            </div>
            <div className="text-gray-400 text-[11px] truncate">{session.email}</div>
          </div>
          <button onClick={onLogout} className="text-gray-400 hover:text-blue-600 transition-colors flex-shrink-0">
            <LogOut size={15} />
          </button>
        </div>
      </div>
    </aside>
  );
}
