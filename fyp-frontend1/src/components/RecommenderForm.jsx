// import React, { useState, useMemo } from "react";
// import { motion, AnimatePresence } from "framer-motion";
// import { useNavigate } from "react-router-dom";

// const stepTitles = ["Basic Information", "Preferences", "Academic & Budget", "Final Requirements"];

// export default function RecommenderForm() {
//   const navigate = useNavigate();
//   const [step, setStep] = useState(0);

//   const [data, setData] = useState({
//     name: "", email: "", phone: "", currentCity: "", currentProvince: "",
//     canMove: false,
//     preferredCities: [],
//     interests: [],
//     preferredField: [],
//     interPercentage: "",
//     feeAffordability: "Medium (50k to 150k)",
//     scholarshipRequired: false,
//     uniType: "Any",
//     campusFacilities: [],
//     languagePreference: "English",
//     additionalRequirements: ""
//   });

//   const [tagInputs, setTagInputs] = useState({
//     cities: "", interests: "", fields: "", facilities: ""
//   });

//   const isStepValid = useMemo(() => {
//     const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
//     const alphaRegex = /^[a-zA-Z\s]+$/;
//     const phoneRegex = /^\d{11}$/;

//     switch (step) {
//       case 0:
//         return (
//           data.name.trim().length >= 3 && alphaRegex.test(data.name) &&
//           emailRegex.test(data.email) &&
//           phoneRegex.test(data.phone) &&
//           data.currentCity.trim().length >= 3 && alphaRegex.test(data.currentCity) &&
//           data.currentProvince.trim().length >= 3 && alphaRegex.test(data.currentProvince)
//         );
//       case 1:
//         const citiesValid = data.canMove ? data.preferredCities.length > 0 : true;
//         return (
//           citiesValid &&
//           data.interests.length > 0 &&
//           data.preferredField.length > 0
//         );
//       case 2:
//         const pct = parseFloat(data.interPercentage);
//         return !isNaN(pct) && pct >= 0 && pct <= 100;
//       case 3:
//         return data.campusFacilities.length > 0;
//       default:
//         return false;
//     }
//   }, [data, step]);

//   const addTag = (field, value, inputKey) => {
//     if (value.trim() && !data[field].includes(value.trim())) {
//       setData({ ...data, [field]: [...data[field], value.trim()] });
//       setTagInputs({ ...tagInputs, [inputKey]: "" });
//     }
//   };

//   const removeTag = (field, tagToRemove) => {
//     setData({ ...data, [field]: data[field].filter((t) => t !== tagToRemove) });
//   };

//   const handleKeyDown = (e, field, inputKey) => {
//     if (e.key === "Enter") {
//       e.preventDefault();
//       addTag(field, e.target.value, inputKey);
//     }
//   };

//   const update = (field) => (e) => {
//     const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
//     setData((d) => ({ ...d, [field]: value }));
//   };

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     if (step < 3) {
//       setStep(step + 1);
//     } else {
//       navigate("/recommendations", { state: { userData: data } });
//     }
//   };

//   const CustomSelect = ({ label, value, onChange, options }) => (
//     <div className="w-full">
//       <label className="block text-sm mb-2 opacity-70">{label}</label>
//       <div className="relative">
//         <select
//           className="w-full p-3 rounded-md bg-white text-black outline-none appearance-none cursor-pointer pr-10"
//           value={value}
//           onChange={onChange}
//         >
//           {options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
//         </select>
//         <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none flex items-center">
//           <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
//           </svg>
//         </div>
//       </div>
//     </div>
//   );

//   return (
//     <section className="min-h-screen flex items-start justify-center bg-[#0B0620] pt-28 md:pt-36 pb-20">
//       <div className="w-full max-w-6xl px-6">
//         <div className="bg-white/10 border border-white/20 rounded-[24px] overflow-hidden backdrop-blur-md">
//           <div className="grid grid-cols-1 md:grid-cols-3">
//             <aside className="bg-[#4F3C61] p-8 text-white">
//               <div className="flex items-center gap-3 text-2xl font-semibold mb-10">
//                 <span className="inline-block w-8 h-8 rounded bg-white text-[#4F3C61] text-center leading-8 text-sm font-bold">2</span>
//                 Recommender
//               </div>
//               <ul className="space-y-6">
//                 {stepTitles.map((title, idx) => (
//                   <li key={title} className={`flex items-center gap-4 transition-opacity ${idx === step ? "opacity-100" : "opacity-40"}`}>
//                     <div className={`w-9 h-9 rounded-full border flex items-center justify-center ${idx === step ? "bg-white text-[#4F3C61]" : "border-white"}`}>
//                       {idx + 1}
//                     </div>
//                     <span className="text-sm font-medium">{title}</span>
//                   </li>
//                 ))}
//               </ul>
//             </aside>

//             <div className="md:col-span-2 p-8 md:p-12 text-white">
//               <h2 className="text-3xl font-bold mb-8">{stepTitles[step]}</h2>
//               <form onSubmit={handleSubmit}>
//                 <AnimatePresence mode="wait">
//                   {step === 0 && (
//                     <motion.div key="s0" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
//                       <div className="md:col-span-2">
//                         <label className="block text-sm mb-2 opacity-70">Full Name * (Letters only)</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.name} onChange={update("name")} placeholder="At least 3 letters" required minLength={3} pattern="^[a-zA-Z\\s]+$" />
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Email Address *</label>
//                         <input type="email" className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.email} onChange={update("email")} placeholder="example@gmail.com" required />
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Phone * (11 digits)</label>
//                         <input type="tel" className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.phone} onChange={update("phone")} placeholder="03001234567" maxLength={11} inputMode="numeric" pattern="^\d{11}$" required />
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Current City * (Letters only)</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.currentCity} onChange={update("currentCity")} required minLength={3} pattern="^[a-zA-Z\\s]+$" />
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Current Province * (Letters only)</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.currentProvince} onChange={update("currentProvince")} required minLength={3} pattern="^[a-zA-Z\\s]+$" />
//                       </div>
//                     </motion.div>
//                   )}

