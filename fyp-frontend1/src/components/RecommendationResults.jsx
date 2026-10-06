// import React from "react";
// import { useLocation, Link } from "react-router-dom";
// import { motion } from "framer-motion";

// // Dummy
// const getDummyUniversities = (userQuery) => [
//   {
//     id: 1,
//     name: "NUST - National University of Sciences & Technology",
//     city: "Islamabad",
//     province: "ICT",
//     matchScore: 98,
//     type: "Public",
//     fee: "150k - 200k / Semester",
//     reason: `Based on your ${userQuery?.interPercentage || 85}% marks and interest in ${(userQuery?.preferredField && userQuery.preferredField[0]) || "CS"}, NUST is the top choice for academic excellence.`,
//     pros: ["Top Global Ranking", "Research Facilities", "Strong Alumni"],
//     cons: ["High Merit", "Rigorous Workload"],
//     rank: "#1 in Engineering",
//     aiAnalysis: "Highly recommended for students seeking a competitive research environment."
//   },
//   {
//     id: 2,
//     name: "FAST NUCES",
//     city: "Lahore",
//     province: "Punjab",
//     matchScore: 92,
//     type: "Private",
//     fee: "250k - 300k / Semester",
//     reason: "Match found for your 'Market Ready' preference and high coding interest.",
//     pros: ["Best Job Placement", "Industry Recognition"],
//     cons: ["Strict Grading", "Limited Social Life"],
//     rank: "#2 in CS",
//     aiAnalysis: "Best choice if your primary goal is immediate employment after graduation."
//   }
// ];

// export default function RecommendationResults() {
//   const location = useLocation();
//   const query = location.state?.userData || location.state?.query;
//   const results = getDummyUniversities(query);

//   return (
//     <div className="min-h-screen bg-[#0B0620] text-white pt-28 pb-20 px-6">
//       <div className="max-w-6xl mx-auto">
//         <header className="mb-12 flex justify-between items-end">
//           <div>
//             <h1 className="text-4xl font-bold mb-2">AI Recommendations</h1>
//             <p className="text-white/60 text-lg">We found {results.length} universities matching your profile.</p>
//           </div>
//           <Link to="/recommend" className="text-purple-400 hover:underline">Edit Preferences</Link>
//         </header>

//         <div className="grid grid-cols-1 gap-8">
//           {results.map((uni, idx) => (
//             <motion.div
//               initial={{ opacity: 0, y: 20 }}
//               animate={{ opacity: 1, y: 0 }}
//               transition={{ delay: idx * 0.1 }}
//               key={uni.id}
//               className="bg-white/5 border border-white/10 rounded-3xl overflow-hidden hover:border-purple-500/50 transition-colors"
//             >
//               <div className="p-8">
//                 <div className="flex flex-wrap justify-between items-start gap-4 mb-6">
//                   <div>
//                     <span className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-bold uppercase tracking-wider mb-2 inline-block">
//                       {uni.type} • {uni.rank}
//                     </span>
//                     <h2 className="text-2xl md:text-3xl font-bold">{uni.name}</h2>
//                     <p className="text-white/50">{uni.city}, {uni.province}</p>
//                   </div>
//                   <div className="text-right">
//                     <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">
//                       {uni.matchScore}%
//                     </div>
//                     <div className="text-xs text-white/40 uppercase font-bold tracking-widest">Match Score</div>
//                   </div>
//                 </div>

//                 <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
//                   <div className="md:col-span-2 space-y-6">
//                     <div>
//                       <h4 className="text-purple-400 font-semibold mb-2">Recommendation Reason</h4>
//                       <p className="text-white/80 leading-relaxed">{uni.reason}</p>
//                     </div>
//                     <div className="p-4 bg-white/5 rounded-xl border border-white/5">
//                       <h4 className="text-sm font-bold text-white/40 uppercase mb-3">AI Analysis</h4>
//                       <p className="text-sm italic text-white/90">"{uni.aiAnalysis}"</p>
//                     </div>
//                   </div>

//                   <div className="space-y-4">
//                     <div className="bg-white/5 p-4 rounded-2xl">
//                       <h4 className="text-xs font-bold text-white/40 uppercase mb-2">Estimated Fee</h4>
//                       <p className="font-semibold">{uni.fee}</p>
//                     </div>
//                     <div className="flex gap-2">
//                       <div className="flex-1">
//                         <h4 className="text-green-400 text-xs font-bold mb-2">Pros</h4>
//                         <ul className="text-xs space-y-1 text-white/60">
//                           {uni.pros.map(p => <li key={p}>• {p}</li>)}
//                         </ul>
//                       </div>
//                       <div className="flex-1">
//                         <h4 className="text-red-400 text-xs font-bold mb-2">Cons</h4>
//                         <ul className="text-xs space-y-1 text-white/60">
//                           {uni.cons.map(c => <li key={c}>• {c}</li>)}
//                         </ul>
//                       </div>
//                     </div>
//                   </div>
//                 </div>
//               </div>
              
//               <div className="bg-white/5 px-8 py-4 flex justify-end gap-4 border-t border-white/5">
//                 <button className="px-6 py-2 rounded-full text-sm font-semibold hover:bg-white/5 transition">Download Details</button>
//                 <Link to="/apply" className="px-6 py-2 rounded-full bg-white text-black text-sm font-bold hover:bg-purple-100 transition">Apply Now</Link>
//               </div>
//             </motion.div>
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// }

