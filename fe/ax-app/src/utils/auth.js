const SESSION_KEY = "wis_session";

async function postJson(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function registerUser(email, password, profile) {
  try {
    const { ok, data } = await postJson("/users/signup", {
      email,
      password,
      name: profile.name,
      position: profile.position,
      department: profile.department,
    });
    if (!ok) {
      return { ok: false, error: data.detail || "회원가입에 실패했습니다." };
    }
    return { ok: true };
  } catch {
    return { ok: false, error: "서버에 연결할 수 없습니다. 백엔드가 켜져 있는지 확인해 주세요." };
  }
}

export async function loginUser(email, password) {
  try {
    const { ok, data } = await postJson("/users/login", { email, password });
    if (!ok) {
      return { ok: false, error: data.detail || "이메일 또는 비밀번호가 올바르지 않습니다." };
    }
    const session = {
      user_num: data.user_num,
      email: data.email,
      name: data.name,
      position: data.position,
      department: data.department,
    };
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    return { ok: true, session };
  } catch {
    return { ok: false, error: "서버에 연결할 수 없습니다. 백엔드가 켜져 있는지 확인해 주세요." };
  }
}

export function getSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY));
  } catch {
    return null;
  }
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}
