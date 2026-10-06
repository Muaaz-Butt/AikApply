// import React, { useState, useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import api from "../api/axios";
// import { getSession, logout } from "../utils/authStore";

// export default function ProfilePage() {
//   const navigate = useNavigate();
//   const session = getSession();
  
//   const [profile, setProfile] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [passwords, setPasswords] = useState({ current: "", new: "", confirm: "" });
//   const [showPass, setShowPass] = useState({ current: false, new: false, confirm: false });
//   const [status, setStatus] = useState({ type: "", msg: "" });
//   const [resetLoading, setResetLoading] = useState(false);

//   useEffect(() => {
//     const fetchProfile = async () => {
//       try {
//         const response = await api.get("/student/profile/");
//         setProfile(response.data);
//       } catch (err) { console.error(err); } 
//       finally { setLoading(false); }
//     };
//     fetchProfile();
//   }, []);

//   const handleUpdatePassword = async (e) => {
//     e.preventDefault();
//     if (passwords.new !== passwords.confirm) {
//       setStatus({ type: "error", msg: "New passwords do not match!" });
//       return;
//     }
//     setResetLoading(true);
//     try {
//       await api.post("/auth/password-change/", {
//         old_password: passwords.current,
//         new_password: passwords.new
//       });
//       setStatus({ type: "success", msg: "Password updated successfully!" });
//       setPasswords({ current: "", new: "", confirm: "" });
//     } catch (err) {
//       setStatus({ type: "error", msg: "Failed to update. Verify current password." });
//     } finally { setResetLoading(false); }
//   };

//   if (loading) return (
//     <div className="min-h-screen bg-[#0B0620] flex items-center justify-center">
//       <div className="w-10 h-10 border-2 border-t-purple-500 border-white/10 rounded-full animate-spin"></div>
//     </div>
//   );

//   return (
//     /* Unified Background Gradient */
//     <section className="min-h-screen bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] text-white">
//       <div className="h-24 w-full" /> {/* Navbar Spacer */}

//       <div className="flex flex-col md:flex-row w-full min-h-[calc(100vh-6rem)]">
        
//         {/* SIDEBAR */}
//         <aside className="w-full md:w-80 bg-white/5 border-r border-white/10 p-8 flex flex-col shrink-0">
//           <div className="mb-10">
//             <p className="text-xs font-semibold text-white/40 uppercase mb-2 tracking-widest">Student Session</p>
//             <h2 className="text-xl font-bold text-white truncate">{session?.username || "Guest"}</h2>
//           </div>

//           <nav className="space-y-2 flex-1">
//             <button onClick={() => navigate("/dashboard")} className="w-full text-left px-5 py-3 rounded-xl hover:bg-white/10 text-white/80 transition font-medium">Dashboard</button>
//             <button className="w-full text-left px-5 py-3 rounded-xl bg-white text-[#0B0620] font-bold shadow-xl">Profile Settings</button>
//           </nav>

//           <button onClick={() => { logout(); navigate("/login"); }} className="mt-10 px-5 py-3 rounded-xl text-red-400 hover:bg-red-400/10 transition text-left font-bold border border-red-400/20">Sign Out</button>
//         </aside>

//         {/* MAIN CONTENT */}
//         <main className="flex-1 p-8 md:p-12 lg:p-16 overflow-y-auto">
//           <div className="max-w-[1400px] mx-auto">
            
//             <header className="mb-12 border-b border-white/10 pb-8">
//               <h1 className="text-4xl font-bold mb-2">Account Settings</h1>
//               <p className="text-white/60 text-lg">Manage your personal data and security preferences.</p>
//             </header>

//             <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 md:gap-12">
              
//               {/* PERSONAL INFO SECTIONS */}
//               <div className="xl:col-span-2 space-y-8">
//                 <section className="bg-white/10 border border-white/20 rounded-[2rem] md:rounded-[2.5rem] p-5 sm:p-8 md:p-10 shadow-2xl backdrop-blur-xl">
//                   <h3 className="text-sm font-bold text-white/50 uppercase tracking-widest mb-10 border-b border-white/5 pb-4">Identity Details</h3>
//                   <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-10">
//                     <ProfileData label="Full Name" value={profile?.student_name} />
//                     <ProfileData label="CNIC / Identity" value={profile?.student_cnic} />
//                     <ProfileData label="Registered Email" value={profile?.email} />
//                     <ProfileData label="Mobile Number" value={profile?.mobile} />
//                     <ProfileData label="City" value={profile?.city} />
//                     <ProfileData label="Province" value={profile?.province} />
//                   </div>
//                 </section>

