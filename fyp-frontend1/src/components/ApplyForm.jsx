// import React, { useMemo, useState } from "react";
// import { motion, AnimatePresence } from "framer-motion";
// import { useNavigate } from "react-router-dom";
// import api from "../api/axios";

// const stepTitles = [
//   "Personal details",
//   "Guardian & Contact",
//   "Academic Background",
//   "Program Preferences",
//   "Document Uploads",
// ];

// const initialData = {
//   student_name: "",
//   student_cnic: "",
//   father_name: "",
//   gender: "Male",
//   dob: "",
//   domicile: "",
//   religion: "Islam",
//   nationality: "Pakistani",
//   father_cnic: "",
//   father_phone: "",
//   mother_name: "",
//   guardian_name: "",
//   guardian_mobile: "", // Added
//   guardian_cnic: "",   // Added
//   mobile: "",
//   email: "",
//   province: "",
//   city: "",
//   address: "",
//   matric_roll: "",
//   board: "",
//   matric_obtained: "",
//   matric_total: "1100",
//   inter_roll: "",
//   inter_part_one: "",
//   inter_total: "550",
//   preference1: "",
//   preference2: "",
//   preference3: "",
//   photo: null,
//   matric_degree: null,
//   inter_degree: null,
//   domicile_upload: null,
//   hafiz_quran: false,
//   hostel: false,
//   father_income: 0,
// };

// function useStepValidation(data) {
//   return useMemo(() => ({
//     0: () => !!(data.student_name && data.student_cnic && data.father_name && data.dob && data.domicile),
//     1: () => !!(data.email.includes("@") && data.mobile && data.province && data.city && data.father_phone && data.father_cnic && data.mother_name && data.guardian_name && data.guardian_mobile && data.guardian_cnic),
//     2: () => !!(data.matric_roll && data.matric_obtained && data.inter_roll && data.board),
//     3: () => !!(data.preference1 && data.preference2 && data.preference3),
//     4: () => !!(data.photo && data.matric_degree),
//   }), [data]);
// }

// export default function ApplyForm({ embedded = false, onClose }) {
//   const [step, setStep] = useState(0);
//   const [data, setData] = useState(initialData);
//   const [loading, setLoading] = useState(false);
//   const navigate = useNavigate();
  
//   const validators = useStepValidation(data);
//   const canNext = validators[step] ? validators[step]() : false;

//   const update = (field, isCheckbox = false) => (e) => {
//     let value;
//     if (isCheckbox) value = e.target.checked;
//     else if (e.target.files) value = e.target.files[0];
//     else value = e.target.value;

//     setData((d) => ({ ...d, [field]: value }));
//   };

//   // Helper to save time for the user
//   const copyFatherToGuardian = () => {
//     setData(d => ({
//       ...d,
//       guardian_name: d.father_name,
//       guardian_mobile: d.father_phone,
//       guardian_cnic: d.father_cnic
//     }));
//   };

//   const onSubmit = async (e) => {
//     e.preventDefault();
//     setLoading(true);

//     const formData = new FormData();
//     Object.keys(data).forEach(key => {
//         if (data[key] !== null) {
//             if (['photo', 'matric_degree', 'inter_degree', 'domicile_upload'].includes(key)) {
//                 if (data[key] instanceof File) formData.append(key, data[key]);
//             } else {
//                 formData.append(key, data[key]);
//             }
//         }
//     });

//     try {
//         const response = await api.post("/student/profile/", formData, {
//             headers: { 'Content-Type': 'multipart/form-data' }
//         });
//         alert("Application Submitted Successfully!");
//         if (embedded && onClose) onClose();
//         else navigate("/dashboard");
//     } catch (err) {
//         console.error("Submission error:", err.response?.data);
//         alert("Failed to submit: " + JSON.stringify(err.response?.data));
//     } finally {
//         setLoading(false);
//     }
//   };

//   return (
//     <section className={`min-h-screen flex items-start justify-center bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] ${embedded ? "pt-0" : "pt-28 md:pt-36"}`}>
//       <div className="w-full max-w-6xl px-6 md:px-10">
//         <div className="bg-white/10 border border-white/20 rounded-[24px] shadow-2xl overflow-hidden">
//           <div className="grid grid-cols-1 md:grid-cols-3">
            
//             <aside className="bg-[#4F3C61]/80 p-8">
//               <nav className="space-y-6">
//                 {stepTitles.map((title, idx) => (
//                   <div key={title} className="flex items-center gap-4">
//                     <div className={`w-8 h-8 rounded-full border flex items-center justify-center text-sm ${idx === step ? "bg-white text-[#4F3C61]" : "text-white/60 border-white/20"}`}>
//                       {idx < step ? "✓" : idx + 1}
//                     </div>
//                     <span className={idx === step ? "text-white font-medium" : "text-white/50"}>{title}</span>
//                   </div>
//                 ))}
//               </nav>
//             </aside>

//             <div className="md:col-span-2 p-10 bg-white/5">
//               <h2 className="text-3xl font-semibold mb-2 text-white">{stepTitles[step]}</h2>
//               <p className="text-white/50 mb-8 text-sm italic">* All fields are required by the University</p>

//               <form onSubmit={onSubmit}>
//                 <AnimatePresence mode="wait">
//                   {step === 0 && (
//                     <motion.div key="s0" initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -20, opacity: 0 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
//                       <div className="col-span-2">
//                         <label className="text-sm text-white/70 mb-2 block">Full Name</label>
//                         <input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.student_name} onChange={update("student_name")} />
//                       </div>
//                       <div><label className="text-sm text-white/70 mb-2 block">Student CNIC</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.student_cnic} onChange={update("student_cnic")} /></div>
//                       <div><label className="text-sm text-white/70 mb-2 block">Father's Name</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.father_name} onChange={update("father_name")} /></div>
//                       <div><label className="text-sm text-white/70 mb-2 block">Domicile District</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.domicile} onChange={update("domicile")} /></div>
//                       <div><label className="text-sm text-white/70 mb-2 block">Date of Birth</label><input type="date" className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.dob} onChange={update("dob")} /></div>
//                     </motion.div>
//                   )}

