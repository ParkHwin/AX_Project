import { useMemo, useState } from "react";
import { RefreshCw, ScanLine, ChevronLeft, ChevronRight, ImageOff, FlaskConical, BookOpen, HelpCircle } from "lucide-react";
import PatternBadge from "./PatternBadge.jsx";
import SearchHeader from "./SearchHeader.jsx";
import StatMiniCard from "./StatMiniCard.jsx";
import { DEFECT_CLASSES, CLASS_COLOR } from "../data/waferPatterns.js";

function badgeStyle(color) {
  return { backgroundColor: `${color}1A`, color };
}

function EvidenceBadge({ type }) {
  if (type === "LIT") return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
      <BookOpen size={8} />문헌
    </span>
  );
  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
      <HelpCircle size={8} />추정
    </span>
  );
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
      <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#f1f5f9" }}>
        <div className="px-8 py-8">
          <SearchHeader title="분석 결과" placeholder="Lot ID로 검색" onSearch={onSearchLot} />
          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-10 text-center">
            <ScanLine size={28} className="text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 text-[17px] mb-1">아직 분석 결과가 없습니다.</p>
            <p className="text-gray-400 text-[15px] mb-5">대시보드에서 웨이퍼 이미지를 업로드하고 AI 분석을 실행해 보세요.</p>
            <button onClick={onGoDashboard} className="px-5 py-2.5 bg-blue-600 text-white rounded-xl text-[16px] font-medium hover:bg-blue-700 transition-colors">
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
  const gradcamSrc = record.gradcam_data ? `data:image/png;base64,${record.gradcam_data}` : null;
  const processInfo = record.process_info || null;

  return (
    <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#f1f5f9" }}>
      <div className="px-8 py-8">
        <SearchHeader title="분석 결과" placeholder="Lot ID로 검색" onSearch={onSearchLot} />

        <div className="flex gap-6 items-start">

          {/* 왼쪽 메인 컬럼 */}
          <div className="flex-1 min-w-0 flex flex-col gap-4">

            {/* 다중 이미지 네비게이션 */}
            {results.length > 1 && (
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm px-5 py-3 flex items-center justify-between">
                <span className="text-[16px] text-gray-500">
                  <strong className="text-gray-800">{record.lot}</strong> · {results.length}장 중 {safeIndex + 1}번째
                </span>
                <div className="flex items-center gap-1">
                  <button onClick={() => setIndex((i) => Math.max(0, i - 1))} disabled={safeIndex === 0}
                    className="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
                    <ChevronLeft size={14} />
                  </button>
                  <button onClick={() => setIndex((i) => Math.min(results.length - 1, i + 1))} disabled={safeIndex === results.length - 1}
                    className="flex items-center gap-1 px-3 h-8 rounded-lg bg-blue-600 text-white text-[15px] font-medium hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
                    다음 <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            )}

            {/* 이미지 + 확률 차트 + 스탯 */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <div className="grid grid-cols-[200px_1fr] gap-5 mb-5">
                <div className={`rounded-xl overflow-hidden bg-gray-100 border-2 flex items-center justify-center aspect-square ${isFail ? "border-rose-400" : "border-emerald-400"}`}>
                  {record.thumbnail
                    ? <img src={record.thumbnail} alt={`${record.lot}`} className="w-full h-full object-cover" />
                    : <ImageOff size={28} className="text-gray-300" />}
                </div>
                <div className="rounded-xl p-4 flex flex-col justify-center gap-3" style={{ background: "#1e293b" }}>
                  {sortedProbs.slice(0, 5).map((p) => (
                    <div key={p.key}>
                      <div className="flex items-center justify-between text-[15px] text-white/90 mb-1">
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
              <div className="grid grid-cols-4 gap-3 pt-5 border-t border-gray-100">
                <StatMiniCard label="예측 클래스" value={topClass} />
                <StatMiniCard label="2위 후보" value={runnerUp.key} />
                <StatMiniCard label="불량 웨이퍼" value={batchFailCount} unit="장" />
                <StatMiniCard label="정상 웨이퍼" value={batchPassCount} unit="장" />
              </div>
            </div>

            {/* 감지된 결함 패턴 + Grad-CAM */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-[17px] font-semibold text-gray-800 mb-3">감지된 결함 패턴</h2>
              <PatternBadge topClass={topClass} topColor={topColor} isFail={isFail} />
              {gradcamSrc && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <p className="text-[14px] font-medium text-gray-600 mb-2">판단 근거 (Grad-CAM)</p>
                  <div className="flex gap-3 items-start">
                    {record.thumbnail && (
                      <div className="w-[100px]">
                        <p className="text-[12px] text-gray-400 mb-1 text-center">원본</p>
                        <img src={record.thumbnail} alt="원본" className="w-full rounded-lg border border-gray-100 aspect-square object-cover" style={{ imageRendering: "pixelated" }} />
                      </div>
                    )}
                    <div className="w-[100px]">
                      <p className="text-[12px] text-gray-400 mb-1 text-center">히트맵</p>
                      <img src={gradcamSrc} alt="GradCAM" className="w-full rounded-lg border border-gray-100 aspect-square object-cover" style={{ imageRendering: "pixelated" }} />
                    </div>
                  </div>
                  <p className="text-[12px] text-gray-400 mt-2">빨간 영역일수록 AI가 판단 시 집중한 부위입니다.</p>
                </div>
              )}
            </div>

            {/* 최근 검사 이력 */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                <h2 className="text-[17px] font-semibold text-gray-800">최근 검사 이력</h2>
                <span className="text-[15px] text-gray-400">최근 {recentTrend.length}건</span>
              </div>
              <table className="w-full text-[15px]">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50">
                    {["Lot ID", "판정 패턴", "신뢰도", "결과"].map((h) => (
                      <th key={h} className="px-6 py-3 text-center text-[14px] text-gray-400 font-medium tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {recentTrend.length === 0 && (
                    <tr><td colSpan={4} className="px-6 py-6 text-center text-gray-400 text-[15px]">아직 검사 이력이 없습니다</td></tr>
                  )}
                  {[...recentTrend].reverse().map((row) => {
                    const color = CLASS_COLOR[row.pattern];
                    const verdict = row.pattern === "none" ? "PASS" : "FAIL";
                    return (
                      <tr key={row.lot} onClick={() => onViewDetail?.(row)}
                        className="border-b border-gray-50 hover:bg-blue-50/40 transition-colors cursor-pointer">
                        <td className="px-6 py-3 text-center text-gray-700">{row.lot}</td>
                        <td className="px-6 py-3 text-center">
                          <span className="px-2 py-0.5 rounded-full text-[13px] font-semibold" style={badgeStyle(color)}>{row.pattern}</span>
                        </td>
                        <td className="px-6 py-3 text-center text-gray-500">{row.confidence}%</td>
                        <td className="px-6 py-3 text-center">
                          <span className={`px-2 py-0.5 rounded-full text-[13px] font-semibold ${verdict === "FAIL" ? "bg-rose-50 text-rose-600" : "bg-emerald-50 text-emerald-600"}`}>
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

          {/* 오른쪽 사이드 컬럼 */}
          <div className="w-[300px] flex-shrink-0 flex flex-col gap-4">

            {/* 종합 판정 */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <div className="text-[15px] text-gray-400 mb-1">종합 판정</div>
              <div className={`text-[36px] font-extrabold leading-none ${isFail ? "text-rose-600" : "text-emerald-600"}`}>
                {isFail ? "FAIL" : "PASS"}
              </div>
              <p className="text-gray-400 text-[15px] mt-3 leading-relaxed">
                {isFail ? `${topClass} 패턴 감지 — 정상 기준 미충족` : "특이 패턴 없이 정상 판정되었습니다."}
              </p>
              <button onClick={onReset} className="mt-4 w-full flex items-center justify-center gap-1.5 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-[16px] font-medium hover:bg-gray-50 transition-colors">
                <RefreshCw size={13} />새 검사
              </button>
            </div>

            {/* 원인공정 분석 */}
            {topClass !== "none" && (
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
                <div className="flex items-center gap-1.5 mb-3">
                  <FlaskConical size={14} className="text-blue-500" />
                  <h3 className="text-[16px] font-semibold text-gray-800">원인공정 분석</h3>
                </div>
                {processInfo && processInfo.length > 0 ? (
                  <div className="space-y-3">
                    {processInfo.map((item, idx) => (
                      <div key={idx} className="border border-gray-100 rounded-xl p-3">
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-[13px] font-semibold text-gray-800 leading-snug">{item.process}</span>
                          <EvidenceBadge type={item.evidence_type} />
                        </div>
                        <div className="h-1 bg-gray-100 rounded-full overflow-hidden mb-2">
                          <div className="h-full rounded-full bg-blue-400" style={{ width: `${item.weight * 100}%` }} />
                        </div>
                        <div className="flex flex-wrap gap-1 mb-1.5">
                          {item.sub_processes.map((sp, i) => (
                            <span key={i} className="px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded text-[11px]">{sp}</span>
                          ))}
                        </div>
                        {item.citations.length > 0 && (
                          <p className="text-[11px] text-gray-400">{item.citations.join(" / ")}</p>
                        )}
                        {item.note && (
                          <p className="text-[11px] text-amber-600 bg-amber-50 rounded px-2 py-1 mt-1.5 leading-relaxed">{item.note}</p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-[14px] text-gray-400">원인공정 데이터 없음</p>
                )}
              </div>
            )}

            {/* 패턴별 검출 건수 */}
            {patternCounts.length > 0 && (
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-[16px] font-semibold text-gray-800">패턴별 검출 건수</h3>
                  <span className="text-[14px] text-gray-400">{patternTotal}건</span>
                </div>
                <div className="space-y-3">
                  {patternCounts.map((p) => (
                    <div key={p.key}>
                      <div className="flex items-center justify-between text-[15px] mb-1">
                        <span className="flex items-center gap-2 text-gray-700 font-medium">
                          <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: p.color }} />
                          {p.key === "none" ? "정상 (none)" : p.key}
                        </span>
                        <span className="font-semibold text-gray-800">{p.count}건</span>
                      </div>
                      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full rounded-full" style={{ width: `${(p.count / patternTotal) * 100}%`, backgroundColor: p.color, opacity: 0.85 }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 분류 클래스 안내 */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <h3 className="text-[16px] font-semibold text-gray-800 mb-3">분류 클래스 안내 (9종)</h3>
              <div className="space-y-2.5">
                {DEFECT_CLASSES.map((c) => (
                  <div key={c.key} className="flex items-start gap-2">
                    <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" style={{ backgroundColor: c.color }} />
                    <div className="min-w-0">
                      <div className="text-[15px] font-semibold text-gray-700">{c.key}</div>
                      <div className="text-[14px] text-gray-400 leading-snug">{c.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