//                   {step === 1 && (
//                     <motion.div key="s1" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
//                       <div className="flex items-center gap-3 bg-white/5 p-4 rounded-lg border border-white/10">
//                         <input type="checkbox" className="w-5 h-5 accent-purple-500 cursor-pointer" checked={data.canMove} onChange={update("canMove")} />
//                         <label className="cursor-pointer">Are you willing to move to other cities?</label>
//                       </div>
//                       {data.canMove && (
//                         <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}>
//                           <label className="block text-sm mb-2 opacity-70">Preferred Cities (Press Enter to add) *</label>
//                           <input className="w-full p-3 rounded-md bg-white text-black outline-none" value={tagInputs.cities} onChange={(e) => setTagInputs({...tagInputs, cities: e.target.value})} onKeyDown={(e) => handleKeyDown(e, "preferredCities", "cities")} placeholder="Type city name and press Enter" />
//                           <div className="flex flex-wrap gap-2 mt-3">
//                             {data.preferredCities.map(tag => (
//                               <span key={tag} className="bg-purple-600 text-white px-3 py-1 rounded-full text-xs flex items-center gap-2">
//                                 {tag} <button type="button" onClick={() => removeTag("preferredCities", tag)}>✕</button>
//                               </span>
//                             ))}
//                           </div>
//                         </motion.div>
//                       )}
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Interests & Hobbies (Press Enter to add) *</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none" value={tagInputs.interests} onChange={(e) => setTagInputs({...tagInputs, interests: e.target.value})} onKeyDown={(e) => handleKeyDown(e, "interests", "interests")} />
//                         <div className="flex flex-wrap gap-2 mt-3">
//                           {data.interests.map(tag => (
//                             <span key={tag} className="bg-purple-600 text-white px-3 py-1 rounded-full text-xs flex items-center gap-2">
//                               {tag} <button type="button" onClick={() => removeTag("interests", tag)}>✕</button>
//                             </span>
//                           ))}
//                         </div>
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Preferred Fields of Study (Press Enter to add) *</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none" value={tagInputs.fields} onChange={(e) => setTagInputs({...tagInputs, fields: e.target.value})} onKeyDown={(e) => handleKeyDown(e, "preferredField", "fields")} />
//                         <div className="flex flex-wrap gap-2 mt-3">
//                           {data.preferredField.map(tag => (
//                             <span key={tag} className="bg-purple-600 text-white px-3 py-1 rounded-full text-xs flex items-center gap-2">
//                               {tag} <button type="button" onClick={() => removeTag("preferredField", tag)}>✕</button>
//                             </span>
//                           ))}
//                         </div>
//                       </div>
//                     </motion.div>
//                   )}

//                   {step === 2 && (
//                     <motion.div key="s2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Intermediate Percentage *</label>
//                         <input type="number" className="w-full p-3 rounded-md bg-white text-black outline-none" value={data.interPercentage} onChange={update("interPercentage")} placeholder="e.g. 85" min={0} max={100} required />
//                       </div>
//                       <CustomSelect label="Fee Affordability (Per Semester) *" value={data.feeAffordability} onChange={update("feeAffordability")} options={["Low (under 50k)", "Medium (50k to 150k)", "High (150k to 300k)", "Above 300k"]} />
//                       <div className="flex items-center gap-3 bg-white/5 p-4 rounded-lg border border-white/10">
//                         <input type="checkbox" className="w-5 h-5 accent-purple-500 cursor-pointer" checked={data.scholarshipRequired} onChange={update("scholarshipRequired")} />
//                         <label className="cursor-pointer">Do you require a scholarship?</label>
//                       </div>
//                     </motion.div>
//                   )}

