// Backend base URL. Local dev talks to Django on :8000; the production build sets
// VITE_API_URL="" so requests go to the same origin that serves the app.
export const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
