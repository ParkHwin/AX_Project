import { ArrowLeft, CheckCircle, XCircle, ImageOff, Circle, BarChart2, Activity } from "lucide-react";
import PatternBadge from "./PatternBadge.jsx";
import SearchHeader from "./SearchHeader.jsx";
import { DEFECT_CLASSES, CLASS_COLOR } from "../data/waferPatterns.js";
import { formatTimestamp } from "../utils/formatTimestamp.js";
import { getImageUrl } from "../utils/api.js";

function badgeStyle(color) {
  return { backgroundColor: `${color}1A`, color };
}

export default function AnalysisDetailView({ record, onBack }) {
  if (!record) {
    return (
      <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#eef1f8" }}>
        <div className="px-8 py-8">
          <SearchHeader title="분석 상세 조회" placeholder="Lot ID로 검색" />
          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-10 text-center">
            <p className="text-gray-500 text-[14px] mb-5">조회할 분석 기록을 찾을 수 없습니다.</p>
            <button onClick={onBack} className="px-5 py-2.5 bg-blue-600 text-white rounded-xl text-[13px] font-medium hover:bg-blue-700 transition-colors">
              검사 이력으로 돌아가기
            </button>
          </div>
        </div>
      </div>
    );
  }

  const topClass = record.pattern;
  const topColor = CLASS_COLOR[topClass];
  const isFail = topClass !== "none";
  const sortedProbs = [...record.probabilities].sort((a, b) => b.prob - a.prob);
  const runnerUp = sortedProbs[1];
  const thumbnailSrc = record.thumbnail || (record.image_id ? getImageUrl(record.image_id) : null);

  return (
    <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#eef1f8" }}>
      <div className="px-8 py-8 max-w-5xl">

        {/* 헤더 */}
        <div className="mb-6">
          <button onClick={onBack} className="flex items-center gap-1.5 text-gray-400 hover:text-gray-600 text-[12px] mb-2 transition-colors">
            <ArrowLeft size={13} />검사 이력으로
          </button>
          <h1 className="text-[26px] font-bold text-[#1b2f5e]">분석 상세 조회</h1>
          <p className="text-gray-400 text-[12px] mt-1">{record.lot} · {formatTimestamp(record.timestamp)}</p>
        </div>

        {/* FAIL / PASS 상태 카드 */}
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 mb-5">
          {/* 썸네일 + 판정 */}
          <div className="flex items-center gap-6">
            <div className={`w-28 h-28 rounded-2xl overflow-hidden bg-gray-100 border-2 flex items-center justify-center flex-shrink-0 ${isFail ? "border-rose-500" : "border-emerald-500"}`}>
              {thumbnailSrc ? (
                <img src={thumbnailSrc} alt={`${record.lot} 웨이퍼 이미지`} className="w-full h-full object-cover" />
              ) : (
                <ImageOff size={22} className="text-gray-300" />
              )}
            </div>

            <div className="flex items-center gap-3">
              {isFail
                ? <XCircle size={30} className="text-rose-500 flex-shrink-0" />
                : <CheckCircle size={30} className="text-emerald-500 flex-shrink-0" />}
              <div>
                <div className={`text-[22px] font-extrabold leading-none ${isFail ? "text-rose-600" : "text-emerald-600"}`}>
                  {isFail ? "FAIL" : "PASS"}
                </div>
                <p className="text-gray-500 text-[13px] mt-1.5">
                  감지 패턴 <strong style={{ color: topColor }}>{topClass}</strong> · 신뢰도 {record.confidence}%
                </p>
              </div>
            </div>
          </div>

          {/* 3개 스탯 (아이콘 + 값 + 바) */}
          <div className="grid grid-cols-3 gap-6 pt-6 mt-6 border-t border-gray-100">
            {/* 예측 클래스 */}
            <div>
              <div className="flex items-center gap-1.5 mb-3">
                <Circle size={11} style={{ color: topColor }} />
                <span className="text-[12px] text-gray-400">예측 클래스</span>
              </div>
              <div className="text-[22px] font-bold text-gray-900 leading-none mb-3">{topClass}</div>
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${Math.min(Math.max(sortedProbs[0].prob, 2), 100)}%`, background: topColor }} />
              </div>
            </div>

            {/* 2위 후보 */}
            <div>
              <div className="flex items-center gap-1.5 mb-3">
                <BarChart2 size={11} className="text-gray-400" />
                <span className="text-[12px] text-gray-400">2위 후보</span>
              </div>
              <div className="text-[22px] font-bold text-gray-900 leading-none mb-3">{runnerUp?.key ?? "-"}</div>
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${Math.min(Math.max(runnerUp?.prob ?? 0, 0.5), 100)}%`, background: "#64748b" }} />
              </div>
            </div>

            {/* 신뢰도 */}
            <div>
              <div className="flex items-center gap-1.5 mb-3">
                <Activity size={11} className="text-blue-500" />
                <span className="text-[12px] text-gray-400">신뢰도</span>
              </div>
              <div className="flex items-baseline gap-1 mb-3">
                <span className="text-[22px] font-bold text-gray-900 leading-none">{record.confidence}</span>
                <span className="text-gray-400 text-[13px]">%</span>
              </div>
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${Math.min(Math.max(record.confidence, 2), 100)}%`, background: "#2563eb" }} />
              </div>
            </div>
          </div>
        </div>

        {/* 결함 패턴 + 분류 결과 */}
        <div className="grid grid-cols-5 gap-5">
          {/* 감지된 결함 패턴 */}
          <div className="col-span-2 bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-[15px] font-semibold text-gray-800 mb-4">감지된 결함 패턴</h2>
            <PatternBadge topClass={topClass} topColor={topColor} isFail={isFail} />
          </div>

          {/* 결함 패턴 분류 결과 */}
          <div className="col-span-3 bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-[15px] font-semibold text-gray-800 mb-4">결함 패턴 분류 결과 (9종)</h2>
            <div className="space-y-3">
              {sortedProbs.slice(0, 3).map((p) => {
                const color = CLASS_COLOR[p.key];
                const isTop = p.key === topClass;
                return (
                  <div key={p.key}>
                    <div className="flex items-center justify-between text-[12px] mb-1">
                      <span className={isTop ? "font-semibold text-gray-800" : "text-gray-500"}>{p.key}</span>
                      <span className={isTop ? "font-semibold" : "text-gray-400"} style={isTop ? { color } : undefined}>{p.prob}%</span>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${Math.max(p.prob, 0.5)}%`, backgroundColor: color }} />
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-5 pt-4 border-t border-gray-100 flex flex-wrap gap-x-3 gap-y-1.5">
              {DEFECT_CLASSES.map((c) => (
                <span key={c.key} className="px-2 py-0.5 rounded-full text-[10px] font-semibold" style={badgeStyle(c.color)}>{c.key}</span>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
