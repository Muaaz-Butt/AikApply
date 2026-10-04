// import React, { useState } from "react";
// import { Link, useNavigate } from "react-router-dom";
// import api from "../api/axios"; // axios instance

// export default function Signup() {
//   const navigate = useNavigate();
//   const [firstName, setFirstName] = useState("");
//   const [lastName, setLastName] = useState("");
//   const [email, setEmail] = useState("");
//   const [phone, setPhone] = useState(""); // optional phone field
//   const [password, setPassword] = useState("");
//   const [confirmPassword, setConfirmPassword] = useState("");
//   const [error, setError] = useState("");

//   const onSubmit = async (e) => {
//     e.preventDefault();

//     if (password.length < 8) {
//       setError("Password must be at least 8 characters.");
//       return;
//     }
//     if (password !== confirmPassword) {
//       setError("Passwords do not match.");
//       return;
//     }

//     setError("");
//     try {
//       await api.post("auth/signup/", {
//         email,
//         name: `${firstName} ${lastName}`, // concatenate first and last name
//         phone,
//         password,
//       });

//       navigate("/login", { replace: true });
//     } catch (err) {
//       if (err.response && err.response.data) {
//         setError(JSON.stringify(err.response.data));
//       } else {
//         setError("Unable to signup. Try again.");
//       }
//     }
//   };

//   return (
//     <section className="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] pt-28 md:pt-36">
//       <div className="w-full max-w-6xl px-6 md:px-10 grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
//         <blockquote className="text-white font-semibold text-3xl md:text-5xl leading-snug md:leading-snug">
//           “Start where you are. Use what you have. Do what you can.”
//         </blockquote>

//         <div className="bg-white/10 border border-white/20 rounded-[28px] p-8 md:p-10 shadow-[0_0_25px_rgba(255,255,255,0.08)]">
//           <h2 className="text-3xl md:text-4xl font-semibold text-center mb-8">Signup</h2>

//           <form onSubmit={onSubmit} noValidate>
//             <div className="grid grid-cols-2 gap-4">
//               <div>
//                 <label className="block text-sm text-white/85 mb-2">Firstname</label>
//                 <input
//                   type="text"
//                   className="w-full px-4 py-2 rounded-md bg-white text-black"
//                   value={firstName}
//                   onChange={(e) => setFirstName(e.target.value)}
//                 />
//               </div>
//               <div>
//                 <label className="block text-sm text-white/85 mb-2">Lastname</label>
//                 <input
//                   type="text"
//                   className="w-full px-4 py-2 rounded-md bg-white text-black"
//                   value={lastName}
//                   onChange={(e) => setLastName(e.target.value)}
//                 />
//               </div>
//             </div>

//             <label className="block text-sm text-white/85 mt-5 mb-2">Email</label>
//             <input
//               type="email"
//               className="w-full px-4 py-2 rounded-md bg-white text-black"
//               value={email}
//               onChange={(e) => setEmail(e.target.value)}
//             />

//             <label className="block text-sm text-white/85 mt-5 mb-2">Phone (optional)</label>
//             <input
//               type="text"
//               className="w-full px-4 py-2 rounded-md bg-white text-black"
//               value={phone}
//               onChange={(e) => setPhone(e.target.value)}
//             />

//             <label className="block text-sm text-white/85 mt-5 mb-2">Password</label>
//             <input
//               type="password"
//               minLength={8}
//               className="w-full px-4 py-2 rounded-md bg-white text-black"
//               value={password}
//               onChange={(e) => setPassword(e.target.value)}
//               autoComplete="off"
//             />

//             <label className="block text-sm text-white/85 mt-5 mb-2">Confirm Password</label>
//             <input
//               type="password"
//               minLength={8}
//               className="w-full px-4 py-2 rounded-md bg-white text-black"
//               value={confirmPassword}
//               onChange={(e) => setConfirmPassword(e.target.value)}
//               autoComplete="off"
//             />

//             {error && <p className="mt-3 text-sm text-red-300">{error}</p>}

//             <div className="text-xs mt-3 text-accentPurple">
//               Already have an account?
//               <Link to="/login" className="ml-1 hover:underline">Login</Link>
//             </div>

//             <div className="flex justify-center mt-6">
//               <button type="submit" className="px-8 py-2 rounded-full bg-[#D9D9D9] text-black">Signup</button>
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

// --- 1. MOVED OUTSIDE TO PREVENT RE-CREATION ON EVERY RENDER ---
const FormInput = ({ label, value, type, name, placeholder, onChange, error, optional = false }) => (
  <div className="w-full">
    <label className="block text-sm text-white/85 mb-2">
      {label} {optional && <span className="text-white/40 text-[10px]">(Optional)</span>}
    </label>
    <input
      type={type}
      name={name}
      className={`w-full px-4 py-2 rounded-md bg-white text-black outline-none border-2 transition-all ${
        error ? "border-red-500 ring-2 ring-red-500/20" : "border-transparent focus:ring-2 focus:ring-accentPurple"
      }`}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
    />
    {error && <p className="text-red-400 text-[11px] mt-1 font-medium">{error}</p>}
  </div>
);