//                   {step === 1 && (
//                     <motion.div key="s1" initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
//                       {/* Father Info */}
//                       <div><label className="text-sm text-white/70 mb-2 block">Father's CNIC</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.father_cnic} onChange={update("father_cnic")} /></div>
//                       <div><label className="text-sm text-white/70 mb-2 block">Father's Mobile</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.father_phone} onChange={update("father_phone")} /></div>
//                       <div className="col-span-2"><label className="text-sm text-white/70 mb-2 block">Mother's Name</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.mother_name} onChange={update("mother_name")} /></div>
                      
//                       {/* Guardian Info with Auto-fill option */}
//                       <div className="col-span-2 flex justify-between items-end border-t border-white/10 pt-4 mt-2">
//                         <label className="text-sm text-white/70 block font-bold text-indigo-300">Guardian Details</label>
//                         <button type="button" onClick={copyFatherToGuardian} className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded border border-indigo-500/30 hover:bg-indigo-500/40">Same as Father?</button>
//                       </div>
//                       <div><label className="text-sm text-white/70 mb-2 block">Guardian Name</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.guardian_name} onChange={update("guardian_name")} /></div>
//                       <div><label className="text-sm text-white/70 mb-2 block">Guardian Mobile</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.guardian_mobile} onChange={update("guardian_mobile")} /></div>
//                       <div className="col-span-2"><label className="text-sm text-white/70 mb-2 block">Guardian CNIC</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.guardian_cnic} onChange={update("guardian_cnic")} /></div>
                      
//                       {/* Contact Info */}
//                       <div className="col-span-2 border-t border-white/10 pt-4 mt-2 grid grid-cols-2 gap-6">
//                         <div><label className="text-sm text-white/70 mb-2 block">Student Email</label><input type="email" className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.email} onChange={update("email")} /></div>
//                         <div><label className="text-sm text-white/70 mb-2 block">Student Mobile</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.mobile} onChange={update("mobile")} /></div>
//                         <div><label className="text-sm text-white/70 mb-2 block">Province</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.province} onChange={update("province")} /></div>
//                         <div><label className="text-sm text-white/70 mb-2 block">City</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.city} onChange={update("city")} /></div>
//                       </div>
                      
//                       <div className="col-span-2">
//                         <label className="text-sm text-white/70 mb-2 block">Residential Address</label>
//                         <textarea className="w-full bg-white/10 border border-white/20 p-3 rounded text-white h-20" value={data.address} onChange={update("address")} />
//                       </div>
//                     </motion.div>
//                   )}

//                   {/* Steps 2, 3, 4 remain same as before */}
//                   {step === 2 && (
//                     <motion.div key="s2" initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
//                       <div><label className="text-sm text-white/70 mb-2 block">Matric Roll #</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.matric_roll} onChange={update("matric_roll")} /></div>
//                       <div><label className="text-sm text-white/70 mb-2 block">Board</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.board} onChange={update("board")} /></div>
//                       <div><label className="text-sm text-white/70 mb-2 block">Matric Marks</label><input type="number" className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.matric_obtained} onChange={update("matric_obtained")} /></div>
//                       <div><label className="text-sm text-white/70 mb-2 block">Inter Roll #</label><input className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data.inter_roll} onChange={update("inter_roll")} /></div>
//                     </motion.div>
//                   )}

//                   {step === 3 && (
//                     <motion.div key="s3" initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="space-y-6">
//                       {[1, 2, 3].map(i => (
//                         <div key={i}>
//                           <label className="text-sm text-white/70 mb-2 block">Preference {i}</label>
//                           <select className="w-full bg-white/10 border border-white/20 p-3 rounded text-white" value={data[`preference${i}`]} onChange={update(`preference${i}`)}>
//                             <option value="" className="text-black">Select Degree</option>
//                             <option value="BSCS" className="text-black">BS Computer Science</option>
//                             <option value="BSSE" className="text-black">BS Software Engineering</option>
//                             <option value="BSIT" className="text-black">BS Information Technology</option>
//                           </select>
//                         </div>
//                       ))}
//                     </motion.div>
//                   )}

//                   {step === 4 && (
//                     <motion.div key="s4" initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="grid grid-cols-1 gap-6">
//                       <div className="bg-white/5 p-4 rounded-lg border border-dashed border-white/30"><label className="text-sm text-white/70 mb-2 block">Profile Photo</label><input type="file" accept="image/*" className="w-full text-white text-sm" onChange={update("photo")} /></div>
//                       <div className="bg-white/5 p-4 rounded-lg border border-dashed border-white/30"><label className="text-sm text-white/70 mb-2 block">Matric Certificate</label><input type="file" accept="image/*,.pdf" className="w-full text-white text-sm" onChange={update("matric_degree")} /></div>
//                       <div className="bg-white/5 p-4 rounded-lg border border-dashed border-white/30"><label className="text-sm text-white/70 mb-2 block">Inter Certificate</label><input type="file" accept="image/*,.pdf" className="w-full text-white text-sm" onChange={update("inter_degree")} /></div>
//                     </motion.div>
//                   )}
//                 </AnimatePresence>

//                 <div className="mt-12 flex justify-between">
//                   <button type="button" onClick={() => setStep(s => s - 1)} disabled={step === 0} className="px-8 py-2 rounded-full border border-white/20 text-white hover:bg-white/10 disabled:opacity-30">Back</button>
//                   {step < 4 ? (
//                     <button type="button" onClick={() => setStep(s => s + 1)} disabled={!canNext} className="px-10 py-2 rounded-full bg-white text-black font-bold hover:bg-white/90 disabled:opacity-30">Next</button>
//                   ) : (
//                     <button type="submit" disabled={loading || !canNext} className="px-10 py-2 rounded-full bg-indigo-500 text-white font-bold hover:bg-indigo-600 disabled:opacity-30 shadow-lg">
//                       {loading ? "Submitting..." : "Submit Application"}
//                     </button>
//                   )}
//                 </div>
//               </form>
//             </div>
//           </div>
//         </div>
//       </div>
//     </section>
//   );
// }


// besttttt
// import React, { useMemo, useState } from "react";
// import { motion, AnimatePresence } from "framer-motion";
// import { useNavigate } from "react-router-dom";
// import api from "../api/axios";

// const stepTitles = [
//   "Personal details",
//   "Guardian & Contact",
//   "Academic Background",
//   "Program Preferences",
//   "Document Uploads",
// ];

