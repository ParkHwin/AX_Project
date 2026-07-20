import { Search } from "lucide-react";

export default function SearchHeader({ title, placeholder = "검색" }) {
  return (
    <div className="flex items-center justify-between gap-6 mb-6 flex-wrap">
      <h1 className="text-[28px] font-bold text-[#1b2f5e]">{title}</h1>
      <div className="relative w-full max-w-sm">
        <input
          type="text"
          placeholder={placeholder}
          className="w-full bg-white border border-gray-200 rounded-full pl-5 pr-11 py-2.5 text-[13px] text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-100 shadow-sm transition-shadow"
        />
        <Search size={15} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400" />
      </div>
    </div>
  );
}
