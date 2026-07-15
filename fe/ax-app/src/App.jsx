import { useState } from "react";
import LoginPage from "./components/LoginPage.jsx";
import SignupPage from "./components/SignupPage.jsx";
import Sidebar from "./components/Sidebar.jsx";
import DashboardView from "./components/DashboardView.jsx";
import ResultsView from "./components/ResultsView.jsx";
import HistoryView from "./components/HistoryView.jsx";
import AnalysisDetailView from "./components/AnalysisDetailView.jsx";
import { getSession, clearSession } from "./utils/auth.js";
import { classifyWafer } from "./data/waferPatterns.js";
import { addInspectionRecord, getRecordByLot } from "./utils/inspectionHistory.js";
import { createThumbnail } from "./utils/thumbnail.js";

export default function App() {
  const [session, setSession] = useState(getSession);
  const [authView, setAuthView] = useState("login");
  const [page, setPage] = useState("dashboard");
  const [uploadedImage, setUploadedImage] = useState(null);
  const [signupNotice, setSignupNotice] = useState("");
  const [currentResult, setCurrentResult] = useState(null);
  const [selectedRecord, setSelectedRecord] = useState(null);

  const handleLogout = () => {
    clearSession();
    setSession(null);
    setAuthView("login");
    setPage("dashboard");
    setUploadedImage(null);
    setSignupNotice("");
    setCurrentResult(null);
  };

  const handleAnalyze = async () => {
    const result = classifyWafer();
    const thumbnail = await createThumbnail(uploadedImage);
    const { record } = addInspectionRecord({
      pattern: result.topClass,
      confidence: result.sortedProbs[0].prob,
      probabilities: result.sortedProbs,
      failDies: result.failDies,
      totalDies: result.totalDies,
      yieldPct: Number(result.yieldPct),
      thumbnail,
    });
    setCurrentResult({ ...result, record });
    setPage("results");
  };

  const handleViewDetail = (record) => {
    setSelectedRecord(record);
    setPage("detail");
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
          if (p === "dashboard" || p === "results" || p === "history") setPage(p);
        }}
        onLogout={handleLogout}
      />

      <div className="flex flex-1 overflow-hidden">
        {page === "results" ? (
          <ResultsView
            result={currentResult}
            onReset={() => {
              setUploadedImage(null);
              setCurrentResult(null);
              setPage("dashboard");
            }}
            onGoDashboard={() => setPage("dashboard")}
            onViewDetail={handleViewDetail}
          />
        ) : page === "history" ? (
          <HistoryView onViewDetail={handleViewDetail} />
        ) : page === "detail" ? (
          <AnalysisDetailView
            record={selectedRecord ? getRecordByLot(selectedRecord.lot) : null}
            onBack={() => setPage("history")}
          />
        ) : (
          <DashboardView
            onAnalyze={handleAnalyze}
            uploadedImage={uploadedImage}
            setUploadedImage={setUploadedImage}
            onGoHistory={() => setPage("history")}
          />
        )}
      </div>
    </div>
  );
}