// const initialData = {
//   student_name: "",
//   student_cnic: "",
//   father_name: "",
//   gender: "Male",
//   dob: "",
//   domicile: "",
//   religion: "Islam",
//   nationality: "Pakistani",
//   father_cnic: "",
//   father_phone: "",
//   mother_name: "",
//   guardian_name: "",
//   guardian_mobile: "",
//   guardian_cnic: "",
//   mobile: "",
//   email: "",
//   province: "",
//   city: "",
//   address: "",
//   matric_roll: "",
//   board: "",
//   matric_obtained: "",
//   matric_total: "1100",
//   inter_roll: "",
//   inter_part_one: "",
//   inter_total: "550",
//   preference1: "",
//   preference2: "",
//   preference3: "",
//   photo: null,
//   matric_degree: null,
//   inter_degree: null,
//   domicile_upload: null,
//   hafiz_quran: false,
//   hostel: false,
//   father_income: 0,
// };

// // --- 1. MOVED OUTSIDE TO PREVENT FOCUS LOSS ---
// const InputField = ({ label, value, error, onChange, type = "text", placeholder = "" }) => (
//   <div className="w-full">
//     <label className="text-sm text-white/70 mb-1 block">{label}</label>
//     <input
//       type={type}
//       className={`w-full bg-white/10 border ${error ? "border-red-500" : "border-white/20"} p-3 rounded text-white focus:outline-none focus:border-indigo-500 transition-colors`}
//       value={value}
//       onChange={onChange}
//       placeholder={placeholder}
//     />
//     {error && <p className="text-red-400 text-xs mt-1">{error}</p>}
//   </div>
// );

// export default function ApplyForm({ embedded = false, onClose }) {
//   const [step, setStep] = useState(0);
//   const [data, setData] = useState(initialData);
//   const [errors, setErrors] = useState({});
//   const [loading, setLoading] = useState(false);
//   const navigate = useNavigate();

//   // --- VALIDATION RULES ---
//   const validate = (name, value) => {
//     let error = "";
//     const cnicRegex = /^\d{5}-\d{7}-\d{1}$/;
//     const phoneRegex = /^03\d{9}$/;
//     const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
//     const nameRegex = /^[a-zA-Z\s]{3,50}$/;

//     switch (name) {
//       case "student_name":
//       case "father_name":
//       case "mother_name":
//       case "guardian_name":
//         if (!nameRegex.test(value)) error = "Enter a valid name (letters only, min 3 chars)";
//         break;
//       case "student_cnic":
//       case "father_cnic":
//       case "guardian_cnic":
//         if (!cnicRegex.test(value)) error = "Format: 00000-0000000-0";
//         break;
//       case "mobile":
//       case "father_phone":
//       case "guardian_mobile":
//         if (!phoneRegex.test(value)) error = "Format: 03XXXXXXXXX (11 digits)";
//         break;
//       case "email":
//         if (!emailRegex.test(value)) error = "Invalid email address";
//         break;
//       case "dob":
//         if (!value) {
//           error = "Date of birth is required";
//         } else {
//           const birthDate = new Date(value);
//           const today = new Date();
//           if (birthDate > today) {
//             error = "Date cannot be in the future";
//           } else {
//             let age = today.getFullYear() - birthDate.getFullYear();
//             const m = today.getMonth() - birthDate.getMonth();
//             if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
//               age--;
//             }
//             if (age < 14 || age > 50) error = "Age must be between 14 and 50";
//           }
//         }
//         break;
//       case "matric_obtained":
//         if (Number(value) < 0 || Number(value) > 1100) error = "Marks must be between 0-1100";
//         break;
//       case "inter_part_one":
//         if (Number(value) < 0 || Number(value) > 550) error = "Marks must be between 0-550";
//         break;
//       case "address":
//         if (value.length < 10) error = "Please provide a complete address";
//         break;
//       case "domicile":
//       case "province":
//       case "city":
//       case "board":
//       case "matric_roll":
//       case "inter_roll":
//         if (!value || value.length < 2) error = "This field is required";
//         break;
//       default:
//         break;
//     }
//     return error;
//   };

//   // --- STEP COMPLETION LOGIC ---
//   const isStepValid = useMemo(() => {
//     const checkFields = (fields) => {
//       return fields.every(f => data[f] && !errors[f]);
//     };

//     const steps = {
//       0: () => checkFields(["student_name", "student_cnic", "father_name", "dob", "domicile"]),
//       1: () => checkFields(["email", "mobile", "province", "city", "father_phone", "father_cnic", "mother_name", "guardian_name", "guardian_mobile", "guardian_cnic", "address"]),
//       2: () => checkFields(["matric_roll", "board", "matric_obtained", "inter_roll", "inter_part_one"]),
//       3: () => data.preference1 && data.preference2 && data.preference3 &&
//                (new Set([data.preference1, data.preference2, data.preference3]).size === 3),
//       4: () => data.photo && data.matric_degree && data.inter_degree,
//     };
//     return steps[step] ? steps[step]() : false;
//   }, [data, errors, step]);

//   const update = (field) => (e) => {
//     let value = e.target.files ? e.target.files[0] : e.target.value;
    
//     // Auto-formatting for CNIC
//     if (field.includes("cnic") && !e.target.files) {
//       value = value.replace(/\D/g, "").substring(0, 13);
//       if (value.length > 5 && value.length <= 12) value = `${value.slice(0, 5)}-${value.slice(5)}`;
//       else if (value.length > 12) value = `${value.slice(0, 5)}-${value.slice(5, 12)}-${value.slice(12, 13)}`;
//     }

//     const error = validate(field, value);
//     setErrors(prev => ({ ...prev, [field]: error }));
//     setData(prev => ({ ...prev, [field]: value }));
//   };

//   const copyFatherToGuardian = () => {
//     const newData = {
//         ...data,
//         guardian_name: data.father_name,
//         guardian_mobile: data.father_phone,
//         guardian_cnic: data.father_cnic
//     };
//     setData(newData);
//     setErrors(prev => ({
//         ...prev,
//         guardian_name: validate("guardian_name", data.father_name),
//         guardian_mobile: validate("guardian_mobile", data.father_phone),
//         guardian_cnic: validate("guardian_cnic", data.father_cnic)
//     }));
//   };

