// Login state for the frontend.
//
// The Django session cookie is the real login. The copy kept in localStorage only lets the UI
// render quickly (navbar, names); it is always checked against the server with /auth/me/
// before protected pages render, and cleared whenever the server says nobody is signed in.
import api from "../api/axios";

const SESSION_KEY = "aikapply.session.v1";
// Old demo data that stored plain-text passwords in the browser; removed on load
const LEGACY_KEYS = ["aikapply.users.v1", "chat_session_id"];
const CHAT_KEY_PREFIX = "aikapply.chat.";
export const AUTH_EVENT = "authUpdate";

LEGACY_KEYS.forEach((key) => {
  try { localStorage.removeItem(key); } catch { /* storage unavailable */ }
});

// One verification request at a time; reset whenever the login changes
let verification = null;

function notify() {
  window.dispatchEvent(new Event(AUTH_EVENT));
}

export function getSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

// isAdmin only controls what the UI shows; the backend enforces admin-only actions itself
export function setSession(username, name, isAdmin = false) {
  const sessionData = { username, name: name || "", isAdmin: !!isAdmin, ts: Date.now() };
  localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
  verification = Promise.resolve(sessionData);
  notify();
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

// Forget everything this browser knows about the signed-in user
export function clearSession() {
  try {
    localStorage.removeItem(SESSION_KEY);
    Object.keys(localStorage)
      .filter((key) => key.startsWith(CHAT_KEY_PREFIX))
      .forEach((key) => localStorage.removeItem(key));
  } catch { /* storage unavailable */ }
  verification = Promise.resolve(null);
  notify();
}

// Ends the session on the server too; without this the cookie stays valid and the next
// person on this browser would be served the previous user's data
export async function logout() {
  try {
    await api.post("auth/logout/");
  } catch { /* still clear locally if the server is unreachable */ }
  clearSession();
}

// Asks the server who is signed in. Resolves to the session, or null if nobody is.
export function verifySession({ force = false } = {}) {
  if (!verification || force) {
    verification = api.get("auth/me/")
      .then(({ data }) => {
        const current = getSession();
        // The server is the source of truth: adopt its user even if localStorage disagrees
        if (!current || current.username?.toLowerCase() !== data.email?.toLowerCase()) {
          return setSession(data.email, data.name, data.is_admin);
        }
        return updateSession({ name: data.name || current.name || "", isAdmin: !!data.is_admin });
      })
      .catch((error) => {
        // Only a definite "not signed in" clears the session; a network blip keeps it
        if (isUnauthenticated(error)) {
          if (getSession()) clearSession();
          return null;
        }
        verification = null;
        return getSession();
      });
  }
  return verification;
}

// DRF answers 401, or 403 with "Authentication credentials were not provided", when the
// session cookie is missing or expired (as opposed to 403 for "not allowed", e.g. admin-only)
export function isUnauthenticated(error) {
  const status = error?.response?.status;
  if (status === 401) return true;
  const detail = String(error?.response?.data?.detail || "");
  return status === 403 && /authentication credentials|not authenticated/i.test(detail);
}

export function chatStorageKey() {
  const user = getSession()?.username;
  return user ? `${CHAT_KEY_PREFIX}${user.toLowerCase()}` : null;
}

// If the server session ends while the app is open (expiry, logout in another tab),
// drop the stale local session so the UI stops showing the previous user
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = error?.config?.url || "";
    if (isUnauthenticated(error) && !/auth\/(login|signup|me)\/?$/.test(url) && getSession()) {
      clearSession();
    }
    return Promise.reject(error);
  },
);

// Keep tabs in sync: logging in or out in one tab updates the others
window.addEventListener("storage", (event) => {
  if (event.key === SESSION_KEY || event.key === null) {
    verification = null;
    notify();
  }
});
