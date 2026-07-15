import { useState } from "react";
import { Mail, Lock, Eye, EyeOff, User } from "lucide-react";
import DeviceLogo from "./DeviceLogo.jsx";
import SemiBg from "./SemiBg.jsx";
import { loginUser } from "../utils/auth.js";

export default function LoginPage({ onLogin, onGoSignup, notice }) {
  const [showPass, setShowPass] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      setError("이메일과 비밀번호를 입력해 주세요.");
      return;
    }
    const result = loginUser(email.trim(), password);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    onLogin(result.session);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden" style={{ background: "#f0f2f6" }}>
      <SemiBg />
      <div className="relative z-10 w-full max-w-sm">
        <div className="text-center mb-7">
          <DeviceLogo className="h-12 w-auto mx-auto mb-5" />
          <p className="text-gray-400 text-[14px]">Wafer Inspection AI Platform</p>
        </div>

        <div
          className="relative rounded-3xl overflow-hidden shadow-2xl px-8 pt-10 pb-8 backdrop-blur-2xl"
          style={{
            background:
              "linear-gradient(155deg, rgba(111,159,242,0.55) 0%, rgba(74,114,214,0.48) 45%, rgba(47,78,163,0.55) 100%)",
          }}
        >
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              background:
                "radial-gradient(120% 90% at 15% 0%, rgba(255,255,255,0.28) 0%, rgba(255,255,255,0) 55%)",
            }}
          />

          <div className="relative flex flex-col items-center mb-8">
            <div className="w-16 h-16 rounded-full bg-white/15 backdrop-blur-md flex items-center justify-center mb-4">
              <User size={28} className="text-white" strokeWidth={1.6} />
            </div>
            <h2 className="text-white/90 text-[16px] font-medium tracking-[0.25em] uppercase">로그인</h2>
          </div>

          {notice && !error && (
            <div className="relative mb-4 bg-emerald-400/20 backdrop-blur-sm text-emerald-50 text-[12px] rounded-lg px-3 py-2">
              {notice}
            </div>
          )}
          {error && (
            <div className="relative mb-4 bg-red-500/25 backdrop-blur-sm text-red-50 text-[12px] rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="relative space-y-6">
            <div className="flex items-center gap-3 border-b border-white/40 pb-2 focus-within:border-white transition-colors">
              <Mail size={16} className="text-white/70 flex-shrink-0" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 min-w-0 bg-transparent text-white placeholder-white/60 text-[14px] focus:outline-none"
                placeholder="Email ID"
                autoComplete="username"
              />
            </div>
            <div className="flex items-center gap-3 border-b border-white/40 pb-2 focus-within:border-white transition-colors">
              <Lock size={16} className="text-white/70 flex-shrink-0" />
              <input
                type={showPass ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="flex-1 min-w-0 bg-transparent text-white placeholder-white/60 text-[14px] focus:outline-none"
                placeholder="Password"
                autoComplete="current-password"
              />
              <button type="button" onClick={() => setShowPass(!showPass)} className="text-white/60 hover:text-white transition-colors flex-shrink-0">
                {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>

            <div className="flex items-center justify-between text-[12px] text-white/80">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-3.5 h-3.5 accent-white" defaultChecked />
                로그인 상태 유지
              </label>
              <button type="button" className="italic hover:text-white transition-colors">Forgot Password?</button>
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-lg bg-[#1b2f5e]/90 backdrop-blur-md hover:bg-[#152449]/95 text-white font-semibold tracking-[0.15em] text-[13px] uppercase shadow-md transition-colors"
            >
              로그인
            </button>
          </form>

          <p className="relative mt-6 text-center text-[13px] text-white/80">
            계정이 없으신가요?{" "}
            <button onClick={onGoSignup} className="text-white font-medium hover:text-white/90">회원가입</button>
          </p>
        </div>

        <p className="mt-6 text-center text-[11px] text-gray-400 font-mono">
          © DEVICE Co., Ltd. · Semiconductor Inspection AI
        </p>
      </div>
    </div>
  );
}