//                   {step === 3 && (
//                     <motion.div key="s3" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
//                       <CustomSelect label="University Type *" value={data.uniType} onChange={update("uniType")} options={["Any", "Public", "Private"]} />
//                       <CustomSelect label="Language Preference *" value={data.languagePreference} onChange={update("languagePreference")} options={["English", "Urdu", "Both"]} />
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Required Campus Facilities (Press Enter to add) *</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none" value={tagInputs.facilities} onChange={(e) => setTagInputs({...tagInputs, facilities: e.target.value})} onKeyDown={(e) => handleKeyDown(e, "campusFacilities", "facilities")} placeholder="e.g. Hostel, Gym" />
//                         <div className="flex flex-wrap gap-2 mt-3">
//                           {data.campusFacilities.map(tag => (
//                             <span key={tag} className="bg-purple-600 text-white px-3 py-1 rounded-full text-xs flex items-center gap-2">
//                               {tag} <button type="button" onClick={() => removeTag("campusFacilities", tag)}>✕</button>
//                             </span>
//                           ))}
//                         </div>
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Additional Requirements</label>
//                         <textarea className="w-full p-3 rounded-md bg-white text-black outline-none" rows="2" value={data.additionalRequirements} onChange={update("additionalRequirements")} />
//                       </div>
//                     </motion.div>
//                   )}
//                 </AnimatePresence>

//                 <div className="flex justify-between mt-12 pt-6 border-t border-white/10">
//                   <button type="button" onClick={() => setStep(step - 1)} disabled={step === 0} className={`px-8 py-2 rounded-full border border-white/30 ${step === 0 ? "opacity-0 pointer-events-none" : "hover:bg-white/10"}`}>Back</button>
//                   <button type="submit" disabled={!isStepValid} className={`px-10 py-2 rounded-full font-bold transition ${isStepValid ? "bg-purple-600 hover:bg-purple-700 text-white" : "bg-white/10 text-white/40 cursor-not-allowed"}`}>
//                     {step === 3 ? "Submit & View Results" : "Submit"}
//                   </button>
//                 </div>
//               </form>
//             </div>
//           </div>
//         </div>
//       </div>
//     </section>
//   );
// }


// bestttttttttt
// import React, { useState, useMemo } from "react";
// import { motion, AnimatePresence } from "framer-motion";
// import { useNavigate } from "react-router-dom";
// import api from "../api/axios"; // Ensure your axios instance is correctly imported

// const stepTitles = ["Basic Information", "Preferences", "Academic & Budget", "Final Requirements"];

// export default function RecommenderForm() {
//   const navigate = useNavigate();
//   const [step, setStep] = useState(0);
//   const [loading, setLoading] = useState(false);

//   const [data, setData] = useState({
//     name: "", email: "", phone: "", currentCity: "", currentProvince: "",
//     canMove: false,
//     preferredCities: [],
//     interests: [],
//     preferredField: [],
//     interPercentage: "",
//     feeAffordability: "Medium (50k to 150k)",
//     scholarshipRequired: false,
//     uniType: "Any",
//     campusFacilities: [],
//     languagePreference: "English",
//     additionalRequirements: ""
//   });

//   const [tagInputs, setTagInputs] = useState({
//     cities: "", interests: "", fields: "", facilities: ""
//   });

//   const isStepValid = useMemo(() => {
//     const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
//     const alphaRegex = /^[a-zA-Z\s]+$/;
//     const phoneRegex = /^\d{11}$/;

//     switch (step) {
//       case 0:
//         return (
//           data.name.trim().length >= 3 && alphaRegex.test(data.name) &&
//           emailRegex.test(data.email) &&
//           phoneRegex.test(data.phone) &&
//           data.currentCity.trim().length >= 3 && alphaRegex.test(data.currentCity) &&
//           data.currentProvince.trim().length >= 3 && alphaRegex.test(data.currentProvince)
//         );
//       case 1:
//        { const citiesValid = data.canMove ? data.preferredCities.length > 0 : true;
//         return (
//           citiesValid &&
//           data.interests.length > 0 &&
//           data.preferredField.length > 0
//         );}
//       case 2:
// {        const pct = parseFloat(data.interPercentage);
//         return !isNaN(pct) && pct >= 0 && pct <= 100;}
//       case 3:
//         return data.campusFacilities.length > 0;
//       default:
//         return false;
//     }
//   }, [data, step]);

//   const addTag = (field, value, inputKey) => {
//     if (value.trim() && !data[field].includes(value.trim())) {
//       setData({ ...data, [field]: [...data[field], value.trim()] });
//       setTagInputs({ ...tagInputs, [inputKey]: "" });
//     }
//   };

//   const removeTag = (field, tagToRemove) => {
//     setData({ ...data, [field]: data[field].filter((t) => t !== tagToRemove) });
//   };

//   const handleKeyDown = (e, field, inputKey) => {
//     if (e.key === "Enter") {
//       e.preventDefault();
//       addTag(field, e.target.value, inputKey);
//     }
//   };

