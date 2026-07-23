import { useMemo, useState, useEffect } from "react";
import { Layers, ImageOff, ChevronRight, ChevronLeft } from "lucide-react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import SearchHeader from "./SearchHeader.jsx";
import StatMiniCard from "./StatMiniCard.jsx";
import { DEFECT_CLASSES, CLASS_COLOR } from "../data/waferPatterns.js";
import { formatTimestamp } from "../utils/formatTimestamp.js";
import { getAnalysisList, getImageUrl } from "../utils/api.js";

const PAGE_SIZE = 5;
const TREND_SIZE = 15;

function badgeStyle(color) {
  return { backgroundColor: `${color}1A`, color };
}

function TrendTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-100 px-3 py-2 max-w-[220px]">
      <div className="text-[14px] font-semibold text-gray-800 truncate mb-1">{d.lot}</div>
      <div className="text-[14px] text-gray-500">
        신뢰도 <span className="font-semibold text-blue-600">{d.confidence}%</span>
      </div>
      <div className="text-[14px] text-gray-400">
        <span style={{ color: CLASS_COLOR[d.pattern] }} className="font-medium">{d.pattern}</span> · {d.verdict}
      </div>
    </div>
  );
}

export default function HistoryView({ session, onViewDetail, onSearchLot }) {
  const [history, setHistory] = useState([]);
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (!session?.user_num) return;
    getAnalysisList(session.user_num)
      .then((data) => {
        setHistory(
          data.items.map((item) => ({
            lot: item.image_name || `A${item.analysis_id}`,
            pattern: item.top_class_name,
            confidence: Math.round(item.confidence * 1000) / 10,
            probabilities: [],
            thumbnail: item.image_id ? getImageUrl(item.image_id) : null,
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

  const trendData = [...history].reverse().map((h) => ({
    lot: h.lot,
    confidence: h.confidence,
    pattern: h.pattern,
    verdict: h.pattern === "none" ? "PASS" : "FAIL",
  }));
  const recentTrend = trendData.slice(-TREND_SIZE);

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
    <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#f1f5f9" }}>
      <div className="px-8 py-8">
        <SearchHeader title="검사 이력" placeholder="Lot ID로 검색" onSearch={onSearchLot} />
        <div className="flex flex-col gap-6">
        <div className="flex gap-6 items-stretch">
          <div className="flex-1 min-w-0 bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <div className="grid grid-cols-[240px_1fr] gap-6 mb-6">
              <div className="flex flex-col justify-between">
                <div>
                  <div className="text-[16px] text-gray-400 mb-2">누적 검사 건수</div>
                  <div className="text-[44px] font-extrabold text-gray-900 leading-none">{total}</div>
                  <div className="flex items-center gap-2 mt-3 text-[16px] text-gray-500">
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
                  <div className="flex items-center gap-4 text-[14px] text-gray-400 mt-2">
                    <span>PASS {passCount}건</span>
                    <span>FAIL {failCount}건</span>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl p-5" style={{ background: "#1e293b" }}>
                <div className="flex items-center justify-between mb-1">
                  <div className="text-slate-400 text-[15px]">Lot별 신뢰도 추이</div>
                  <div className="text-slate-300 text-[13px] font-medium px-2 py-0.5 rounded-full" style={{ background: "rgba(255,255,255,0.08)" }}>
                    최근 {recentTrend.length}건 (최신순 고정)
                  </div>
                </div>
                <div style={{ height: 185 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={recentTrend} margin={{ top: 12, right: 8, left: -8, bottom: 0 }}>
                      <defs>
                        <linearGradient id="historyTrendFill" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#ffffff" stopOpacity={0.35} />
                          <stop offset="100%" stopColor="#ffffff" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="rgba(255,255,255,0.15)" strokeDasharray="4 4" vertical={false} />
                      <XAxis dataKey="lot" tick={false} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: "rgba(255,255,255,0.75)", fontSize: 11 }} axisLine={false} tickLine={false} width={40} domain={[0, 100]} />
                      <Tooltip content={<TrendTooltip />} cursor={{ stroke: "rgba(255,255,255,0.4)", strokeWidth: 1 }} />
                      <Area
                        type="monotone"
                        dataKey="confidence"
                        stroke="#ffffff"
                        strokeWidth={2}
                        fill="url(#historyTrendFill)"
                        dot={({ cx, cy, payload, index }) => (
                          <circle
                            key={`${payload.lot}-${index}`}
                            cx={cx}
                            cy={cy}
                            r={payload.verdict === "FAIL" ? 4 : 2.5}
                            fill={payload.verdict === "FAIL" ? "#ef4444" : "#ffffff"}
                            stroke={payload.verdict === "FAIL" ? "#ffffff" : "#3b82f6"}
                            strokeWidth={1.2}
                          />
                        )}
                        activeDot={{ r: 5, stroke: "#ffffff", strokeWidth: 2 }}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex items-center gap-3 mt-1 text-[13px] text-white/60">
                  <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-white inline-block" />PASS</span>
                  <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-red-500 inline-block" />FAIL</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4 pt-6 border-t border-gray-100">
              <StatMiniCard label="총 검사" value={total} unit="건" />
              <StatMiniCard label="PASS" value={passCount} unit="건" />
              <StatMiniCard label="FAIL" value={failCount} unit="건" />
              <StatMiniCard label="평균 불량률" value={avgDefectRate} unit="%" />
            </div>
          </div>

          <div className="w-[300px] flex-shrink-0 flex flex-col gap-6">
            <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
              <div className="text-[16px] text-gray-400 mb-2">최근 판정</div>
              {latest ? (
                <>
                  <div className={`text-[32px] font-extrabold leading-none ${latest.pattern === "none" ? "text-emerald-600" : "text-rose-600"}`}>
                    {latest.pattern === "none" ? "PASS" : "FAIL"}
                  </div>
                  <p className="text-gray-400 text-[15px] mt-3 leading-relaxed">
                    {latest.lot} · <strong style={{ color: CLASS_COLOR[latest.pattern] }}>{latest.pattern}</strong> · 신뢰도 {latest.confidence}%
                  </p>
                  <div className="text-[14px] text-gray-300 mt-1">{formatTimestamp(latest.timestamp)}</div>
                </>
              ) : (
                <p className="text-gray-400 text-[16px] mt-2">아직 검사 이력이 없습니다.</p>
              )}
            </div>

            {patternCounts.length > 0 && (
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 flex-1 flex flex-col">
                <h3 className="text-[16px] font-semibold text-gray-800 mb-4">패턴별 검출 건수</h3>
                <div className="space-y-3">
                  {patternCounts.map((p) => (
                    <div key={p.key} className="flex items-center gap-3">
                      <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: p.color }} />
                      <span className="text-[15px] text-gray-600 flex-1">{p.key}</span>
                      <span className="text-[15px] font-semibold text-gray-800">{p.count}건</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h2 className="text-[18px] font-semibold text-gray-800">전체 검사 이력</h2>
              <span className="text-[15px] text-gray-400">총 {total}건</span>
            </div>
            <div>
              <table className="w-full text-[15px] table-fixed">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50">
                    {[
                      { label: "", w: "w-[56px]" },
                      { label: "Lot ID", w: "w-[130px]" },
                      { label: "검사 일시", w: "w-[150px]" },
                      { label: "판정 패턴", w: "w-[90px]" },
                      { label: "신뢰도", w: "w-[64px]" },
                      { label: "결과", w: "w-[64px]" },
                      { label: "", w: "w-[36px]" },
                    ].map((h, i) => (
                      <th key={i} className={`px-3 py-3 text-center align-middle text-[14px] text-gray-400 font-medium tracking-wide whitespace-nowrap ${h.w}`}>{h.label}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {history.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-3 py-8 text-center text-gray-400">아직 검사 이력이 없습니다. 대시보드에서 웨이퍼 이미지를 업로드하고 분석을 실행해 보세요.</td>
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
                        <td className="px-3 py-2.5 align-middle text-center">
                          <div className="w-8 h-8 mx-auto rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
                            {row.thumbnail ? (
                              <img src={row.thumbnail} alt={row.lot} className="w-full h-full object-cover" />
                            ) : (
                              <ImageOff size={13} className="text-gray-300" />
                            )}
                          </div>
                        </td>
                        <td className="px-3 py-2.5 align-middle text-center text-gray-700 truncate" title={row.lot}>{row.lot}</td>
                        <td className="px-3 py-2.5 align-middle text-center text-gray-400 whitespace-nowrap">{formatTimestamp(row.timestamp)}</td>
                        <td className="px-3 py-2.5 align-middle text-center truncate">
                          <span className="inline-block max-w-full truncate px-2 py-0.5 rounded-full text-[13px] font-semibold leading-normal" style={badgeStyle(color)}>{row.pattern}</span>
                        </td>
                        <td className="px-3 py-2.5 align-middle text-center text-gray-500 whitespace-nowrap">{row.confidence}%</td>
                        <td className="px-3 py-2.5 align-middle text-center whitespace-nowrap">
                          <span className={`inline-block px-2 py-0.5 rounded-full text-[13px] font-semibold leading-normal ${verdict === "FAIL" ? "bg-rose-50 text-rose-600" : "bg-emerald-50 text-emerald-600"}`}>
                            {verdict}
                          </span>
                        </td>
                        <td className="px-3 py-2.5 align-middle text-center whitespace-nowrap">
                          <ChevronRight size={14} className="text-gray-300 inline-block" />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-between">
                <span className="text-[15px] text-gray-400">
                  {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, history.length)} / {history.length}건
                </span>
                <div className="flex items-center gap-1">
                  <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
                    <ChevronLeft size={14} />
                  </button>
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                    <button key={p} onClick={() => setPage(p)} className={`w-8 h-8 flex items-center justify-center rounded-lg text-[15px] font-medium transition-colors ${p === page ? "bg-blue-600 text-white" : "text-gray-500 hover:bg-gray-50"}`}>
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
      </div>
    </div>
  );
}
