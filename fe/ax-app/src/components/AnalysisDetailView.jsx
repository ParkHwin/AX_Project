import { ArrowLeft, CheckCircle, XCircle, ImageOff, Target, BarChart2, AlertTriangle } from "lucide-react";
import WaferMap from "./WaferMap.jsx";
import StatMiniCard from "./StatMiniCard.jsx";
import SearchHeader from "./SearchHeader.jsx";
import { DEFECT_CLASSES, CLASS_COLOR } from "../data/waferPatterns.js";
import { formatTimestamp } from "../utils/formatTimestamp.js";

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

  return (
    <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#eef1f8" }}>
      <div className="px-8 py-8 max-w-5xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <button onClick={onBack} className="flex items-center gap-1.5 text-gray-400 hover:text-gray-600 text-[12px] mb-2 transition-colors">
              <ArrowLeft size={13} />검사 이력으로
            </button>
            <h1 className="text-[26px] font-bold text-[#1b2f5e]">분석 상세 조회</h1>
            <p className="text-gray-400 text-[12px] mt-1">{record.lot} · {formatTimestamp(record.timestamp)}</p>
          </div>
        </div>

        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 mb-6">
          <div className="grid grid-cols-[112px_1fr_auto] gap-6 items-center">
            <div className="w-28 h-28 rounded-2xl overflow-hidden bg-gray-100 flex items-center justify-center flex-shrink-0">
              {record.thumbnail ? (
                <img src={record.thumbnail} alt={`${record.lot} 웨이퍼 이미지`} className="w-full h-full object-cover" />
              ) : (
                <ImageOff size={22} className="text-gray-300" />
              )}
            </div>
            <div className="flex items-center gap-3">
              {isFail ? <XCircle size={30} className="text-rose-500 flex-shrink-0" /> : <CheckCircle size={30} className="text-emerald-500 flex-shrink-0" />}
              <div>
                <div className={`text-[22px] font-extrabold leading-none ${isFail ? "text-rose-600" : "text-emerald-600"}`}>{isFail ? "FAIL" : "PASS"}</div>
                <p className="text-gray-500 text-[13px] mt-1">
                  감지 패턴 <strong style={{ color: topColor }}>{topClass}</strong> · 불량 다이 {record.failDies}/{record.totalDies}ea
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4 pt-6 mt-6 border-t border-gray-100">
            <StatMiniCard icon={Target} iconBg={`${topColor}1A`} iconColor={topColor} label="예측 클래스" value={topClass} progress={sortedProbs[0].prob} progressColor={topColor} />
            <StatMiniCard icon={BarChart2} iconBg="#f1f5f9" iconColor="#64748b" label="2위 후보" value={runnerUp?.key ?? "-"} progress={runnerUp?.prob ?? 0} progressColor="#64748b" />
            <StatMiniCard icon={AlertTriangle} iconBg="#fff1f2" iconColor="#e11d48" label="불량 다이" value={record.failDies} unit="ea" progress={(record.failDies / record.totalDies) * 100} progressColor="#e11d48" />
            <StatMiniCard icon={CheckCircle} iconBg="#ecfdf5" iconColor="#059669" label="정상 다이" value={record.totalDies - record.failDies} unit="ea" progress={((record.totalDies - record.failDies) / record.totalDies) * 100} progressColor="#059669" />
          </div>
        </div>

        <div className="grid grid-cols-5 gap-5">
          <div className="col-span-2 bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-[15px] font-semibold text-gray-800">웨이퍼 결함 맵</h2>
              <span className="text-[11px] text-gray-400">Φ 300mm</span>
            </div>
            <div className="aspect-square"><WaferMap pattern={topClass} failColor={topColor} /></div>
          </div>

          <div className="col-span-3 bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-[15px] font-semibold text-gray-800 mb-4">결함 패턴 분류 결과 (9종)</h2>
            <div className="space-y-2.5">
              {sortedProbs.map((p) => {
                const color = CLASS_COLOR[p.key];
                const isTop = p.key === topClass;
                return (
                  <div key={p.key}>
                    <div className="flex items-center justify-between text-[12px] mb-1">
                      <span className={isTop ? "font-semibold text-gray-800" : "text-gray-500"}>{p.key}</span>
                      <span className={isTop ? "font-semibold" : "text-gray-400"} style={isTop ? { color } : undefined}>{p.prob}%</span>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${Math.max(p.prob, 1)}%`, backgroundColor: color }} />
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-5 pt-4 border-t border-gray-100 flex flex-wrap gap-x-4 gap-y-1">
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
