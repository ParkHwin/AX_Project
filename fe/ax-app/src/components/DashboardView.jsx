import { useState, useRef, useCallback, useEffect } from "react";
import {
  Upload, CheckCircle, Scan, RefreshCw, X, Plus,
  Activity,
} from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, LabelList, Cell,
} from "recharts";
import SearchHeader from "./SearchHeader.jsx";
import StatMiniCard from "./StatMiniCard.jsx";
import { getDashboard } from "../utils/api.js";

function readAsDataUrl(file) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target?.result);
    reader.readAsDataURL(file);
  });
}

function HourlyTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-100 px-2.5 py-1.5">
      <div className="text-[11px] font-semibold text-gray-800">{d.hour}</div>
      <div className="text-[11px] text-blue-600 font-medium">{d.v}건 처리</div>
    </div>
  );
}

function WeeklyDefectTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-100 px-3 py-2">
      <div className="text-[12px] font-semibold text-gray-800 mb-1">{d.day}요일</div>
      <div className="text-[11px] text-gray-500">
        불량률 <span className="font-semibold text-rose-500">{d.rate.toFixed(1)}%</span>
      </div>
      <div className="text-[11px] text-gray-400">불량 {d.fail}건 / 총 {d.total}건</div>
    </div>
  );
}

export default function DashboardView({ session, onQueueStart, onAnalyzeImage, onQueueDone, uploadedImages, setUploadedImages }) {
  const [isDragging, setIsDragging] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [dashboard, setDashboard] = useState(null);
  const fileRef = useRef(null);
  const intervalRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    if (!session?.user_num) return;
    getDashboard(session.user_num).then(setDashboard).catch(() => {});
  }, [session?.user_num]);

  useEffect(
    () => () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    },
    [],
  );

  const addFiles = useCallback(
    async (fileList) => {
      const files = [...fileList].filter((f) => f.type.startsWith("image/"));
      if (files.length === 0) return;
      const items = await Promise.all(
        files.map(async (file) => ({
          id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
          name: file.name,
          file,
          dataUrl: await readAsDataUrl(file),
          status: "pending",
        })),
      );
      setUploadedImages((prev) => [...prev, ...items]);
    },
    [setUploadedImages],
  );

  const removeImage = (id) => {
    setUploadedImages((prev) => prev.filter((img) => img.id !== id));
  };

  const runProgress = () =>
    new Promise((resolve) => {
      setProgress(0);
      intervalRef.current = setInterval(() => {
        setProgress((p) => {
          if (p >= 94) {
            clearInterval(intervalRef.current);
            timeoutRef.current = setTimeout(resolve, 400);
            return 96;
          }
          return p + Math.random() * 9 + 3;
        });
      }, 140);
    });

  const handleAnalyzeAll = async () => {
    const pending = uploadedImages.filter((img) => img.status === "pending");
    if (pending.length === 0) return;
    setAnalyzing(true);
    onQueueStart();

    for (const img of pending) {
      setActiveIndex((i) => i + 1);
      setUploadedImages((prev) => prev.map((x) => (x.id === img.id ? { ...x, status: "analyzing" } : x)));
      await runProgress();
      await onAnalyzeImage(img.file, img.dataUrl);
      setUploadedImages((prev) => prev.map((x) => (x.id === img.id ? { ...x, status: "done" } : x)));
    }

    setAnalyzing(false);
    setActiveIndex(-1);
    onQueueDone();
  };

  const pendingCount = uploadedImages.filter((img) => img.status === "pending").length;
  const doneCount = uploadedImages.filter((img) => img.status === "done").length;
  const currentImage = uploadedImages.find((img) => img.status === "analyzing");
  const totalQueued = uploadedImages.filter((img) => img.status !== "done").length;

  const todayCount = dashboard?.today_count ?? 0;
  const defectRate = dashboard ? dashboard.today_defect_rate.toFixed(1) : "0.0";
  const avgConfidence = dashboard ? (dashboard.average_confidence * 100).toFixed(1) : "0.0";
  const sparklineData = dashboard?.hourly_counts
    ? dashboard.hourly_counts.slice(-12).map((h) => ({ hour: h.hour, v: h.count }))
    : Array.from({ length: 12 }, (_, i) => ({ hour: `${i}시`, v: 0 }));
  const peakHour = sparklineData.length
    ? sparklineData.reduce((max, h) => (h.v > max.v ? h : max), sparklineData[0])
    : null;
  const weeklyData = dashboard?.weekday_defect_rates
    ? dashboard.weekday_defect_rates.map((w) => ({
        day: w.weekday,
        rate: w.defect_rate,
        total: w.total_count,
        fail: w.fail_count,
      }))
    : [];
  const worstWeekday = weeklyData.length
    ? weeklyData.reduce((max, w) => (w.rate > max.rate ? w : max), weeklyData[0])
    : null;

  return (
    <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#eef1f8" }}>
      <div className="flex gap-6 px-8 py-8">
        <div className="flex-1 min-w-0">
          <SearchHeader title="대시보드" showSearch={false} />

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6 mb-6">
            <div className="grid grid-cols-[240px_1fr] gap-6 mb-6">
              <div className="flex flex-col justify-between">
                <div>
                  <div className="text-[13px] text-gray-400 mb-2">오늘 검사 현황</div>
                  <div className="text-[44px] font-extrabold text-gray-900 leading-none">{todayCount}</div>
                  <div className="flex items-center gap-2 mt-3 text-[13px] text-gray-500">
                    <Activity size={15} className="text-blue-500" />
                    시간당 처리 건수
                  </div>
                </div>
                <div className="mt-4">
                  <div style={{ height: 50 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={sparklineData}>
                        <Tooltip content={<HourlyTooltip />} cursor={{ stroke: "#c7d2fe", strokeWidth: 1 }} />
                        <Line
                          type="monotone"
                          dataKey="v"
                          stroke="#3b82f6"
                          strokeWidth={2}
                          dot={false}
                          activeDot={{ r: 4, fill: "#3b82f6", stroke: "#fff", strokeWidth: 1.5 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-gray-400 mt-1">
                    <span>최근 12시간 추이</span>
                    {peakHour && peakHour.v > 0 && (
                      <span className="text-gray-500 font-medium">피크 {peakHour.hour} · {peakHour.v}건</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="bg-blue-500 rounded-2xl p-5">
                <div className="flex items-center justify-between mb-1">
                  <div className="text-white/80 text-[12px]">요일별 평균 불량률</div>
                  {worstWeekday && (
                    <div className="text-white text-[10px] font-medium bg-white/15 px-2 py-0.5 rounded-full">
                      최고 {worstWeekday.day}요일 {worstWeekday.rate.toFixed(1)}%
                    </div>
                  )}
                </div>
                <div style={{ height: 195 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={weeklyData} margin={{ top: 16, right: 4, left: -8, bottom: 0 }}>
                      <CartesianGrid stroke="rgba(255,255,255,0.25)" strokeDasharray="4 4" vertical={false} />
                      <XAxis dataKey="day" tick={{ fill: "rgba(255,255,255,0.75)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis
                        tick={{ fill: "rgba(255,255,255,0.75)", fontSize: 11 }}
                        axisLine={false}
                        tickLine={false}
                        width={24}
                        unit="%"
                        domain={[0, (dataMax) => Math.max(10, Math.ceil(dataMax + 5))]}
                      />
                      <Tooltip content={<WeeklyDefectTooltip />} cursor={{ fill: "rgba(255,255,255,0.12)" }} />
                      <Bar dataKey="rate" radius={[4, 4, 0, 0]}>
                        {weeklyData.map((w, i) => (
                          <Cell
                            key={i}
                            fill={worstWeekday && w.day === worstWeekday.day ? "#fecaca" : "#ffffff"}
                            opacity={worstWeekday && w.day === worstWeekday.day ? 1 : 0.85}
                          />
                        ))}
                        <LabelList
                          dataKey="rate"
                          position="top"
                          formatter={(v) => `${Number(v).toFixed(0)}%`}
                          style={{ fill: "rgba(255,255,255,0.85)", fontSize: 10, fontWeight: 600 }}
                        />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4 pt-6 border-t border-gray-100">
              <StatMiniCard label="오늘 검사" value={todayCount} unit="개" progress={Math.min(todayCount, 100)} progressColor="#1b2f5e" />
              <StatMiniCard label="평균 불량률" value={defectRate} unit="%" progress={Number(defectRate)} progressColor="#e11d48" />
              <StatMiniCard label="AI 정확도" value={avgConfidence} unit="%" progress={Number(avgConfidence)} progressColor="#059669" />
              <StatMiniCard
                label="처리 대기"
                value={uploadedImages.length > 0 ? totalQueued : 0}
                unit="lot"
                progress={uploadedImages.length > 0 ? (totalQueued / uploadedImages.length) * 100 : 0}
                progressColor="#d97706"
              />
            </div>
          </div>

          <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-[15px] font-semibold text-gray-800">웨이퍼 이미지 업로드</h2>
              {uploadedImages.length > 0 && !analyzing && (
                <button
                  onClick={() => setUploadedImages([])}
                  className="text-[12px] text-gray-400 hover:text-gray-600 transition-colors"
                >
                  모두 지우기
                </button>
              )}
            </div>

            <div
              className={`relative bg-white rounded-2xl border-2 transition-all ${
                isDragging
                  ? "border-blue-400 bg-blue-50/30"
                  : uploadedImages.length > 0
                    ? "border-gray-200"
                    : "border-dashed border-gray-300 hover:border-blue-400 cursor-pointer"
              }`}
              onDragOver={(e) => {
                e.preventDefault();
                if (!analyzing) setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                if (analyzing) return;
                if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
              }}
              onClick={() => uploadedImages.length === 0 && !analyzing && fileRef.current?.click()}
            >
              <input
                ref={fileRef}
                type="file"
                multiple
                className="hidden"
                accept="image/*"
                onChange={(e) => {
                  if (e.target.files?.length) addFiles(e.target.files);
                  e.target.value = "";
                }}
              />

              {uploadedImages.length > 0 ? (
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-4 text-[13px] text-gray-600">
                    <CheckCircle size={15} className="text-emerald-500" />
                    <span className="font-medium">{uploadedImages.length}장 업로드됨</span>
                    {doneCount > 0 && <span className="text-gray-400">· 완료 {doneCount}장</span>}
                    {!analyzing && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          fileRef.current?.click();
                        }}
                        className="ml-auto flex items-center gap-1 text-blue-500 hover:text-blue-600 text-[12px] font-medium"
                      >
                        <Plus size={13} />
                        이미지 추가
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-6 gap-3 mb-5">
                    {uploadedImages.map((img) => (
                      <div key={img.id} className="relative aspect-square rounded-xl overflow-hidden border border-gray-200 bg-gray-50">
                        <img src={img.dataUrl} alt={img.name} className="w-full h-full object-cover" />
                        {img.status === "pending" && !analyzing && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              removeImage(img.id);
                            }}
                            className="absolute top-1 right-1 w-5 h-5 rounded-full bg-black/50 hover:bg-black/70 flex items-center justify-center transition-colors"
                          >
                            <X size={11} className="text-white" />
                          </button>
                        )}
                        {img.status === "analyzing" && (
                          <div className="absolute inset-0 bg-white/80 flex items-center justify-center">
                            <RefreshCw size={16} className="text-blue-500 animate-spin" />
                          </div>
                        )}
                        {img.status === "done" && (
                          <div className="absolute bottom-1 right-1 w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center shadow">
                            <CheckCircle size={11} className="text-white" />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="flex gap-2.5">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAnalyzeAll();
                      }}
                      disabled={analyzing || pendingCount === 0}
                      className="flex items-center gap-2 px-5 py-2 bg-blue-600 text-white rounded-lg text-[13px] font-medium hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-60"
                    >
                      {analyzing ? (
                        <>
                          <RefreshCw size={13} className="animate-spin" />
                          <span>분석 중... ({Math.min(activeIndex + 1, uploadedImages.length)}/{uploadedImages.length})</span>
                        </>
                      ) : (
                        <>
                          <Scan size={13} />
                          <span>AI 불량 분석 시작{pendingCount > 0 ? ` (${pendingCount}장)` : ""}</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-14 px-8">
                  <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center">
                    <Upload size={22} className="text-blue-500" />
                  </div>
                  <p className="text-gray-700 font-medium text-[15px] mb-1">웨이퍼 이미지를 드래그하거나 클릭하여 업로드</p>
                  <p className="text-gray-400 text-[13px]">PNG(팔레트 모드) · 최대 5 MB</p>
                  <div className="flex items-center justify-center gap-5 mt-6">
                    {["SEM Scan", "Optical", "Dark Field", "Bright Field"].map((t) => (
                      <span key={t} className="text-[11px] text-gray-300">{t}</span>
                    ))}
                  </div>
                </div>
              )}

              {analyzing && (
                <div className="absolute inset-0 bg-white/92 rounded-2xl flex flex-col items-center justify-center backdrop-blur-sm z-10">
                  {currentImage && (
                    <img src={currentImage.dataUrl} alt="" className="w-16 h-16 object-cover rounded-lg border border-gray-200 mb-4" />
                  )}
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
                  <p className="text-gray-400 text-[12px]">
                    {Math.min(activeIndex + 1, uploadedImages.length)}/{uploadedImages.length}번째 이미지 분석 중 — 잠시만 기다려 주세요
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