//   const onSubmit = async (e) => {
//     e.preventDefault();
//     if (!isStepValid) return;
//     setLoading(true);

//     const formData = new FormData();
//     Object.keys(data).forEach(key => {
//         if (data[key] instanceof File) formData.append(key, data[key]);
//         else formData.append(key, data[key]);
//     });

//     try {
//         await api.post("/student/profile/", formData);
//         alert("Application Submitted Successfully!");
//         embedded && onClose ? onClose() : navigate("/dashboard");
//     } catch (err) {
//         alert("Submission Error: Check all fields.");
//     } finally { setLoading(false); }
//   };

//   return (
//     <section className={`min-h-screen flex items-start justify-center bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] ${embedded ? "pt-0" : "pt-28 md:pt-36 pb-20"}`}>
//       <div className="w-full max-w-6xl px-6">
//         <div className="bg-white/10 border border-white/20 rounded-[24px] shadow-2xl overflow-hidden">
//           <div className="grid grid-cols-1 md:grid-cols-3">
            
//             <aside className="bg-[#4F3C61]/80 p-8">
//               <nav className="space-y-6">
//                 {stepTitles.map((title, idx) => (
//                   <div key={title} className="flex items-center gap-4">
//                     <div className={`w-8 h-8 rounded-full border flex items-center justify-center text-sm ${idx === step ? "bg-white text-[#4F3C61]" : idx < step ? "bg-green-500 border-green-500 text-white" : "text-white/60 border-white/20"}`}>
//                       {idx < step ? "✓" : idx + 1}
//                     </div>
//                     <span className={idx === step ? "text-white font-medium" : "text-white/50"}>{title}</span>
//                   </div>
//                 ))}
//               </nav>
//             </aside>

//             <div className="md:col-span-2 p-10 bg-white/5 text-white">
//               <h2 className="text-3xl font-semibold mb-2">{stepTitles[step]}</h2>
//               <p className="text-white/50 mb-8 text-sm italic">* Validation is strictly enforced for security</p>

//               <form onSubmit={onSubmit}>
//                 <AnimatePresence mode="wait">
//                   {step === 0 && (
//                     <motion.div key="s0" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
//                       <div className="col-span-2">
//                         <InputField label="Full Name" value={data.student_name} error={errors.student_name} onChange={update("student_name")} />
//                       </div>
//                       <InputField label="Student CNIC" value={data.student_cnic} error={errors.student_cnic} onChange={update("student_cnic")} placeholder="xxxxx-xxxxxxx-x" />
//                       <InputField label="Father's Name" value={data.father_name} error={errors.father_name} onChange={update("father_name")} />
//                       <InputField label="Domicile District" value={data.domicile} error={errors.domicile} onChange={update("domicile")} />
//                       <InputField label="Date of Birth" value={data.dob} error={errors.dob} onChange={update("dob")} type="date" />
//                     </motion.div>
//                   )}

//                   {step === 1 && (
//                     <motion.div key="s1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
//                       <InputField label="Father's CNIC" value={data.father_cnic} error={errors.father_cnic} onChange={update("father_cnic")} />
//                       <InputField label="Father's Mobile" value={data.father_phone} error={errors.father_phone} onChange={update("father_phone")} />
//                       <div className="col-span-2">
//                         <InputField label="Mother's Name" value={data.mother_name} error={errors.mother_name} onChange={update("mother_name")} />
//                       </div>
                      
//                       <div className="col-span-2 flex justify-between items-center border-t border-white/10 pt-4">
//                         <label className="text-sm font-bold text-indigo-300">Guardian Details</label>
//                         <button type="button" onClick={copyFatherToGuardian} className="text-xs bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded border border-indigo-500/30 hover:bg-indigo-500/40 transition">Copy Father's Info</button>
//                       </div>
//                       <InputField label="Guardian Name" value={data.guardian_name} error={errors.guardian_name} onChange={update("guardian_name")} />
//                       <InputField label="Guardian Mobile" value={data.guardian_mobile} error={errors.guardian_mobile} onChange={update("guardian_mobile")} />
//                       <div className="col-span-2">
//                         <InputField label="Guardian CNIC" value={data.guardian_cnic} error={errors.guardian_cnic} onChange={update("guardian_cnic")} />
//                       </div>

//                       <InputField label="Student Email" value={data.email} error={errors.email} onChange={update("email")} type="email" />
//                       <InputField label="Student Mobile" value={data.mobile} error={errors.mobile} onChange={update("mobile")} />
//                       <InputField label="Province" value={data.province} error={errors.province} onChange={update("province")} />
//                       <InputField label="City" value={data.city} error={errors.city} onChange={update("city")} />
//                       <div className="col-span-2">
//                         <label className="text-sm text-white/70 mb-1 block">Residential Address</label>
//                         <textarea
//                           className={`w-full bg-white/10 border ${errors.address ? "border-red-500" : "border-white/20"} p-3 rounded text-white h-20 outline-none focus:border-indigo-500 transition-colors`}
//                           value={data.address}
//                           onChange={update("address")}
//                         />
//                         {errors.address && <p className="text-red-400 text-xs mt-1">{errors.address}</p>}
//                       </div>
//                     </motion.div>
//                   )}

//                   {step === 2 && (
//                     <motion.div key="s2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
//                       <InputField label="Matric Roll #" value={data.matric_roll} error={errors.matric_roll} onChange={update("matric_roll")} />
//                       <InputField label="Board Name" value={data.board} error={errors.board} onChange={update("board")} />
//                       <InputField label="Matric Obtained Marks" value={data.matric_obtained} error={errors.matric_obtained} onChange={update("matric_obtained")} type="number" />
//                       <InputField label="Inter Roll #" value={data.inter_roll} error={errors.inter_roll} onChange={update("inter_roll")} />
//                       <InputField label="Inter Part-I Marks" value={data.inter_part_one} error={errors.inter_part_one} onChange={update("inter_part_one")} type="number" />
//                     </motion.div>
//                   )}

