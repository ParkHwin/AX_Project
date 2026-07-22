import { useMemo, useState } from "react";
import { RefreshCw, ScanLine, ChevronLeft, ChevronRight, ImageOff } from "lucide-react";
import PatternBadge from "./PatternBadge.jsx";
import SearchHeader from "./SearchHeader.jsx";
import StatMiniCard from "./StatMiniCard.jsx";
import { DEFECT_CLASSES, CLASS_COLOR } from "../data/waferPatterns.js";

function badgeStyle(color) {
  return { backgroundColor: `${color}1A`, color };
}

export default function ResultsView({ results, recentHistory = [], onReset, onGoDashboard, onViewDetail, onSearchLot }) {
  const [index, setIndex] = useState(0);

  const recentTrend = recentHistory.slice(-8);
  const patternCounts = useMemo(() => {
    const counts = {};
    recentHistory.forEach((h) => {
      counts[h.pattern] = (counts[h.pattern] || 0) + 1;
    });
    return DEFECT_CLASSES
      .map((c) => ({ key: c.key, color: c.color, count: counts[c.key] || 0 }))
      .filter((c) => c.count > 0)
      .sort((a, b) => b.count - a.count);
  }, [recentHistory]);
  const patternTotal = patternCounts.reduce((sum, p) => sum + p.count, 0);

  if (!results || results.length === 0) {
    return (
      <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#eef1f8" }}>
        <div className="px-8 py-8">
          <SearchHeader title="분석 결과" placeholder="Lot ID로 검색" onSearch={onSearchLot} />
          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-10 text-center">
            <ScanLine size={28} className="text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 text-[14px] mb-1">아직 분석 결과가 없습니다.</p>
            <p className="text-gray-400 text-[12px] mb-5">대시보드에서 웨이퍼 이미지를 업로드하고 AI 분석을 실행해 보세요.</p>
            <button onClick={onGoDashboard} className="px-5 py-2.5 bg-blue-600 text-white rounded-xl text-[13px] font-medium hover:bg-blue-700 transition-colors">
              대시보드로 이동
            </button>
          </div>
        </div>
      </div>
    );
  }

  const safeIndex = Math.min(index, results.length - 1);
  const result = results[safeIndex];
  const { topClass, topColor, isFail, sortedProbs, runnerUp, record } = result;
  const batchFailCount = results.filter((r) => r.isFail).length;
  const batchPassCount = results.length - batchFailCount;

  return (
    <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#eef1f8" }}>
      <div className="px-8 py-8">
        <SearchHeader title="분석 결과" placeholder="Lot ID로 검색" onSearch={onSearchLot} />
        <div className="flex flex-col gap-6">
        <div className="flex gap-6 items-stretch">
        <div className="flex-1 min-w-0 flex flex-col gap-6">
          {results.length > 1 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm px-5 py-3 flex items-center justify-between">
              <span className="text-[13px] text-gray-500">
                <strong className="text-gray-800">{record.lot}</strong> · 이번에 분석한 {results.length}장 중 {safeIndex + 1}번째
              </span>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setIndex((i) => Math.max(0, i - 1))}
                  disabled={safeIndex === 0}
                  className="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft size={14} />
                </button>
                <button
                  onClick={() => setIndex((i) => Math.min(results.length - 1, i + 1))}
                  disabled={safeIndex === results.length - 1}
                  className="flex items-center gap-1 px-3 h-8 rounded-lg bg-blue-600 text-white text-[12px] font-medium hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  다음
                  <ChevronRight size={14} />
                </button>
              </div>
            </div>
          )}

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <div className="grid grid-cols-[240px_1fr] gap-6 mb-6">
              <div className={`rounded-2xl overflow-hidden bg-gray-100 border-2 flex items-center justify-center aspect-square ${isFail ? "border-rose-500" : "border-emerald-500"}`}>
                {record.thumbnail ? (
                  <img src={record.thumbnail} alt={`${record.lot} 웨이퍼 이미지`} className="w-full h-full object-cover" />
                ) : (
                  <ImageOff size={32} className="text-gray-300" />
                )}
              </div>

              <div className="bg-blue-500 rounded-2xl p-5 flex flex-col justify-center gap-3">
                {sortedProbs.slice(0, 5).map((p) => (
                  <div key={p.key}>
                    <div className="flex items-center justify-between text-[12px] text-white/90 mb-1">
                      <span>{p.key}</span>
                      <span className="font-semibold">{p.prob}%</span>
                    </div>
                    <div className="h-1.5 bg-white/20 rounded-full overflow-hidden">
                      <div className="h-full bg-white rounded-full" style={{ width: `${Math.max(p.prob, 1)}%`, opacity: 0.9 }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4 pt-6 border-t border-gray-100">
              <StatMiniCard label="예측 클래스" value={topClass} progress={sortedProbs[0].prob} progressColor={topColor} />
              <StatMiniCard label="2위 후보" value={runnerUp.key} progress={runnerUp.prob} progressColor="#64748b" />
              <StatMiniCard label="불량 웨이퍼" value={batchFailCount} unit="장" progress={(batchFailCount / results.length) * 100} progressColor="#e11d48" />
              <StatMiniCard label="정상 웨이퍼" value={batchPassCount} unit="장" progress={(batchPassCount / results.length) * 100} progressColor="#059669" />
            </div>
          </div>

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 flex-1 flex flex-col">
            <h2 className="text-[15px] font-semibold text-gray-800 mb-2">감지된 결함 패턴</h2>
            <PatternBadge topClass={topClass} topColor={topColor} isFail={isFail} />
          </div>
        </div>

        <div className="w-[300px] flex-shrink-0 flex flex-col gap-6">
          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <div className="text-[13px] text-gray-400 mb-2">종합 판정</div>
            <div className={`text-[36px] font-extrabold leading-none ${isFail ? "text-rose-600" : "text-emerald-600"}`}>{isFail ? "FAIL" : "PASS"}</div>
            <p className="text-gray-400 text-[12px] mt-3 leading-relaxed">
              {isFail
                ? `${topClass} 패턴 감지 — 정상 판정 기준을 충족하지 못했습니다.`
                : "특이 패턴 없이 정상 판정되었습니다."}
            </p>
            <div className="flex gap-2 mt-4">
              <button onClick={onReset} className="flex-1 flex items-center justify-center gap-1.5 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-[13px] font-medium hover:bg-gray-50 transition-colors">
                <RefreshCw size={13} />새 검사
              </button>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 flex-1 flex flex-col">
            <h3 className="text-[13px] font-semibold text-gray-800 mb-4">분류 클래스 안내 (9종)</h3>
            <div className="space-y-3">
              {DEFECT_CLASSES.map((c) => (
                <div key={c.key} className="flex items-start gap-2.5">
                  <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" style={{ backgroundColor: c.color }} />
                  <div className="min-w-0">
                    <div className="text-[12px] font-semibold text-gray-700">{c.key}</div>
                    <div className="text-[11px] text-gray-400 leading-snug">{c.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        </div>

        <div className="flex gap-6 items-start">
          <div className="flex-1 min-w-0 bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h2 className="text-[15px] font-semibold text-gray-800">최근 검사 이력</h2>
              <span className="text-[12px] text-gray-400">최근 {recentTrend.length}건</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-[12px]">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50">
                    {["Lot ID", "판정 패턴", "신뢰도", "결과"].map((h) => (
                      <th key={h} className="px-6 py-3 text-center text-[11px] text-gray-400 font-medium tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {recentTrend.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-6 py-8 text-center text-gray-400">아직 검사 이력이 없습니다</td>
                    </tr>
                  )}
                  {[...recentTrend].reverse().map((row) => {
                    const color = CLASS_COLOR[row.pattern];
                    const verdict = row.pattern === "none" ? "PASS" : "FAIL";
                    return (
                      <tr
                        key={row.lot}
                        onClick={() => onViewDetail?.(row)}
                        className="border-b border-gray-50 hover:bg-blue-50/40 transition-colors cursor-pointer"
                      >
                        <td className="px-6 py-3 text-center text-gray-700">{row.lot}</td>
                        <td className="px-6 py-3 text-center">
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold" style={badgeStyle(color)}>{row.pattern}</span>
                        </td>
                        <td className="px-6 py-3 text-center text-gray-500">{row.confidence}%</td>
                        <td className="px-6 py-3 text-center">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${verdict === "FAIL" ? "bg-rose-50 text-rose-600" : "bg-emerald-50 text-emerald-600"}`}>
                            {verdict}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="w-[300px] flex-shrink-0">
            {patternCounts.length > 0 && (
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-[13px] font-semibold text-gray-800">패턴별 검출 건수</h3>
                  <span className="text-[11px] text-gray-400">최근 {patternTotal}건 기준</span>
                </div>
                <div className="space-y-3">
                  {patternCounts.map((p) => (
                    <div key={p.key}>
                      <div className="flex items-center justify-between text-[12px] mb-1">
                        <span className="flex items-center gap-2 text-gray-700 font-medium">
                          <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: p.color }} />
                          {p.key === "none" ? "정상 (none)" : p.key}
                        </span>
                        <span className="font-semibold text-gray-800">{p.count}건</span>
                      </div>
                      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${(p.count / patternTotal) * 100}%`, backgroundColor: p.color, opacity: 0.85 }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
        </div>
      </div>
    </div>
  );
}
