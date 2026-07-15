import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import DeviceLogo from "./DeviceLogo.jsx";
import SemiBg from "./SemiBg.jsx";
import { registerUser } from "../utils/auth.js";

const inputCls =
  "w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-2.5 text-[14px] text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-400 focus:bg-white transition-colors";

const EMPTY_FORM = {
  name: "",
  position: "",
  email: "",
  department: "",
  password: "",
  passwordConfirm: "",
};

export default function SignupPage({ onGoLogin, onSignedUp }) {
  const [showPass, setShowPass] = useState(false);
  const [showConfirmPass, setShowConfirmPass] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");

  const update = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { name, email, password, passwordConfirm, position, department } = form;
    if (!name.trim() || !email.trim() || !password) {
      setError("필수 항목을 모두 입력해 주세요.");
      return;
    }
    if (password.length < 8) {
      setError("비밀번호는 8자 이상이어야 합니다.");
      return;
    }
    if (password !== passwordConfirm) {
      setError("비밀번호가 일치하지 않습니다.");
      return;
    }
    const result = await registerUser(email.trim(), password, {
      name: name.trim(),
      position: position.trim(),
      department: department.trim(),
    });
    if (!result.ok) {
      setError(result.error);
      return;
    }
    onSignedUp();
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10 relative overflow-hidden" style={{ background: "#f0f2f6" }}>
      <SemiBg />
      <div className="relative z-10 w-full max-w-sm">
        <div className="text-center mb-7">
          <DeviceLogo className="h-12 w-auto mx-auto mb-5" />
          <p className="text-gray-400 text-[14px]">새 계정을 생성하세요</p>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-7 shadow-sm">
          <h2 className="text-[17px] font-semibold text-gray-900 mb-5">회원가입</h2>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 text-[12px] rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[12px] text-gray-500 font-mono mb-1.5">성명</label>
                <input type="text" className={inputCls} placeholder="홍길동" value={form.name} onChange={update("name")} required />
              </div>
              <div>
                <label className="block text-[12px] text-gray-500 font-mono mb-1.5">직책</label>
                <input type="text" className={inputCls} placeholder="선임연구원" value={form.position} onChange={update("position")} />
              </div>
            </div>
            <div>
              <label className="block text-[12px] text-gray-500 font-mono mb-1.5">회사 이메일</label>
              <input type="email" className={inputCls} placeholder="your@device.co.kr" value={form.email} onChange={update("email")} required />
            </div>
            <div>
              <label className="block text-[12px] text-gray-500 font-mono mb-1.5">부서</label>
              <input type="text" className={inputCls} placeholder="공정기술팀" value={form.department} onChange={update("department")} />
            </div>
            <div>
              <label className="block text-[12px] text-gray-500 font-mono mb-1.5">비밀번호</label>
              <div className="relative">
                <input type={showPass ? "text" : "password"} className={inputCls} placeholder="8자 이상" value={form.password} onChange={update("password")} required />
                <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors">
                  {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>
            <div>
              <label className="block text-[12px] text-gray-500 font-mono mb-1.5">비밀번호 확인</label>
              <div className="relative">
                <input type={showConfirmPass ? "text" : "password"} className={inputCls} placeholder="••••••••" value={form.passwordConfirm} onChange={update("passwordConfirm")} required />
                <button type="button" onClick={() => setShowConfirmPass(!showConfirmPass)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors">
                  {showConfirmPass ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>
            <button type="submit" className="w-full py-2.5 mt-1 bg-blue-600 text-white rounded-lg font-medium text-[14px] hover:bg-blue-700 transition-colors shadow-sm">
              계정 만들기
            </button>
          </form>
          <p className="mt-5 text-center text-[13px] text-gray-400">
            이미 계정이 있으신가요?{" "}
            <button onClick={onGoLogin} className="text-blue-600 hover:text-blue-700 font-medium">로그인</button>
          </p>
        </div>
      </div>
    </div>
  );
}