//                   {step === 3 && (
//                     <motion.div key="s3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
//                       {[1, 2, 3].map(i => (
//                         <div key={i}>
//                           <label className="text-sm text-white/70 mb-2 block">Preference {i}</label>
//                           <select
//                             className="w-full bg-[#1A1138] border border-white/20 p-3 rounded text-white outline-none focus:border-indigo-500 transition-colors"
//                             value={data[`preference${i}`]}
//                             onChange={update(`preference${i}`)}
//                           >
//                             <option value="">Select Degree</option>
//                             <option value="BSCS">BS Computer Science</option>
//                             <option value="BSSE">BS Software Engineering</option>
//                             <option value="BSIT">BS Information Technology</option>
//                           </select>
//                         </div>
//                       ))}
//                     </motion.div>
//                   )}

//                   {step === 4 && (
//                     <motion.div key="s4" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="grid grid-cols-1 gap-6">
//                       <div className="bg-white/5 p-4 rounded-lg border border-dashed border-white/30">
//                         <label className="text-sm text-white/70 mb-2 block">Profile Photo (JPG/PNG)</label>
//                         <input type="file" accept="image/*" className="w-full text-white text-sm cursor-pointer" onChange={update("photo")} />
//                       </div>
//                       <div className="bg-white/5 p-4 rounded-lg border border-dashed border-white/30">
//                         <label className="text-sm text-white/70 mb-2 block">Matric Certificate (PDF/Image)</label>
//                         <input type="file" accept="image/*,.pdf" className="w-full text-white text-sm cursor-pointer" onChange={update("matric_degree")} />
//                       </div>
//                       <div className="bg-white/5 p-4 rounded-lg border border-dashed border-white/30">
//                         <label className="text-sm text-white/70 mb-2 block">Inter Certificate (PDF/Image)</label>
//                         <input type="file" accept="image/*,.pdf" className="w-full text-white text-sm cursor-pointer" onChange={update("inter_degree")} />
//                       </div>
//                       <div className="bg-white/5 p-4 rounded-lg border border-dashed border-white/30">
//       <label className="text-sm text-white/70 mb-2 block">Domicile Certificate (PDF/Image)</label>
//       <input type="file" accept="image/*,.pdf" className="w-full text-white text-sm cursor-pointer" onChange={update("domicile_upload")} />
//     </div>
//                     </motion.div>
//                   )}
//                 </AnimatePresence>

//                 <div className="mt-12 flex justify-between">
//                   <button type="button" onClick={() => setStep(s => s - 1)} disabled={step === 0} className="px-8 py-2 rounded-full border border-white/20 text-white hover:bg-white/10 disabled:opacity-30">Back</button>
//                   {step < 4 ? (
//                     <button type="button" onClick={() => setStep(s => s + 1)} disabled={!isStepValid} className="px-10 py-2 rounded-full bg-white text-black font-bold hover:bg-indigo-100 disabled:opacity-30 transition-all">Next Step</button>
//                   ) : (
//                     <button type="submit" disabled={loading || !isStepValid} className="px-10 py-2 rounded-full bg-indigo-500 text-white font-bold hover:bg-indigo-600 disabled:opacity-30 shadow-lg transition-all">
//                       {loading ? "Processing..." : "Submit Application"}
//                     </button>
//                   )}
//                 </div>
//               </form>
//             </div>
//           </div>
//         </div>
//       </div>
//     </section>
//   );
// }

