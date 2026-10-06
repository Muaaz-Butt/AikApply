// import React, { useState } from "react";
// import { Link, useLocation, useNavigate } from "react-router-dom";

// export default function Navbar() {
//   const location = useLocation();
//   const navigate = useNavigate();
//   const [open, setOpen] = useState(false);

//   const goToSection = (id) => {
//     if (location.pathname !== "/") {
//       navigate("/", { state: { scrollTo: id } });
//       return;
//     }
//     const el = document.getElementById(id);
//     if (el) {
//       el.scrollIntoView({ behavior: "smooth", block: "start" });
//     }
//   };

//   return (
//     <nav className="fixed top-4 left-1/2 -translate-x-1/2 w-[92%] md:w-[85%] bg-white/10 backdrop-blur-xl rounded-full border border-white/20 py-2 pl-5 pr-2 flex justify-between items-center shadow-[0_0_30px_rgba(255,255,255,0.12)] z-50">
//       <h1 className="text-xl md:text-2xl font-semibold tracking-wide">
//         <span className="inline-block w-6 h-6 mr-2 rounded bg-white/80 text-darkPurple text-center align-middle">1</span>
//         Apply
//       </h1>
//       <button className="md:hidden px-3 py-2 rounded-full bg-white/20 border border-white/30" onClick={() => setOpen((v)=>!v)} aria-label="Toggle menu">☰</button>
//       <div className={`items-center gap-6 text-sm md:text-base ${open ? "absolute top-14 left-0 right-0 mx-4 p-4 rounded-2xl bg-[#2A013D]/95 border border-white/20 flex flex-col" : "hidden"} md:flex md:static md:bg-transparent md:border-0 md:p-0 md:flex`}>
//         <Link to="/" className="text-white/90 hover:text-white transition">Home</Link>
//         <button onClick={() => goToSection("about")} className="text-white/90 hover:text-white transition">About</button>
//         <button onClick={() => goToSection("contact")} className="text-white/90 hover:text-white transition">Contact</button>
//         <Link
//           to="/signup"
//           className="ml-1 px-4 py-2 rounded-full bg-white/20 border border-white/30 hover:bg-white/30 hover:shadow-[0_0_12px_rgba(255,255,255,0.35)] transition"
//         >
//           Sign Up
//         </Link>
//       </div>
//     </nav>
//   );
// }
import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { getSession, logout } from "../utils/authStore";
import useProfilePhoto from "../utils/useProfilePhoto";

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(!!getSession());
  const photo = useProfilePhoto();
  const [photoFailed, setPhotoFailed] = useState(false);

  useEffect(() => { setPhotoFailed(false); }, [photo]);

  useEffect(() => {
    const syncAuth = () => {
      setIsLoggedIn(!!getSession());
    };

    // Listen for the custom "authUpdate" event from your authStore
    window.addEventListener("authUpdate", syncAuth);
    syncAuth();

    return () => window.removeEventListener("authUpdate", syncAuth);
  }, [location]);

  const handleLogout = () => {
    logout(); 
    setOpen(false);
    navigate("/login");
  };

  const goToSection = (id) => {
    setOpen(false);
    if (location.pathname !== "/") {
      navigate("/", { state: { scrollTo: id } });
      return;
    }
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <nav className="fixed top-0 left-0 w-full bg-white/10 backdrop-blur-xl border-b border-white/20 py-4 px-6 md:px-12 flex justify-between items-center z-50">
      
      {/* Brand Logo */}
      <h1 className="text-xl md:text-2xl font-semibold tracking-wide text-white flex items-center">
        <span className="inline-block w-6 h-6 mr-2 rounded bg-white text-[#0B0620] text-center leading-6 text-sm font-bold">1</span>
        Apply
      </h1>

      {/* Mobile Toggle */}
      <button className="md:hidden text-white text-2xl" onClick={() => setOpen(!open)}>
        {open ? "✕" : "☰"}
      </button>

      {/* Navigation Links */}
      <div className={`items-center gap-8 ${open ? "absolute top-full left-0 w-full p-6 bg-[#2A013D] flex flex-col shadow-xl" : "hidden"} md:flex md:static md:bg-transparent md:p-0`}> 
        
        {/* HIDE THESE WHEN LOGGED IN */}
        {!isLoggedIn ? (
          <>
            <Link to="/" onClick={() => setOpen(false)} className="text-white/90 hover:text-white transition font-medium">Home</Link>
            <button onClick={() => goToSection("about")} className="text-white/90 hover:text-white transition font-medium">About</button>
            <button onClick={() => goToSection("contact")} className="text-white/90 hover:text-white transition font-medium">Contact</button>
            <Link
              to="/signup"
              onClick={() => setOpen(false)}
              className="px-5 py-2 rounded-full bg-white/20 border border-white/30 text-white hover:bg-white/30 transition"
            >
              Sign Up
            </Link>
          </>
        ) : (
          /* SHOW THESE ONLY WHEN LOGGED IN */
          <div className="flex flex-col md:flex-row items-center gap-6 md:gap-8">
          {/* Phones: the menu needs real links, not just the profile photo */}
          <Link to="/dashboard" onClick={() => setOpen(false)} className="md:hidden text-white/90 hover:text-white transition font-medium">Dashboard</Link>
          <Link to="/my-application" onClick={() => setOpen(false)} className="md:hidden text-white/90 hover:text-white transition font-medium">My Application</Link>
          <Link to="/recommend" onClick={() => setOpen(false)} className="md:hidden text-white/90 hover:text-white transition font-medium">University Recommender</Link>
          <Link
          to="/profile"
          onClick={() => setOpen(false)}
          className="text-white/90 hover:text-white transition font-medium"
          title="Profile"
        >
          {photo && !photoFailed ? (
            <img
              src={photo}
              alt="Profile"
              onError={() => setPhotoFailed(true)}
              className="w-10 h-10 rounded-full object-cover border-2 border-white/40 hover:border-white transition"
            />
          ) : (
            "Profile"
          )}
        </Link>
          <button onClick={handleLogout} className="md:hidden text-red-400 hover:text-red-300 transition font-semibold">Log Out</button>

          </div>
        )}
      </div>
    </nav>
  );
}