//                 <section className="bg-white/10 border border-white/20 rounded-[2rem] md:rounded-[2.5rem] p-5 sm:p-8 md:p-10 shadow-2xl backdrop-blur-xl">
//                   <h3 className="text-sm font-bold text-white/50 uppercase tracking-widest mb-10 border-b border-white/5 pb-4">Education Summary</h3>
//                   <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
//                     <ProfileData label="Matric Marks" value={profile?.matric_obtained} />
//                     <ProfileData label="Board" value={profile?.board} />
//                     <ProfileData label="Inter Roll" value={profile?.inter_roll} />
//                   </div>
//                 </section>
//               </div>

//               {/* SECURITY SECTION */}
//               <div className="xl:col-span-1">
//                 <div className="bg-white/10 border border-white/20 rounded-[2rem] md:rounded-[2.5rem] p-5 sm:p-8 md:p-10 shadow-2xl xl:sticky top-10 backdrop-blur-xl">
//                   <h3 className="text-2xl font-bold mb-8">Security</h3>
                  
//                   <form onSubmit={handleUpdatePassword} className="space-y-6">
//                     <PasswordInput 
//                       label="Current Password" 
//                       value={passwords.current} 
//                       show={showPass.current}
//                       onToggle={() => setShowPass({...showPass, current: !showPass.current})}
//                       onChange={(v) => setPasswords({...passwords, current: v})}
//                     />

//                     <div className="h-px bg-white/10 my-4" />

//                     <PasswordInput 
//                       label="New Password" 
//                       value={passwords.new} 
//                       show={showPass.new}
//                       onToggle={() => setShowPass({...showPass, new: !showPass.new})}
//                       onChange={(v) => setPasswords({...passwords, new: v})}
//                     />

//                     <PasswordInput 
//                       label="Confirm New Password" 
//                       value={passwords.confirm} 
//                       show={showPass.confirm}
//                       onToggle={() => setShowPass({...showPass, confirm: !showPass.confirm})}
//                       onChange={(v) => setPasswords({...passwords, confirm: v})}
//                     />

//                     {status.msg && (
//                       <div className={`p-4 rounded-xl text-sm font-bold ${status.type === "error" ? "bg-red-500/10 text-red-400" : "bg-green-500/10 text-green-400"}`}>
//                         {status.msg}
//                       </div>
//                     )}

//                     {/* Button Color Fixed to Theme Secondary */}
//                     <button 
//                       type="submit" 
//                       disabled={resetLoading} 
//                       className="w-full py-4 rounded-full bg-[#D9D9D9] hover:bg-white text-black font-bold transition-all shadow-lg active:scale-95"
//                     >
//                       {resetLoading ? "Updating..." : "Update Password"}
//                     </button>
//                   </form>
//                 </div>
//               </div>

//             </div>
//           </div>
//         </main>
//       </div>
//     </section>
//   );
// }

// function ProfileData({ label, value }) {
//   return (
//     <div className="space-y-1">
//       <p className="text-xs font-bold text-white/40 uppercase tracking-widest">{label}</p>
//       <p className="text-white text-xl font-semibold tracking-tight">{value || "Not Set"}</p>
//     </div>
//   );
// }

// function PasswordInput({ label, value, show, onToggle, onChange }) {
//   return (
//     <div className="space-y-2">
//       <label className="text-sm font-semibold text-white/80 ml-1">{label}</label>
//       <div className="relative">
//         <input 
//           type={show ? "text" : "password"} 
//           required
//           value={value}
//           onChange={(e) => onChange(e.target.value)}
//           /* Input colors fixed to match Login Form inputs */
//           className="w-full bg-white text-black border-none rounded-2xl px-5 py-4 outline-none focus:ring-2 focus:ring-purple-500 transition-all shadow-inner" 
//         />
//         <button 
//           type="button" 
//           onClick={onToggle} 
//           className="absolute right-5 top-1/2 -translate-y-1/2 text-[11px] font-bold text-purple-600 hover:text-purple-800 transition uppercase"
//         >
//           {show ? "Hide" : "Show"}
//         </button>
//       </div>
//     </div>
//   );
// }

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import { getSession, logout } from "../utils/authStore";

