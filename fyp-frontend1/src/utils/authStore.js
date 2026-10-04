// Simple localStorage-based auth store for demo purposes only

const STORAGE_KEY = "aikapply.users.v1";
const SESSION_KEY = "aikapply.session.v1";
// Add this to your authStore.js
// isAdmin only controls what the UI shows; the backend enforces admin-only actions itself
export function setSession(username, name, isAdmin = false) {
  const sessionData = { username, name: name || "", isAdmin: !!isAdmin, ts: Date.now() };
  localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
  return sessionData;
}

// Update fields on the existing session (e.g. name/role fetched from /auth/me/)
export function updateSession(updates) {
  const session = getSession();
  if (!session) return null;
  const updated = { ...session, ...updates };
  localStorage.setItem(SESSION_KEY, JSON.stringify(updated));
  return updated;
}

export function setSessionName(name) {
  return updateSession({ name });
}
export function getUsers() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveUsers(users) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users));
}

export function registerUser({ username, password, firstName, lastName }) {
  const users = getUsers();
  const exists = users.some((u) => u.username.toLowerCase() === username.toLowerCase());
  if (exists) {
    return { ok: false, error: "User already exists" };
  }
  users.push({ username, password, firstName, lastName, createdAt: Date.now() });
  saveUsers(users);
  return { ok: true };
}

export function findUser(username) {
  return getUsers().find((u) => u.username.toLowerCase() === username.toLowerCase());
}

export function updateUser(username, updates) {
  const users = getUsers();
  const idx = users.findIndex((u) => u.username.toLowerCase() === username.toLowerCase());
  if (idx === -1) return { ok: false, error: "User not found" };
  users[idx] = { ...users[idx], ...updates, updatedAt: Date.now() };
  saveUsers(users);
  return { ok: true };
}

export function login(username, password) {
  const user = findUser(username);
  if (!user) return { ok: false, error: "User not found" };
  if (user.password !== password) return { ok: false, error: "Invalid credentials" };
  localStorage.setItem(SESSION_KEY, JSON.stringify({ username: user.username, ts: Date.now() }));
  return { ok: true };
}

export function logout() {
  localStorage.removeItem(SESSION_KEY);
}

export function getSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}


