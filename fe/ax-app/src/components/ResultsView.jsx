import { useMemo, useState } from "react";
import { CheckCircle, XCircle, RefreshCw, Download, Target, BarChart2, AlertTriangle, Gauge, ScanLine } from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from "recharts";
import WaferMap from "./WaferMap.jsx";
import SearchHeader from "./SearchHeader.jsx";
import StatMiniCard from "./StatMiniCard.jsx";
import { DEFECT_CLASSES, CLASS_COLOR } from "../data/waferPatterns.js";
import { getHistory } from "../utils/inspectionHistory.js";

function badgeStyle(color) {
  return { backgroundColor: `${color}1A`, color };
}

export default function ResultsView({ result, onReset, onGoDashboard, onViewDetail }) {
  const [history] = useState(() => getHistory());

  const recentTrend = history.slice(-8);
  const patternCounts = useMemo(() => {
    const counts = {};
    history.forEach((h) => {
      counts[h.pattern] = (counts[h.pattern] || 0) + 1;
    });
    return DEFECT_CLASSES.map((c) => ({ key: c.key, color: c.color, count: counts[c.key] || 0 })).filter((c) => c.count > 0);
  }, [history]);

  if (!result) {
    return (
      <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#eef1f8" }}>
        <div className="px-8 py-8">
          <SearchHeader title="분석 결과" placeholder="Lot ID로 검색" />
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

  const { topClass, topColor, isFail, totalDies, failDies, yieldPct, sortedProbs, runnerUp } = result;
  const sparklineData = recentTrend.map((h, i) => ({ i, v: h.yieldPct }));

  return (
    <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#eef1f8" }}>
      <div className="flex gap-6 px-8 py-8">
        <div className="flex-1 min-w-0">
          <SearchHeader title="분석 결과" placeholder="Lot ID로 검색" />

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 mb-6">
            <div className="grid grid-cols-[240px_1fr] gap-6 mb-6">
              <div className="flex flex-col justify-between">
                <div>
                  <div className="text-[13px] text-gray-400 mb-2">이번 검사 수율</div>
                  <div className="text-[44px] font-extrabold leading-none" style={{ color: isFail ? "#e11d48" : "#059669" }}>{yieldPct}%</div>
                  <div className="flex items-center gap-2 mt-3 text-[13px] text-gray-500">
                    {isFail ? <XCircle size={15} className="text-rose-500" /> : <CheckCircle size={15} className="text-emerald-500" />}
                    감지 패턴 <strong style={{ color: topColor }}>{topClass}</strong>
                  </div>
                </div>
                <div className="mt-4">
                  <div style={{ height: 50 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={sparklineData}>
                        <Line type="monotone" dataKey="v" stroke="#3b82f6" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="text-[11px] text-gray-400 mt-1">최근 수율 추이</div>
                </div>
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
              <StatMiniCard icon={Target} iconBg={`${topColor}1A`} iconColor={topColor} label="예측 클래스" value={topClass} progress={sortedProbs[0].prob} progressColor={topColor} />
              <StatMiniCard icon={BarChart2} iconBg="#f1f5f9" iconColor="#64748b" label="2위 후보" value={runnerUp.key} progress={runnerUp.prob} progressColor="#64748b" />
              <StatMiniCard icon={AlertTriangle} iconBg="#fff1f2" iconColor="#e11d48" label="불량 다이" value={failDies} unit="ea" progress={(failDies / totalDies) * 100} progressColor="#e11d48" />
              <StatMiniCard icon={Gauge} iconBg={isFail ? "#fff1f2" : "#ecfdf5"} iconColor={isFail ? "#e11d48" : "#059669"} label="수율" value={`${yieldPct}%`} progress={Number(yieldPct)} progressColor={isFail ? "#e11d48" : "#059669"} />
            </div>
          </div>

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-[15px] font-semibold text-gray-800">웨이퍼 결함 맵</h2>
              <span className="text-[11px] text-gray-400">Φ 300mm</span>
            </div>
            <div className="grid grid-cols-[auto_1fr] gap-8 items-center">
              <div className="w-56 h-56"><WaferMap pattern={topClass} failColor={topColor} /></div>
              <div>
                <div className="flex items-center gap-6 text-[13px] mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: "#7fa8d9" }} />
                    <span className="text-gray-500">양품</span>
                    <span className="text-gray-700 font-semibold">{totalDies - failDies}ea</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: topColor }} />
                    <span className="text-gray-500">불량 ({topClass})</span>
                    <span className="text-gray-700 font-semibold">{failDies}ea</span>
                  </div>
                </div>
                <p className="text-gray-500 text-[13px] leading-relaxed">
                  {isFail
                    ? `${topClass} 패턴이 감지되었습니다 — 공정 점검 및 추가 검토가 필요합니다.`
                    : "특이 결함 패턴이 감지되지 않았습니다."}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 mb-6">
            <div className="mb-4">
              <h2 className="text-[15px] font-semibold text-gray-800">검사 이력 추이</h2>
              <p className="text-[11px] text-gray-400 mt-0.5">최근 검사한 로트마다 불량으로 판정된 다이(die) 개수 변화 — 검사를 실행할 때마다 자동으로 기록됩니다.</p>
            </div>
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={recentTrend} barSize={20}>
                  <CartesianGrid vertical={false} stroke="#f3f4f6" />
                  <XAxis dataKey="lot" tick={{ fill: "#9ca3af", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} axisLine={false} tickLine={false} width={28} />
                  <Tooltip contentStyle={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, fontSize: 12 }} labelStyle={{ color: "#374151" }} itemStyle={{ color: "#1a56db" }} cursor={{ fill: "#f3f4f6" }} />
                  <Bar dataKey="failDies" radius={[3, 3, 0, 0]}>
                    {recentTrend.map((row, i) => (
                      <Cell key={i} fill={CLASS_COLOR[row.pattern]} opacity={0.85} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h2 className="text-[15px] font-semibold text-gray-800">최근 검사 이력</h2>
              <span className="text-[12px] text-gray-400">최근 {recentTrend.length}건</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-[12px]">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50">
                    {["Lot ID", "판정 패턴", "신뢰도", "불량 다이", "수율", "결과"].map((h) => (
                      <th key={h} className="px-6 py-3 text-left text-[11px] text-gray-400 font-medium tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {recentTrend.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-gray-400">아직 검사 이력이 없습니다</td>
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
                        <td className="px-6 py-3 text-gray-700">{row.lot}</td>
                        <td className="px-6 py-3">
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold" style={badgeStyle(color)}>{row.pattern}</span>
                        </td>
                        <td className="px-6 py-3 text-gray-500">{row.confidence}%</td>
                        <td className="px-6 py-3 text-gray-500">{row.failDies}ea</td>
                        <td className="px-6 py-3 text-gray-500">{row.yieldPct}%</td>
                        <td className="px-6 py-3">
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
        </div>

        <aside className="w-[300px] flex-shrink-0 space-y-6">
          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <div className="text-[13px] text-gray-400 mb-2">종합 판정</div>
            <div className={`text-[36px] font-extrabold leading-none ${isFail ? "text-rose-600" : "text-emerald-600"}`}>{isFail ? "FAIL" : "PASS"}</div>
            <p className="text-gray-400 text-[12px] mt-3 leading-relaxed">
              {isFail
                ? `${topClass} 패턴 감지 — 수율 ${yieldPct}%로 기준치(95.0%) 미달입니다.`
                : `특이 패턴 없이 수율 ${yieldPct}%로 기준을 충족했습니다.`}
            </p>
            <div className="flex gap-2 mt-4">
              <button onClick={onReset} className="flex-1 flex items-center justify-center gap-1.5 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-[13px] font-medium hover:bg-gray-50 transition-colors">
                <RefreshCw size={13} />새 검사
              </button>
              <button className="flex-1 flex items-center justify-center gap-1.5 py-2.5 bg-blue-50 text-blue-600 rounded-xl text-[13px] font-medium hover:bg-blue-100 transition-colors">
                <Download size={13} />리포트
              </button>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
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

          {patternCounts.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <h3 className="text-[13px] font-semibold text-gray-800 mb-3">패턴별 검출 건수</h3>
              <div style={{ height: 110 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={patternCounts}>
                    <XAxis dataKey="key" tick={{ fill: "#9ca3af", fontSize: 10 }} axisLine={false} tickLine={false} interval={0} angle={-20} textAnchor="end" height={30} />
                    <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                      {patternCounts.map((p, i) => (
                        <Cell key={i} fill={p.color} opacity={0.85} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
