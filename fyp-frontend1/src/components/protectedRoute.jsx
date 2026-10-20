import React, { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { AUTH_EVENT, verifySession } from "../utils/authStore";

const Spinner = () => (
  <div className="min-h-screen bg-[#0B0620] flex items-center justify-center">
    <div className="w-10 h-10 border-2 border-t-purple-500 border-white/10 rounded-full animate-spin" />
  </div>
);

// Renders children only once the server confirms someone is signed in.
// guestOnly flips it: login/sign-up pages send signed-in users to the dashboard.
export default function ProtectedRoute({ children, guestOnly = false }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [status, setStatus] = useState("checking");
  const redirected = useRef(false);

  useEffect(() => {
    let active = true;
    const check = () => {
      verifySession().then((session) => {
        if (active) setStatus(session ? "signed-in" : "signed-out");
      });
    };
    check();
    // Protected pages react to logins/logouts while open. Login and sign-up pages only check
    // once on arrival; after a successful login the page itself decides where to go next.
    if (!guestOnly) window.addEventListener(AUTH_EVENT, check);
    return () => {
      active = false;
      window.removeEventListener(AUTH_EVENT, check);
    };
  }, [guestOnly]);

  // Redirect once, from an effect. Rendering <Navigate> here caused an endless redirect loop:
  // the page-transition animation keeps re-rendering the outgoing page, and <Navigate>
  // navigates again on every render until Chrome starts ignoring navigation entirely.
  useEffect(() => {
    if (redirected.current) return;
    if (!guestOnly && status === "signed-out") {
      redirected.current = true;
      navigate("/login", { replace: true, state: { from: location.pathname } });
    } else if (guestOnly && status === "signed-in") {
      redirected.current = true;
      navigate("/dashboard", { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, guestOnly]);

  if (guestOnly) {
    // Login and sign-up render straight away unless a session is confirmed
    return status === "signed-in" ? null : children;
  }
  // Wait for the server: a session left in localStorage may belong to someone who logged out
  return status === "signed-in" ? children : <Spinner />;
}
