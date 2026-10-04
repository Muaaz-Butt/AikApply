import React from "react";
import { Navigate } from "react-router-dom";
import { getSession } from "../utils/authStore";

const ProtectedRoute = ({ children }) => {
  const session = getSession();

  // If no session exists, send them to login
  if (!session) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;