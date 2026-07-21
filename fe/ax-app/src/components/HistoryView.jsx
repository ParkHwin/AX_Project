import { useMemo, useState, useEffect } from "react";
import { Layers, CheckCircle, XCircle, Gauge, TrendingUp, ImageOff, ChevronRight, ChevronLeft } from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import SearchHeader from "./SearchHeader.jsx";
import StatMiniCard from "./StatMiniCard.jsx";
import { DEFECT_CLASSES, CLASS_COLOR } from "../data/waferPatterns.js";
import { formatTimestamp } from "../utils/formatTimestamp.js";
import { getAnalysisList } from "../utils/api.js";

const PAGE_SIZE = 10;

function badgeStyle(color) {
  return { backgroundColor: `${color}1A`, color };
}

export default function HistoryView({ session, onViewDetail }) {
  const [history, setHistory] = useState([]);
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (!session?.user_num) return;
    getAnalysisList(session.user_num)
      .then((data) => {
        setHistory(
          data.items.map((item) => ({
            lot: `A${item.analysis_id}`,
            pattern: item.top_class_name,
            confidence: Math.round(item.confidence * 1000) / 10,
            probabilities: [],
            thumbnail: null,
            timestamp: new Date(item.created_at).getTime(),
            analysis_id: item.analysis_id,
            image_id: item.image_id,
          }))
        );
      })
      .catch(() => {});
  }, [session?.user_num]);

  const total = history.length;
  const passCount = history.filter((h) => h.pattern === "none").length;
  const failCount = total - passCount;
  const avgDefectRate = total ? ((failCount / total) * 100).toFixed(1) : "0.0";
  const latest = history[0];

  const trendData = [...history].reverse().map((h) => ({ lot: h.lot, confidence: h.confidence }));

  const patternCounts = useMemo(() => {
    const counts = {};
    history.forEach((h) => { counts[h.pattern] = (counts[h.pattern] || 0) + 1; });
    return DEFECT_CLASSES.map((c) => ({ key: c.key, color: c.color, count: counts[c.key] || 0 }))
      .filter((c) => c.count > 0)
      .sort((a, b) => b.count - a.count);
  }, [history]);

  const totalPages = Math.max(1, Math.ceil(history.length / PAGE_SIZE));
  const pagedHistory = history.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#eef1f8" }}>
      <div className="flex gap-6 px-8 py-8">
        <div className="flex-1 min-w-0">
          <SearchHeader title="검사 이력" placeholder="Lot ID로 검색" />

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 mb-6">
            <div className="grid grid-cols-[240px_1fr] gap-6 mb-6">
              <div className="flex flex-col justify-between">
                <div>
                  <div className="text-[13px] text-gray-400 mb-2">누적 검사 건수</div>
                  <div className="text-[44px] font-extrabold text-gray-900 leading-none">{total}</div>
                  <div className="flex items-center gap-2 mt-3 text-[13px] text-gray-500">
                    <Layers size={15} className="text-blue-500" />
                    서버에 기록된 전체 이력
                  </div>
                </div>
                <div className="mt-4">
                  <div className="flex h-2 rounded-full overflow-hidden bg-gray-100">
                    {total > 0 && (
                      <>
                        <div className="h-full bg-emerald-500" style={{ width: `${(passCount / total) * 100}%` }} />
                        <div className="h-full bg-rose-500" style={{ width: `${(failCount / total) * 100}%` }} />
                      </>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-[11px] text-gray-400 mt-2">
                    <span>PASS {passCount}건</span>
                    <span>FAIL {failCount}건</span>
                  </div>
                </div>
              </div>

              <div className="bg-blue-500 rounded-2xl p-5">
                <div style={{ height: 220 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={trendData}>
                      <CartesianGrid stroke="rgba(255,255,255,0.25)" strokeDasharray="4 4" vertical={false} />
                      <XAxis dataKey="lot" tick={{ fill: "rgba(255,255,255,0.75)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: "rgba(255,255,255,0.75)", fontSize: 11 }} axisLine={false} tickLine={false} width={28} domain={[0, 100]} />
                      <Bar dataKey="confidence" fill="#ffffff" radius={[4, 4, 0, 0]} opacity={0.9} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4 pt-6 border-t border-gray-100">
              <StatMiniCard icon={Layers} iconBg="#eef1f6" iconColor="#1b2f5e" label="총 검사" value={total} unit="건" progress={100} progressColor="#1b2f5e" />
              <StatMiniCard icon={CheckCircle} iconBg="#ecfdf5" iconColor="#059669" label="PASS" value={passCount} unit="건" progress={total ? (passCount / total) * 100 : 0} progressColor="#059669" />
              <StatMiniCard icon={XCircle} iconBg="#fff1f2" iconColor="#e11d48" label="FAIL" value={failCount} unit="건" progress={total ? (failCount / total) * 100 : 0} progressColor="#e11d48" />
              <StatMiniCard icon={Gauge} iconBg="#eff6ff" iconColor="#2563eb" label="평균 불량률" value={avgDefectRate} unit="%" progress={Number(avgDefectRate)} progressColor="#2563eb" />
            </div>
          </div>

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h2 className="text-[15px] font-semibold text-gray-800">전체 검사 이력</h2>
              <span className="text-[12px] text-gray-400">총 {total}건</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-[12px]">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50">
                    {["", "Lot ID", "검사 일시", "판정 패턴", "신뢰도", "결과", ""].map((h, i) => (
                      <th key={i} className="px-6 py-3 text-left text-[11px] text-gray-400 font-medium tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {history.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-6 py-8 text-center text-gray-400">아직 검사 이력이 없습니다. 대시보드에서 웨이퍼 이미지를 업로드하고 분석을 실행해 보세요.</td>
                    </tr>
                  )}
                  {pagedHistory.map((row) => {
                    const color = CLASS_COLOR[row.pattern];
                    const verdict = row.pattern === "none" ? "PASS" : "FAIL";
                    return (
                      <tr
                        key={row.lot}
                        onClick={() => onViewDetail?.(row)}
                        className="border-b border-gray-50 hover:bg-blue-50/40 transition-colors cursor-pointer"
                      >
                        <td className="pl-6 py-2.5">
                          <div className="w-9 h-9 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
                            <ImageOff size={14} className="text-gray-300" />
                          </div>
                        </td>
                        <td className="px-6 py-3 text-gray-700">{row.lot}</td>
                        <td className="px-6 py-3 text-gray-400">{formatTimestamp(row.timestamp)}</td>
                        <td className="px-6 py-3">
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold" style={badgeStyle(color)}>{row.pattern}</span>
                        </td>
                        <td className="px-6 py-3 text-gray-500">{row.confidence}%</td>
                        <td className="px-6 py-3">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${verdict === "FAIL" ? "bg-rose-50 text-rose-600" : "bg-emerald-50 text-emerald-600"}`}>
                            {verdict}
                          </span>
                        </td>
                        <td className="px-6 py-3 text-right">
                          <ChevronRight size={14} className="text-gray-300" />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-between">
                <span className="text-[12px] text-gray-400">
                  {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, history.length)} / {history.length}건
                </span>
                <div className="flex items-center gap-1">
                  <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
                    <ChevronLeft size={14} />
                  </button>
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                    <button key={p} onClick={() => setPage(p)} className={`w-8 h-8 flex items-center justify-center rounded-lg text-[12px] font-medium transition-colors ${p === page ? "bg-blue-600 text-white" : "text-gray-500 hover:bg-gray-50"}`}>
                      {p}
                    </button>
                  ))}
                  <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
                    <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        <aside className="w-[300px] flex-shrink-0 space-y-6">
          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <div className="text-[13px] text-gray-400 mb-2">최근 판정</div>
            {latest ? (
              <>
                <div className={`text-[32px] font-extrabold leading-none ${latest.pattern === "none" ? "text-emerald-600" : "text-rose-600"}`}>
                  {latest.pattern === "none" ? "PASS" : "FAIL"}
                </div>
                <p className="text-gray-400 text-[12px] mt-3 leading-relaxed">
                  {latest.lot} · <strong style={{ color: CLASS_COLOR[latest.pattern] }}>{latest.pattern}</strong> · 신뢰도 {latest.confidence}%
                </p>
                <div className="text-[11px] text-gray-300 mt-1">{formatTimestamp(latest.timestamp)}</div>
              </>
            ) : (
              <p className="text-gray-400 text-[13px] mt-2">아직 검사 이력이 없습니다.</p>
            )}
          </div>

          {patternCounts.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <h3 className="text-[13px] font-semibold text-gray-800 mb-4">패턴별 검출 건수</h3>
              <div className="space-y-3">
                {patternCounts.map((p) => (
                  <div key={p.key} className="flex items-center gap-3">
                    <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: p.color }} />
                    <span className="text-[12px] text-gray-600 flex-1">{p.key}</span>
                    <span className="text-[12px] font-semibold text-gray-800">{p.count}건</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <h3 className="text-[13px] font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <TrendingUp size={13} className="text-blue-500" />신뢰도 추이
            </h3>
            <div style={{ height: 110 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <XAxis dataKey="lot" tick={{ fill: "#9ca3af", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, fontSize: 12 }} />
                  <Line type="monotone" dataKey="confidence" stroke="#3b82f6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
