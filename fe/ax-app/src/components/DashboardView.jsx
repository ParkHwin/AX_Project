import { useState, useRef, useCallback, useEffect } from "react";
import {
  Upload, CheckCircle, Scan, RefreshCw, AlertTriangle, X, Plus,
  ClipboardCheck, Target, Clock, Activity,
} from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
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
    ? dashboard.hourly_counts.slice(-12).map((h, i) => ({ i, v: h.count }))
    : Array.from({ length: 12 }, (_, i) => ({ i, v: 0 }));
  const weeklyData = dashboard?.weekday_defect_rates
    ? dashboard.weekday_defect_rates.map((w) => ({ day: w.weekday, rate: w.defect_rate }))
    : [];

  return (
    <div className="flex-1 overflow-y-auto scrollbar-hide" style={{ background: "#eef1f8" }}>
      <div className="flex gap-6 px-8 py-8 max-w-5xl mx-auto">
        <div className="flex-1 min-w-0">
          <SearchHeader title="대시보드" placeholder="Lot ID로 검색" />

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
                    <BarChart data={weeklyData}>
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
              <StatMiniCard icon={ClipboardCheck} iconBg="#eef1f6" iconColor="#1b2f5e" label="오늘 검사" value={todayCount} unit="개" progress={Math.min(todayCount, 100)} progressColor="#1b2f5e" />
              <StatMiniCard icon={AlertTriangle} iconBg="#fff1f2" iconColor="#e11d48" label="평균 불량률" value={defectRate} unit="%" progress={Number(defectRate)} progressColor="#e11d48" />
              <StatMiniCard icon={Target} iconBg="#ecfdf5" iconColor="#059669" label="AI 정확도" value={avgConfidence} unit="%" progress={Number(avgConfidence)} progressColor="#059669" />
              <StatMiniCard
                icon={Clock}
                iconBg="#fffbeb"
                iconColor="#d97706"
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
