// import React, { useState } from "react";
// import { Link, useNavigate } from "react-router-dom";
// import api from "../api/axios";
// import { setSession } from "../utils/authStore"; // Use the new setSession function

// export default function Login() {
//   const navigate = useNavigate();
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [error, setError] = useState("");
//   const [loading, setLoading] = useState(false);

//   const onLogin = async (e) => {
//     if (e) e.preventDefault();
    
//     setError("");
//     setLoading(true);

//     try {
//       // 1. Send credentials to Django
//       const response = await api.post("auth/login/", {
//         email: email,
//         password: password,
//       });

//       console.log("Django Login Success:", response.data);

//       // 2. Set the local session badge
//       // This allows getSession() in ProtectedRoute to return true
//       setSession(email);

//       // 3. Redirect to dashboard
//       // replace: true prevents the user from going "back" to login
//       navigate("/dashboard", { replace: true });
      
//     } catch (err) {
//       console.error("Login error:", err);
      
//       if (err.response && err.response.data) {
//         // Handle Django's error response
//         const serverError = err.response.data.error || err.response.data.detail;
//         setError(serverError || "Invalid email or password.");
//       } else {
//         setError("Network error. Please check your connection.");
//       }
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <section className="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] pt-28 md:pt-36">
//       <div className="w-full max-w-6xl px-6 md:px-10 grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
        
//         <blockquote className="text-white font-semibold text-3xl md:text-5xl leading-snug">
//           “Your journey to greatness begins with a single login.”
//         </blockquote>

//         <div className="bg-white/10 border border-white/20 rounded-[28px] p-8 md:p-10 shadow-[0_0_25px_rgba(255,255,255,0.08)]">
//           <h2 className="text-3xl md:text-4xl font-semibold text-center mb-8 text-white">Login</h2>

//           <form onSubmit={onLogin}>
//             <div className="mb-5">
//               <label className="block text-sm text-white/85 mb-2">Enter Email</label>
//               <input
//                 type="email"
//                 required
//                 className="w-full px-4 py-2 rounded-md bg-white text-black outline-none focus:ring-2 focus:ring-accentPurple"
//                 value={email}
//                 onChange={(e) => setEmail(e.target.value)}
//               />
//             </div>

//             <div className="mb-2">
//               <label className="block text-sm text-white/85 mb-2">Enter Password</label>
//               <input
//                 type="password"
//                 required
//                 className="w-full px-4 py-2 rounded-md bg-white text-black outline-none focus:ring-2 focus:ring-accentPurple"
//                 value={password}
//                 onChange={(e) => setPassword(e.target.value)}
//                 autoComplete="current-password"
//               />
//             </div>

//             {error && <p className="text-sm text-red-400 mt-3 font-medium">{error}</p>}

//             <div className="text-sm mt-4">
//               <span className="text-white/60">Don't have an account? </span>
//               <Link to="/signup" className="text-white hover:underline font-medium">
//                 Sign Up
//               </Link>
//             </div>

