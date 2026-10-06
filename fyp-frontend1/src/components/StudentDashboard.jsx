
// import React from "react";
// import { useNavigate } from "react-router-dom";
// import { getSession, logout } from "../utils/authStore";
// import ApplyForm from "./ApplyForm";
// import Chatbot from "./Chatbot";
// import UpcomingDeadlines from "./deadline";

// const defaultUniversities = [
//   {
//     id: "u1",
//     name: "FAST NUCES",
//     deadline: "2025-11-15",
//     status: "Pending",
//     lastUpdate: "—",
//   },
//   {
//     id: "u2",
//     name: "NUST",
//     deadline: "2025-12-01",
//     status: "Pending",
//     lastUpdate: "—",
//   },
//   {
//     id: "u3",
//     name: "GIKI",
//     deadline: "2025-12-10",
//     status: "Pending",
//     lastUpdate: "—",
//   },
//   {
//     id: "u4",
//     name: "UET Lahore",
//     deadline: "2025-11-30",
//     status: "Pending",
//     lastUpdate: "—",
//   },
// ];

// export default function StudentDashboard() {
//   const navigate = useNavigate();
//   const session = getSession();
//   const [tab, setTab] = React.useState("home");
//   const [universities, setUniversities] = React.useState(defaultUniversities);

//   const storageKey = session
//     ? `aikapply.universities.${session.username}`
//     : "aikapply.universities.anonymous";

//   // Data Persistence
//   React.useEffect(() => {
//     try {
//       const raw = localStorage.getItem(storageKey);
//       if (raw) setUniversities(JSON.parse(raw));
//     } catch {}
//   }, [storageKey]);

//   React.useEffect(() => {
//     try {
//       localStorage.setItem(storageKey, JSON.stringify(universities));
//     } catch {}
//   }, [universities, storageKey]);

//   const onApplyUni = (id) => {
//     setUniversities((list) =>
//       list.map((u) =>
//         u.id === id
//           ? {
//               ...u,
//               status: "Applied",
//               lastUpdate: new Date().toISOString().slice(0, 10),
//             }
//           : u,
//       ),
//     );
//     setTab("applications");
//   };

//   const onLogout = () => {
//     logout();
//     navigate("/login", { replace: true });
//   };

//   return (
//     <section className="min-h-screen bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] pt-20">
//       <div className="flex flex-col md:flex-row w-full min-h-[calc(100vh-5rem)]">
//         {/* --- SIDEBAR (Logo Removed) --- */}
//         <aside className="w-full md:w-80 bg-white/5 backdrop-blur-md border-r border-white/10 p-8 flex flex-col shrink-0">
//           {/* User Session Info Card */}
//           <div className="mb-12">
//             <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
//               <p className="text-[10px] font-bold text-white/40 uppercase tracking-[0.2em] mb-1">
//                 Active Session
//               </p>
//               <div className="text-base font-semibold text-white truncate">
//                 {session ? session.username : "Guest User"}
//               </div>
//             </div>
//           </div>

//           <nav className="space-y-1 flex-1">
//             <p className="px-4 text-[10px] font-bold text-white/30 uppercase mb-3 tracking-widest">
//               Navigation
//             </p>
//             <button
//               className={`w-full text-left px-5 py-3.5 rounded-xl transition-all duration-200 ${tab === "home" ? "bg-white text-[#0B0620] font-bold shadow-xl" : "text-white/60 hover:bg-white/10 hover:text-white"}`}
//               onClick={() => setTab("home")}
//             >
//               Home
//             </button>
//             <button
//               className={`w-full text-left px-5 py-3.5 rounded-xl transition-all duration-200 ${tab === "applications" ? "bg-white text-[#0B0620] font-bold shadow-xl" : "text-white/60 hover:bg-white/10 hover:text-white"}`}
//               onClick={() => setTab("applications")}
//             >
//               My Applications
//             </button>

//             <div className="pt-8 pb-2">
//               <p className="px-4 text-[10px] font-bold text-white/30 uppercase mb-3 tracking-widest">
//                 AI Services
//               </p>
//             </div>
//             <button
//               className="w-full text-left px-5 py-3.5 rounded-xl text-white/60 hover:bg-white/10 hover:text-white transition-all font-medium border border-white/5 hover:border-white/20 mb-2"
//               onClick={() => navigate("/apply")}
//             >
//               Application Form
//             </button>
//             <button
//               className="w-full text-left px-5 py-3.5 rounded-xl text-white/60 hover:bg-white/10 hover:text-white transition-all font-medium border border-white/5 hover:border-white/20 mb-2"
//               onClick={() => navigate("/recommend")}
//             >
//               University Recommender
//             </button>

//             <button
//               className={`w-full text-left px-5 py-3.5 rounded-xl transition-all duration-200 ${tab === "chatbot" ? "bg-white text-[#0B0620] font-bold shadow-xl" : "text-white/60 hover:bg-white/10 hover:text-white"}`}
//               onClick={() => setTab("chatbot")}
//             >
//               Chatbot
//             </button>

//             <div className="mt-10 pt-6 border-t border-white/5">
//               <button
//                 className="w-full text-left px-5 py-3 rounded-xl text-red-400 hover:bg-red-400/10 transition-all text-sm font-semibold"
//                 onClick={onLogout}
//               >
//                 Log Out
//               </button>
//             </div>
//           </nav>
//         </aside>

//         {/* --- MAIN CONTENT --- */}
//         <main className="flex-1 p-8 md:p-12 lg:p-16 overflow-y-auto">
//           <div className="max-w-[1400px]">
//             {tab === "home" && (
 
//               <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
//                 <h1 className="text-4xl font-bold mb-3 text-white">
//                   Available Universities
//                 </h1>

//                 <p className="text-white/50 text-lg mb-12">
//                   Select an institution to start your automated application
//                   process.
//                 </p>

//                 <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
//                   {universities.map((u) => (
//                     <div
//                       key={u.id}
//                       className="group bg-white/5 border border-white/10 rounded-[2rem] p-8 flex flex-col gap-6 hover:bg-white/[0.08] hover:border-white/20 transition-all duration-300 shadow-2xl"
//                     >
//                       {/* HEADER */}
//                       <div className="flex items-start justify-between">
//                         <h3 className="text-xl font-bold text-white">
//                           {u.name}
//                         </h3>

//                         <span
//                           className={`text-[10px] px-3 py-1.5 rounded-lg uppercase font-black tracking-widest
//                 ${
//                   u.status === "Pending"
//                     ? "bg-yellow-400/10 text-yellow-400 border border-yellow-400/20"
//                     : u.status === "Processing"
//                       ? "bg-blue-400/10 text-blue-400 border border-blue-400/20"
//                       : u.status === "Applied"
//                         ? "bg-green-400/10 text-green-400 border border-green-400/20"
//                         : "bg-red-400/10 text-red-400 border border-red-400/20"
//                 }`}
//                         >
//                           {u.status}
//                         </span>
//                       </div>

//                       {/* INFO */}
//                       <div className="text-sm text-white/40 space-y-2 py-4 border-y border-white/5">
//                         <div className="flex justify-between">
//                           <span>Admission Deadline</span>
//                           <span className="text-white/80 font-medium">
//                             {u.deadline}
//                           </span>
//                         </div>

//                         <div className="flex justify-between">
//                           <span>System Status</span>
//                           <span className="text-white/80 font-medium">
//                             {u.status === "Processing"
//                               ? "Running automation..."
//                               : "Ready"}
//                           </span>
//                         </div>
//                       </div>

//                       {/* BUTTON */}
//                       <button
//                         disabled={u.status === "Processing"}
//                         className="w-full py-4 rounded-2xl bg-white text-a[#0B0620] font-bold hover:bg-purple-100 transition-all shadow-lg active:scale-95 disabled:opacity-50"
//                         onClick={async () => {
//                           try {
//                             console.log("🚀 STARTING AUTOMATION:", u.id);

//                             // 1. set UI to processing
//                             setUniversities((prev) =>
//                               prev.map((item) =>
//                                 item.id === u.id
//                                   ? {
//                                       ...item,
//                                       status: "Processing",
//                                       error: null,
//                                       errorDetails: null,
//                                     }
//                                   : item,
//                               ),
//                             );

//                             // 2. API CALL (MATCH BACKEND EXACTLY)
//                             const response = await fetch(
//                               "http://127.0.0.1:8000/automation_engine/submit/",
//                               {
//                                 method: "POST",
//                                 headers: {
//                                   "Content-Type": "application/json",
//                                 },
//                                 body: JSON.stringify({
//                                   university_id: u.id,
//                                 }),
//                               },
//                             );

//                             const data = await response.json();

//                             console.log("🔥 BACKEND RESPONSE:", data);

//                             // 3. FAIL HANDLING
//                             if (!response.ok || data.status !== "success") {
//                               throw new Error(
//                                 data.message || "Automation failed",
//                               );
//                             }

//                             // 4. SUCCESS UPDATE
//                             setUniversities((prev) =>
//                               prev.map((item) =>
//                                 item.id === u.id
//                                   ? {
//                                       ...item,
//                                       status: "Applied",
//                                       screenshots: data.screenshots || [],
//                                       stepsCompleted: data.completed_steps || 0,
//                                       lastUpdate: new Date().toLocaleString(),
//                                       error: null,
//                                       errorDetails: null,
//                                     }
//                                   : item,
//                               ),
//                             );
//                           } catch (err) {
//                             console.error("❌ AUTOMATION ERROR:", err);

//                             // 5. FAILURE UPDATE
//                             setUniversities((prev) =>
//                               prev.map((item) =>
//                                 item.id === u.id
//                                   ? {
//                                       ...item,
//                                       status: "Failed",
//                                       error: err.message,
//                                       errorDetails: err.toString(),
//                                       lastUpdate: new Date().toLocaleString(),
//                                     }
//                                   : item,
//                               ),
//                             );
//                           }
//                         }}
//                       >
//                         {u.status === "Processing"
//                           ? "Applying..."
//                           : u.status === "Applied"
//                             ? "✓ Applied"
//                             : u.status === "Failed"
//                               ? "Retry"
//                               : "Apply Automatically"}
//                       </button>

//                       {/* ERROR MESSAGE */}
//                       {u.status === "Failed" && (
//                         <p className="text-xs text-red-300">
//                           ⚠️ Application failed. Check Active Submissions tab
//                           for details.
//                         </p>
//                       )}
//                     </div>
//                   ))}
//                 </div>
//               </div>
//             )}

//             {tab === "applications" && (

//               <div className="animate-in fade-in duration-500">
//                 <h1 className="text-3xl font-bold mb-3 text-white">
//                   Active Submissions
//                 </h1>
//                 <p className="text-white/50 mb-10">
//                   Track and manage your automated university applications.
//                 </p>

//                 <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
//                   {universities
//                     .filter(
//                       (u) => u.status === "Applied" || u.status === "Failed",
//                     )
//                     .map((u) => (
//                       <div
//                         key={u.id}
//                         className={`rounded-[2rem] p-8 flex flex-col gap-4 border-l-4 transition-all
//             ${
//               u.status === "Applied"
//                 ? "bg-white/5 border border-white/10 border-l-emerald-500"
//                 : "bg-red-950/20 border border-red-900/30 border-l-red-500"
//             }`}
//                       >
//                         {/* Header with Status */}
//                         <div className="flex items-center justify-between mb-2">
//                           <h3 className="text-lg font-bold text-white">
//                             {u.name}
//                           </h3>
//                           <span
//                             className={`text-[10px] px-3 py-1.5 rounded-lg uppercase font-black tracking-widest
//               ${
//                 u.status === "Applied"
//                   ? "bg-emerald-400/10 text-emerald-400 border border-emerald-400/20"
//                   : "bg-red-400/10 text-red-400 border border-red-400/20"
//               }`}
//                           >
//                             {u.status}
//                           </span>
//                         </div>

//                         {/* Metadata */}
//                         <div className="text-xs text-white/40 space-y-1">
//                           <p>Submitted: {u.lastUpdate || "N/A"}</p>
//                           <p>ID: {u.id.toUpperCase()}</p>
//                         </div>

