import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import { DEGREE_OPTIONS, mediaUrl } from "./ApplyForm";

const DEGREE_LABELS = Object.fromEntries(
  DEGREE_OPTIONS.flatMap(({ options }) => options.map(o => [o.value, o.label]))
);

const yesNo = (v) => (v ? "Yes" : "No");
const marks = (obtained, total) =>
  obtained === null || obtained === undefined || obtained === "" ? null : `${obtained} / ${total || "—"}`;

export default function ApplicationView() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/student/profile/")
      .then(({ data }) => setProfile(data))
      .catch(() => setProfile(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B0620] flex items-center justify-center">
        <div className="w-10 h-10 border-2 border-t-purple-500 border-white/10 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!profile) {
    return (
      <section className="min-h-screen bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] text-white pt-36 px-6">
        <div className="max-w-xl mx-auto text-center bg-white/10 border border-white/20 rounded-[2rem] p-10">
          <h1 className="text-3xl font-bold mb-3">No application yet</h1>
          <p className="text-white/60 mb-8">You haven't submitted your application form. Fill it in once and we'll reuse it for every university.</p>
          <div className="flex justify-center gap-4">
            <button onClick={() => navigate("/dashboard")} className="px-6 py-2.5 rounded-full border border-white/20 hover:bg-white/10 transition">Back to Dashboard</button>
            <button onClick={() => navigate("/apply")} className="px-6 py-2.5 rounded-full bg-white text-black font-bold hover:bg-purple-100 transition">Fill Application Form</button>
          </div>
        </div>
      </section>
    );
  }

  const sections = [
    {
      title: "Personal Information",
      items: [
        ["Full Name", profile.student_name],
        ["Student CNIC", profile.student_cnic],
        ["Date of Birth", profile.dob],
        ["Gender", profile.gender],
        ["Religion", profile.religion],
        ["Nationality", profile.nationality],
        ["Domicile District", profile.domicile],
        ["Hafiz-e-Quran", yesNo(profile.hafiz_quran)],
        ["Hostel Required", yesNo(profile.hostel)],
      ],
    },
    {
      title: "Contact Details",
      items: [
        ["Email", profile.email],
        ["Mobile", profile.mobile],
        ["Province", profile.province],
        ["City", profile.city],
        ["Address", profile.address, true],
      ],
    },
    {
      title: "Family & Guardian",
      items: [
        ["Father's Name", profile.father_name],
        ["Father's CNIC", profile.father_cnic],
        ["Father's Mobile", profile.father_phone],
        ["Mother's Name", profile.mother_name],
        ["Guardian Name", profile.guardian_name],
        ["Guardian Mobile", profile.guardian_mobile],
        ["Guardian CNIC", profile.guardian_cnic],
      ],
    },
    {
      title: "Academic Record",
      items: [
        ["Board", profile.board],
        ["Matric Roll #", profile.matric_roll],
        ["Matric Marks", marks(profile.matric_obtained, profile.matric_total)],
        ["Inter Roll #", profile.inter_roll],
        ["Inter Part-I Marks", marks(profile.inter_part_one, profile.inter_total)],
      ],
    },
    {
      title: "Degree Preferences",
      items: [
        ["1st Preference", DEGREE_LABELS[profile.preference1] || profile.preference1],
        ["2nd Preference", DEGREE_LABELS[profile.preference2] || profile.preference2],
        ["3rd Preference", DEGREE_LABELS[profile.preference3] || profile.preference3],
      ],
    },
  ];

  const documents = [
    ["Profile Photo", profile.photo],
    ["Matric Certificate", profile.matric_degree],
    ["Inter Certificate", profile.inter_degree],
    ["Domicile Certificate", profile.domicile_upload],
  ];

  return (
    <section className="min-h-screen bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] text-white pt-28 md:pt-36 pb-20 px-6">
      <div className="max-w-6xl mx-auto">
        <header className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-white/10 pb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2 tracking-tight">My Application Form</h1>
            <p className="text-white/60">
              The details you submitted
              {profile.created_at && ` on ${new Date(profile.created_at).toLocaleDateString()}`}.
            </p>
          </div>
          <div className="flex gap-3">
            <button onClick={() => navigate("/dashboard")} className="px-6 py-2.5 rounded-full border border-white/20 hover:bg-white/10 transition">Back to Dashboard</button>
            <button onClick={() => navigate("/apply")} className="px-6 py-2.5 rounded-full bg-white text-black font-bold hover:bg-purple-100 transition">Edit Application</button>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {sections.map(({ title, items }) => (
            <section key={title} className="bg-white/10 border border-white/20 rounded-[2rem] p-8 backdrop-blur-xl">
              <h3 className="text-sm font-bold text-white/50 uppercase tracking-widest mb-6 border-b border-white/5 pb-3">{title}</h3>
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
                {items.map(([label, value, wide]) => (
                  <div key={label} className={wide ? "sm:col-span-2" : ""}>
                    <dt className="text-xs font-bold text-white/40 uppercase tracking-widest mb-1">{label}</dt>
                    <dd className="text-white font-medium break-words">{value || "Not set"}</dd>
                  </div>
                ))}
              </dl>
            </section>
          ))}

          <section className="bg-white/10 border border-white/20 rounded-[2rem] p-8 backdrop-blur-xl">
            <h3 className="text-sm font-bold text-white/50 uppercase tracking-widest mb-6 border-b border-white/5 pb-3">Documents</h3>
            <ul className="space-y-4">
              {documents.map(([label, file]) => (
                <li key={label} className="flex items-center justify-between gap-4">
                  <span className="text-white/80">{label}</span>
                  {file ? (
                    <a href={mediaUrl(file)} target="_blank" rel="noreferrer" className="text-sm font-semibold text-purple-300 hover:text-purple-200 underline">View</a>
                  ) : (
                    <span className="text-sm text-white/40">Not uploaded</span>
                  )}
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>
    </section>
  );
}
