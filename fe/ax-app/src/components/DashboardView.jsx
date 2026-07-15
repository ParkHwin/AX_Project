import { useState, useRef, useCallback, useEffect } from "react";
import {
  Upload, CheckCircle, Scan, RefreshCw, AlertTriangle,
  ClipboardCheck, Target, Clock, Activity,
} from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
} from "recharts";
import SearchHeader from "./SearchHeader.jsx";
import StatMiniCard from "./StatMiniCard.jsx";

const SPARKLINE_DATA = [3, 4, 4, 6, 5, 7, 6, 8, 7, 9, 8, 10].map((v, i) => ({ i, v }));

const WEEKLY_DEFECT_RATE = [
  { day: "월", rate: 2.4 }, { day: "화", rate: 3.1 }, { day: "수", rate: 1.8 },
  { day: "목", rate: 4.2 }, { day: "금", rate: 2.9 },
];

export default function DashboardView({ onAnalyze, uploadedImage, setUploadedImage, onGoHistory }) {
  const [isDragging, setIsDragging] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileRef = useRef(null);
  const intervalRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(
    () => () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    },
    [],
  );

  const handleFile = useCallback(
    (file) => {
      if (!file.type.startsWith("image/")) return;
      const reader = new FileReader();
      reader.onload = (e) => setUploadedImage(e.target?.result);
      reader.readAsDataURL(file);
    },
    [setUploadedImage],
  );

  const handleAnalyze = () => {
    setAnalyzing(true);
    setProgress(0);
    intervalRef.current = setInterval(() => {
      setProgress((p) => {
        if (p >= 94) {
          clearInterval(intervalRef.current);
          timeoutRef.current = setTimeout(() => {
            setAnalyzing(false);
            onAnalyze();
          }, 500);
          return 96;
        }
        return p + Math.random() * 9 + 3;
      });
    }, 160);
  };

  return (
    <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#eef1f8" }}>
      <div className="flex gap-6 px-8 py-8">
        <div className="flex-1 min-w-0">
          <SearchHeader title="대시보드" placeholder="Lot ID로 검색" />

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 mb-6">
            <div className="grid grid-cols-[240px_1fr] gap-6 mb-6">
              <div className="flex flex-col justify-between">
                <div>
                  <div className="text-[13px] text-gray-400 mb-2">오늘 검사 현황</div>
                  <div className="text-[44px] font-extrabold text-gray-900 leading-none">47</div>
                  <div className="flex items-center gap-2 mt-3 text-[13px] text-gray-500">
                    <Activity size={15} className="text-blue-500" />
                    시간당 처리 건수
                  </div>
                </div>
                <div className="mt-4">
                  <div style={{ height: 50 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={SPARKLINE_DATA}>
                        <Line type="monotone" dataKey="v" stroke="#3b82f6" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="text-[11px] text-gray-400 mt-1">최근 12시간 추이</div>
                </div>
              </div>

              <div className="bg-blue-500 rounded-2xl p-5">
                <div className="text-white/80 text-[12px] mb-1">요일별 평균 불량률</div>
                <div style={{ height: 195 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={WEEKLY_DEFECT_RATE}>
                      <CartesianGrid stroke="rgba(255,255,255,0.25)" strokeDasharray="4 4" vertical={false} />
                      <XAxis dataKey="day" tick={{ fill: "rgba(255,255,255,0.75)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: "rgba(255,255,255,0.75)", fontSize: 11 }} axisLine={false} tickLine={false} width={24} unit="%" />
                      <Bar dataKey="rate" fill="#ffffff" radius={[4, 4, 0, 0]} opacity={0.9} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4 pt-6 border-t border-gray-100">
              <StatMiniCard icon={ClipboardCheck} iconBg="#eef1f6" iconColor="#1b2f5e" label="오늘 검사" value="47" unit="개" progress={62} progressColor="#1b2f5e" />
              <StatMiniCard icon={AlertTriangle} iconBg="#fff1f2" iconColor="#e11d48" label="평균 불량률" value="3.2" unit="%" progress={32} progressColor="#e11d48" />
              <StatMiniCard icon={Target} iconBg="#ecfdf5" iconColor="#059669" label="AI 정확도" value="99.1" unit="%" progress={99} progressColor="#059669" />
              <StatMiniCard icon={Clock} iconBg="#fffbeb" iconColor="#d97706" label="처리 대기" value="6" unit="lot" progress={40} progressColor="#d97706" />
            </div>
          </div>

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <h2 className="text-[15px] font-semibold text-gray-800 mb-4">웨이퍼 이미지 업로드</h2>

            <div
              className={`relative bg-white rounded-2xl border-2 transition-all ${
                isDragging
                  ? "border-blue-400 bg-blue-50/30"
                  : uploadedImage
                    ? "border-gray-200"
                    : "border-dashed border-gray-300 hover:border-blue-400 cursor-pointer"
              }`}
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                const f = e.dataTransfer.files[0];
                if (f) handleFile(f);
              }}
              onClick={() => !uploadedImage && !analyzing && fileRef.current?.click()}
            >
              <input
                ref={fileRef}
                type="file"
                className="hidden"
                accept="image/*"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) handleFile(f);
                }}
              />

              {uploadedImage ? (
                <div className="flex gap-6 items-start p-6">
                  <div className="relative flex-shrink-0">
                    <img src={uploadedImage} alt="업로드된 웨이퍼 이미지" className="w-40 h-40 object-cover rounded-xl border border-gray-200" />
                    <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center shadow">
                      <CheckCircle size={13} className="text-white" />
                    </div>
                  </div>
                  <div className="flex-1 py-1">
                    <div className="flex items-center gap-2 mb-4">
                      <CheckCircle size={15} className="text-emerald-500" />
                      <span className="text-emerald-700 text-[13px] font-medium">이미지 업로드 완료</span>
                    </div>
                    <div className="grid grid-cols-3 gap-x-6 gap-y-2.5 mb-5">
                      {[
                        ["파일 형식", "TIFF"], ["해상도", "2048 × 2048"],
                        ["스캔 모드", "Bright Field"], ["Lot ID", "WF-2024-A1047"],
                        ["웨이퍼 크기", "300 mm"], ["노드 공정", "3nm GAA"],
                      ].map(([k, v]) => (
                        <div key={k}>
                          <div className="text-[11px] text-gray-400 mb-0.5">{k}</div>
                          <div className={`text-[13px] font-medium ${k === "Lot ID" ? "text-blue-600" : "text-gray-700"}`}>{v}</div>
                        </div>
                      ))}
                    </div>
                    <div className="flex gap-2.5">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAnalyze();
                        }}
                        disabled={analyzing}
                        className="flex items-center gap-2 px-5 py-2 bg-blue-600 text-white rounded-lg text-[13px] font-medium hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-60"
                      >
                        {analyzing ? (
                          <>
                            <RefreshCw size={13} className="animate-spin" />
                            <span>분석 중...</span>
                          </>
                        ) : (
                          <>
                            <Scan size={13} />
                            <span>AI 불량 분석 시작</span>
                          </>
                        )}
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setUploadedImage(null);
                        }}
                        className="px-4 py-2 border border-gray-300 text-gray-500 rounded-lg text-[13px] hover:border-gray-400 hover:text-gray-700 transition-colors"
                      >
                        재업로드
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-14 px-8">
                  <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center">
                    <Upload size={22} className="text-blue-500" />
                  </div>
                  <p className="text-gray-700 font-medium text-[15px] mb-1">웨이퍼 이미지를 드래그하거나 클릭하여 업로드</p>
                  <p className="text-gray-400 text-[13px]">TIFF, PNG, BMP 지원 · 최대 500 MB</p>
                  <div className="flex items-center justify-center gap-5 mt-6">
                    {["SEM Scan", "Optical", "Dark Field", "Bright Field"].map((t) => (
                      <span key={t} className="text-[11px] text-gray-300">{t}</span>
                    ))}
                  </div>
                </div>
              )}

              {analyzing && (
                <div className="absolute inset-0 bg-white/92 rounded-2xl flex flex-col items-center justify-center backdrop-blur-sm z-10">
                  <div className="w-64 mb-5">
                    <div className="flex items-center justify-between text-[12px] mb-2">
                      <span className="text-gray-600 font-medium">
                        {progress < 30
                          ? "이미지 전처리 중..."
                          : progress < 60
                            ? "결함 패턴 감지 중..."
                            : progress < 85
                              ? "분류 모델 실행 중..."
                              : "결과 집계 중..."}
                      </span>
                      <span className="text-blue-600 font-medium">{Math.min(Math.round(progress), 96)}%</span>
                    </div>
                    <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-600 rounded-full transition-all duration-200" style={{ width: `${Math.min(progress, 96)}%` }} />
                    </div>
                  </div>
                  <p className="text-gray-400 text-[12px]">AI 모델 분석 진행 중 — 잠시만 기다려 주세요</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <aside className="w-[300px] flex-shrink-0 space-y-6">
          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <div className="text-[13px] text-gray-400 mb-2">이번 달 처리 현황</div>
            <div className="text-[36px] font-extrabold text-gray-900 leading-none">1,284<span className="text-[16px] text-gray-400 font-medium ml-1">lot</span></div>
            <p className="text-gray-400 text-[12px] mt-3 leading-relaxed">전체 검사 이력을 로트별로 확인하고<br />추이를 분석해 보세요.</p>
            <button
              onClick={onGoHistory}
              className="mt-4 w-full py-2.5 bg-blue-50 text-blue-600 rounded-xl text-[13px] font-medium hover:bg-blue-100 transition-colors"
            >
              전체 이력 보기
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}