//                         {/* 🆕 ERROR SECTION - Show if failed */}
//                         {u.status === "Failed" && u.error && (
//                           <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 space-y-2">
//                             <p className="text-sm font-semibold text-red-300">
//                               ❌ Error
//                             </p>
//                             <p className="text-xs text-red-200">{u.error}</p>
//                             {u.errorDetails && (
//                               <details className="text-xs text-red-100/70">
//                                 <summary className="cursor-pointer font-semibold text-red-200 mb-2">
//                                   Technical Details
//                                 </summary>
//                                 <pre className="bg-black/30 p-2 rounded text-[10px] overflow-auto max-h-40">
//                                   {typeof u.errorDetails === "string"
//                                     ? u.errorDetails
//                                     : JSON.stringify(u.errorDetails, null, 2)}
//                                 </pre>
//                               </details>
//                             )}
//                           </div>
//                         )}

//                         {/* 🆕 SCREENSHOTS SECTION - Show if applied */}
//                         {u.status === "Applied" &&
//                           u.screenshots &&
//                           u.screenshots.length > 0 && (
//                             <div className="space-y-2">
//                               <p className="text-xs text-white/50 font-semibold">
//                                 📸 Automation Screenshots (
//                                 {u.screenshots.length})
//                               </p>

//                               {u.screenshots.map((img, index) => (
//                                 <div key={index} className="space-y-1">
//                                   <p className="text-[10px] text-white/30">
//                                     Step {index + 1}
//                                   </p>
//                                   <img
//                                     src={`http://127.0.0.1:8000/media/screenshots/${img
//                                       .split("\\")
//                                       .pop()}`}
//                                     alt={`step-${index}`}
//                                     className="rounded-xl border border-white/10 w-full hover:border-white/30 transition-all cursor-pointer"
//                                   />
//                                 </div>
//                               ))}
//                             </div>
//                           )}

//                         {/* Steps Completed */}
//                         {u.status === "Applied" && u.stepsCompleted && (
//                           <div className="text-xs text-white/40">
//                             <p>✓ Completed {u.stepsCompleted} steps</p>
//                           </div>
//                         )}

//                         {/* Action Buttons */}
//                         <div className="flex gap-2 mt-4">
//                           <button
//                             className="flex-1 py-3 rounded-xl border border-white/10 hover:bg-white/5 transition-all text-sm font-bold text-white"
//                             onClick={() =>
//                               navigate("/apply", {
//                                 state: { edit: true, universityId: u.id },
//                               })
//                             }
//                           >
//                             View Application
//                           </button>

//                           {/* 🆕 Retry button for failed applications */}
//                           {u.status === "Failed" && (
//                             <button
//                               className="flex-1 py-3 rounded-xl bg-red-500/20 border border-red-400/50 hover:bg-red-500/30 transition-all text-sm font-bold text-red-200"
//                               onClick={async () => {
//                                 try {
//                                   setUniversities((prev) =>
//                                     prev.map((item) =>
//                                       item.id === u.id
//                                         ? {
//                                             ...item,
//                                             status: "Processing",
//                                             error: null,
//                                           }
//                                         : item,
//                                     ),
//                                   );

//                                   const response = await fetch(
//                                     "http://127.0.0.1:8000/automation_engine/submit/",
//                                     {
//                                       method: "POST",
//                                       headers: {
//                                         "Content-Type": "application/json",
//                                       },
//                                       body: JSON.stringify({
//                                         university_id: u.id,
//                                       }),
//                                     },
//                                   );

//                                   const data = await response.json();

//                                   if (data.status === "success") {
//                                     setUniversities((prev) =>
//                                       prev.map((item) =>
//                                         item.id === u.id
//                                           ? {
//                                               ...item,
//                                               status: "Applied",
//                                               screenshots: data.screenshots,
//                                               stepsCompleted:
//                                                 data.completed_steps,
//                                               lastUpdate:
//                                                 new Date().toLocaleString(),
//                                               error: null,
//                                               errorDetails: null,
//                                             }
//                                           : item,
//                                       ),
//                                     );
//                                   } else {
//                                     throw new Error(
//                                       data.message || "Retry failed",
//                                     );
//                                   }
//                                 } catch (err) {
//                                   console.error(err);

//                                   setUniversities((prev) =>
//                                     prev.map((item) =>
//                                       item.id === u.id
//                                         ? {
//                                             ...item,
//                                             status: "Failed",
//                                             error:
//                                               err.message || "Retry failed",
//                                             lastUpdate:
//                                               new Date().toLocaleString(),
//                                           }
//                                         : item,
//                                     ),
//                                   );
//                                 }
//                               }}
//                             >
//                               Retry
//                             </button>
//                           )}
//                         </div>
//                       </div>
//                     ))}
//                 </div>

//                 {/* Empty State */}
//                 {universities.filter(
//                   (u) => u.status === "Applied" || u.status === "Failed",
//                 ).length === 0 && (
//                   <div className="text-center py-12">
//                     <p className="text-white/40">
//                       No applications submitted yet.
//                     </p>
//                     <p className="text-white/20 text-sm">
//                       Go to Home tab and click "Apply Automatically" to get
//                       started.
//                     </p>
//                   </div>
//                 )}
//               </div>
//             )}

//             {tab === "chatbot" && (
//               <div className="h-[calc(100vh-14rem)] bg-white/5 border border-white/10 rounded-[2.5rem] overflow-hidden shadow-2xl">
//                 <Chatbot />
//               </div>
//             )}
            
//           </div>
//         </main>
//       </div>
//     </section>
//   );
// }

// // bestt after deadlinee
// import React from "react";
// import { useNavigate } from "react-router-dom";
// import { getSession, logout } from "../utils/authStore";
// import ApplyForm from "./ApplyForm";
// import Chatbot from "./Chatbot";
// import UpcomingDeadlines from "./deadline";

// // const defaultUniversities = [
// //   { id: "u1", name: "FAST NUCES", deadline: "2025-11-15", status: "Pending", lastUpdate: "—" },
// //   { id: "u2", name: "NUST",       deadline: "2025-12-01", status: "Pending", lastUpdate: "—" },
// //   { id: "u3", name: "GIKI",       deadline: "2025-12-10", status: "Pending", lastUpdate: "—" },
// //   { id: "u4", name: "UET Lahore", deadline: "2025-11-30", status: "Pending", lastUpdate: "—" },
// // ];
// // Add university portal URLs to your defaultUniversities array
// const defaultUniversities = [
//   { id: "u1", name: "FAST NUCES", url: "http://localhost:3000/apply", deadline: "2025-11-15", status: "Pending", lastUpdate: "—" },
//   { id: "u2", name: "NUST",       url: "http://localhost:3000/apply", deadline: "2025-12-01", status: "Pending", lastUpdate: "—" },
//   { id: "u3", name: "GIKI",       url: "http://localhost:3000/apply", deadline: "2025-12-10", status: "Pending", lastUpdate: "—" },
//   { id: "u4", name: "UET Lahore", url: "http://localhost:3000/apply", deadline: "2025-11-30", status: "Pending", lastUpdate: "—" },
// ];

// export default function StudentDashboard() {
//   const navigate = useNavigate();
//   const session = getSession();
//   const [tab, setTab] = React.useState("home");
//   const [universities, setUniversities] = React.useState(defaultUniversities);
//   const [deadlinePanelOpen, setDeadlinePanelOpen] = React.useState(false);

//   const storageKey = session
//     ? `aikapply.universities.${session.username}`
//     : "aikapply.universities.anonymous";

//   React.useEffect(() => {
//     try {
//       const raw = localStorage.getItem(storageKey);
//       if (raw) setUniversities(JSON.parse(raw));
//     } catch {}
//   }, [storageKey]);

//   React.useEffect(() => {
//     try {
//       localStorage.setItem(storageKey, JSON.stringify(universities));
//     } catch {}
//   }, [universities, storageKey]);

//   const onLogout = () => {
//     logout();
//     navigate("/login", { replace: true });
//   };

//   // const runAutomation = async (u) => {
//   //   setUniversities((prev) =>
//   //     prev.map((item) =>
//   //       item.id === u.id ? { ...item, status: "Processing", error: null, errorDetails: null } : item
//   //     )
//   //   );
//   //   try {
//   //     const response = await fetch("http://127.0.0.1:8000/automation_engine/submit/", {
//   //       method: "POST",
//   //       headers: { "Content-Type": "application/json" },
//   //       body: JSON.stringify({ university_id: u.id }),
//   //     });
//   //     const data = await response.json();
//   //     if (!response.ok || data.status !== "success") throw new Error(data.message || "Automation failed");
//   //     setUniversities((prev) =>
//   //       prev.map((item) =>
//   //         item.id === u.id
//   //           ? { ...item, status: "Applied", screenshots: data.screenshots || [], stepsCompleted: data.completed_steps || 0, lastUpdate: new Date().toLocaleString(), error: null, errorDetails: null }
//   //           : item
//   //       )
//   //     );
//   //   } catch (err) {
//   //     setUniversities((prev) =>
//   //       prev.map((item) =>
//   //         item.id === u.id
//   //           ? { ...item, status: "Failed", error: err.message, errorDetails: err.toString(), lastUpdate: new Date().toLocaleString() }
//   //           : item
//   //       )
//   //     );
//   //   }
//   // };

//   const runAutomation = async (u) => {
//     setUniversities((prev) =>
//       prev.map((item) =>
//         item.id === u.id ? { ...item, status: "Processing", error: null, errorDetails: null } : item
//       )
//     );
  
//     try {
//       const response = await fetch("http://127.0.0.1:8000/api/automation-pipeline/apply/", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         credentials: "include", // ← sends session cookie for auth
//         body: JSON.stringify({ url: u.url }), // ← new API expects "url"
//       });
  
//       const data = await response.json();
  
//       // Handle profile not set up yet
//       if (response.status === 404 && data.error === "profile_missing") {
//         setUniversities((prev) =>
//           prev.map((item) =>
//             item.id === u.id
//               ? { ...item, status: "Failed", error: data.message, lastUpdate: new Date().toLocaleString() }
//               : item
//           )
//         );
//         alert("⚠️ Please complete your application form before using auto-apply.");
//         navigate("/apply");
//         return;
//       }
  
//       if (!response.ok || data.status === "failed") {
//         throw new Error(data.message || data.details || "Automation failed");
//       }
  
//       setUniversities((prev) =>
//         prev.map((item) =>
//           item.id === u.id
//             ? {
//                 ...item,
//                 status: "Applied",
//                 screenshots: data.screenshots || [],
//                 stepsCompleted: data.completed_steps || 0,
//                 applicationId: data.application_id,
//                 mappingFile: data.mapping_file,
//                 lastUpdate: new Date().toLocaleString(),
//                 error: null,
//                 errorDetails: null,
//               }
//             : item
//         )
//       );
  
//     } catch (err) {
//       setUniversities((prev) =>
//         prev.map((item) =>
//           item.id === u.id
//             ? { ...item, status: "Failed", error: err.message, errorDetails: err.toString(), lastUpdate: new Date().toLocaleString() }
//             : item
//         )
//       );
//     }
//   };

//   // How many deadlines are critical (≤14 days)
//   const criticalCount = universities.filter((u) => {
//     const days = Math.ceil((new Date(u.deadline) - new Date()) / 86400000);
//     return days >= 0 && days <= 14;
//   }).length;

//   return (
//     <section className="min-h-screen bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] pt-20">
//       <div className="flex w-full min-h-[calc(100vh-5rem)]">

//         {/* ── LEFT SIDEBAR ── */}
//         <aside className="w-full md:w-72 bg-white/5 backdrop-blur-md border-r border-white/10 p-6 flex flex-col shrink-0">
//           {/* Session card */}
//           <div className="mb-8">
//             <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
//               <p className="text-[10px] font-bold text-white/40 uppercase tracking-[0.2em] mb-1">Active Session</p>
//               <div className="text-base font-semibold text-white truncate">
//                 {session ? session.username : "Guest User"}
//               </div>
//             </div>
//           </div>

//           <nav className="space-y-1 flex-1">
//             <p className="px-4 text-[10px] font-bold text-white/30 uppercase mb-3 tracking-widest">Navigation</p>