//   const update = (field) => (e) => {
//     const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
//     setData((d) => ({ ...d, [field]: value }));
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (step < 3) {
//       setStep(step + 1);
//     } else {
//       setLoading(true);
//       try {

//         const response = await api.post("/api/user-profiles/submit-and-recommend/", data);
        

//         navigate("/recommendations", { state: { userData: response.data } });
//       } catch (err) {
//         console.error("Submission error:", err);
//         alert("Failed to generate recommendations. Please check your network or try again.");
//       } finally {
//         setLoading(false);
//       }
//     }
//   };

//   const CustomSelect = ({ label, value, onChange, options }) => (
//     <div className="w-full">
//       <label className="block text-sm mb-2 opacity-70">{label}</label>
//       <div className="relative">
//         <select
//           className="w-full p-3 rounded-md bg-white text-black outline-none appearance-none cursor-pointer pr-10"
//           value={value}
//           onChange={onChange}
//         >
//           {options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
//         </select>
//         <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none flex items-center">
//           <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
//           </svg>
//         </div>
//       </div>
//     </div>
//   );

//   return (
//     <section className="min-h-screen flex items-start justify-center bg-[#0B0620] pt-28 md:pt-36 pb-20">
//       <div className="w-full max-w-6xl px-6">
//         <div className="bg-white/10 border border-white/20 rounded-[24px] overflow-hidden backdrop-blur-md">
//           <div className="grid grid-cols-1 md:grid-cols-3">
//             <aside className="bg-[#4F3C61] p-8 text-white">
//               <div className="flex items-center gap-3 text-2xl font-semibold mb-10">
//                 <span className="inline-block w-8 h-8 rounded bg-white text-[#4F3C61] text-center leading-8 text-sm font-bold">2</span>
//                 Recommender
//               </div>
//               <ul className="space-y-6">
//                 {stepTitles.map((title, idx) => (
//                   <li key={title} className={`flex items-center gap-4 transition-opacity ${idx === step ? "opacity-100" : "opacity-40"}`}>
//                     <div className={`w-9 h-9 rounded-full border flex items-center justify-center ${idx === step ? "bg-white text-[#4F3C61]" : "border-white"}`}>
//                       {idx + 1}
//                     </div>
//                     <span className="text-sm font-medium">{title}</span>
//                   </li>
//                 ))}
//               </ul>
//             </aside>

//             <div className="md:col-span-2 p-8 md:p-12 text-white">
//               <h2 className="text-3xl font-bold mb-8">{stepTitles[step]}</h2>
//               <form onSubmit={handleSubmit}>
//                 <AnimatePresence mode="wait">
//                   {step === 0 && (
//                     <motion.div key="s0" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
//                       <div className="md:col-span-2">
//                         <label className="block text-sm mb-2 opacity-70">Full Name * (Letters only)</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.name} onChange={update("name")} placeholder="At least 3 letters" required minLength={3} pattern="^[a-zA-Z\s]+$" />
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Email Address *</label>
//                         <input type="email" className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.email} onChange={update("email")} placeholder="example@gmail.com" required />
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Phone * (11 digits)</label>
//                         <input type="tel" className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.phone} onChange={update("phone")} placeholder="03001234567" maxLength={11} inputMode="numeric" pattern="^\d{11}$" required />
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Current City * (Letters only)</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.currentCity} onChange={update("currentCity")} required minLength={3} pattern="^[a-zA-Z\s]+$" />
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Current Province * (Letters only)</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.currentProvince} onChange={update("currentProvince")} required minLength={3} pattern="^[a-zA-Z\s]+$" />
//                       </div>
//                     </motion.div>
//                   )}

//                   {step === 1 && (
//                     <motion.div key="s1" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
//                       <div className="flex items-center gap-3 bg-white/5 p-4 rounded-lg border border-white/10">
//                         <input type="checkbox" className="w-5 h-5 accent-purple-500 cursor-pointer" checked={data.canMove} onChange={update("canMove")} />
//                         <label className="cursor-pointer">Are you willing to move to other cities?</label>
//                       </div>
//                       {data.canMove && (
//                         <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}>
//                           <label className="block text-sm mb-2 opacity-70">Preferred Cities (Press Enter to add) *</label>
//                           <input className="w-full p-3 rounded-md bg-white text-black outline-none" value={tagInputs.cities} onChange={(e) => setTagInputs({...tagInputs, cities: e.target.value})} onKeyDown={(e) => handleKeyDown(e, "preferredCities", "cities")} placeholder="Type city name and press Enter" />
//                           <div className="flex flex-wrap gap-2 mt-3">
//                             {data.preferredCities.map(tag => (
//                               <span key={tag} className="bg-purple-600 text-white px-3 py-1 rounded-full text-xs flex items-center gap-2">
//                                 {tag} <button type="button" onClick={() => removeTag("preferredCities", tag)}>✕</button>
//                               </span>
//                             ))}
//                           </div>
//                         </motion.div>
//                       )}
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Interests & Hobbies (Press Enter to add) *</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none" value={tagInputs.interests} onChange={(e) => setTagInputs({...tagInputs, interests: e.target.value})} onKeyDown={(e) => handleKeyDown(e, "interests", "interests")} />
//                         <div className="flex flex-wrap gap-2 mt-3">
//                           {data.interests.map(tag => (
//                             <span key={tag} className="bg-purple-600 text-white px-3 py-1 rounded-full text-xs flex items-center gap-2">
//                               {tag} <button type="button" onClick={() => removeTag("interests", tag)}>✕</button>
//                             </span>
//                           ))}
//                         </div>
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Preferred Fields of Study (Press Enter to add) *</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none" value={tagInputs.fields} onChange={(e) => setTagInputs({...tagInputs, fields: e.target.value})} onKeyDown={(e) => handleKeyDown(e, "preferredField", "fields")} />
//                         <div className="flex flex-wrap gap-2 mt-3">
//                           {data.preferredField.map(tag => (
//                             <span key={tag} className="bg-purple-600 text-white px-3 py-1 rounded-full text-xs flex items-center gap-2">
//                               {tag} <button type="button" onClick={() => removeTag("preferredField", tag)}>✕</button>
//                             </span>
//                           ))}
//                         </div>
//                       </div>
//                     </motion.div>
//                   )}