//             <div className="flex justify-center mt-8">
//               <button
//                 type="submit"
//                 disabled={loading}
//                 className={`px-10 py-2 rounded-full font-semibold transition-all ${
//                   loading
//                   ? "bg-gray-500 cursor-not-allowed"
//                   : "bg-[#D9D9D9] hover:bg-white text-black"
//                 }`}
//               >
//                 {loading ? "Logging in..." : "Login"}
//               </button>
//             </div>
//           </form>
//         </div>
//       </div>
//     </section>
//   );
// }

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios"; 
import { setSession } from "../utils/authStore";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  
  // Use an object for field-specific errors
  const [errors, setErrors] = useState({ email: "", password: "", general: "" });

  // 1. Validation Logic
  const validateForm = () => {
    let tempErrors = { email: "", password: "", general: "" };
    let isValid = true;

    // Email Regex: Standard format check
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      tempErrors.email = "Email is required.";
      isValid = false;
    } else if (!emailRegex.test(email)) {
      tempErrors.email = "Please enter a valid email address.";
      isValid = false;
    }

    // Password Check: Minimum length (adjust as per your backend policy)
    if (!password) {
      tempErrors.password = "Password is required.";
      isValid = false;
    } else if (password.length < 6) {
      tempErrors.password = "Password must be at least 6 characters.";
      isValid = false;
    }

    setErrors(tempErrors);
    return isValid;
  };

  const onLogin = async (e) => {
    e.preventDefault();
    
    // Clear previous errors
    setErrors({ email: "", password: "", general: "" });

    // 2. Client-side validation check
    if (!validateForm()) return;

    setLoading(true);

    try {
      const response = await api.post("auth/login/", {
        email: email.trim(), // Trim whitespace
        password: password,
      });

      setSession(email, response.data?.name, response.data?.is_admin);
      navigate("/dashboard", { replace: true });
      
    } catch (err) {
      console.error("Login error:", err);
      
      if (err.response && err.response.data) {
        // Handle specific field errors from Django (if your API returns them)
        // Otherwise, fall back to general error
        const serverError = err.response.data.error || err.response.data.detail;
        setErrors(prev => ({ 
          ...prev, 
          general: serverError || "Invalid email or password." 
        }));
      } else {
        setErrors(prev => ({ 
          ...prev, 
          general: "Network error. Please check your connection." 
        }));
      }
    } finally {
      setLoading(false);
    }
  };

  // Helper to clear errors when user starts typing again
  const handleInputChange = (setter, field) => (e) => {
    setter(e.target.value);
    if (errors[field] || errors.general) {
      setErrors(prev => ({ ...prev, [field]: "", general: "" }));
    }
  };

  return (
    <section className="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] pt-28 md:pt-36">
      <div className="w-full max-w-6xl px-6 md:px-10 grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
        
        <blockquote className="text-white font-semibold text-3xl md:text-5xl leading-snug">
          “Your journey to greatness begins with a single login.”
        </blockquote>

        <div className="bg-white/10 border border-white/20 rounded-[28px] p-8 md:p-10 shadow-[0_0_25px_rgba(255,255,255,0.08)]">
          <h2 className="text-3xl md:text-4xl font-semibold text-center mb-8 text-white">Login</h2>

          <form onSubmit={onLogin} noValidate> {/* noValidate prevents default browser bubbles so our custom UI shows */}
            <div className="mb-5">
              <label className="block text-sm text-white/85 mb-2">Enter Email</label>
              <input
                type="email"
                className={`w-full px-4 py-2 rounded-md bg-white text-black outline-none border-2 transition-all ${
                  errors.email ? "border-red-500 ring-2 ring-red-500/20" : "border-transparent focus:ring-2 focus:ring-accentPurple"
                }`}
                value={email}
                onChange={handleInputChange(setEmail, "email")}
                placeholder="email@example.com"
              />
              {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email}</p>}
            </div>

            <div className="mb-2">
              <label className="block text-sm text-white/85 mb-2">Enter Password</label>
              <input
                type="password"
                className={`w-full px-4 py-2 rounded-md bg-white text-black outline-none border-2 transition-all ${
                  errors.password ? "border-red-500 ring-2 ring-red-500/20" : "border-transparent focus:ring-2 focus:ring-accentPurple"
                }`}
                value={password}
                onChange={handleInputChange(setPassword, "password")}
                autoComplete="current-password"
                placeholder="••••••••"
              />
              {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password}</p>}
            </div>

            {errors.general && (
              <div className="bg-red-500/20 border border-red-500/50 p-3 rounded-md mt-4">
                <p className="text-sm text-red-200 text-center font-medium">{errors.general}</p>
              </div>
            )}

            <div className="text-sm mt-4">
              <span className="text-white/60">Don't have an account? </span>
              <Link to="/signup" className="text-white hover:underline font-medium">
                Sign Up
              </Link>
            </div>

            <div className="flex justify-center mt-8">
              <button
                type="submit"
                disabled={loading}
                className={`px-10 py-2 rounded-full font-semibold transition-all shadow-lg ${
                  loading 
                  ? "bg-gray-500 cursor-not-allowed scale-95" 
                  : "bg-[#D9D9D9] hover:bg-white text-black hover:scale-105 active:scale-95"
                }`}
              >
                {loading ? (
                   <span className="flex items-center gap-2">
                     <svg className="animate-spin h-4 w-4 text-black" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                     </svg>
                     Logging in...
                   </span>
                ) : "Login"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}