//             {[
//               { key: "home", label: "Home" },
//               { key: "applications", label: "My Applications" },
//             ].map(({ key, label }) => (
//               <button
//                 key={key}
//                 className={`w-full text-left px-5 py-3.5 rounded-xl transition-all duration-200 ${
//                   tab === key
//                     ? "bg-white text-[#0B0620] font-bold shadow-xl"
//                     : "text-white/60 hover:bg-white/10 hover:text-white"
//                 }`}
//                 onClick={() => setTab(key)}
//               >
//                 {label}
//               </button>
//             ))}

//             {/* Deadlines button with badge */}
//             <button
//               className={`w-full text-left px-5 py-3.5 rounded-xl transition-all duration-200 flex items-center justify-between ${
//                 tab === "deadlines"
//                   ? "bg-white text-[#0B0620] font-bold shadow-xl"
//                   : "text-white/60 hover:bg-white/10 hover:text-white"
//               }`}
//               onClick={() => setTab("deadlines")}
//             >
//               <span>Deadlines</span>
//               {criticalCount > 0 && (
//                 <span className={`text-[10px] font-black px-2 py-0.5 rounded-md ${tab === "deadlines" ? "bg-red-500 text-white" : "bg-red-500/20 text-red-400 border border-red-500/30"}`}>
//                   {criticalCount} urgent
//                 </span>
//               )}
//             </button>

//             <div className="pt-6 pb-2">
//               <p className="px-4 text-[10px] font-bold text-white/30 uppercase mb-3 tracking-widest">AI Services</p>
//             </div>

//             <button
//               className="w-full text-left px-5 py-3.5 rounded-xl text-white/60 hover:bg-white/10 hover:text-white transition-all font-medium border border-white/5 hover:border-white/20 mb-2"
//               onClick={() => navigate("/apply")}
//             >
//               Application Form
//             </button>
//             <button
//               className="w-full text-left px-5 py-3.5 rounded-xl text-white/60 hover:bg-white/10 hover:text-white transition-all font-medium border border-white/5 hover:border-white/20 mb-2"
//               onClick={() => navigate("/recommend")}
//             >
//               University Recommender
//             </button>
//             <button
//               className={`w-full text-left px-5 py-3.5 rounded-xl transition-all duration-200 ${
//                 tab === "chatbot"
//                   ? "bg-white text-[#0B0620] font-bold shadow-xl"
//                   : "text-white/60 hover:bg-white/10 hover:text-white"
//               }`}
//               onClick={() => setTab("chatbot")}
//             >
//               Chatbot
//             </button>

//             <div className="mt-10 pt-6 border-t border-white/5">
//               <button
//                 className="w-full text-left px-5 py-3 rounded-xl text-red-400 hover:bg-red-400/10 transition-all text-sm font-semibold"
//                 onClick={onLogout}
//               >
//                 Log Out
//               </button>
//             </div>
//           </nav>
//         </aside>

//         {/* ── MAIN CONTENT ── */}
//         <main className="flex-1 p-8 md:p-12 lg:p-16 overflow-y-auto">
//           <div className="max-w-[1400px]">

//             {/* ── HOME TAB ── */}
//             {tab === "home" && (
//               <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
//                 <div className="flex flex-col lg:flex-row lg:gap-16">
//                   {/* University grid */}
//                   <div className="flex-1">
//                     <h1 className="text-4xl font-bold mb-3 text-white">Available Universities</h1>
//                     <p className="text-white/50 text-lg mb-12">Select an institution to start your automated application process.</p>

//                     <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
//                       {universities.map((u) => (
//                         <div
//                           key={u.id}
//                           className="group bg-white/5 border border-white/10 rounded-[2rem] p-8 flex flex-col gap-6 hover:bg-white/[0.08] hover:border-white/20 transition-all duration-300 shadow-2xl"
//                         >
//                           <div className="flex items-start justify-between">
//                             <h3 className="text-xl font-bold text-white">{u.name}</h3>
//                             <span
//                               className={`text-[10px] px-3 py-1.5 rounded-lg uppercase font-black tracking-widest ${
//                                 u.status === "Pending"
//                                   ? "bg-yellow-400/10 text-yellow-400 border border-yellow-400/20"
//                                   : u.status === "Processing"
//                                   ? "bg-blue-400/10 text-blue-400 border border-blue-400/20"
//                                   : u.status === "Applied"
//                                   ? "bg-green-400/10 text-green-400 border border-green-400/20"
//                                   : "bg-red-400/10 text-red-400 border border-red-400/20"
//                               }`}
//                             >
//                               {u.status}
//                             </span>
//                           </div>

//                           <div className="text-sm text-white/40 space-y-2 py-4 border-y border-white/5">
//                             <div className="flex justify-between">
//                               <span>Admission Deadline</span>
//                               <span className="text-white/80 font-medium">{u.deadline}</span>
//                             </div>
//                             <div className="flex justify-between">
//                               <span>Days Remaining</span>
//                               <span className={`font-bold ${
//                                 Math.ceil((new Date(u.deadline) - new Date()) / 86400000) <= 14
//                                   ? "text-red-400"
//                                   : Math.ceil((new Date(u.deadline) - new Date()) / 86400000) <= 30
//                                   ? "text-orange-400"
//                                   : "text-white/80"
//                               }`}>
//                                 {Math.max(0, Math.ceil((new Date(u.deadline) - new Date()) / 86400000))}d
//                               </span>
//                             </div>
//                             <div className="flex justify-between">
//                               <span>System Status</span>
//                               <span className="text-white/80 font-medium">
//                                 {u.status === "Processing" ? "Running automation..." : "Ready"}
//                               </span>
//                             </div>
//                           </div>

//                           <button
//                             disabled={u.status === "Processing"}
//                             className="w-full py-4 rounded-2xl bg-white text-[#0B0620] font-bold hover:bg-purple-100 transition-all shadow-lg active:scale-95 disabled:opacity-50"
//                             onClick={() => runAutomation(u)}
//                           >
//                             {u.status === "Processing"
//                               ? "Applying..."
//                               : u.status === "Applied"
//                               ? "✓ Applied"
//                               : u.status === "Failed"
//                               ? "Retry"
//                               : "Apply Automatically"}
//                           </button>

//                           {u.status === "Failed" && (
//                             <p className="text-xs text-red-300">⚠️ Application failed. Check Active Submissions tab for details.</p>
//                           )}
//                         </div>
//                       ))}
//                     </div>
//                   </div>

//                   {/* Inline deadline panel on large screens */}
//                   <div className="hidden lg:block w-80 shrink-0">
//                     <div className="sticky top-8 bg-white/5 border border-white/10 rounded-[2rem] p-6 shadow-2xl">
//                       <UpcomingDeadlines universities={universities} />
//                     </div>
//                   </div>
//                 </div>

//                 {/* Mobile deadline strip */}
//                 <div className="lg:hidden mt-12 bg-white/5 border border-white/10 rounded-[2rem] p-6">
//                   <UpcomingDeadlines universities={universities} />
//                 </div>
//               </div>
//             )}

//             {/* ── DEADLINES TAB ── */}
//             {tab === "deadlines" && (
//               <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
//                 <h1 className="text-4xl font-bold mb-3 text-white">Deadlines</h1>
//                 <p className="text-white/50 text-lg mb-12">Track how much time you have left for each university.</p>

//                 <div className="max-w-2xl bg-white/5 border border-white/10 rounded-[2rem] p-8 shadow-2xl">
//                   <UpcomingDeadlines universities={universities} />
//                 </div>

//                 {/* Priority explainer cards */}
//                 <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-10 max-w-2xl">
//                   {[
//                     { label: "Critical", days: "≤ 14 days", color: "bg-red-500/10 border-red-500/20 text-red-400" },
//                     { label: "High",     days: "≤ 30 days", color: "bg-orange-500/10 border-orange-500/20 text-orange-400" },
//                     { label: "Medium",   days: "≤ 60 days", color: "bg-yellow-500/10 border-yellow-500/20 text-yellow-400" },
//                     { label: "Low",      days: "60+ days",  color: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" },
//                   ].map((p) => (
//                     <div key={p.label} className={`rounded-2xl p-4 border text-center ${p.color}`}>
//                       <p className="font-black text-sm uppercase tracking-wider">{p.label}</p>
//                       <p className="text-xs opacity-70 mt-1">{p.days}</p>
//                     </div>
//                   ))}
//                 </div>
//               </div>
//             )}

//             {/* ── APPLICATIONS TAB ── */}
//             {tab === "applications" && (
//               <div className="animate-in fade-in duration-500">
//                 <h1 className="text-3xl font-bold mb-3 text-white">Active Submissions</h1>
//                 <p className="text-white/50 mb-10">Track and manage your automated university applications.</p>

//                 <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
//                   {universities
//                     .filter((u) => u.status === "Applied" || u.status === "Failed")
//                     .map((u) => (
//                       <div
//                         key={u.id}
//                         className={`rounded-[2rem] p-8 flex flex-col gap-4 border-l-4 transition-all ${
//                           u.status === "Applied"
//                             ? "bg-white/5 border border-white/10 border-l-emerald-500"
//                             : "bg-red-950/20 border border-red-900/30 border-l-red-500"
//                         }`}
//                       >
//                         <div className="flex items-center justify-between mb-2">
//                           <h3 className="text-lg font-bold text-white">{u.name}</h3>
//                           <span
//                             className={`text-[10px] px-3 py-1.5 rounded-lg uppercase font-black tracking-widest ${
//                               u.status === "Applied"
//                                 ? "bg-emerald-400/10 text-emerald-400 border border-emerald-400/20"
//                                 : "bg-red-400/10 text-red-400 border border-red-400/20"
//                             }`}
//                           >
//                             {u.status}
//                           </span>
//                         </div>

//                         <div className="text-xs text-white/40 space-y-1">
//                           <p>Submitted: {u.lastUpdate || "N/A"}</p>
//                           <p>ID: {u.id.toUpperCase()}</p>
//                         </div>

//                         {u.status === "Failed" && u.error && (
//                           <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 space-y-2">
//                             <p className="text-sm font-semibold text-red-300">❌ Error</p>
//                             <p className="text-xs text-red-200">{u.error}</p>
//                             {u.errorDetails && (
//                               <details className="text-xs text-red-100/70">
//                                 <summary className="cursor-pointer font-semibold text-red-200 mb-2">Technical Details</summary>
//                                 <pre className="bg-black/30 p-2 rounded text-[10px] overflow-auto max-h-40">
//                                   {typeof u.errorDetails === "string" ? u.errorDetails : JSON.stringify(u.errorDetails, null, 2)}
//                                 </pre>
//                               </details>
//                             )}
//                           </div>
//                         )}

//                         {u.status === "Applied" && u.screenshots && u.screenshots.length > 0 && (
//                           <div className="space-y-2">
//                             <p className="text-xs text-white/50 font-semibold">📸 Automation Screenshots ({u.screenshots.length})</p>
//                             {u.screenshots.map((img, index) => (
//                               <div key={index} className="space-y-1">
//                                 <p className="text-[10px] text-white/30">Step {index + 1}</p>
//                                 <img
//                                   src={`http://127.0.0.1:8000/media/screenshots/${img.split("\\").pop()}`}
//                                   alt={`step-${index}`}
//                                   className="rounded-xl border border-white/10 w-full hover:border-white/30 transition-all cursor-pointer"
//                                 />
//                               </div>
//                             ))}
//                           </div>
//                         )}

//                         {u.status === "Applied" && u.stepsCompleted && (
//                           <div className="text-xs text-white/40">
//                             <p>✓ Completed {u.stepsCompleted} steps</p>
//                           </div>
//                         )}

//                         <div className="flex gap-2 mt-4">
//                           <button
//                             className="flex-1 py-3 rounded-xl border border-white/10 hover:bg-white/5 transition-all text-sm font-bold text-white"
//                             onClick={() => navigate("/apply", { state: { edit: true, universityId: u.id } })}
//                           >
//                             View Application
//                           </button>
//                           {u.status === "Failed" && (
//                             <button
//                               className="flex-1 py-3 rounded-xl bg-red-500/20 border border-red-400/50 hover:bg-red-500/30 transition-all text-sm font-bold text-red-200"
//                               onClick={() => runAutomation(u)}
//                             >
//                               Retry
//                             </button>
//                           )}
//                         </div>
//                       </div>
//                     ))}
//                 </div>