export default function Signup() {
  const navigate = useNavigate();

  // State for form data
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Validation and UI states
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  // --- VALIDATION LOGIC ---
  const validateField = (name, value) => {
    let error = "";
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const phoneRegex = /^03\d{9}$/;
    const nameRegex = /^[a-zA-Z\s]{2,20}$/;

    switch (name) {
      case "firstName":
      case "lastName":
        if (!value) error = "Name is required.";
        else if (!nameRegex.test(value)) error = "Use letters only (2-20 chars).";
        break;
      case "email":
        if (!value) error = "Email is required.";
        else if (!emailRegex.test(value)) error = "Invalid email format.";
        break;
      case "phone":
        if (value && !phoneRegex.test(value)) error = "Format: 03XXXXXXXXX (11 digits).";
        break;
      case "password":
        if (value.length < 8) error = "Password must be at least 8 characters.";
        break;
      case "confirmPassword":
        if (value !== password) error = "Passwords do not match.";
        break;
      default:
        break;
    }
    return error;
  };

  const handleInputChange = (setter, fieldName) => (e) => {
    const value = e.target.value;
    setter(value);

    // Validate on the fly
    const fieldError = validateField(fieldName, value);
    setErrors((prev) => ({ ...prev, [fieldName]: fieldError, server: "" }));

    // Special case: if changing password, re-validate confirmPassword
    if (fieldName === "password" && confirmPassword) {
      const confirmError = value !== confirmPassword ? "Passwords do not match." : "";
      setErrors((prev) => ({ ...prev, confirmPassword: confirmError }));
    }
  };

  const onSubmit = async (e) => {
    e.preventDefault();

    const newErrors = {
      firstName: validateField("firstName", firstName),
      lastName: validateField("lastName", lastName),
      email: validateField("email", email),
      phone: validateField("phone", phone),
      password: validateField("password", password),
      confirmPassword: validateField("confirmPassword", confirmPassword),
    };

    setErrors(newErrors);

    if (Object.values(newErrors).some((x) => x !== "")) return;

    setLoading(true);
    try {
      await api.post("auth/signup/", {
        email: email.trim(),
        name: `${firstName.trim()} ${lastName.trim()}`,
        phone: phone,
        password: password,
      });

      navigate("/login", { replace: true });
    } catch (err) {
      if (err.response && err.response.data) {
        const serverMsg = typeof err.response.data === "object"
          ? Object.values(err.response.data).flat().join(" ")
          : "Signup failed. Please try again.";
        setErrors((prev) => ({ ...prev, server: serverMsg }));
      } else {
        setErrors((prev) => ({ ...prev, server: "Network error. Check your connection." }));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="min-h-screen flex items-center justify-center bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] pt-28 md:pt-36 pb-12">
      <div className="w-full max-w-6xl px-6 md:px-10 grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
        <blockquote className="text-white font-semibold text-3xl md:text-5xl leading-snug md:leading-snug">
          “Start where you are. Use what you have. Do what you can.”
        </blockquote>

        <div className="bg-white/10 border border-white/20 rounded-[28px] p-8 md:p-10 shadow-[0_0_25px_rgba(255,255,255,0.08)]">
          <h2 className="text-3xl md:text-4xl font-semibold text-center mb-8 text-white">Signup</h2>

          <form onSubmit={onSubmit} noValidate>
            <div className="grid grid-cols-2 gap-4 mb-5">
              <FormInput 
                label="Firstname" 
                name="firstName" 
                value={firstName} 
                onChange={handleInputChange(setFirstName, "firstName")} 
                error={errors.firstName}
                type="text" 
              />
              <FormInput 
                label="Lastname" 
                name="lastName" 
                value={lastName} 
                onChange={handleInputChange(setLastName, "lastName")} 
                error={errors.lastName}
                type="text" 
              />
            </div>

            <div className="space-y-5">
              <FormInput 
                label="Email" 
                name="email" 
                value={email} 
                onChange={handleInputChange(setEmail, "email")} 
                error={errors.email}
                type="email" 
                placeholder="example@mail.com" 
              />
              
              <FormInput 
                label="Phone" 
                name="phone" 
                value={phone} 
                onChange={handleInputChange(setPhone, "phone")} 
                error={errors.phone}
                type="text" 
                placeholder="03XXXXXXXXX" 
                optional={true} 
              />
              
              <FormInput 
                label="Password" 
                name="password" 
                value={password} 
                onChange={handleInputChange(setPassword, "password")} 
                error={errors.password}
                type="password" 
              />
              
              <FormInput 
                label="Confirm Password" 
                name="confirmPassword" 
                value={confirmPassword} 
                onChange={handleInputChange(setConfirmPassword, "confirmPassword")} 
                error={errors.confirmPassword}
                type="password" 
              />
            </div>

            {errors.server && (
              <div className="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-md">
                <p className="text-xs text-red-200 text-center">{errors.server}</p>
              </div>
            )}

            <div className="text-xs mt-4 text-white/60">
              Already have an account?
              <Link to="/login" className="ml-1 text-white hover:underline font-medium">Login</Link>
            </div>

            <div className="flex justify-center mt-8">
              <button 
                type="submit" 
                disabled={loading}
                className={`px-10 py-2 rounded-full font-semibold transition-all shadow-lg ${
                  loading 
                  ? "bg-gray-500 cursor-not-allowed opacity-70" 
                  : "bg-[#D9D9D9] hover:bg-white text-black hover:scale-105 active:scale-95"
                }`}
              >
                {loading ? "Creating Account..." : "Signup"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}
