import { useState } from "react";
import { Search, Loader2 } from "lucide-react";

export default function SearchHeader({ title, placeholder = "검색", showSearch = true, onSearch }) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | notfound

  const runSearch = async () => {
    const q = query.trim();
    if (!q || !onSearch) return;
    setStatus("loading");
    const found = await onSearch(q);
    setStatus(found ? "idle" : "notfound");
  };

  return (
    <div className="flex items-center justify-between gap-6 mb-6 flex-wrap">
      <h1 className="text-[28px] font-bold text-gray-800">{title}</h1>
      {showSearch && (
        <div className="w-[220px] flex-shrink-0">
          <div className="relative w-full">
            <input
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                if (status === "notfound") setStatus("idle");
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") runSearch();
              }}
              placeholder={placeholder}
              className="w-full bg-white border border-gray-200 rounded-full pl-5 pr-11 py-2.5 text-[16px] text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-100 shadow-sm transition-shadow"
            />
            <button
              type="button"
              onClick={runSearch}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-500 transition-colors"
            >
              {status === "loading" ? <Loader2 size={15} className="animate-spin" /> : <Search size={15} />}
            </button>
          </div>
          {status === "notfound" && (
            <p className="text-[14px] text-rose-500 mt-1.5 pl-1">일치하는 웨이퍼를 찾을 수 없습니다.</p>
          )}
        </div>
      )}
    </div>
  );
}