//                 {universities.filter((u) => u.status === "Applied" || u.status === "Failed").length === 0 && (
//                   <div className="text-center py-12">
//                     <p className="text-white/40">No applications submitted yet.</p>
//                     <p className="text-white/20 text-sm">Go to Home tab and click "Apply Automatically" to get started.</p>
//                   </div>
//                 )}
//               </div>
//             )}

//             {/* ── CHATBOT TAB ── */}
//             {tab === "chatbot" && (
//               <div className="h-[calc(100vh-14rem)] bg-white/5 border border-white/10 rounded-[2.5rem] overflow-hidden shadow-2xl">
//                 <Chatbot />
//               </div>
//             )}
//           </div>
//         </main>
//       </div>
//     </section>
//   );
// }



// bestt

// import React from "react";
// import { useNavigate } from "react-router-dom";
// import { getSession, logout } from "../utils/authStore";
// import Chatbot from "./Chatbot";
// import UpcomingDeadlines from "./deadline";

// const API = "http://127.0.0.1:8000/api/deadlines";

// // ── tiny helpers ─────────────────────────────────────────────────────────────

// function daysLeft(deadline) {
//   const today = new Date(); today.setHours(0,0,0,0);
//   const d = new Date(deadline); d.setHours(0,0,0,0);
//   return Math.ceil((d - today) / 86400000);
// }

// function statusBadgeClass(status) {
//   return {
//     Pending:    "bg-yellow-400/10 text-yellow-400 border border-yellow-400/20",
//     Processing: "bg-blue-400/10 text-blue-400 border border-blue-400/20",
//     Applied:    "bg-green-400/10 text-green-400 border border-green-400/20",
//     Failed:     "bg-red-400/10 text-red-400 border border-red-400/20",
//   }[status] || "bg-white/10 text-white/50";
// }

// // ── Empty / upload prompt ─────────────────────────────────────────────────────

// function EmptyDeadlinesPrompt({ onUpload, uploading, error }) {
//   const fileRef = React.useRef();

//   return (
//     <div className="flex flex-col items-center justify-center py-20 text-center gap-6">
//       <div className="w-20 h-20 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center text-4xl">
//         📅
//       </div>
//       <div>
//         <h2 className="text-2xl font-bold text-white mb-2">No deadlines in database</h2>
//         <p className="text-white/40 max-w-md">
//           Upload your <span className="text-white/70 font-mono text-sm">universities_deadlines.xlsx</span> file
//           to populate the deadline tracker, or run:
//         </p>
//         <code className="mt-3 block text-xs bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-emerald-400 font-mono">
//           python manage.py import_deadlines universities_deadlines.xlsx
//         </code>
//       </div>

//       {error && (
//         <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 max-w-md">
//           ⚠️ {error}
//         </p>
//       )}

//       <div className="flex flex-col sm:flex-row gap-3 items-center">
//         <input
//           ref={fileRef}
//           type="file"
//           accept=".xlsx,.xlsm"
//           className="hidden"
//           onChange={(e) => e.target.files[0] && onUpload(e.target.files[0])}
//         />
//         <button
//           disabled={uploading}
//           onClick={() => fileRef.current.click()}
//           className="px-8 py-4 rounded-2xl bg-white text-[#0B0620] font-bold hover:bg-purple-100 transition-all shadow-lg active:scale-95 disabled:opacity-50 min-w-[200px]"
//         >
//           {uploading ? "Uploading…" : "Upload Excel File"}
//         </button>
//         <span className="text-white/30 text-sm">.xlsx files only</span>
//       </div>
//     </div>
//   );
// }

// // ── Main dashboard ────────────────────────────────────────────────────────────

// export default function StudentDashboard() {
//   const navigate = useNavigate();
//   const session  = getSession();

//   const [tab, setTab]                 = React.useState("home");
//   const [apiUnis, setApiUnis]         = React.useState([]);   // from /api/deadlines/summary/
//   const [appUnis, setAppUnis]         = React.useState([]);   // local apply-status overlay
//   const [dbPopulated, setDbPopulated] = React.useState(true); // assume true until checked
//   const [loadingApi, setLoadingApi]   = React.useState(true);
//   const [uploadErr, setUploadErr]     = React.useState("");
//   const [uploading, setUploading]     = React.useState(false);
//   const fileInputRef = React.useRef();

//   const storageKey = session
//     ? `aikapply.appstatus.${session.username}`
//     : "aikapply.appstatus.anonymous";

//   // ── load local apply-status from localStorage ──────────────────────────────
//   React.useEffect(() => {
//     try {
//       const raw = localStorage.getItem(storageKey);
//       if (raw) setAppUnis(JSON.parse(raw));
//     } catch {}
//   }, [storageKey]);

//   React.useEffect(() => {
//     try { localStorage.setItem(storageKey, JSON.stringify(appUnis)); } catch {}
//   }, [appUnis, storageKey]);

//   // ── fetch deadlines from API ───────────────────────────────────────────────
//   const fetchDeadlines = React.useCallback(async () => {
//     setLoadingApi(true);
//     try {
//       const res  = await fetch(`${API}/summary/`);
//       const data = await res.json();
//       if (data.universities && data.universities.length > 0) {
//         setDbPopulated(true);
//         setApiUnis(data.universities);
//         // initialise appUnis for any uni not yet tracked locally
//         setAppUnis(prev => {
//           const existingIds = new Set(prev.map(u => u.university_id));
//           const fresh = data.universities
//             .filter(u => !existingIds.has(u.university_id))
//             .map(u => ({ university_id: u.university_id, status: "Pending", lastUpdate: "—", screenshots: [], stepsCompleted: 0 }));
//           return [...prev, ...fresh];
//         });
//       } else {
//         setDbPopulated(false);
//       }
//     } catch (e) {
//       console.error("API fetch failed:", e);
//       setDbPopulated(false);
//     } finally {
//       setLoadingApi(false);
//     }
//   }, []);

//   React.useEffect(() => { fetchDeadlines(); }, [fetchDeadlines]);

//   // ── merge API data + local status into one list ────────────────────────────
//   const universities = React.useMemo(() => {
//     return apiUnis.map(apiU => {
//       const local = appUnis.find(a => a.university_id === apiU.university_id) || {};
//       return {
//         ...apiU,
//         id:         apiU.university_id,
//         status:     local.status      || "Pending",
//         lastUpdate: local.lastUpdate  || "—",
//         screenshots: local.screenshots || [],
//         stepsCompleted: local.stepsCompleted || 0,
//         error:       local.error      || null,
//         errorDetails: local.errorDetails || null,
//       };
//     });
//   }, [apiUnis, appUnis]);

//   // ── apply automation ───────────────────────────────────────────────────────
//   // const runAutomation = async (u) => {
//   //   setAppUnis(prev => prev.map(a =>
//   //     a.university_id === u.university_id
//   //       ? { ...a, status: "Processing", error: null, errorDetails: null }
//   //       : a
//   //   ));
//   //   try {
//   //     const res  = await fetch("http://127.0.0.1:8000/automation_engine/submit/", {
//   //       method:  "POST",
//   //       headers: { "Content-Type": "application/json" },
//   //       body:    JSON.stringify({ university_id: u.university_id }),
//   //     });
//   //     const data = await res.json();
//   //     if (!res.ok || data.status !== "success") throw new Error(data.message || "Automation failed");
//   //     setAppUnis(prev => prev.map(a =>
//   //       a.university_id === u.university_id
//   //         ? { ...a, status: "Applied", screenshots: data.screenshots || [], stepsCompleted: data.completed_steps || 0, lastUpdate: new Date().toLocaleString(), error: null }
//   //         : a
//   //     ));
//   //   } catch (err) {
//   //     setAppUnis(prev => prev.map(a =>
//   //       a.university_id === u.university_id
//   //         ? { ...a, status: "Failed", error: err.message, errorDetails: err.toString(), lastUpdate: new Date().toLocaleString() }
//   //         : a
//   //     ));
//   //   }
//   // };

//   // ========== QUICK FIX: Copy this entire function ==========
// // Replace your existing runAutomation() with this:

// const runAutomation = async (u) => {
//   setAppUnis(prev => prev.map(a =>
//     a.university_id === u.university_id
//       ? { ...a, status: "Processing", error: null, errorDetails: null }
//       : a
//   ));
//   try {
//     // ✅ NEW ENDPOINT: /automation-pipeline/apply/
//     // Expects: { "url": "https://..." }
//     // Returns: { status, screenshots, completed_steps, mapping_file, application_id }
//     const res  = await fetch("http://127.0.0.1:8000/api/automation-pipeline/apply/", {
//       method:  "POST",
//       headers: { "Content-Type": "application/json" },
//       credentials: "include", // ← Include session cookies for authentication
//       body:    JSON.stringify({ url: u.website }), // ← Pass the website URL from Excel
//     });
//     const data = await res.json();
    
//     // Handle missing profile (404 with error: "profile_missing")
//     if (res.status === 404 && data.error === "profile_missing") {
//       setAppUnis(prev => prev.map(a =>
//         a.university_id === u.university_id
//           ? { ...a, status: "Failed", error: data.message, lastUpdate: new Date().toLocaleString() }
//           : a
//       ));
//       alert("⚠️ Please complete your application form before using auto-apply.");
//       return;
//     }
    
//     // Check for automation failure
//     if (!res.ok || data.status === "failed") {
//       throw new Error(data.message || data.details || "Automation failed");
//     }
    
//     // ✅ SUCCESS: Update with automation results
//     setAppUnis(prev => prev.map(a =>
//       a.university_id === u.university_id
//         ? {
//             ...a,
//             status: "Applied",
//             screenshots: data.screenshots || [],
//             stepsCompleted: data.completed_steps || 0,
//             lastUpdate: new Date().toLocaleString(),
//             error: null,
//             errorDetails: null,
//             mappingFile: data.mapping_file,
//             applicationId: data.application_id
//           }
//         : a
//     ));
//   } catch (err) {
//     // ❌ ERROR: Mark as failed with error message
//     setAppUnis(prev => prev.map(a =>
//       a.university_id === u.university_id
//         ? { ...a, status: "Failed", error: err.message, errorDetails: err.toString(), lastUpdate: new Date().toLocaleString() }
//         : a
//     ));
//   }
// };

// // ========== WHAT CHANGED ==========
// /*
// 1. Endpoint URL:
//    OLD: /automation_engine/submit/
//    NEW: /automation-pipeline/apply/

// 2. Request body:
//    OLD: { "university_id": "u5" }
//    NEW: { "url": "http://localhost:3000/apply" }
   
// 3. Authentication:
//    OLD: No credentials
//    NEW: credentials: "include" (sends session cookie)
   
// 4. Error handling:
//    NEW: Check for 404 profile_missing error
//    NEW: Check for data.status === "failed"
   
// 5. Response fields:
//    NEW: mapping_file, application_id (in addition to existing fields)
// */

// // ========== DATA FLOW ==========
// /*
// Frontend                          Backend
// ─────────                        ───────────
// university object (u)
//   ├─ university_id: "u5"
//   ├─ name: "LUMS"
//   ├─ website: "http://localhost:3000/apply"  ← Use this
//   ├─ deadline: "2026-06-15"
//   └─ priority: "critical"

//          POST to /automation-pipeline/apply/
//          { url: u.website }
//                     ↓
//          ApplyPipelineView
//          1. Load StudentProfile (check if form completed)
//          2. Generate AI mapping (AIService)
//          3. Save mapping file
//          4. Run automation (AutomationService)
//          5. Return { status, screenshots, mapping_file, application_id }
//                     ↓
//          setAppUnis() with:
//          - status: "Applied"
//          - screenshots: [...]
//          - stepsCompleted: 0
//          - lastUpdate: new Date().toLocaleString()
//          - mappingFile: "..."
//          - applicationId: "..."
// */

//   // ── upload Excel ───────────────────────────────────────────────────────────
//   const handleExcelUpload = async (file) => {
//     setUploading(true);
//     setUploadErr("");
//     const form = new FormData();
//     form.append("file", file);
//     try {
//       const res  = await fetch(`${API}/upload/`, { method: "POST", body: form });
//       const data = await res.json();
//       if (data.status === "error") throw new Error(data.errors?.[0] || "Upload failed");
//       await fetchDeadlines();
//     } catch (e) {
//       setUploadErr(e.message);
//     } finally {
//       setUploading(false);
//     }
//   };

