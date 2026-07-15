const USERS_KEY = "wis_users";
const SESSION_KEY = "wis_session";

function loadUsers() {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY)) || {};
  } catch {
    return {};
  }
}

function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

export function registerUser(email, password, profile) {
  const users = loadUsers();
  if (users[email]) {
    return { ok: false, error: "이미 가입된 이메일입니다." };
  }
  users[email] = { password, ...profile };
  saveUsers(users);
  return { ok: true };
}

export function loginUser(email, password) {
  const users = loadUsers();
  const user = users[email];
  if (!user || user.password !== password) {
    return { ok: false, error: "이메일 또는 비밀번호가 올바르지 않습니다." };
  }
  const session = {
    email,
    name: user.name,
    position: user.position,
    department: user.department,
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
