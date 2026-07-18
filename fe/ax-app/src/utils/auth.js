const SESSION_KEY = "wis_session";

export async function registerUser(email, password, profile) {
  const res = await fetch("http://localhost:8000/users/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: email,
      password,
      name: profile.name,
      email,
    }),
  });
  if (!res.ok) {
    const data = await res.json();
    return { ok: false, error: data.detail || "회원가입 실패" };
  }
  return { ok: true };
}

export async function loginUser(email, password) {
  const res = await fetch("http://localhost:8000/users/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: email, password }),
  });
  if (!res.ok) {
    const data = await res.json();
    return { ok: false, error: data.detail || "로그인 실패" };
  }
  const user = await res.json();
  const session = {
    email,
    name: user.name,
  };
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return { ok: true, session };
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
