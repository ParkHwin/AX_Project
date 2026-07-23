import { ArrowLeft, CheckCircle, XCircle, ImageOff, Circle, BarChart2, Activity } from "lucide-react";
import PatternBadge from "./PatternBadge.jsx";
import { CLASS_COLOR } from "../data/waferPatterns.js";
import { formatTimestamp } from "../utils/formatTimestamp.js";
import { getImageUrl } from "../utils/api.js";

export default function AnalysisDetailView({ record, onBack }) {
  if (!record) {
    return (
      <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#f1f5f9" }}>
        <div className="px-8 py-8">
          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-10 text-center">
            <p className="text-gray-500 text-[17px] mb-5">조회할 분석 기록을 찾을 수 없습니다.</p>
            <button onClick={onBack} className="px-5 py-2.5 bg-blue-600 text-white rounded-xl text-[16px] font-medium hover:bg-blue-700 transition-colors">
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
    <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#f1f5f9" }}>
      <div className="px-8 py-8">

        {/* 헤더 */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-[28px] font-bold text-gray-800">분석 상세 조회</h1>
            <p className="text-gray-400 text-[15px] mt-0.5">{record.lot} · {formatTimestamp(record.timestamp)}</p>
          </div>
          <button onClick={onBack} className="flex items-center gap-1.5 text-gray-800 hover:text-gray-600 text-[16px] font-medium transition-colors">
            <ArrowLeft size={14} />검사 이력으로
          </button>
        </div>

        {/* 상단: 판정 + 썸네일 + 스탯 */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
          <div className="flex items-center gap-6 mb-6">
            <div className={`w-24 h-24 rounded-xl overflow-hidden bg-gray-100 border-2 flex items-center justify-center flex-shrink-0 ${isFail ? "border-rose-400" : "border-emerald-400"}`}>
              {thumbnailSrc ? (
                <img src={thumbnailSrc} alt={`${record.lot} 웨이퍼 이미지`} className="w-full h-full object-cover" />
              ) : (
                <ImageOff size={20} className="text-gray-300" />
              )}
            </div>
            <div className="flex items-center gap-3">
              {isFail ? <XCircle size={28} className="text-rose-500 flex-shrink-0" /> : <CheckCircle size={28} className="text-emerald-500 flex-shrink-0" />}
              <div>
                <div className={`text-[28px] font-extrabold leading-none ${isFail ? "text-rose-600" : "text-emerald-600"}`}>
                  {isFail ? "FAIL" : "PASS"}
                </div>
                <p className="text-gray-500 text-[16px] mt-1">
                  감지 패턴 <strong style={{ color: topColor }}>{topClass}</strong> · 신뢰도 {record.confidence}%
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 pt-5 border-t border-gray-100">
            {/* 예측 클래스 */}
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <Circle size={10} style={{ color: topColor }} />
                <span className="text-[14px] text-gray-500 font-medium uppercase tracking-wide">예측 클래스</span>
              </div>
              <div className="text-[20px] font-bold text-gray-900 leading-none mb-2">{topClass}</div>
              <div className="h-1 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${Math.min(Math.max(sortedProbs[0].prob, 2), 100)}%`, background: topColor }} />
              </div>
            </div>

            {/* 2위 후보 */}
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <BarChart2 size={10} className="text-gray-400" />
                <span className="text-[14px] text-gray-500 font-medium uppercase tracking-wide">2위 후보</span>
              </div>
              <div className="text-[20px] font-bold text-gray-900 leading-none mb-2">{runnerUp?.key ?? "-"}</div>
              <div className="h-1 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${Math.min(Math.max(runnerUp?.prob ?? 0, 0.5), 100)}%`, background: "#94a3b8" }} />
              </div>
            </div>

            {/* 신뢰도 */}
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <Activity size={10} className="text-blue-400" />
                <span className="text-[14px] text-gray-500 font-medium uppercase tracking-wide">신뢰도</span>
              </div>
              <div className="flex items-baseline gap-1 mb-2">
                <span className="text-[20px] font-bold text-gray-900 leading-none">{record.confidence}</span>
                <span className="text-gray-500 text-[15px]">%</span>
              </div>
              <div className="h-1 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${Math.min(Math.max(record.confidence, 2), 100)}%`, background: "#3b82f6" }} />
              </div>
            </div>
          </div>
        </div>

        {/* 하단: 결함 패턴 + 분류 결과 */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-[17px] font-semibold text-gray-800 mb-4">감지된 결함 패턴</h2>
            <PatternBadge topClass={topClass} topColor={topColor} isFail={isFail} />
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-[17px] font-semibold text-gray-800 mb-4">결함 패턴 분류 결과 (9종)</h2>
            <div className="space-y-3">
              {sortedProbs.slice(0, 3).map((p) => {
                const color = CLASS_COLOR[p.key];
                const isTop = p.key === topClass;
                return (
                  <div key={p.key}>
                    <div className="flex items-center justify-between text-[15px] mb-1">
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
          </div>
        </div>

      </div>
    </div>
  );
}