export default function ProfilePage() {
  const navigate = useNavigate();
  const session = getSession();
  
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [passwords, setPasswords] = useState({ current: "", new: "", confirm: "" });
  const [showPass, setShowPass] = useState({ current: false, new: false, confirm: false });
  const [status, setStatus] = useState({ type: "", msg: "" });
  const [resetLoading, setResetLoading] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get("/student/profile/");
        setProfile(response.data);
      } catch (err) { 
        console.error(err); 
      } finally { 
        setLoading(false); 
      }
    };
    fetchProfile();
  }, []);

  const handleUpdatePassword = async (e) => {
    e.preventDefault();
    
    // Client-side validation
    if (passwords.new !== passwords.confirm) {
      setStatus({ type: "error", msg: "New passwords do not match!" });
      return;
    }

    if (passwords.new.length < 8) {
        setStatus({ type: "error", msg: "New password must be at least 8 characters." });
        return;
    }

    setResetLoading(true);
    setStatus({ type: "", msg: "" });

    try {

      await api.post("/auth/change-password/", {
        old_password: passwords.current,
        new_password: passwords.new
      });

      setStatus({ type: "success", msg: "Password updated successfully!" });
      setPasswords({ current: "", new: "", confirm: "" });
      
      // Optional: Clear success message after 5 seconds
      setTimeout(() => setStatus({ type: "", msg: "" }), 5000);

    } catch (err) {
      // Backend error handling
      const errorMsg = err.response?.data?.detail || err.response?.data?.old_password?.[0] || "Failed to update. Verify current password.";
      setStatus({ type: "error", msg: errorMsg });
    } finally { 
      setResetLoading(false); 
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-[#0B0620] flex items-center justify-center">
      <div className="w-10 h-10 border-2 border-t-purple-500 border-white/10 rounded-full animate-spin"></div>
    </div>
  );

  return (
    <section className="min-h-screen bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] text-white font-poppins">
      <div className="h-24 w-full" /> 

      <div className="flex flex-col md:flex-row w-full min-h-[calc(100vh-6rem)]">
        
        {/* SIDEBAR */}
        <aside className="w-full md:w-80 bg-white/5 border-b md:border-b-0 md:border-r border-white/10 p-4 md:p-8 flex flex-col shrink-0">
          <div className="mb-4 md:mb-10 px-1 md:px-0">
            <p className="text-xs font-semibold text-white/40 uppercase mb-2 tracking-widest">Student Session</p>
            <h2 className="text-xl font-bold text-white truncate">{session?.name || session?.username || "Guest"}</h2>
          </div>

          {/* Wrapping row of tabs on phones, a vertical list from md up */}
          <nav className="flex flex-wrap md:flex-nowrap md:flex-col gap-2 md:gap-0 md:space-y-2 flex-1">
            <button onClick={() => navigate("/dashboard")} className="shrink-0 md:w-full text-left px-4 md:px-5 py-2.5 md:py-3 rounded-xl hover:bg-white/10 text-white/80 transition font-medium text-sm md:text-base border border-white/10 md:border-0">Dashboard</button>
            <button onClick={() => navigate("/my-application")} className="shrink-0 md:w-full text-left px-4 md:px-5 py-2.5 md:py-3 rounded-xl hover:bg-white/10 text-white/80 transition font-medium text-sm md:text-base border border-white/10 md:border-0">My Application Form</button>
            <button className="shrink-0 md:w-full text-left px-4 md:px-5 py-2.5 md:py-3 rounded-xl bg-white text-[#0B0620] font-bold shadow-xl text-sm md:text-base">Profile Settings</button>
            <button onClick={() => { logout(); navigate("/login"); }} className="md:hidden shrink-0 px-4 py-2.5 rounded-xl text-red-400 transition font-bold border border-red-400/20 text-sm">Log Out</button>
          </nav>

          <button onClick={() => { logout(); navigate("/login"); }} className="hidden md:block mt-10 px-5 py-3 rounded-xl text-red-400 hover:bg-red-400/10 transition text-left font-bold border border-red-400/20">Log Out</button>
        </aside>

        {/* MAIN CONTENT */}
        <main className="flex-1 min-w-0 px-4 py-6 sm:p-8 md:p-12 lg:p-16 overflow-y-auto">
          <div className="max-w-[1400px] mx-auto">
            
            <header className="mb-8 md:mb-12 border-b border-white/10 pb-6 md:pb-8">
              <h1 className="text-3xl md:text-4xl font-bold mb-2 tracking-tight">Account Settings</h1>
              <p className="text-white/60 text-base md:text-lg">Manage your personal data and security preferences.</p>
            </header>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 md:gap-12">
              
              <div className="xl:col-span-2 space-y-8">
                <section className="bg-white/10 border border-white/20 rounded-[2rem] md:rounded-[2.5rem] p-5 sm:p-8 md:p-10 shadow-2xl backdrop-blur-xl">
                  <h3 className="text-sm font-bold text-white/50 uppercase tracking-widest mb-10 border-b border-white/5 pb-4">Identity Details</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-10">
                    <ProfileData label="Full Name" value={profile?.student_name} />
                    <ProfileData label="CNIC / Identity" value={profile?.student_cnic} />
                    <ProfileData label="Registered Email" value={profile?.email} />
                    <ProfileData label="Mobile Number" value={profile?.mobile} />
                    <ProfileData label="City" value={profile?.city} />
                    <ProfileData label="Province" value={profile?.province} />
                  </div>
                </section>

                <section className="bg-white/10 border border-white/20 rounded-[2rem] md:rounded-[2.5rem] p-5 sm:p-8 md:p-10 shadow-2xl backdrop-blur-xl">
                  <h3 className="text-sm font-bold text-white/50 uppercase tracking-widest mb-10 border-b border-white/5 pb-4">Education Summary</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <ProfileData label="Matric Marks" value={profile?.matric_obtained} />
                    <ProfileData label="Board" value={profile?.board} />
                    <ProfileData label="Inter Roll" value={profile?.inter_roll} />
                  </div>
                </section>
              </div>

              <div className="xl:col-span-1">
                <div className="bg-white/10 border border-white/20 rounded-[2rem] md:rounded-[2.5rem] p-5 sm:p-8 md:p-10 shadow-2xl xl:sticky top-10 backdrop-blur-xl">
                  <h3 className="text-2xl font-bold mb-8 tracking-tight">Security</h3>
                  
                  <form onSubmit={handleUpdatePassword} className="space-y-6">
                    <PasswordInput 
                      label="Current Password" 
                      value={passwords.current} 
                      show={showPass.current}
                      onToggle={() => setShowPass({...showPass, current: !showPass.current})}
                      onChange={(v) => setPasswords({...passwords, current: v})}
                    />

                    <div className="h-px bg-white/10 my-4" />

                    <PasswordInput 
                      label="New Password" 
                      value={passwords.new} 
                      show={showPass.new}
                      onToggle={() => setShowPass({...showPass, new: !showPass.new})}
                      onChange={(v) => setPasswords({...passwords, new: v})}
                    />

                    <PasswordInput 
                      label="Confirm New Password" 
                      value={passwords.confirm} 
                      show={showPass.confirm}
                      onToggle={() => setShowPass({...showPass, confirm: !showPass.confirm})}
                      onChange={(v) => setPasswords({...passwords, confirm: v})}
                    />

                    {status.msg && (
                      <div className={`p-4 rounded-xl text-sm font-bold ${status.type === "error" ? "bg-red-500/10 text-red-400" : "bg-green-500/10 text-green-400"}`}>
                        {status.msg}
                      </div>
                    )}

                    <button 
                      type="submit" 
                      disabled={resetLoading} 
                      className="w-full py-4 rounded-full bg-[#D9D9D9] hover:bg-white text-black font-bold transition-all shadow-lg active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {resetLoading ? "Updating..." : "Update Password"}
                    </button>
                  </form>
                </div>
              </div>

            </div>
          </div>
        </main>
      </div>
    </section>
  );
}

function ProfileData({ label, value }) {
  return (
    <div className="space-y-1">
      <p className="text-xs font-bold text-white/40 uppercase tracking-widest">{label}</p>
      <p className="text-white text-xl font-semibold tracking-tight">{value || "Not Set"}</p>
    </div>
  );
}

function PasswordInput({ label, value, show, onToggle, onChange }) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-semibold text-white/80 ml-1">{label}</label>
      <div className="relative">
        <input 
          type={show ? "text" : "password"} 
          required
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full bg-white text-black border-none rounded-2xl px-5 py-4 outline-none focus:ring-2 focus:ring-purple-500 transition-all shadow-inner" 
        />
        <button 
          type="button" 
          onClick={onToggle} 
          className="absolute right-5 top-1/2 -translate-y-1/2 text-[11px] font-bold text-purple-600 hover:text-purple-800 transition uppercase"
        >
          {show ? "Hide" : "Show"}
        </button>
      </div>
    </div>
  );
}