import { useState } from "react";
import LoginPage from "./components/LoginPage.jsx";
import SignupPage from "./components/SignupPage.jsx";
import Sidebar from "./components/Sidebar.jsx";
import DashboardView from "./components/DashboardView.jsx";
import ResultsView from "./components/ResultsView.jsx";
import HistoryView from "./components/HistoryView.jsx";
import AnalysisDetailView from "./components/AnalysisDetailView.jsx";
import { getSession, clearSession } from "./utils/auth.js";
import { uploadWaferImage, getAnalysisDetail, getAnalysisList } from "./utils/api.js";
import { CLASS_COLOR } from "./data/waferPatterns.js";
import { createThumbnail } from "./utils/thumbnail.js";

export default function App() {
  const [session, setSession] = useState(getSession);
  const [authView, setAuthView] = useState("login");
  const [page, setPage] = useState("dashboard");
  const [uploadedImages, setUploadedImages] = useState([]);
  const [signupNotice, setSignupNotice] = useState("");
  const [batchResults, setBatchResults] = useState([]);
  const [selectedRecord, setSelectedRecord] = useState(null);

  const handleLogout = () => {
    clearSession();
    setSession(null);
    setAuthView("login");
    setPage("dashboard");
    setUploadedImages([]);
    setSignupNotice("");
    setBatchResults([]);
  };

  const handleQueueStart = () => setBatchResults([]);

  const handleAnalyzeImage = async (file, dataUrl) => {
    try {
      const upload = await uploadWaferImage(file, session.user_num);
      const sortedProbs = upload.class_name.map((name, i) => ({
        key: name,
        prob: Math.round(upload.confidence[i] * 1000) / 10,
      }));
      const topClass = sortedProbs[0].key;
      const topColor = CLASS_COLOR[topClass];
      const isFail = upload.class_id[0] !== 8;
      const runnerUp = sortedProbs[1];
      const thumbnail = await createThumbnail(dataUrl);
      const record = {
        lot: file.name,
        pattern: topClass,
        confidence: sortedProbs[0].prob,
        probabilities: sortedProbs,
        thumbnail,
        timestamp: Date.now(),
        gradcam_data: upload.gradcam_data || null,
        process_info: upload.process_info || null,
      };
      setBatchResults((prev) => [...prev, { topClass, topColor, isFail, sortedProbs, runnerUp, record }]);
    } catch (err) {
      console.error("분석 실패:", err.message);
    }
  };

  const handleQueueDone = () => setPage("results");

  const goDashboard = () => {
    setUploadedImages([]);
    setPage("dashboard");
  };

  const resetAndGoDashboard = () => {
    setUploadedImages([]);
    setBatchResults([]);
    setPage("dashboard");
  };

  const handleViewDetail = async (item) => {
    if (item.analysis_id) {
      try {
        const detail = await getAnalysisDetail(item.analysis_id, session.user_num);
        const probs = detail.top_predictions.map((p) => ({
          key: p.class_name,
          prob: Math.round(p.confidence * 1000) / 10,
        }));
        setSelectedRecord({
          lot: detail.image_name || `A${detail.analysis_id}`,
          pattern: detail.top_predictions[0].class_name,
          confidence: Math.round(detail.top_predictions[0].confidence * 1000) / 10,
          probabilities: probs,
          thumbnail: null,
          timestamp: new Date(detail.created_at).getTime(),
          image_id: detail.image_id,
          gradcam_data: detail.gradcam_data || null,
          process_info: detail.process_info || null,
        });
      } catch {
        setSelectedRecord(item);
      }
    } else {
      setSelectedRecord(item);
    }
    setPage("detail");
  };

  const handleSearchLot = async (query) => {
    if (!query || !session?.user_num) return false;
    try {
      const data = await getAnalysisList(session.user_num, 1, 100);
      const q = query.trim().toLowerCase();
      const match =
        data.items.find((it) => (it.image_name || "").toLowerCase() === q) ||
        data.items.find((it) => (it.image_name || "").toLowerCase().includes(q));
      if (!match) return false;
      await handleViewDetail({
        lot: match.image_name || `A${match.analysis_id}`,
        pattern: match.top_class_name,
        confidence: Math.round(match.confidence * 1000) / 10,
        probabilities: [],
        thumbnail: null,
        timestamp: new Date(match.created_at).getTime(),
        analysis_id: match.analysis_id,
        image_id: match.image_id,
      });
      return true;
    } catch {
      return false;
    }
  };

  if (!session) {
    if (authView === "signup") {
      return (
        <SignupPage
          onGoLogin={() => setAuthView("login")}
          onSignedUp={() => {
            setSignupNotice("회원가입이 완료되었습니다. 로그인해 주세요.");
            setAuthView("login");
          }}
        />
      );
    }
    return (
      <LoginPage
        notice={signupNotice}
        onGoSignup={() => {
          setSignupNotice("");
          setAuthView("signup");
        }}
        onLogin={(s) => setSession(s)}
      />
    );
  }

  return (
    <div className="h-screen bg-gray-50 flex overflow-hidden">
      <Sidebar
        active={page === "detail" ? "history" : page}
        session={session}
        onNavigate={(p) => {
          if (p === "dashboard") goDashboard();
          else if (p === "results" || p === "history") setPage(p);
        }}
        onLogout={handleLogout}
      />

      <div className="flex flex-1 overflow-hidden">
        {page === "results" ? (
          <ResultsView
            results={batchResults}
            recentHistory={batchResults.map((r) => r.record).filter(Boolean)}
            onReset={resetAndGoDashboard}
            onGoDashboard={goDashboard}
            onViewDetail={handleViewDetail}
            onSearchLot={handleSearchLot}
          />
        ) : page === "history" ? (
          <HistoryView session={session} onViewDetail={handleViewDetail} onSearchLot={handleSearchLot} />
        ) : page === "detail" ? (
          <AnalysisDetailView
            record={selectedRecord}
            onBack={() => setPage("history")}
          />
        ) : (
          <DashboardView
            session={session}
            onQueueStart={handleQueueStart}
            onAnalyzeImage={handleAnalyzeImage}
            onQueueDone={handleQueueDone}
            uploadedImages={uploadedImages}
            setUploadedImages={setUploadedImages}
          />
        )}
      </div>
    </div>
  );
}