//   const onLogout = () => { logout(); navigate("/login", { replace: true }); };

//   const criticalCount = universities.filter(u => {
//     const d = daysLeft(u.deadline);
//     return d >= 0 && d <= 14;
//   }).length;

//   // ── nav items ──────────────────────────────────────────────────────────────
//   const navItems = [
//     { key: "home",         label: "Home" },
//     { key: "applications", label: "My Applications" },
//     { key: "deadlines",    label: "Deadlines", badge: criticalCount > 0 ? `${criticalCount} urgent` : null },
//     { key: "chatbot",      label: "Chatbot" },
//   ];

//   // ── render ─────────────────────────────────────────────────────────────────
//   return (
//     <section className="min-h-screen bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] pt-20">
//       <div className="flex w-full min-h-[calc(100vh-5rem)]">

//         {/* ── SIDEBAR ── */}
//         <aside className="w-full md:w-72 bg-white/5 backdrop-blur-md border-r border-white/10 p-6 flex flex-col shrink-0">
//           <div className="mb-8">
//             <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
//               <p className="text-[10px] font-bold text-white/40 uppercase tracking-[0.2em] mb-1">Active Session</p>
//               <div className="text-base font-semibold text-white truncate">
//                 {session ? session.username : "Guest User"}
//               </div>
//             </div>
//           </div>

//           <nav className="space-y-1 flex-1">
//             <p className="px-4 text-[10px] font-bold text-white/30 uppercase mb-3 tracking-widest">Navigation</p>
//             {navItems.map(({ key, label, badge }) => (
//               <button
//                 key={key}
//                 onClick={() => setTab(key)}
//                 className={`w-full text-left px-5 py-3.5 rounded-xl transition-all duration-200 flex items-center justify-between
//                   ${tab === key ? "bg-white text-[#0B0620] font-bold shadow-xl" : "text-white/60 hover:bg-white/10 hover:text-white"}`}
//               >
//                 <span>{label}</span>
//                 {badge && (
//                   <span className={`text-[10px] font-black px-2 py-0.5 rounded-md
//                     ${tab === key ? "bg-red-500 text-white" : "bg-red-500/20 text-red-400 border border-red-500/30"}`}>
//                     {badge}
//                   </span>
//                 )}
//               </button>
//             ))}

//             <div className="pt-6 pb-2">
//               <p className="px-4 text-[10px] font-bold text-white/30 uppercase mb-3 tracking-widest">AI Services</p>
//             </div>
//             <button onClick={() => navigate("/apply")}
//               className="w-full text-left px-5 py-3.5 rounded-xl text-white/60 hover:bg-white/10 hover:text-white transition-all font-medium border border-white/5 hover:border-white/20 mb-2">
//               Application Form
//             </button>
//             <button onClick={() => navigate("/recommend")}
//               className="w-full text-left px-5 py-3.5 rounded-xl text-white/60 hover:bg-white/10 hover:text-white transition-all font-medium border border-white/5 hover:border-white/20">
//               University Recommender
//             </button>

//             {/* Upload Excel shortcut */}
//             <div className="mt-6 pt-4 border-t border-white/5">
//               <p className="px-4 text-[10px] font-bold text-white/30 uppercase mb-3 tracking-widest">Data</p>
//               <input ref={fileInputRef} type="file" accept=".xlsx,.xlsm" className="hidden"
//                 onChange={e => e.target.files[0] && handleExcelUpload(e.target.files[0])} />
//               <button
//                 onClick={() => fileInputRef.current.click()}
//                 disabled={uploading}
//                 className="w-full text-left px-5 py-3.5 rounded-xl text-white/60 hover:bg-white/10 hover:text-white transition-all font-medium border border-white/5 hover:border-white/20 disabled:opacity-40"
//               >
//                 {uploading ? "⏳ Uploading…" : "📤 Upload Excel"}
//               </button>
//               {!dbPopulated && !loadingApi && (
//                 <p className="mt-2 px-2 text-[11px] text-red-400">
//                   ⚠ No deadline data — upload your Excel file
//                 </p>
//               )}
//             </div>

//             <div className="mt-6 pt-4 border-t border-white/5">
//               <button onClick={onLogout}
//                 className="w-full text-left px-5 py-3 rounded-xl text-red-400 hover:bg-red-400/10 transition-all text-sm font-semibold">
//                 Log Out
//               </button>
//             </div>
//           </nav>
//         </aside>

//         {/* ── MAIN CONTENT ── */}
//         <main className="flex-1 p-8 md:p-12 lg:p-16 overflow-y-auto">
//           <div className="max-w-[1400px]">

//             {/* HOME */}
//             {tab === "home" && (
//               <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
//                 <div className="flex flex-col lg:flex-row lg:gap-16">
//                   <div className="flex-1">
//                     <h1 className="text-4xl font-bold mb-3 text-white">Available Universities</h1>
//                     <p className="text-white/50 text-lg mb-12">
//                       Select an institution to start your automated application process.
//                     </p>

//                     {loadingApi ? (
//                       <div className="flex items-center gap-3 text-white/40 py-20">
//                         <div className="w-5 h-5 border-2 border-white/20 border-t-white/60 rounded-full animate-spin" />
//                         Loading universities…
//                       </div>
//                     ) : !dbPopulated ? (
//                       <EmptyDeadlinesPrompt
//                         onUpload={handleExcelUpload}
//                         uploading={uploading}
//                         error={uploadErr}
//                       />
//                     ) : (
//                       <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
//                         {universities.map((u) => {
//                           const d = daysLeft(u.deadline);
//                           const urgentColor = d <= 14 ? "text-red-400" : d <= 30 ? "text-orange-400" : "text-white/80";
//                           return (
//                             <div key={u.id}
//                               className="group bg-white/5 border border-white/10 rounded-[2rem] p-8 flex flex-col gap-6 hover:bg-white/[0.08] hover:border-white/20 transition-all duration-300 shadow-2xl">
//                               <div className="flex items-start justify-between">
//                                 <div>
//                                   <h3 className="text-xl font-bold text-white">{u.name}</h3>
//                                   {u.program && <p className="text-sm text-white/40 mt-1">{u.program}</p>}
//                                 </div>
//                                 <span className={`text-[10px] px-3 py-1.5 rounded-lg uppercase font-black tracking-widest ${statusBadgeClass(u.status)}`}>
//                                   {u.status}
//                                 </span>
//                               </div>

//                               <div className="text-sm text-white/40 space-y-2 py-4 border-y border-white/5">
//                                 <div className="flex justify-between">
//                                   <span>Deadline</span>
//                                   <span className="text-white/80 font-medium">{u.deadline}</span>
//                                 </div>
//                                 <div className="flex justify-between">
//                                   <span>Days Left</span>
//                                   <span className={`font-bold ${urgentColor}`}>{Math.max(0, d)}d</span>
//                                 </div>
//                                 <div className="flex justify-between">
//                                   <span>Priority</span>
//                                   <span className={`font-bold capitalize ${urgentColor}`}>{u.priority}</span>
//                                 </div>
//                                 {u.city && (
//                                   <div className="flex justify-between">
//                                     <span>City</span>
//                                     <span className="text-white/80">{u.city}</span>
//                                   </div>
//                                 )}
//                               </div>

//                               <button
//                                 disabled={u.status === "Processing"}
//                                 onClick={() => runAutomation(u)}
//                                 className="w-full py-4 rounded-2xl bg-white text-[#0B0620] font-bold hover:bg-purple-100 transition-all shadow-lg active:scale-95 disabled:opacity-50"
//                               >
//                                 {u.status === "Processing" ? "Applying…"
//                                   : u.status === "Applied"  ? "✓ Applied"
//                                   : u.status === "Failed"   ? "Retry"
//                                   : "Apply Automatically"}
//                               </button>

//                               {u.status === "Failed" && (
//                                 <p className="text-xs text-red-300">⚠️ Failed — see Active Submissions for details.</p>
//                               )}
//                             </div>
//                           );
//                         })}
//                       </div>
//                     )}
//                   </div>

//                   {/* Sticky deadline panel */}
//                   {dbPopulated && !loadingApi && (
//                     <div className="hidden lg:block w-80 shrink-0">
//                       <div className="sticky top-8 bg-white/5 border border-white/10 rounded-[2rem] p-6 shadow-2xl">
//                         <UpcomingDeadlines universities={universities} />
//                       </div>
//                     </div>
//                   )}
//                 </div>

//                 {/* Mobile deadline panel */}
//                 {dbPopulated && !loadingApi && (
//                   <div className="lg:hidden mt-12 bg-white/5 border border-white/10 rounded-[2rem] p-6">
//                     <UpcomingDeadlines universities={universities} />
//                   </div>
//                 )}
//               </div>
//             )}

//             {/* DEADLINES TAB */}
//             {tab === "deadlines" && (
//               <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
//                 <div className="flex items-center justify-between mb-3">
//                   <h1 className="text-4xl font-bold text-white">Deadlines</h1>
//                   <button
//                     onClick={() => fileInputRef.current.click()}
//                     disabled={uploading}
//                     className="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-sm font-semibold border border-white/10 transition-all disabled:opacity-40"
//                   >
//                     {uploading ? "Uploading…" : "📤 Update Excel"}
//                   </button>
//                 </div>
//                 <p className="text-white/50 text-lg mb-12">Live data from your uploaded Excel file.</p>

//                 {loadingApi ? (
//                   <div className="flex items-center gap-3 text-white/40 py-20">
//                     <div className="w-5 h-5 border-2 border-white/20 border-t-white/60 rounded-full animate-spin" />
//                     Loading…
//                   </div>
//                 ) : !dbPopulated ? (
//                   <EmptyDeadlinesPrompt onUpload={handleExcelUpload} uploading={uploading} error={uploadErr} isAdmin={isAdmin} />
//                 ) : (
//                   <>
//                     <div className="max-w-2xl bg-white/5 border border-white/10 rounded-[2rem] p-8 shadow-2xl">
//                       <UpcomingDeadlines universities={universities} />
//                     </div>
//                     <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-10 max-w-2xl">
//                       {[
//                         { label: "Critical", days: "≤ 14 days", color: "bg-red-500/10 border-red-500/20 text-red-400" },
//                         { label: "High",     days: "≤ 30 days", color: "bg-orange-500/10 border-orange-500/20 text-orange-400" },
//                         { label: "Medium",   days: "≤ 60 days", color: "bg-yellow-500/10 border-yellow-500/20 text-yellow-400" },
//                         { label: "Low",      days: "60+ days",  color: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" },
//                       ].map(p => (
//                         <div key={p.label} className={`rounded-2xl p-4 border text-center ${p.color}`}>
//                           <p className="font-black text-sm uppercase tracking-wider">{p.label}</p>
//                           <p className="text-xs opacity-70 mt-1">{p.days}</p>
//                         </div>
//                       ))}
//                     </div>
//                   </>
//                 )}
//               </div>
//             )}

//             {/* APPLICATIONS TAB */}
//             {tab === "applications" && (
//               <div className="animate-in fade-in duration-500">
//                 <h1 className="text-3xl font-bold mb-3 text-white">Active Submissions</h1>
//                 <p className="text-white/50 mb-10">Track and manage your automated university applications.</p>

//                 <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
//                   {universities.filter(u => u.status === "Applied" || u.status === "Failed").map(u => (
//                     <div key={u.id}
//                       className={`rounded-[2rem] p-8 flex flex-col gap-4 border-l-4 transition-all
//                         ${u.status === "Applied"
//                           ? "bg-white/5 border border-white/10 border-l-emerald-500"
//                           : "bg-red-950/20 border border-red-900/30 border-l-red-500"}`}>
//                       <div className="flex items-center justify-between mb-2">
//                         <div>
//                           <h3 className="text-lg font-bold text-white">{u.name}</h3>
//                           {u.program && <p className="text-xs text-white/30 mt-0.5">{u.program}</p>}
//                         </div>
//                         <span className={`text-[10px] px-3 py-1.5 rounded-lg uppercase font-black tracking-widest ${statusBadgeClass(u.status)}`}>
//                           {u.status}
//                         </span>
//                       </div>