import React, { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import { mediaUrl, notifyProfileUpdated } from "../utils/useProfilePhoto";
import BackToDashboard from "./BackToDashboard";

const stepTitles = [
  "Personal details",
  "Guardian & Contact",
  "Academic Background",
  "Program Preferences",
  "Document Uploads",
];

// --- EXPANDED DEGREE OPTIONS ---
export const DEGREE_OPTIONS = [
  // Computer & IT
  { group: "Computer & IT", options: [
    { value: "BSCS", label: "BS Computer Science" },
    { value: "BSSE", label: "BS Software Engineering" },
    { value: "BSIT", label: "BS Information Technology" },
    { value: "BSAI", label: "BS Artificial Intelligence" },
    { value: "BSDS", label: "BS Data Science" },
    { value: "BSCY", label: "BS Cybersecurity" },
    { value: "BSGD", label: "BS Game Development" },
    { value: "BSNE", label: "BS Network Engineering" },
  ]},
  // Engineering
  { group: "Engineering", options: [
    { value: "BEEE", label: "BE Electrical Engineering" },
    { value: "BEME", label: "BE Mechanical Engineering" },
    { value: "BECE", label: "BE Civil Engineering" },
    { value: "BECH", label: "BE Chemical Engineering" },
    { value: "BETEL", label: "BE Telecommunication Engineering" },
    { value: "BEENV", label: "BE Environmental Engineering" },
    { value: "BEINDT", label: "BE Industrial & Manufacturing Engineering" },
    { value: "BEPET", label: "BE Petroleum Engineering" },
    { value: "BEMED", label: "BE Mechatronics Engineering" },
    { value: "BEARCH", label: "BS Architecture" },
  ]},
  // Medical & Health Sciences
  { group: "Medical & Health Sciences", options: [
    { value: "MBBS", label: "MBBS (Medicine & Surgery)" },
    { value: "BDS", label: "BDS (Dental Surgery)" },
    { value: "BPHARM", label: "BS Pharmacy" },
    { value: "BNURSING", label: "BS Nursing" },
    { value: "BPHT", label: "BS Physiotherapy" },
    { value: "BMLT", label: "BS Medical Lab Technology" },
    { value: "BPUBH", label: "BS Public Health" },
    { value: "BNUTR", label: "BS Nutrition & Dietetics" },
  ]},
  // Business & Management
  { group: "Business & Management", options: [
    { value: "BBA", label: "BBA (Business Administration)" },
    { value: "BSACC", label: "BS Accounting & Finance" },
    { value: "BSECO", label: "BS Economics" },
    { value: "BSIB", label: "BS Islamic Banking & Finance" },
    { value: "BSHRM", label: "BS Human Resource Management" },
    { value: "BSMKT", label: "BS Marketing" },
    { value: "BSCOM", label: "BS Commerce" },
  ]},
  // Social Sciences & Humanities
  { group: "Social Sciences & Humanities", options: [
    { value: "BSPSY", label: "BS Psychology" },
    { value: "BSSOC", label: "BS Sociology" },
    { value: "BSPOL", label: "BS Political Science" },
    { value: "BSIR", label: "BS International Relations" },
    { value: "BSLAW", label: "LLB (Law)" },
    { value: "BSMAS", label: "BS Mass Communication" },
    { value: "BSENG", label: "BS English Literature" },
    { value: "BSURDU", label: "BS Urdu Literature" },
    { value: "BSHIST", label: "BS History" },
    { value: "BSISLS", label: "BS Islamic Studies" },
  ]},
  // Natural Sciences
  { group: "Natural Sciences", options: [
    { value: "BSPHY", label: "BS Physics" },
    { value: "BSCHEM", label: "BS Chemistry" },
    { value: "BSMATH", label: "BS Mathematics" },
    { value: "BSBIO", label: "BS Biology / Zoology" },
    { value: "BSBOT", label: "BS Botany" },
    { value: "BSBTECH", label: "BS Biotechnology" },
    { value: "BSENV", label: "BS Environmental Science" },
    { value: "BSGEO", label: "BS Geography" },
  ]},
  // Education & Arts
  { group: "Education & Arts", options: [
    { value: "BSED", label: "BS Education" },
    { value: "BED", label: "B.Ed (Education)" },
    { value: "BSFA", label: "BS Fine Arts" },
    { value: "BSDES", label: "BS Graphic Design" },
    { value: "BSFASH", label: "BS Fashion Design" },
    { value: "BSMUSI", label: "BS Music" },
    { value: "BSSPORT", label: "BS Sports Sciences" },
  ]},
  // Agriculture & Food
  { group: "Agriculture & Food", options: [
    { value: "BSAGRI", label: "BS Agriculture" },
    { value: "BSFOOD", label: "BS Food Science & Technology" },
    { value: "BSVETS", label: "BS Veterinary Science (DVM)" },
    { value: "BSHORT", label: "BS Horticulture" },
  ]},
];

const initialData = {
  student_name: "", student_cnic: "", father_name: "", gender: "Male",
  dob: "", domicile: "", religion: "Islam", nationality: "Pakistani",
  father_cnic: "", father_phone: "", mother_name: "", guardian_name: "",
  guardian_mobile: "", guardian_cnic: "", mobile: "", email: "",
  province: "", city: "", address: "", matric_roll: "", board: "",
  matric_obtained: "", matric_total: "1100", inter_roll: "",
  inter_part_one: "", inter_total: "550", preference1: "",
  preference2: "", preference3: "", photo: null, matric_degree: null,
  inter_degree: null, domicile_upload: null, hafiz_quran: false,
  hostel: false, father_income: 0,
};

const FILE_FIELDS = ["photo", "matric_degree", "inter_degree", "domicile_upload"];

export { mediaUrl };

const InputField = ({ label, value, error, onChange, type = "text", placeholder = "" }) => (
  <div className="w-full">
    <label className="text-sm text-white/70 mb-1 block">{label}</label>
    <input
      type={type}
      className={`w-full bg-white/10 border ${error ? "border-red-500" : "border-white/20"} p-3 rounded text-white focus:outline-none focus:border-indigo-500 transition-colors`}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
    />
    {error && <p className="text-red-400 text-xs mt-1">{error}</p>}
  </div>
);

// Grouped select for degree preferences
const DegreeSelect = ({ label, value, onChange, exclude = [] }) => (
  <div>
    <label className="text-sm text-white/70 mb-2 block">{label}</label>
    <div className="relative">
      <select
        className="w-full bg-[#1A1138] border border-white/20 p-3 rounded text-white outline-none focus:border-indigo-500 transition-colors appearance-none pr-10"
        value={value}
        onChange={onChange}
      >
        <option value="">— Select a Discipline —</option>
        {DEGREE_OPTIONS.map(({ group, options }) => (
          <optgroup key={group} label={group}>
            {options
              .filter(o => !exclude.includes(o.value) || o.value === value)
              .map(o => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
          </optgroup>
        ))}
      </select>
      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
        <svg className="w-4 h-4 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  </div>
);

export default function ApplyForm({ embedded = false, onClose }) {
  const [step, setStep] = useState(0);
  const [data, setData] = useState(initialData);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [existingFiles, setExistingFiles] = useState({});
  const navigate = useNavigate();

  // If the student already submitted an application, load it so they edit it instead of starting over
  useEffect(() => {
    let cancelled = false;
    api.get("/student/profile/")
      .then(({ data: profile }) => {
        if (cancelled || !profile) return;
        const loaded = {};
        Object.keys(initialData).forEach(key => {
          if (FILE_FIELDS.includes(key)) return;
          const value = profile[key];
          loaded[key] = value === null || value === undefined ? initialData[key] : value;
        });
        setData(prev => ({ ...prev, ...loaded }));
        setExistingFiles(Object.fromEntries(FILE_FIELDS.map(key => [key, profile[key]])));
        setIsEdit(true);
      })
      .catch(() => {}); // No application yet: show the empty form
    return () => { cancelled = true; };
  }, []);

  const validate = (name, value) => {
    let error = "";
    const cnicRegex = /^\d{5}-\d{7}-\d{1}$/;
    const phoneRegex = /^03\d{9}$/;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const nameRegex = /^[a-zA-Z\s]{3,50}$/;

    switch (name) {
      case "student_name": case "father_name": case "mother_name": case "guardian_name":
        if (!nameRegex.test(value)) error = "Enter a valid name (letters only, min 3 chars)"; break;
      case "student_cnic": case "father_cnic": case "guardian_cnic":
        if (!cnicRegex.test(value)) error = "Format: 00000-0000000-0"; break;
      case "mobile": case "father_phone": case "guardian_mobile":
        if (!phoneRegex.test(value)) error = "Format: 03XXXXXXXXX (11 digits)"; break;
      case "email":
        if (!emailRegex.test(value)) error = "Invalid email address"; break;
      case "dob":
        if (!value) { error = "Date of birth is required"; }
        else {
          const birthDate = new Date(value); const today = new Date();
          if (birthDate > today) { error = "Date cannot be in the future"; }
          else {
            let age = today.getFullYear() - birthDate.getFullYear();
            const m = today.getMonth() - birthDate.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) age--;
            if (age < 14 || age > 50) error = "Age must be between 14 and 50";
          }
        }
        break;
      case "matric_obtained":
        if (Number(value) < 0 || Number(value) > 1100) error = "Marks must be between 0-1100"; break;
      case "inter_part_one":
        if (Number(value) < 0 || Number(value) > 550) error = "Marks must be between 0-550"; break;
      case "address":
        if (value.length < 10) error = "Please provide a complete address"; break;
      case "domicile": case "province": case "city": case "board": case "matric_roll": case "inter_roll":
        if (!value || value.length < 2) error = "This field is required"; break;
      default: break;
    }
    return error;
  };

  const isStepValid = useMemo(() => {
    const checkFields = (fields) => fields.every(f => data[f] && !errors[f]);
    const steps = {
      0: () => checkFields(["student_name", "student_cnic", "father_name", "dob", "domicile"]),
      1: () => checkFields(["email", "mobile", "province", "city", "father_phone", "father_cnic", "mother_name", "guardian_name", "guardian_mobile", "guardian_cnic", "address"]),
      2: () => checkFields(["matric_roll", "board", "matric_obtained", "inter_roll", "inter_part_one"]),
      3: () => data.preference1 && data.preference2 && data.preference3 &&
               (new Set([data.preference1, data.preference2, data.preference3]).size === 3),
      // Previously uploaded documents count, so editing doesn't force re-uploads
      4: () => ["photo", "matric_degree", "inter_degree"].every(f => data[f] || existingFiles[f]),
    };
    return steps[step] ? steps[step]() : false;
  }, [data, errors, step, existingFiles]);

  const update = (field) => (e) => {
    let value = e.target.files ? e.target.files[0] : e.target.value;
    if (field.includes("cnic") && !e.target.files) {
      value = value.replace(/\D/g, "").substring(0, 13);
      if (value.length > 5 && value.length <= 12) value = `${value.slice(0, 5)}-${value.slice(5)}`;
      else if (value.length > 12) value = `${value.slice(0, 5)}-${value.slice(5, 12)}-${value.slice(12, 13)}`;
    }
    const error = validate(field, value);
    setErrors(prev => ({ ...prev, [field]: error }));
    setData(prev => ({ ...prev, [field]: value }));
  };

  const copyFatherToGuardian = () => {
    setData(d => ({ ...d, guardian_name: d.father_name, guardian_mobile: d.father_phone, guardian_cnic: d.father_cnic }));
    setErrors(prev => ({
      ...prev,
      guardian_name: validate("guardian_name", data.father_name),
      guardian_mobile: validate("guardian_mobile", data.father_phone),
      guardian_cnic: validate("guardian_cnic", data.father_cnic),
    }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!isStepValid) return;
    setLoading(true);
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      // Only send files the student actually picked; when editing, the saved ones are kept
      if (FILE_FIELDS.includes(key) && !(data[key] instanceof File)) return;
      formData.append(key, data[key]);
    });
    try {
      if (isEdit) {
        await api.patch("/student/profile/edit/", formData);
        notifyProfileUpdated();
        alert("Application Updated Successfully!");
        embedded && onClose ? onClose() : navigate("/my-application");
      } else {
        await api.post("/student/profile/", formData);
        notifyProfileUpdated();
        alert("Application Submitted Successfully!");
        embedded && onClose ? onClose() : navigate("/dashboard");
      }
    } catch (err) {
      alert(`${isEdit ? "Update" : "Submission"} Error: Check all fields.`);
    } finally { setLoading(false); }
  };

  // Already-chosen preferences to prevent duplicates
  const chosenPrefs = [data.preference1, data.preference2, data.preference3].filter(Boolean);

  return (
    <section className={`min-h-screen flex items-start justify-center bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] ${embedded ? "pt-0" : "pt-28 md:pt-36 pb-20"}`}>
      <div className="w-full max-w-6xl px-4 sm:px-6">
        {!embedded && <BackToDashboard className="mb-6" />}
        <div className="bg-white/10 border border-white/20 rounded-[24px] shadow-2xl overflow-hidden">
          <div className="grid grid-cols-1 md:grid-cols-3">

            <aside className="bg-[#4F3C61]/80 p-5 md:p-8">
              {/* Phones: compact progress instead of the full step list */}
              <div className="md:hidden">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white font-medium">{stepTitles[step]}</span>
                  <span className="text-white/60">Step {step + 1} of {stepTitles.length}</span>
                </div>
                <div className="mt-3 h-1.5 rounded-full bg-white/15 overflow-hidden">
                  <div className="h-full rounded-full bg-white transition-all duration-300" style={{ width: `${((step + 1) / stepTitles.length) * 100}%` }} />
                </div>
              </div>
              <nav className="hidden md:block space-y-6">
                {stepTitles.map((title, idx) => (
                  <div key={title} className="flex items-center gap-4">
                    <div className={`w-8 h-8 rounded-full border flex items-center justify-center text-sm shrink-0 ${idx === step ? "bg-white text-[#4F3C61]" : idx < step ? "bg-green-500 border-green-500 text-white" : "text-white/60 border-white/20"}`}>
                      {idx < step ? "✓" : idx + 1}
                    </div>
                    <span className={idx === step ? "text-white font-medium" : "text-white/50"}>{title}</span>
                  </div>
                ))}
              </nav>
            </aside>

            <div className="md:col-span-2 p-5 sm:p-8 md:p-10 bg-white/5 text-white">
              <h2 className="text-2xl sm:text-3xl font-semibold mb-2">{stepTitles[step]}</h2>
              <p className="text-white/50 mb-8 text-sm italic">* Validation is strictly enforced for security</p>
              {isEdit && (
                <div className="mb-8 p-4 rounded-lg bg-indigo-500/10 border border-indigo-400/30 text-sm text-indigo-100">
                  You are editing your submitted application. Your saved details are filled in below.
                </div>
              )}

              <form onSubmit={onSubmit}>
                <AnimatePresence mode="wait">

                  {step === 0 && (
                    <motion.div key="s0" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="md:col-span-2">
                        <InputField label="Full Name" value={data.student_name} error={errors.student_name} onChange={update("student_name")} />
                      </div>
                      <InputField label="Student CNIC" value={data.student_cnic} error={errors.student_cnic} onChange={update("student_cnic")} placeholder="xxxxx-xxxxxxx-x" />
                      <InputField label="Father's Name" value={data.father_name} error={errors.father_name} onChange={update("father_name")} />
                      <InputField label="Domicile District" value={data.domicile} error={errors.domicile} onChange={update("domicile")} />
                      <InputField label="Date of Birth" value={data.dob} error={errors.dob} onChange={update("dob")} type="date" />
                    </motion.div>
                  )}

                  {step === 1 && (
                    <motion.div key="s1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <InputField label="Father's CNIC" value={data.father_cnic} error={errors.father_cnic} onChange={update("father_cnic")} />
                      <InputField label="Father's Mobile" value={data.father_phone} error={errors.father_phone} onChange={update("father_phone")} />
                      <div className="md:col-span-2">
                        <InputField label="Mother's Name" value={data.mother_name} error={errors.mother_name} onChange={update("mother_name")} />
                      </div>
                      <div className="md:col-span-2 flex justify-between items-center border-t border-white/10 pt-4">
                        <label className="text-sm font-bold text-indigo-300">Guardian Details</label>
                        <button type="button" onClick={copyFatherToGuardian} className="text-xs bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded border border-indigo-500/30 hover:bg-indigo-500/40 transition">Copy Father's Info</button>
                      </div>
                      <InputField label="Guardian Name" value={data.guardian_name} error={errors.guardian_name} onChange={update("guardian_name")} />
                      <InputField label="Guardian Mobile" value={data.guardian_mobile} error={errors.guardian_mobile} onChange={update("guardian_mobile")} />
                      <div className="md:col-span-2">
                        <InputField label="Guardian CNIC" value={data.guardian_cnic} error={errors.guardian_cnic} onChange={update("guardian_cnic")} />
                      </div>
                      <InputField label="Student Email" value={data.email} error={errors.email} onChange={update("email")} type="email" />
                      <InputField label="Student Mobile" value={data.mobile} error={errors.mobile} onChange={update("mobile")} />
                      <InputField label="Province" value={data.province} error={errors.province} onChange={update("province")} />
                      <InputField label="City" value={data.city} error={errors.city} onChange={update("city")} />
                      <div className="md:col-span-2">
                        <label className="text-sm text-white/70 mb-1 block">Residential Address</label>
                        <textarea className={`w-full bg-white/10 border ${errors.address ? "border-red-500" : "border-white/20"} p-3 rounded text-white h-20 outline-none focus:border-indigo-500 transition-colors`} value={data.address} onChange={update("address")} />
                        {errors.address && <p className="text-red-400 text-xs mt-1">{errors.address}</p>}
                      </div>
                    </motion.div>
                  )}

                  {step === 2 && (
                    <motion.div key="s2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <InputField label="Matric Roll #" value={data.matric_roll} error={errors.matric_roll} onChange={update("matric_roll")} />
                      <InputField label="Board Name" value={data.board} error={errors.board} onChange={update("board")} />
                      <InputField label="Matric Obtained Marks" value={data.matric_obtained} error={errors.matric_obtained} onChange={update("matric_obtained")} type="number" />
                      <InputField label="Inter Roll #" value={data.inter_roll} error={errors.inter_roll} onChange={update("inter_roll")} />
                      <InputField label="Inter Part-I Marks" value={data.inter_part_one} error={errors.inter_part_one} onChange={update("inter_part_one")} type="number" />
                    </motion.div>
                  )}

                  {step === 3 && (
                    <motion.div key="s3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
                      <p className="text-white/50 text-xs -mt-4">Each preference must be a different discipline.</p>
                      <DegreeSelect
                        label="1st Preference"
                        value={data.preference1}
                        onChange={update("preference1")}
                        exclude={[data.preference2, data.preference3].filter(Boolean)}
                      />
                      <DegreeSelect
                        label="2nd Preference"
                        value={data.preference2}
                        onChange={update("preference2")}
                        exclude={[data.preference1, data.preference3].filter(Boolean)}
                      />
                      <DegreeSelect
                        label="3rd Preference"
                        value={data.preference3}
                        onChange={update("preference3")}
                        exclude={[data.preference1, data.preference2].filter(Boolean)}
                      />
                    </motion.div>
                  )}

                  {step === 4 && (
                    <motion.div key="s4" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="grid grid-cols-1 gap-6">
                      {[
                        { key: "photo", label: "Profile Photo (JPG/PNG)", accept: "image/*" },
                        { key: "matric_degree", label: "Matric Certificate (PDF/Image)", accept: "image/*,.pdf" },
                        { key: "inter_degree", label: "Inter Certificate (PDF/Image)", accept: "image/*,.pdf" },
                        { key: "domicile_upload", label: "Domicile Certificate (PDF/Image)", accept: "image/*,.pdf" },
                      ].map(({ key, label, accept }) => (
                        <div key={key} className="bg-white/5 p-4 rounded-lg border border-dashed border-white/30">
                          <label className="text-sm text-white/70 mb-2 block">{label}</label>
                          {existingFiles[key] && (
                            <p className="text-xs text-white/50 mb-2">
                              Already uploaded —{" "}
                              <a href={mediaUrl(existingFiles[key])} target="_blank" rel="noreferrer" className="text-indigo-300 underline">view current file</a>
                              . Choose a new file only if you want to replace it.
                            </p>
                          )}
                          <input type="file" accept={accept} className="w-full text-white text-sm cursor-pointer" onChange={update(key)} />
                        </div>
                      ))}
                    </motion.div>
                  )}

                </AnimatePresence>

                <div className="mt-12 flex justify-between">
                  <button type="button" onClick={() => setStep(s => s - 1)} disabled={step === 0} className="px-8 py-2 rounded-full border border-white/20 text-white hover:bg-white/10 disabled:opacity-30">Back</button>
                  {step < 4 ? (
                    <button type="button" onClick={() => setStep(s => s + 1)} disabled={!isStepValid} className="px-10 py-2 rounded-full bg-white text-black font-bold hover:bg-indigo-100 disabled:opacity-30 transition-all">Next Step</button>
                  ) : (
                    <button type="submit" disabled={loading || !isStepValid} className="px-10 py-2 rounded-full bg-indigo-500 text-white font-bold hover:bg-indigo-600 disabled:opacity-30 shadow-lg transition-all">
                      {loading ? "Processing..." : isEdit ? "Save Changes" : "Submit Application"}
                    </button>
                  )}
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}