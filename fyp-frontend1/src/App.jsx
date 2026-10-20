import React from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Footer from "./components/Footer";
import Login from "./components/Login";
import Signup from "./components/Signup";
import ApplyForm from "./components/ApplyForm";
import StudentDashboard from "./components/StudentDashboard";
import ProtectedRoute from "./components/protectedRoute";
import ProfilePage from "./components/Profile";
import RecommenderForm from "./components/RecommenderForm";
import RecommendationResults from "./components/RecommendationResults";
import ApplicationView from "./components/ApplicationView";
import Legal from "./components/Legal";

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
            <Route path="/privacy" element={<Legal page="privacy" />} />
            <Route path="/terms" element={<Legal page="terms" />} />
            <Route path="/login" element={<ProtectedRoute guestOnly><Login /></ProtectedRoute>} />
            <Route path="/signup" element={<ProtectedRoute guestOnly><Signup /></ProtectedRoute>} />
            {/* The server must confirm a signed-in user before these render */}
            <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
            <Route path="/recommend" element={<ProtectedRoute><RecommenderForm /></ProtectedRoute>} />
            <Route path="/recommendations" element={<ProtectedRoute><RecommendationResults /></ProtectedRoute>} />
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