//                       <div className="text-xs text-white/40 space-y-1">
//                         <p>Submitted: {u.lastUpdate || "N/A"}</p>
//                         <p>ID: {u.university_id?.toUpperCase()}</p>
//                       </div>

//                       {u.status === "Failed" && u.error && (
//                         <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 space-y-2">
//                           <p className="text-sm font-semibold text-red-300">❌ Error</p>
//                           <p className="text-xs text-red-200">{u.error}</p>
//                           {u.errorDetails && (
//                             <details className="text-xs text-red-100/70">
//                               <summary className="cursor-pointer font-semibold text-red-200 mb-2">Technical Details</summary>
//                               <pre className="bg-black/30 p-2 rounded text-[10px] overflow-auto max-h-40">
//                                 {typeof u.errorDetails === "string" ? u.errorDetails : JSON.stringify(u.errorDetails, null, 2)}
//                               </pre>
//                             </details>
//                           )}
//                         </div>
//                       )}

//                       {u.status === "Applied" && u.screenshots?.length > 0 && (
//                         <div className="space-y-2">
//                           <p className="text-xs text-white/50 font-semibold">📸 Screenshots ({u.screenshots.length})</p>
//                           {u.screenshots.map((img, i) => (
//                             <div key={i} className="space-y-1">
//                               <p className="text-[10px] text-white/30">Step {i + 1}</p>
//                               <img
//                                 src={`http://127.0.0.1:8000/media/screenshots/${img.split("\\").pop()}`}
//                                 alt={`step-${i}`}
//                                 className="rounded-xl border border-white/10 w-full hover:border-white/30 transition-all cursor-pointer"
//                               />
//                             </div>
//                           ))}
//                         </div>
//                       )}

//                       {u.status === "Applied" && u.stepsCompleted > 0 && (
//                         <p className="text-xs text-white/40">✓ Completed {u.stepsCompleted} steps</p>
//                       )}

//                       <div className="flex gap-2 mt-4">
//                         <button
//                           onClick={() => navigate("/apply", { state: { edit: true, universityId: u.university_id } })}
//                           className="flex-1 py-3 rounded-xl border border-white/10 hover:bg-white/5 transition-all text-sm font-bold text-white"
//                         >
//                           View Application
//                         </button>
//                         {u.status === "Failed" && (
//                           <button
//                             onClick={() => runAutomation(u)}
//                             className="flex-1 py-3 rounded-xl bg-red-500/20 border border-red-400/50 hover:bg-red-500/30 transition-all text-sm font-bold text-red-200"
//                           >
//                             Retry
//                           </button>
//                         )}
//                       </div>
//                     </div>
//                   ))}
//                 </div>

//                 {universities.filter(u => u.status === "Applied" || u.status === "Failed").length === 0 && (
//                   <div className="text-center py-12">
//                     <p className="text-white/40">No applications submitted yet.</p>
//                     <p className="text-white/20 text-sm mt-1">Go to Home and click "Apply Automatically" to get started.</p>
//                   </div>
//                 )}
//               </div>
//               )}

//             {/* CHATBOT TAB */}
//             {tab === "chatbot" && (
//               <div className="h-[calc(100vh-14rem)] bg-white/5 border border-white/10 rounded-[2.5rem] overflow-hidden shadow-2xl">
//                 <Chatbot />
//               </div>
//             )}
//           </div>
//         </main>
//       </div>
//     </section>
//   );
// }
import React from "react";
import ReactDOM from "react-dom";
import { useNavigate } from "react-router-dom";
import { getSession, logout, updateSession } from "../utils/authStore";
import api from "../api/axios";
import Chatbot from "./Chatbot";
import UpcomingDeadlines from "./deadline";
import { API_BASE } from "../config";

const API = `${API_BASE}/api/deadlines`;

// ── tiny helpers ─────────────────────────────────────────────────────────────

function daysLeft(deadline) {
  const today = new Date(); today.setHours(0,0,0,0);
  const d = new Date(deadline); d.setHours(0,0,0,0);
  return Math.ceil((d - today) / 86400000);
}

function statusBadgeClass(status) {
  return {
    Pending:    "bg-yellow-400/10 text-yellow-400 border border-yellow-400/20",
    Processing: "bg-blue-400/10 text-blue-400 border border-blue-400/20",
    Applied:    "bg-green-400/10 text-green-400 border border-green-400/20",
    Failed:     "bg-red-400/10 text-red-400 border border-red-400/20",
  }[status] || "bg-white/10 text-white/50";
}

// ── Empty / upload prompt ─────────────────────────────────────────────────────

function EmptyDeadlinesPrompt({ onUpload, uploading, error, isAdmin }) {
  const fileRef = React.useRef();

  // Only admins can load university data; students just see that none is available yet
  if (!isAdmin) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center gap-6">
        <div className="w-20 h-20 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center text-4xl">
          📅
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">No universities available yet</h2>
          <p className="text-white/40 max-w-md">
            The admissions team hasn't published any universities or deadlines yet. Please check back soon.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-20 text-center gap-6">
      <div className="w-20 h-20 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center text-4xl">
        📅
      </div>
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">No deadlines in database</h2>
        <p className="text-white/40 max-w-md">
          Upload your <span className="text-white/70 font-mono text-sm">universities_deadlines.xlsx</span> file
          to populate the deadline tracker, or run:
        </p>
        <code className="mt-3 block text-xs bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-emerald-400 font-mono">
          python manage.py import_deadlines universities_deadlines.xlsx
        </code>
      </div>

      {error && (
        <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 max-w-md">
          ⚠️ {error}
        </p>
      )}

      <div className="flex flex-col sm:flex-row gap-3 items-center">
        <input
          ref={fileRef}
          type="file"
          accept=".xlsx,.xlsm"
          className="hidden"
          onChange={(e) => e.target.files[0] && onUpload(e.target.files[0])}
        />
        <button
          disabled={uploading}
          onClick={() => fileRef.current.click()}
          className="px-8 py-4 rounded-2xl bg-white text-[#0B0620] font-bold hover:bg-purple-100 transition-all shadow-lg active:scale-95 disabled:opacity-50 min-w-[200px]"
        >
          {uploading ? "Uploading…" : "Upload Excel File"}
        </button>
        <span className="text-white/30 text-sm">.xlsx files only</span>
      </div>
    </div>
  );
}

// ── Screenshot lightbox ───────────────────────────────────────────────────────

