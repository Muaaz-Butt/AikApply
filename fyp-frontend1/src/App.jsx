import React from "react";
import { Routes, Route, useLocation, Navigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Footer from "./components/Footer";
import Login from "./components/Login";
import Signup from "./components/Signup";
import ApplyForm from "./components/ApplyForm";
import StudentDashboard from "./components/StudentDashboard";
import { getSession } from "./utils/authStore"; // Import your session checker
import ProfilePage from "./components/Profile";
import RecommenderForm from "./components/RecommenderForm";
import RecommendationResults from "./components/RecommendationResults";
import ApplicationView from "./components/ApplicationView";

// Simple Protected Route Component
const ProtectedRoute = ({ children }) => {
  const session = getSession();
  if (!session) {
    // Redirect to login if no session is found
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default function App() {
  const location = useLocation();

  return (
    <>
      <Navbar />
      <AnimatePresence mode="wait">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.25, ease: "easeOut" }}
        >
          <Routes location={location}>
            <Route path="/" element={<Hero />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/recommend" element={<RecommenderForm />} />
<Route path="/recommendations" element={<RecommendationResults />} />
            {/* Protected Routes */}
            <Route path="/apply" element={
              <ProtectedRoute>
                <ApplyForm />
              </ProtectedRoute>
            } />

            <Route path="/my-application" element={
              <ProtectedRoute>
                <ApplicationView />
              </ProtectedRoute>
            } />

            <Route path="/dashboard" element={
              <ProtectedRoute>
                <StudentDashboard />
              </ProtectedRoute>
            } />

          </Routes>
        </motion.div>
      </AnimatePresence>
      <Footer />
    </>
  );
}