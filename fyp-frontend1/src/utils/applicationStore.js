const APP_KEY = "aikapply.applications.v1";

function getAll() {
  try {
    const raw = localStorage.getItem(APP_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveAll(obj) {
  localStorage.setItem(APP_KEY, JSON.stringify(obj));
}

export function saveApplication(username, application) {
  const all = getAll();
  all[username] = { ...application, updatedAt: Date.now() };
  saveAll(all);
}

export function getApplication(username) {
  const all = getAll();
  return all[username] || null;
}

export function hasApplication(username) {
  return Boolean(getApplication(username));
}

export function exportApplicationCsv(username) {
  const app = getApplication(username);
  if (!app) return false;
  // Flatten data into CSV rows
  const entries = Object.entries(app.data || {});
  const header = entries.map(([k]) => k).join(",");
  const row = entries.map(([, v]) => JSON.stringify(String(v || "")).replace(/^"|"$/g, '')).join(",");
  const csv = `${header}\n${row}`;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${username}_application.csv`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  return true;
}


