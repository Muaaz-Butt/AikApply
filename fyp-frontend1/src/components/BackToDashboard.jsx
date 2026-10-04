import React from "react";
import { useNavigate } from "react-router-dom";
import { getSession } from "../utils/authStore";

// Returns logged-in users to the dashboard home; visitors go back to the landing page
export default function BackToDashboard({ className = "" }) {
  const navigate = useNavigate();
  const loggedIn = !!getSession();

  return (
    <button
      type="button"
      onClick={() => navigate(loggedIn ? "/dashboard" : "/")}
      className={`inline-flex items-center gap-2 px-5 py-2 rounded-full border border-white/20 bg-white/5 text-sm font-medium text-white/80 hover:bg-white/10 hover:text-white transition ${className}`}
    >
      <span aria-hidden="true">←</span>
      {loggedIn ? "Back to Dashboard" : "Back to Home"}
    </button>
  );
}