import React, { useEffect, useState } from "react";
import { useLocation, Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../api/axios";
import { getSession } from "../utils/authStore";
import BackToDashboard from "./BackToDashboard";
import { downloadRecommendationPdf } from "../utils/recommendationPdf";

export default function RecommendationResults() {
  const location = useLocation();
  const navigate = useNavigate();
  const [checkingApplication, setCheckingApplication] = useState(false);
  const [savingPdf, setSavingPdf] = useState(null); // index of the card being saved

  const handleSavePdf = async (uni, idx) => {
    setSavingPdf(idx);
    try {
      await downloadRecommendationPdf(uni);
    } catch (err) {
      console.error("PDF generation failed:", err);
      alert("Could not create the PDF. Please try again.");
    } finally {
      setSavingPdf(null);
    }
  };

  // Students who already submitted the application form go to the dashboard
  // (where they can auto-apply); everyone else fills in the form first.
  const handleApplyNow = async () => {
    if (!getSession()) {
      navigate("/apply");
      return;
    }
    setCheckingApplication(true);
    try {
      await api.get("/student/profile/");
      navigate("/dashboard");
    } catch {
      navigate("/apply");
    } finally {
      setCheckingApplication(false);
    }
  };

  // Retrieve the actual recommendations sent from the RecommenderForm
  const results = location.state?.userData;

  // Security: If no results exist, send them back to the form
  useEffect(() => {
    if (!results) {
      navigate("/recommend");
    }
  }, [results, navigate]);

  if (!results || !Array.isArray(results)) {
    return (
      <div className="min-h-screen bg-[#0B0620] flex items-center justify-center text-white">
        <p className="animate-pulse">Loading your recommendations...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0620] text-white pt-28 pb-20 px-4 sm:px-6 font-poppins">
      <div className="max-w-6xl mx-auto">
        <BackToDashboard className="mb-6" />
        <header className="mb-8 sm:mb-12 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold mb-2 tracking-tight">AI Recommendations</h1>
            <p className="text-white/60 text-base sm:text-lg">
              We found {results.length} universities matching your profile.
            </p>
          </div>
          <Link to="/recommend" className="text-purple-400 hover:text-purple-300 transition font-medium flex items-center gap-2">
            <span>←</span> Edit Preferences
          </Link>
        </header>

        <div className="grid grid-cols-1 gap-6 sm:gap-8">
          {results.map((uni, idx) => (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              key={uni.id || idx} 
              className="bg-white/5 border border-white/10 rounded-3xl overflow-hidden hover:border-purple-500/50 transition-all duration-300 shadow-xl"
            >
              <div className="p-5 sm:p-8">
                <div className="flex flex-wrap justify-between items-start gap-4 mb-6">
                  <div className="min-w-0">
                    <span className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-bold uppercase tracking-wider mb-2 inline-block">
                      {uni.type} • {uni.rank}
                    </span>
                    <h2 className="text-2xl md:text-3xl font-bold tracking-tight">{uni.name}</h2>
                    <p className="text-white/50">{uni.city}, {uni.province}</p>
                  </div>
                  <div className="text-left sm:text-right">
                    <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">
                      {uni.matchScore}%
                    </div>
                    <div className="text-xs text-white/40 uppercase font-bold tracking-widest">Match Score</div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                  <div className="md:col-span-2 space-y-6">
                    <div>
                      <h4 className="text-purple-400 font-semibold mb-2">Recommendation Reason</h4>
                      <p className="text-white/80 leading-relaxed">
                        {uni.reason}
                      </p>
                    </div>
                    
                    {/* AI Analysis section is dynamic from Gemini */}
                    {uni.aiAnalysis && (
                      <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                        <h4 className="text-sm font-bold text-white/40 uppercase mb-3 tracking-widest">AI Deep Analysis</h4>
                        <p className="text-sm italic text-white/90 leading-relaxed">"{uni.aiAnalysis}"</p>
                      </div>
                    )}
                  </div>

                  <div className="space-y-4">
                    <div className="bg-white/5 p-4 rounded-2xl border border-white/5">
                      <h4 className="text-xs font-bold text-white/40 uppercase mb-2">Estimated Fee</h4>
                      <p className="font-semibold text-indigo-200">{uni.fee}</p>
                    </div>
                    
                    <div className="flex gap-4">
                      <div className="flex-1">
                        <h4 className="text-green-400 text-xs font-bold mb-2 uppercase tracking-tighter">Pros</h4>
                        <ul className="text-xs space-y-2 text-white/60">
                          {uni.pros?.map((p, i) => <li key={i} className="flex gap-2"><span>•</span>{p}</li>)}
                        </ul>
                      </div>
                      <div className="flex-1">
                        <h4 className="text-red-400 text-xs font-bold mb-2 uppercase tracking-tighter">Cons</h4>
                        <ul className="text-xs space-y-2 text-white/60">
                          {uni.cons?.map((c, i) => <li key={i} className="flex gap-2"><span>•</span>{c}</li>)}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white/5 px-8 py-4 flex justify-end gap-4 border-t border-white/5 items-center">
                <button
                  type="button"
                  onClick={() => handleSavePdf(uni, idx)}
                  disabled={savingPdf === idx}
                  className="px-6 py-2 rounded-full text-sm font-semibold hover:bg-white/10 transition-all border border-transparent hover:border-white/10 disabled:opacity-60"
                >
                  {savingPdf === idx ? "Saving…" : "Save PDF"}
                </button>
                <button
                  type="button"
                  onClick={handleApplyNow}
                  disabled={checkingApplication}
                  className="px-8 py-2 rounded-full bg-white text-black text-sm font-black hover:bg-purple-100 transition-all shadow-lg active:scale-95 disabled:opacity-60"
                >
                  {checkingApplication ? "Checking…" : "Apply Now"}
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}