function ScreenshotLightbox({ src, onClose }) {
  React.useEffect(() => {
    const handler = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  return ReactDOM.createPortal(
    <div
      onClick={onClose}
      style={{
        position: "fixed", inset: 0, zIndex: 9999,
        display: "flex", alignItems: "center", justifyContent: "center",
        background: "rgba(0,0,0,0.88)",
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{ position: "relative", maxWidth: "90vw", maxHeight: "90vh" }}
      >
        <button
          onClick={onClose}
          style={{
            position: "absolute", top: "-14px", right: "-14px",
            width: "32px", height: "32px", borderRadius: "50%",
            background: "rgba(255,255,255,0.12)", border: "1px solid rgba(255,255,255,0.2)",
            color: "#fff", fontSize: "18px", cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}
        >
          ✕
        </button>
        <img
          src={src}
          alt="Screenshot"
          style={{
            display: "block", borderRadius: "16px",
            maxHeight: "85vh", maxWidth: "90vw",
            objectFit: "contain",
            border: "1px solid rgba(255,255,255,0.1)",
          }}
        />
      </div>
    </div>,
    document.body
  );
}

// ── Tab error boundary ───────────────────────────────────────────────────────

class TabErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(error) { return { error }; }
  componentDidCatch(error, info) { console.error("Tab crashed:", error, info); }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: "2rem", background: "rgba(220,38,38,0.1)", border: "1px solid rgba(220,38,38,0.3)", borderRadius: "1rem", color: "#fca5a5" }}>
          <p style={{ fontWeight: 700, marginBottom: "0.5rem" }}>Something went wrong in this tab:</p>
          <pre style={{ fontSize: "12px", overflowX: "auto", whiteSpace: "pre-wrap" }}>{this.state.error.message}</pre>
          <pre style={{ fontSize: "11px", overflowX: "auto", whiteSpace: "pre-wrap", marginTop: "0.5rem", opacity: 0.6 }}>{this.state.error.stack}</pre>
          <button
            onClick={() => this.setState({ error: null })}
            style={{ marginTop: "1rem", padding: "0.5rem 1rem", background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.2)", borderRadius: "0.5rem", color: "#fff", cursor: "pointer" }}
          >
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ── Main dashboard ────────────────────────────────────────────────────────────

export default function StudentDashboard() {
  const navigate = useNavigate();
  const session  = getSession();

  const [tab, setTab]                 = React.useState("home");
  const [apiUnis, setApiUnis]         = React.useState([]);
  const [appUnis, setAppUnis]         = React.useState([]);
  const [dbPopulated, setDbPopulated] = React.useState(true);
  const [loadingApi, setLoadingApi]   = React.useState(true);
  const [uploadErr, setUploadErr]     = React.useState("");
  const [uploading, setUploading]     = React.useState(false);
  const [lightboxSrc, setLightboxSrc] = React.useState(null);
  const [menuOpen, setMenuOpen]       = React.useState(false);  // mobile sidebar
  const fileInputRef = React.useRef();
  const [displayName, setDisplayName] = React.useState(session?.name || "");
  const [isAdmin, setIsAdmin]         = React.useState(!!session?.isAdmin);

  // Refresh name and role from the server (older sessions lack them, and roles can change)
  React.useEffect(() => {
    if (!session) return;
    api.get("/auth/me/")
      .then(({ data }) => {
        updateSession({ name: data?.name || session.name || "", isAdmin: !!data?.is_admin });
        if (data?.name) setDisplayName(data.name);
        setIsAdmin(!!data?.is_admin);
      })
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const storageKey = session
    ? `aikapply.appstatus.${session.username}`
    : "aikapply.appstatus.anonymous";

  // ── load local apply-status from localStorage ──────────────────────────────
  React.useEffect(() => {
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw) setAppUnis(JSON.parse(raw));
    } catch {}
  }, [storageKey]);

  React.useEffect(() => {
    try { localStorage.setItem(storageKey, JSON.stringify(appUnis)); } catch {}
  }, [appUnis, storageKey]);

  // ── fetch deadlines from API ───────────────────────────────────────────────
  const fetchDeadlines = React.useCallback(async () => {
    setLoadingApi(true);
    try {
      const res  = await fetch(`${API}/summary/`);
      const data = await res.json();
      if (data.universities && data.universities.length > 0) {
        setDbPopulated(true);
        setApiUnis(data.universities);
        setAppUnis(prev => {
          const existingIds = new Set(prev.map(u => u.university_id));
          const fresh = data.universities
            .filter(u => !existingIds.has(u.university_id))
            .map(u => ({ university_id: u.university_id, status: "Pending", lastUpdate: "—", screenshots: [], stepsCompleted: 0 }));
          return [...prev, ...fresh];
        });
      } else {
        setDbPopulated(false);
      }
    } catch (e) {
      console.error("API fetch failed:", e);
      setDbPopulated(false);
    } finally {
      setLoadingApi(false);
    }
  }, []);

  React.useEffect(() => { fetchDeadlines(); }, [fetchDeadlines]);

  // ── merge API data + local status into one list ────────────────────────────
  const universities = React.useMemo(() => {
    return apiUnis.map(apiU => {
      const local = appUnis.find(a => a.university_id === apiU.university_id) || {};
      return {
        ...apiU,
        id:             apiU.university_id,
        status:         local.status         || "Pending",
        lastUpdate:     local.lastUpdate     || "—",
        screenshots:    local.screenshots    || [],
        stepsCompleted: local.stepsCompleted || 0,
        error:          local.error          || null,
        errorDetails:   local.errorDetails   || null,
        mappingFile:    local.mappingFile    || null,
        applicationId:  local.applicationId  || null,
      };
    });
  }, [apiUnis, appUnis]);

  // ── apply automation ───────────────────────────────────────────────────────
  const runAutomation = async (u) => {
    setAppUnis(prev => prev.map(a =>
      a.university_id === u.university_id
        ? { ...a, status: "Processing", error: null, errorDetails: null }
        : a
    ));
    try {
      const res  = await fetch(`${API_BASE}/api/automation-pipeline/apply/`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body:    JSON.stringify({ url: u.website }),
      });
      const data = await res.json();

      // Online demo host can't run the browser automation — not the student's failure
      if (data.error === "auto_apply_disabled") {
        setAppUnis(prev => prev.map(a =>
          a.university_id === u.university_id ? { ...a, status: "Pending" } : a
        ));
        alert(`ℹ️ ${data.message}`);
        return;
      }

      if (res.status === 404 && data.error === "profile_missing") {
        setAppUnis(prev => prev.map(a =>
          a.university_id === u.university_id
            ? { ...a, status: "Failed", error: data.message, lastUpdate: new Date().toLocaleString() }
            : a
        ));
        alert("⚠️ Please complete your application form before using auto-apply.");
        return;
      }

      if (!res.ok || data.status === "failed") {
        throw new Error(data.message || data.details || "Automation failed");
      }

      setAppUnis(prev => prev.map(a =>
        a.university_id === u.university_id
          ? {
              ...a,
              status:         "Applied",
              screenshots:    data.screenshots    || [],
              stepsCompleted: data.completed_steps || 0,
              lastUpdate:     new Date().toLocaleString(),
              error:          null,
              errorDetails:   null,
              mappingFile:    data.mapping_file,
              applicationId:  data.application_id,
            }
          : a
      ));
    } catch (err) {
      setAppUnis(prev => prev.map(a =>
        a.university_id === u.university_id
          ? { ...a, status: "Failed", error: err.message, errorDetails: err.toString(), lastUpdate: new Date().toLocaleString() }
          : a
      ));
    }
  };

  // ── upload Excel ───────────────────────────────────────────────────────────
  const handleExcelUpload = async (file) => {
    setUploading(true);
    setUploadErr("");
    const form = new FormData();
    form.append("file", file);
    try {
      const res  = await fetch(`${API}/upload/`, { method: "POST", body: form, credentials: "include" });
      const data = await res.json();
      if (res.status === 401 || res.status === 403) throw new Error("Only admins can upload university data.");
      if (data.status === "error") throw new Error(data.errors?.[0] || "Upload failed");
      await fetchDeadlines();
    } catch (e) {
      setUploadErr(e.message);
    } finally {
      setUploading(false);
    }
  };

  const onLogout = () => { logout(); navigate("/login", { replace: true }); };

  const criticalCount = universities.filter(u => {
    const d = daysLeft(u.deadline);
    return d >= 0 && d <= 14;
  }).length;

  // ── nav items ──────────────────────────────────────────────────────────────
  // Items with `path` open another page; the rest switch dashboard tabs.
  const navItems = [
    { key: "home",         label: "Home" },
    { key: "applications", label: "My Applications" },
    { key: "deadlines",    label: "Deadlines", badge: criticalCount > 0 ? `${criticalCount} urgent` : null },
    { key: "form",         label: "Application Form", path: "/my-application" },
  ];

  const aiNavItems = [
    { key: "chatbot",   label: "AI Chatbot" },
    { key: "recommend", label: "University Recommender", path: "/recommend" },
  ];

  const renderNavItem = ({ key, label, badge, path }) => (
    <button
      key={key}
      onClick={() => { setMenuOpen(false); path ? navigate(path) : setTab(key); }}
      className={`w-full text-left px-5 py-3.5 rounded-xl transition-all duration-200 flex items-center justify-between
        ${!path && tab === key ? "bg-white text-[#0B0620] font-bold shadow-xl" : "text-white/60 hover:bg-white/10 hover:text-white"}`}
    >
      <span>{label}</span>
      {badge && (
        <span className={`text-[10px] font-black px-2 py-0.5 rounded-md
          ${tab === key ? "bg-red-500 text-white" : "bg-red-500/20 text-red-400 border border-red-500/30"}`}>
          {badge}
        </span>
      )}
    </button>
  );

  // ── render ─────────────────────────────────────────────────────────────────
  return (
    <>
    <section className="min-h-screen bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] pt-20">

      <div className="flex flex-col md:flex-row w-full min-h-[calc(100vh-5rem)]">

        {/* ── MOBILE MENU TOGGLE ── */}
        <div className="md:hidden px-4 pt-4">
          <button
            onClick={() => setMenuOpen(o => !o)}
            aria-expanded={menuOpen}
            className="w-full flex items-center justify-between px-5 py-3.5 rounded-xl bg-white/5 border border-white/10 text-white font-semibold"
          >
            <span className="truncate">{[...navItems, ...aiNavItems].find(n => n.key === tab)?.label || "Menu"}</span>
            <span className="text-white/60 text-sm shrink-0 ml-3">{menuOpen ? "✕ Close" : "☰ Menu"}</span>
          </button>
        </div>

        {/* ── SIDEBAR ── */}
        <aside className={`${menuOpen ? "flex" : "hidden"} md:flex w-auto md:w-72 mx-4 mt-2 md:m-0 rounded-2xl md:rounded-none bg-white/5 backdrop-blur-md border border-white/10 md:border-0 md:border-r p-4 md:p-6 flex-col shrink-0`}>
          <div className="mb-6 md:mb-8">
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
              <p className="text-[10px] font-bold text-white/40 uppercase tracking-[0.2em] mb-1">Active Session</p>
              <div className="text-base font-semibold text-white truncate">
                {session ? (displayName || session.username) : "Guest User"}
              </div>
            </div>
          </div>

          <nav className="space-y-1 flex-1">
            <p className="px-4 text-[10px] font-bold text-white/30 uppercase mb-3 tracking-widest">Navigation</p>
            {navItems.map(renderNavItem)}

            <div className="pt-6 pb-2">
              <p className="px-4 text-[10px] font-bold text-white/30 uppercase mb-3 tracking-widest">AI Services</p>
            </div>
            {aiNavItems.map(renderNavItem)}

            {/* Upload Excel shortcut — admins only */}
            {isAdmin && (
            <div className="mt-6 pt-4 border-t border-white/5">
              <p className="px-4 text-[10px] font-bold text-white/30 uppercase mb-3 tracking-widest">Admin · University Data</p>
              <input ref={fileInputRef} type="file" accept=".xlsx,.xlsm" className="hidden"
                onChange={e => e.target.files[0] && handleExcelUpload(e.target.files[0])} />
              <button
                onClick={() => fileInputRef.current.click()}
                disabled={uploading}
                className="w-full text-left px-5 py-3.5 rounded-xl text-white/60 hover:bg-white/10 hover:text-white transition-all font-medium border border-white/5 hover:border-white/20 disabled:opacity-40"
              >
                {uploading ? "⏳ Uploading…" : "📤 Upload Excel"}
              </button>
              {!dbPopulated && !loadingApi && (
                <p className="mt-2 px-2 text-[11px] text-red-400">
                  ⚠ No deadline data — upload your Excel file
                </p>
              )}
              {uploadErr && (
                <p className="mt-2 px-2 text-[11px] text-red-400">⚠ {uploadErr}</p>
              )}
              <a href={`${API_BASE}/admin/deadline/university/`} target="_blank" rel="noreferrer"
                className="block mt-2 px-5 py-3 rounded-xl text-white/60 hover:bg-white/10 hover:text-white transition-all text-sm border border-white/5 hover:border-white/20">
                ✏️ Edit / delete universities
              </a>
            </div>
            )}

            <div className="mt-6 pt-4 border-t border-white/5">
              <button onClick={onLogout}
                className="w-full text-left px-5 py-3 rounded-xl text-red-400 hover:bg-red-400/10 transition-all text-sm font-semibold">
                Log Out
              </button>
            </div>
          </nav>
        </aside>

        {/* ── MAIN CONTENT ── */}
        <main className="flex-1 min-w-0 px-4 py-6 sm:p-8 md:p-12 lg:p-16 overflow-y-auto">
          <div className="max-w-[1400px]">

            {/* HOME */}
            {tab === "home" && (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex flex-col lg:flex-row lg:gap-16">
                  <div className="flex-1">
                    <h1 className="text-3xl sm:text-4xl font-bold mb-3 text-white">Available Universities</h1>
                    <p className="text-white/50 text-base sm:text-lg mb-8 sm:mb-12">
                      Select an institution to start your automated application process.
                    </p>

                    {loadingApi ? (
                      <div className="flex items-center gap-3 text-white/40 py-20">
                        <div className="w-5 h-5 border-2 border-white/20 border-t-white/60 rounded-full animate-spin" />
                        Loading universities…
                      </div>
                    ) : !dbPopulated ? (
                      <EmptyDeadlinesPrompt
                        onUpload={handleExcelUpload}
                        uploading={uploading}
                        error={uploadErr}
                        isAdmin={isAdmin}
                      />
                    ) : (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 sm:gap-8">
                        {universities.map((u) => {
                          const d = daysLeft(u.deadline);
                          const urgentColor = d <= 14 ? "text-red-400" : d <= 30 ? "text-orange-400" : "text-white/80";
                          return (
                            <div key={u.id}
                              className="group bg-white/5 border border-white/10 rounded-[2rem] p-6 sm:p-8 flex flex-col gap-6 hover:bg-white/[0.08] hover:border-white/20 transition-all duration-300 shadow-2xl">
                              <div className="flex items-start justify-between gap-3">
                                <div className="min-w-0">
                                  <h3 className="text-xl font-bold text-white break-words">{u.name}</h3>
                                  {u.program && <p className="text-sm text-white/40 mt-1">{u.program}</p>}
                                </div>
                                <span className={`text-[10px] px-3 py-1.5 rounded-lg uppercase font-black tracking-widest shrink-0 ${statusBadgeClass(u.status)}`}>
                                  {u.status}
                                </span>
                              </div>

                              <div className="text-sm text-white/40 space-y-2 py-4 border-y border-white/5">
                                <div className="flex justify-between">
                                  <span>Deadline</span>
                                  <span className="text-white/80 font-medium">{u.deadline}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Days Left</span>
                                  <span className={`font-bold ${urgentColor}`}>{Math.max(0, d)}d</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Priority</span>
                                  <span className={`font-bold capitalize ${urgentColor}`}>{u.priority}</span>
                                </div>
                                {u.city && (
                                  <div className="flex justify-between">
                                    <span>City</span>
                                    <span className="text-white/80">{u.city}</span>
                                  </div>
                                )}
                              </div>

                              <button
                                disabled={u.status === "Processing"}
                                onClick={() => runAutomation(u)}
                                className="w-full py-4 rounded-2xl bg-white text-[#0B0620] font-bold hover:bg-purple-100 transition-all shadow-lg active:scale-95 disabled:opacity-50"
                              >
                                {u.status === "Processing" ? "Applying…"
                                  : u.status === "Applied"  ? "✓ Applied"
                                  : u.status === "Failed"   ? "Retry"
                                  : "Apply Automatically"}
                              </button>

                              {u.status === "Failed" && (
                                <p className="text-xs text-red-300">⚠️ Failed — see My Applications for details.</p>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>

                  {/* Sticky deadline panel */}
                  {dbPopulated && !loadingApi && (
                    <div className="hidden lg:block w-80 shrink-0">
                      <div className="sticky top-8 bg-white/5 border border-white/10 rounded-[2rem] p-6 shadow-2xl">
                        <UpcomingDeadlines universities={universities} />
                      </div>
                    </div>
                  )}
                </div>

                {/* Mobile deadline panel */}
                {dbPopulated && !loadingApi && (
                  <div className="lg:hidden mt-8 sm:mt-12 bg-white/5 border border-white/10 rounded-[2rem] p-5 sm:p-6">
                    <UpcomingDeadlines universities={universities} />
                  </div>
                )}
              </div>
            )}

            {/* DEADLINES TAB */}
            {tab === "deadlines" && (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
                  <h1 className="text-3xl sm:text-4xl font-bold text-white">Deadlines</h1>
                  {isAdmin && (
                    <button
                      onClick={() => fileInputRef.current.click()}
                      disabled={uploading}
                      className="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-sm font-semibold border border-white/10 transition-all disabled:opacity-40"
                    >
                      {uploading ? "Uploading…" : "📤 Update Excel"}
                    </button>
                  )}
                </div>
                <p className="text-white/50 text-base sm:text-lg mb-8 sm:mb-12">Upcoming admission deadlines for all listed universities.</p>

                {loadingApi ? (
                  <div className="flex items-center gap-3 text-white/40 py-20">
                    <div className="w-5 h-5 border-2 border-white/20 border-t-white/60 rounded-full animate-spin" />
                    Loading…
                  </div>
                ) : !dbPopulated ? (
                  <EmptyDeadlinesPrompt onUpload={handleExcelUpload} uploading={uploading} error={uploadErr} isAdmin={isAdmin} />
                ) : (
                  <>
                    <div className="max-w-2xl bg-white/5 border border-white/10 rounded-[2rem] p-5 sm:p-8 shadow-2xl">
                      <UpcomingDeadlines universities={universities} />
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-10 max-w-2xl">
                      {[
                        { label: "Critical", days: "≤ 14 days", color: "bg-red-500/10 border-red-500/20 text-red-400" },
                        { label: "High",     days: "≤ 30 days", color: "bg-orange-500/10 border-orange-500/20 text-orange-400" },
                        { label: "Medium",   days: "≤ 60 days", color: "bg-yellow-500/10 border-yellow-500/20 text-yellow-400" },
                        { label: "Low",      days: "60+ days",  color: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" },
                      ].map(p => (
                        <div key={p.label} className={`rounded-2xl p-4 border text-center ${p.color}`}>
                          <p className="font-black text-sm uppercase tracking-wider">{p.label}</p>
                          <p className="text-xs opacity-70 mt-1">{p.days}</p>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )}

            {/* APPLICATIONS TAB */}
            {tab === "applications" && (
              <TabErrorBoundary>
              <div className="animate-in fade-in duration-500">
                <div className="mb-10">
                  <h1 className="text-3xl font-bold text-white mb-2">My Applications</h1>
                  <p className="text-white/50">Track every submission — applied, processing, and failed.</p>
                </div>

                {loadingApi ? (
                  <div className="flex items-center gap-3 text-white/40 py-20">
                    <div className="w-5 h-5 border-2 border-white/20 border-t-white/60 rounded-full animate-spin" />
                    Loading applications…
                  </div>
                ) : (
                  <>
                    {/* Stats strip */}
                    {universities.length > 0 && (
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
                        {[
                          {
                            label: "Total",
                            value: universities.length,
                            color: "bg-white/5 border-white/10 text-white",
                          },
                          {
                            label: "Applied",
                            value: universities.filter(u => u.status === "Applied").length,
                            color: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400",
                          },
                          {
                            label: "Processing",
                            value: universities.filter(u => u.status === "Processing").length,
                            color: "bg-blue-500/10 border-blue-500/20 text-blue-400",
                          },
                          {
                            label: "Failed",
                            value: universities.filter(u => u.status === "Failed").length,
                            color: "bg-red-500/10 border-red-500/20 text-red-400",
                          },
                        ].map(s => (
                          <div key={s.label} className={`rounded-2xl p-5 border text-center ${s.color}`}>
                            <p className="text-3xl font-black">{s.value}</p>
                            <p className="text-xs uppercase tracking-widest font-bold mt-1 opacity-70">{s.label}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                      {universities
                        .filter(u => ["Applied", "Failed", "Processing"].includes(u.status))
                        .map(u => {
                          const screenshots = (u.screenshots || []).map(img => {
                            const url = typeof img === "string" ? img : img?.url;
                            if (!url) return null;
                            return url.startsWith("http")
                              ? url
                              : `${API_BASE}${url}`;
                          }).filter(Boolean);

                          return (
                            <div
                              key={u.id}
                              className={`rounded-[2rem] flex flex-col overflow-hidden border transition-all duration-300
                                ${u.status === "Applied"
                                  ? "bg-white/5 border-white/10"
                                  : u.status === "Processing"
                                  ? "bg-blue-950/20 border-blue-900/30"
                                  : "bg-red-950/20 border-red-900/30"}`}
                            >
                              {/* Card top accent bar */}
                              <div className={`h-1 w-full
                                ${u.status === "Applied"    ? "bg-emerald-500"
                                : u.status === "Processing" ? "bg-blue-400"
                                :                            "bg-red-500"}`}
                              />

                              <div className="p-5 sm:p-7 flex flex-col gap-5 flex-1">

                                {/* Header */}
                                <div className="flex items-start justify-between gap-3">
                                  <div className="flex-1 min-w-0">
                                    <h3 className="text-lg font-bold text-white truncate">{u.name}</h3>
                                    {u.program && (
                                      <p className="text-xs text-white/30 mt-0.5 truncate">{u.program}</p>
                                    )}
                                  </div>
                                  <span className={`text-[10px] px-3 py-1.5 rounded-lg uppercase font-black tracking-widest shrink-0 ${statusBadgeClass(u.status)}`}>
                                    {u.status}
                                  </span>
                                </div>

                                {/* Processing state */}
                                {u.status === "Processing" && (
                                  <div className="flex items-center gap-3 bg-blue-500/10 border border-blue-500/20 rounded-2xl px-4 py-3">
                                    <div className="w-4 h-4 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin shrink-0" />
                                    <div>
                                      <p className="text-sm font-semibold text-blue-300">Automation running</p>
                                      <p className="text-xs text-blue-400/60 mt-0.5">This may take a minute…</p>
                                    </div>
                                  </div>
                                )}

                                {/* Meta info */}
                                <div className="bg-white/[0.04] rounded-2xl px-4 py-3 space-y-2 text-xs">
                                  <div className="flex justify-between">
                                    <span className="text-white/40">University ID</span>
                                    <span className="text-white/70 font-mono">{u.university_id?.toUpperCase()}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-white/40">Last updated</span>
                                    <span className="text-white/70">{u.lastUpdate || "—"}</span>
                                  </div>
                                  {u.applicationId && (
                                    <div className="flex justify-between">
                                      <span className="text-white/40">App ID</span>
                                      <span className="text-white/70 font-mono truncate max-w-[140px]">{u.applicationId}</span>
                                    </div>
                                  )}
                                  {u.stepsCompleted > 0 && (
                                    <div className="flex justify-between">
                                      <span className="text-white/40">Steps completed</span>
                                      <span className="text-emerald-400 font-semibold">✓ {u.stepsCompleted}</span>
                                    </div>
                                  )}
                                  {u.mappingFile && (
                                    <div className="flex justify-between">
                                      <span className="text-white/40">Mapping file</span>
                                      <span className="text-white/50 font-mono truncate max-w-[140px]">
                                        {u.mappingFile.split("/").pop()}
                                      </span>
                                    </div>
                                  )}
                                </div>

                                {/* Error block */}
                                {u.status === "Failed" && u.error && (
                                  <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 space-y-2">
                                    <p className="text-sm font-semibold text-red-300">❌ Error</p>
                                    <p className="text-xs text-red-200 leading-relaxed">{u.error}</p>
                                    {u.errorDetails && (
                                      <details className="text-xs text-red-100/60">
                                        <summary className="cursor-pointer font-semibold text-red-300 mb-2 hover:text-red-200 transition-colors">
                                          Technical details ▾
                                        </summary>
                                        <pre className="bg-black/30 p-3 rounded-xl text-[10px] overflow-auto max-h-36 mt-1">
                                          {typeof u.errorDetails === "string"
                                            ? u.errorDetails
                                            : JSON.stringify(u.errorDetails, null, 2)}
                                        </pre>
                                      </details>
                                    )}
                                  </div>
                                )}

                                {/* Screenshots */}
                                {u.status === "Applied" && screenshots.length > 0 && (
                                  <div className="space-y-3">
                                    <div className="flex items-center justify-between">
                                      <p className="text-xs font-semibold text-white/60 uppercase tracking-widest">
                                        Screenshots
                                      </p>
                                      <span className="text-[10px] bg-white/10 text-white/50 px-2 py-0.5 rounded-full">
                                        {screenshots.length}
                                      </span>
                                    </div>

                                    {/* Screenshot grid */}
                                    <div className={`grid gap-2 ${screenshots.length === 1 ? "grid-cols-1" : "grid-cols-2"}`}>
                                      {screenshots.map((src, i) => (
                                        <div
                                          key={i}
                                          className="relative group cursor-pointer rounded-xl overflow-hidden border border-white/10 hover:border-white/30 transition-all"
                                          onClick={() => setLightboxSrc(src)}
                                        >
                                          <img
                                            src={src}
                                            alt={`Step ${i + 1}`}
                                            className="w-full h-24 object-cover object-top transition-transform duration-300 group-hover:scale-105"
                                            onError={e => {
                                              e.currentTarget.parentElement.innerHTML =
                                                `<div class="w-full h-24 flex items-center justify-center bg-white/5 text-white/20 text-xs rounded-xl">Failed to load</div>`;
                                            }}
                                          />
                                          {/* Hover overlay */}
                                          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center">
                                            <span className="text-white text-xs font-semibold opacity-0 group-hover:opacity-100 transition-opacity bg-black/60 px-2 py-1 rounded-lg">
                                              Step {i + 1} · View
                                            </span>
                                          </div>
                                        </div>
                                      ))}
                                    </div>

                                    {/* If more than 4, show a count */}
                                    {screenshots.length > 4 && (
                                      <p className="text-[11px] text-white/30 text-center">
                                        Click any screenshot to view full size
                                      </p>
                                    )}
                                  </div>
                                )}

                                {/* No screenshots yet for applied */}
                                {u.status === "Applied" && screenshots.length === 0 && (
                                  <div className="flex items-center gap-2 text-white/20 text-xs bg-white/[0.03] rounded-xl px-4 py-3">
                                    <span>📷</span>
                                    <span>No screenshots captured</span>
                                  </div>
                                )}

                                {/* Action buttons */}
                                <div className="flex gap-2 mt-auto pt-2">
                                  <button
                                    onClick={() => navigate("/apply", { state: { edit: true, universityId: u.university_id } })}
                                    className="flex-1 py-3 rounded-xl border border-white/10 hover:bg-white/5 transition-all text-sm font-bold text-white"
                                  >
                                    View Form
                                  </button>
                                  {u.status === "Failed" && (
                                    <button
                                      onClick={() => runAutomation(u)}
                                      className="flex-1 py-3 rounded-xl bg-red-500/20 border border-red-400/40 hover:bg-red-500/30 transition-all text-sm font-bold text-red-300"
                                    >
                                      Retry
                                    </button>
                                  )}
                                  {u.status === "Applied" && screenshots.length > 0 && (
                                    <button
                                      onClick={() => setLightboxSrc(screenshots[0])}
                                      className="flex-1 py-3 rounded-xl bg-emerald-500/10 border border-emerald-400/30 hover:bg-emerald-500/20 transition-all text-sm font-bold text-emerald-300"
                                    >
                                      View Proof
                                    </button>
                                  )}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                    </div>

                    {/* Empty state */}
                    {universities.filter(u => ["Applied", "Failed", "Processing"].includes(u.status)).length === 0 && (
                      <div className="flex flex-col items-center justify-center py-24 text-center gap-5">
                        <div className="w-20 h-20 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center text-4xl">
                          📋
                        </div>
                        <div>
                          <p className="text-white/50 text-lg font-semibold">No applications yet</p>
                          <p className="text-white/25 text-sm mt-1">
                            Go to Home and click "Apply Automatically" on any university to get started.
                          </p>
                        </div>
                        <button
                          onClick={() => setTab("home")}
                          className="px-6 py-3 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10 text-white text-sm font-semibold transition-all"
                        >
                          Go to Home →
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
              </TabErrorBoundary>
            )}

            {/* CHATBOT TAB */}
            {tab === "chatbot" && (
              <div className="h-[calc(100dvh-12rem)] md:h-[calc(100vh-14rem)] min-h-[420px] bg-white/5 border border-white/10 rounded-[1.5rem] md:rounded-[2.5rem] overflow-hidden shadow-2xl">
                <Chatbot />
              </div>
            )}

          </div>
        </main>
      </div>
    </section>
    {lightboxSrc && (
      <ScreenshotLightbox src={lightboxSrc} onClose={() => setLightboxSrc(null)} />
    )}
    </>
  );
}