//                   {step === 2 && (
//                     <motion.div key="s2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Intermediate Percentage *</label>
//                         <input type="number" className="w-full p-3 rounded-md bg-white text-black outline-none" value={data.interPercentage} onChange={update("interPercentage")} placeholder="e.g. 85" min={0} max={100} required />
//                       </div>
//                       <CustomSelect label="Fee Affordability (Per Semester) *" value={data.feeAffordability} onChange={update("feeAffordability")} options={["Low (under 50k)", "Medium (50k to 150k)", "High (150k to 300k)", "Above 300k"]} />
//                       <div className="flex items-center gap-3 bg-white/5 p-4 rounded-lg border border-white/10">
//                         <input type="checkbox" className="w-5 h-5 accent-purple-500 cursor-pointer" checked={data.scholarshipRequired} onChange={update("scholarshipRequired")} />
//                         <label className="cursor-pointer">Do you require a scholarship?</label>
//                       </div>
//                     </motion.div>
//                   )}

//                   {step === 3 && (
//                     <motion.div key="s3" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
//                       <CustomSelect label="University Type *" value={data.uniType} onChange={update("uniType")} options={["Any", "Public", "Private"]} />
//                       <CustomSelect label="Language Preference *" value={data.languagePreference} onChange={update("languagePreference")} options={["English", "Urdu", "Both"]} />
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Required Campus Facilities (Press Enter to add) *</label>
//                         <input className="w-full p-3 rounded-md bg-white text-black outline-none" value={tagInputs.facilities} onChange={(e) => setTagInputs({...tagInputs, facilities: e.target.value})} onKeyDown={(e) => handleKeyDown(e, "campusFacilities", "facilities")} placeholder="e.g. Hostel, Gym" />
//                         <div className="flex flex-wrap gap-2 mt-3">
//                           {data.campusFacilities.map(tag => (
//                             <span key={tag} className="bg-purple-600 text-white px-3 py-1 rounded-full text-xs flex items-center gap-2">
//                               {tag} <button type="button" onClick={() => removeTag("campusFacilities", tag)}>✕</button>
//                             </span>
//                           ))}
//                         </div>
//                       </div>
//                       <div>
//                         <label className="block text-sm mb-2 opacity-70">Additional Requirements</label>
//                         <textarea className="w-full p-3 rounded-md bg-white text-black outline-none" rows="2" value={data.additionalRequirements} onChange={update("additionalRequirements")} />
//                       </div>
//                     </motion.div>
//                   )}
//                 </AnimatePresence>

//                 <div className="flex justify-between mt-12 pt-6 border-t border-white/10">
//                   <button type="button" onClick={() => setStep(step - 1)} disabled={step === 0 || loading} className={`px-8 py-2 rounded-full border border-white/30 ${step === 0 ? "opacity-0 pointer-events-none" : "hover:bg-white/10 disabled:opacity-50"}`}>Back</button>
//                   <button type="submit" disabled={!isStepValid || loading} className={`px-10 py-2 rounded-full font-bold transition flex items-center gap-2 ${isStepValid && !loading ? "bg-purple-600 hover:bg-purple-700 text-white" : "bg-white/10 text-white/40 cursor-not-allowed"}`}>
//                     {loading ? (
//                       <>
//                         <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
//                         Processing...
//                       </>
//                     ) : (
//                       step === 3 ? "Submit & View Results" : "Submit"
//                     )}
//                   </button>
//                 </div>
//               </form>
//             </div>
//           </div>
//         </div>
//       </div>
//     </section>
//   );
// }

