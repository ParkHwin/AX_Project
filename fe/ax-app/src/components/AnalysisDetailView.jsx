import { ArrowLeft, CheckCircle, XCircle, ImageOff, Circle, BarChart2, Activity, FlaskConical, BookOpen, HelpCircle } from "lucide-react";
import PatternBadge from "./PatternBadge.jsx";
import { CLASS_COLOR } from "../data/waferPatterns.js";
import { formatTimestamp } from "../utils/formatTimestamp.js";
import { getImageUrl } from "../utils/api.js";

function EvidenceBadge({ type }) {
  if (type === "LIT") return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
      <BookOpen size={9} />문헌 근거
    </span>
  );
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
      <HelpCircle size={9} />추정치
    </span>
  );
}

function ProcessInfoPanel({ processInfo, topClass }) {
  if (topClass === "none") {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <FlaskConical size={16} className="text-emerald-500" />
          <h2 className="text-[17px] font-semibold text-gray-800">원인공정 분석</h2>
        </div>
        <p className="text-gray-400 text-[15px]">정상 판정 — 원인공정 해당 없음</p>
      </div>
    );
  }
  if (!processInfo || processInfo.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <FlaskConical size={16} className="text-blue-500" />
          <h2 className="text-[17px] font-semibold text-gray-800">원인공정 분석</h2>
        </div>
        <p className="text-gray-400 text-[15px]">원인공정 데이터 없음</p>
      </div>
    );
  }
  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <FlaskConical size={16} className="text-blue-500" />
        <h2 className="text-[17px] font-semibold text-gray-800">원인공정 분석</h2>
      </div>
      <div className="space-y-4">
        {processInfo.map((item, idx) => (
          <div key={idx} className="border border-gray-100 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[15px] font-semibold text-gray-800">{item.process}</span>
              <div className="flex items-center gap-2">
                <span className="text-[13px] text-gray-400">{Math.round(item.weight * 100)}%</span>
                <EvidenceBadge type={item.evidence_type} />
              </div>
            </div>
            <div className="h-1 bg-gray-100 rounded-full overflow-hidden mb-3">
              <div className="h-full rounded-full bg-blue-400" style={{ width: `${item.weight * 100}%` }} />
            </div>
            <div className="flex flex-wrap gap-1 mb-2">
              {item.sub_processes.map((sp, i) => (
                <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-md text-[12px]">{sp}</span>
              ))}
            </div>
            {item.citations.length > 0 && (
              <p className="text-[12px] text-gray-400">출처: {item.citations.join(" / ")}</p>
            )}
            {item.note && (
              <p className="text-[12px] text-amber-600 bg-amber-50 rounded-lg px-3 py-1.5 mt-2 leading-relaxed">{item.note}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

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
  const gradcamSrc = record.gradcam_data ? `data:image/png;base64,${record.gradcam_data}` : null;
  const heatmapSrc = record.gradcam_heatmap_data ? `data:image/png;base64,${record.gradcam_heatmap_data}` : null;
  const processInfo = record.process_info || null;

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

        {/* 원인공정 */}
        <div className="mb-4">
          <ProcessInfoPanel processInfo={processInfo} topClass={topClass} />
        </div>

        {/* 하단: 결함 패턴 + 분류 결과 */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-[17px] font-semibold text-gray-800 mb-4">감지된 결함 패턴</h2>
            {gradcamSrc && (
              <div className="mb-4 pb-4 border-b border-gray-100">
                <p className="text-[14px] font-medium text-gray-600 mb-2 text-center">판단 근거 (Grad-CAM)</p>
                <div className="flex gap-3 items-start justify-center">
                  {thumbnailSrc && (
                    <div className="flex-1">
                      <p className="text-[12px] text-gray-400 mb-1.5 text-center">원본 이미지</p>
                      <img src={thumbnailSrc} alt="원본" className="w-full rounded-lg border border-gray-100 object-cover aspect-square" style={{ imageRendering: "pixelated" }} />
                    </div>
                  )}
                  {heatmapSrc && (
                    <div className="flex-1">
                      <p className="text-[12px] text-gray-400 mb-1.5 text-center">히트맵</p>
                      <img src={heatmapSrc} alt="히트맵" className="w-full rounded-lg border border-gray-100 object-cover aspect-square" style={{ imageRendering: "pixelated" }} />
                    </div>
                  )}
                  <div className="flex-1">
                    <p className="text-[12px] text-gray-400 mb-1.5 text-center">오버레이</p>
                    <img src={gradcamSrc} alt="GradCAM 오버레이" className="w-full rounded-lg border border-gray-100 object-cover aspect-square" style={{ imageRendering: "pixelated" }} />
                  </div>
                </div>
                <p className="text-[12px] text-gray-400 mt-3 leading-relaxed text-center">빨간 영역일수록 AI가 판단 시 집중한 부위입니다.</p>
              </div>
            )}
            {!gradcamSrc && <p className="text-gray-400 text-[15px]">Grad-CAM 데이터 없음</p>}
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
            <div className="mt-5 pt-5 border-t border-gray-100">
              <PatternBadge topClass={topClass} topColor={topColor} isFail={isFail} />
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
