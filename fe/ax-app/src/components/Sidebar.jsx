import { LogOut, LayoutDashboard, ScanLine, ClipboardList } from "lucide-react";
import DeviceLogo from "./DeviceLogo.jsx";

export default function Sidebar({ active, onNavigate, onLogout, session }) {
  const navItems = [
    { id: "dashboard", label: "대시보드", icon: LayoutDashboard },
    { id: "results",   label: "분석 결과", icon: ScanLine },
    { id: "history",   label: "검사 이력", icon: ClipboardList },
  ];

  const initial = (session.name || session.email || "?").slice(0, 1);

  return (
    <aside className="w-56 flex-shrink-0 flex flex-col bg-white border-r border-gray-200">
      <div className="px-5 pt-6 pb-4">
        <DeviceLogo className="h-7 w-auto" />
        <div className="mt-1.5 text-[14px] tracking-wide text-gray-400">
          Wafer Inspection AI
        </div>
      </div>

      <nav className="flex-1 px-3 py-2 space-y-0.5">
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 text-[16px] rounded-lg transition-all ${
              active === id
                ? "text-blue-600 font-medium bg-blue-50"
                : "text-gray-500 hover:text-gray-800 hover:bg-gray-100"
            }`}
          >
            <Icon size={15} strokeWidth={active === id ? 2.2 : 1.8} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="px-3 py-4 border-t border-gray-200">
        <div className="flex items-center gap-2.5 px-3 py-2">
          <div className="w-7 h-7 rounded-full bg-blue-500 flex items-center justify-center text-white text-[14px] font-bold flex-shrink-0">
            {initial}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-[16px] font-medium truncate text-gray-700">
              {session.name || session.email}
            </div>
            <div className="text-[13px] truncate text-gray-400">{session.email}</div>
          </div>
          <button onClick={onLogout} className="text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0">
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </aside>
  );
}