import React, { useState, useMemo, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import { getSession } from "../utils/authStore";
import BackToDashboard from "./BackToDashboard";

const stepTitles = ["Basic Information", "Preferences", "Academic & Budget", "Final Requirements"];

const CITIES_OPTIONS = [
  "Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad",
  "Multan", "Peshawar", "Quetta", "Sialkot", "Gujranwala",
  "Hyderabad", "Abbottabad", "Bahawalpur", "Sargodha", "Sukkur"
];

const INTERESTS_OPTIONS = [
  "Programming & Technology", "Art & Design", "Sports & Fitness",
  "Music", "Reading & Literature", "Business & Entrepreneurship",
  "Science & Research", "Gaming", "Travel & Culture",
  "Social Work & Community", "Photography", "Mathematics",
  "Writing & Journalism", "Environment & Sustainability", "Healthcare"
];

const FIELDS_OPTIONS = [
  "Computer Science", "Software Engineering", "Electrical Engineering",
  "Mechanical Engineering", "Civil Engineering", "Business Administration",
  "Medicine (MBBS)", "Pharmacy", "Architecture", "Law",
  "Economics", "Psychology", "Accounting & Finance",
  "Mass Communication", "Education", "Biotechnology",
  "Data Science / AI", "Cybersecurity", "Environmental Science", "Sociology"
];

const FACILITIES_OPTIONS = [
  "Hostel / Accommodation", "Transport", "Gym & Sports Facilities",
  "Library", "Research Labs", "Cafeteria", "Mosque / Prayer Area",
  "Medical Center", "Wi-Fi Campus", "Career Services",
  "Student Clubs", "Auditorium", "Swimming Pool", "Parking", "Day Care"
];

// Application-form degree codes -> recommender field of study
const DEGREE_TO_FIELD = {
  BSCS: "Computer Science", BSSE: "Software Engineering",
  BSAI: "Data Science / AI", BSDS: "Data Science / AI", BSCY: "Cybersecurity",
  BEEE: "Electrical Engineering", BEME: "Mechanical Engineering", BECE: "Civil Engineering",
  BBA: "Business Administration", MBBS: "Medicine (MBBS)", BPHARM: "Pharmacy",
  BEARCH: "Architecture", BSLAW: "Law", BSECO: "Economics", BSPSY: "Psychology",
  BSACC: "Accounting & Finance", BSMAS: "Mass Communication",
  BSED: "Education", BED: "Education", BSBTECH: "Biotechnology",
  BSENV: "Environmental Science", BSSOC: "Sociology",
};

// Build recommender fields from the saved application (StudentProfile)
function profileToRecommenderData(p) {
  const fields = [p.preference1, p.preference2, p.preference3]
    .map(code => DEGREE_TO_FIELD[code])
    .filter(Boolean);
  const interTotal = Number(p.inter_total) || 550;
  const interPct = p.inter_part_one != null && p.inter_part_one !== ""
    ? String(Math.round((Number(p.inter_part_one) / interTotal) * 10000) / 100)
    : "";
  return {
    name: p.student_name || "",
    email: p.email || "",
    phone: p.mobile || "",
    currentCity: p.city || "",
    currentProvince: p.province || "",
    preferredField: [...new Set(fields)],
    interPercentage: interPct,
    campusFacilities: p.hostel ? ["Hostel / Accommodation"] : [],
  };
}

export default function RecommenderForm() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [prefilled, setPrefilled] = useState(false);

  const [data, setData] = useState({
    name: "", email: "", phone: "", currentCity: "", currentProvince: "",
    canMove: false,
    preferredCities: [],
    interests: [],
    preferredField: [],
    interPercentage: "",
    feeAffordability: "Medium (50k to 150k)",
    scholarshipRequired: false,
    uniType: "Any",
    campusFacilities: [],
    languagePreference: "English",
    additionalRequirements: ""
  });

  // Pre-fill from the saved application form, if the user has one.
  // Only empty fields are filled, so anything the user already typed is kept.
  useEffect(() => {
    if (!getSession()) return;
    let cancelled = false;
    api.get("/student/profile/")
      .then(({ data: profile }) => {
        if (cancelled || !profile) return;
        const fromProfile = profileToRecommenderData(profile);
        setData(d => {
          const merged = { ...d };
          Object.entries(fromProfile).forEach(([key, value]) => {
            const isEmpty = Array.isArray(d[key]) ? d[key].length === 0 : !d[key];
            if (isEmpty) merged[key] = value;
          });
          return merged;
        });
        setPrefilled(true);
      })
      .catch(() => {}); // No application yet (404) or not logged in: keep the empty form
    return () => { cancelled = true; };
  }, []);

  const isStepValid = useMemo(() => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const alphaRegex = /^[a-zA-Z\s]+$/;
    const phoneRegex = /^\d{11}$/;

    switch (step) {
      case 0:
        return (
          data.name.trim().length >= 3 && alphaRegex.test(data.name) &&
          emailRegex.test(data.email) &&
          phoneRegex.test(data.phone) &&
          data.currentCity.trim().length >= 3 && alphaRegex.test(data.currentCity) &&
          data.currentProvince.trim().length >= 3 && alphaRegex.test(data.currentProvince)
        );
      case 1: {
        const citiesValid = data.canMove ? data.preferredCities.length > 0 : true;
        return citiesValid && data.interests.length > 0 && data.preferredField.length > 0;
      }
      case 2: {
        const pct = parseFloat(data.interPercentage);
        return !isNaN(pct) && pct >= 0 && pct <= 100;
      }
      case 3:
        return data.campusFacilities.length > 0;
      default:
        return false;
    }
  }, [data, step]);

  const toggleMultiSelect = (field, value) => {
    setData(d => ({
      ...d,
      [field]: d[field].includes(value)
        ? d[field].filter(v => v !== value)
        : [...d[field], value]
    }));
  };

  const update = (field) => (e) => {
    const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setData(d => ({ ...d, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (step < 3) {
      setStep(step + 1);
    } else {
      setLoading(true);
      try {
        const response = await api.post("/api/user-profiles/submit-and-recommend/", data);
        navigate("/recommendations", { state: { userData: response.data } });
      } catch (err) {
        console.error("Submission error:", err);
        alert("Failed to generate recommendations. Please check your network or try again.");
      } finally {
        setLoading(false);
      }
    }
  };

  // Reusable styled select
  const CustomSelect = ({ label, value, onChange, options }) => (
    <div className="w-full">
      <label className="block text-sm mb-2 opacity-70">{label}</label>
      <div className="relative">
        <select
          className="w-full p-3 rounded-md bg-white text-black outline-none appearance-none cursor-pointer pr-10"
          value={value}
          onChange={onChange}
        >
          {options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
        </select>
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    </div>
  );

  // Reusable pill-based multi-select from a fixed list
  const MultiSelectPills = ({ label, field, options, required }) => (
    <div>
      <label className="block text-sm mb-2 opacity-70">
        {label} {required && "*"}{" "}
        <span className="opacity-50 font-normal">(select all that apply)</span>
      </label>
      <div className="flex flex-wrap gap-2">
        {options.map(opt => {
          const selected = data[field].includes(opt);
          return (
            <button
              key={opt}
              type="button"
              onClick={() => toggleMultiSelect(field, opt)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-all duration-150 cursor-pointer select-none
                ${selected
                  ? "bg-purple-600 border-purple-600 text-white"
                  : "bg-white/5 border-white/20 text-white/70 hover:border-purple-400 hover:text-white"
                }`}
            >
              {selected && <span className="mr-1">✓</span>}{opt}
            </button>
          );
        })}
      </div>
      {data[field].length > 0 && (
        <p className="mt-2 text-xs text-purple-300 opacity-80">
          {data[field].length} selected
        </p>
      )}
    </div>
  );

  return (
    <section className="min-h-screen flex items-start justify-center bg-[#0B0620] pt-28 md:pt-36 pb-20">
      <div className="w-full max-w-6xl px-4 sm:px-6">
        <BackToDashboard className="mb-6" />
        <div className="bg-white/10 border border-white/20 rounded-[24px] overflow-hidden backdrop-blur-md">
          <div className="grid grid-cols-1 md:grid-cols-3">
            {/* Sidebar */}
            <aside className="bg-[#4F3C61] p-5 md:p-8 text-white">
              <div className="flex items-center gap-3 text-xl md:text-2xl font-semibold mb-4 md:mb-10">
                <span className="inline-block w-8 h-8 rounded bg-white text-[#4F3C61] text-center leading-8 text-sm font-bold">2</span>
                Recommender
              </div>
              {/* Phones: compact progress instead of the full step list */}
              <div className="md:hidden">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{stepTitles[step]}</span>
                  <span className="text-white/60">Step {step + 1} of {stepTitles.length}</span>
                </div>
                <div className="mt-3 h-1.5 rounded-full bg-white/15 overflow-hidden">
                  <div className="h-full rounded-full bg-white transition-all duration-300" style={{ width: `${((step + 1) / stepTitles.length) * 100}%` }} />
                </div>
              </div>
              <ul className="hidden md:block space-y-6">
                {stepTitles.map((title, idx) => (
                  <li key={title} className={`flex items-center gap-4 transition-opacity ${idx === step ? "opacity-100" : "opacity-40"}`}>
                    <div className={`w-9 h-9 rounded-full border flex items-center justify-center shrink-0 ${idx === step ? "bg-white text-[#4F3C61]" : "border-white"}`}>
                      {idx + 1}
                    </div>
                    <span className="text-sm font-medium">{title}</span>
                  </li>
                ))}
              </ul>
            </aside>

            {/* Main content */}
            <div className="md:col-span-2 p-5 sm:p-8 md:p-12 text-white">
              <h2 className="text-2xl sm:text-3xl font-bold mb-6 sm:mb-8">{stepTitles[step]}</h2>
              {prefilled && (
                <div className="mb-8 p-4 rounded-lg bg-purple-500/10 border border-purple-400/30 text-sm text-purple-100">
                  Some fields have been pre-filled from your application form. You can edit any of them before submitting.
                </div>
              )}
              <form onSubmit={handleSubmit}>
                <AnimatePresence mode="wait">

                  {/* Step 0 — Basic Info */}
                  {step === 0 && (
                    <motion.div key="s0" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="md:col-span-2">
                        <label className="block text-sm mb-2 opacity-70">Full Name * (Letters only)</label>
                        <input className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.name} onChange={update("name")} placeholder="At least 3 letters" required minLength={3} pattern="^[a-zA-Z\s]+$" />
                      </div>
                      <div>
                        <label className="block text-sm mb-2 opacity-70">Email Address *</label>
                        <input type="email" className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.email} onChange={update("email")} placeholder="example@gmail.com" required />
                      </div>
                      <div>
                        <label className="block text-sm mb-2 opacity-70">Phone * (11 digits)</label>
                        <input type="tel" className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.phone} onChange={update("phone")} placeholder="03001234567" maxLength={11} inputMode="numeric" pattern="^\d{11}$" required />
                      </div>
                      <div>
                        <label className="block text-sm mb-2 opacity-70">Current City * (Letters only)</label>
                        <input className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.currentCity} onChange={update("currentCity")} required minLength={3} pattern="^[a-zA-Z\s]+$" />
                      </div>
                      <div>
                        <label className="block text-sm mb-2 opacity-70">Current Province * (Letters only)</label>
                        <input className="w-full p-3 rounded-md bg-white text-black outline-none focus:ring-2 ring-purple-500" value={data.currentProvince} onChange={update("currentProvince")} required minLength={3} pattern="^[a-zA-Z\s]+$" />
                      </div>
                    </motion.div>
                  )}

                  {/* Step 1 — Preferences */}
                  {step === 1 && (
                    <motion.div key="s1" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
                      <div className="flex items-center gap-3 bg-white/5 p-4 rounded-lg border border-white/10">
                        <input type="checkbox" className="w-5 h-5 accent-purple-500 cursor-pointer" checked={data.canMove} onChange={update("canMove")} id="canMove" />
                        <label htmlFor="canMove" className="cursor-pointer">Are you willing to move to other cities?</label>
                      </div>

                      {data.canMove && (
                        <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}>
                          <MultiSelectPills label="Preferred Cities" field="preferredCities" options={CITIES_OPTIONS} required />
                        </motion.div>
                      )}

                      <MultiSelectPills label="Interests & Hobbies" field="interests" options={INTERESTS_OPTIONS} required />
                      <MultiSelectPills label="Preferred Fields of Study" field="preferredField" options={FIELDS_OPTIONS} required />
                    </motion.div>
                  )}

                  {/* Step 2 — Academic & Budget */}
                  {step === 2 && (
                    <motion.div key="s2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
                      <div>
                        <label className="block text-sm mb-2 opacity-70">Intermediate Percentage *</label>
                        <input type="number" className="w-full p-3 rounded-md bg-white text-black outline-none" value={data.interPercentage} onChange={update("interPercentage")} placeholder="e.g. 85.45" min={0} max={100} step="0.01" inputMode="decimal" required />
                      </div>
                      <CustomSelect label="Fee Affordability (Per Semester) *" value={data.feeAffordability} onChange={update("feeAffordability")} options={["Low (under 50k)", "Medium (50k to 150k)", "High (150k to 300k)", "Above 300k"]} />
                      <div className="flex items-center gap-3 bg-white/5 p-4 rounded-lg border border-white/10">
                        <input type="checkbox" id="scholarship" className="w-5 h-5 accent-purple-500 cursor-pointer" checked={data.scholarshipRequired} onChange={update("scholarshipRequired")} />
                        <label htmlFor="scholarship" className="cursor-pointer">Do you require a scholarship?</label>
                      </div>
                    </motion.div>
                  )}

                  {/* Step 3 — Final Requirements */}
                  {step === 3 && (
                    <motion.div key="s3" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
                      <CustomSelect label="University Type *" value={data.uniType} onChange={update("uniType")} options={["Any", "Public", "Private"]} />
                      <CustomSelect label="Language Preference *" value={data.languagePreference} onChange={update("languagePreference")} options={["English", "Urdu", "Both"]} />
                      <MultiSelectPills label="Required Campus Facilities" field="campusFacilities" options={FACILITIES_OPTIONS} required />
                      <div>
                        <label className="block text-sm mb-2 opacity-70">Additional Requirements</label>
                        <textarea className="w-full p-3 rounded-md bg-white text-black outline-none" rows="2" value={data.additionalRequirements} onChange={update("additionalRequirements")} />
                      </div>
                    </motion.div>
                  )}

                </AnimatePresence>

                <div className="flex justify-between mt-12 pt-6 border-t border-white/10">
                  <button type="button" onClick={() => setStep(step - 1)} disabled={step === 0 || loading}
                    className={`px-8 py-2 rounded-full border border-white/30 ${step === 0 ? "opacity-0 pointer-events-none" : "hover:bg-white/10 disabled:opacity-50"}`}>
                    Back
                  </button>
                  <button type="submit" disabled={!isStepValid || loading}
                    className={`px-10 py-2 rounded-full font-bold transition flex items-center gap-2 ${isStepValid && !loading ? "bg-purple-600 hover:bg-purple-700 text-white" : "bg-white/10 text-white/40 cursor-not-allowed"}`}>
                    {loading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        Processing...
                      </>
                    ) : (
                      step === 3 ? "Submit & View Results" : "Next"
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}