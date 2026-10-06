import React, { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import robot from "../assets/robot.png";

export default function Hero() {
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const target = location.state?.scrollTo;
    if (target) {
      setTimeout(() => {
        const el = document.getElementById(target);
        if (el) {
          el.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }, 50);
    }
  }, [location.state]);

  return (
    <section 
      id="home" 
      className="min-h-screen flex flex-col items-center justify-start bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] pt-28 md:pt-36 relative overflow-x-hidden"
    >
      {/* --- PEEKING ROBOT CONTAINER --- */}
      {/* This div is pinned to the absolute left of the screen */}
      {/* --- PEEKING ROBOT CONTAINER (Adjusted Right) --- */}
      <div className="hidden md:block absolute left-0 top-24 md:top-40 z-0 pointer-events-none select-none">
        <div className="relative -left-8 md:-left-2 w-44 md:w-80">
          <img 
            src={robot} 
            alt="Robot" 
            className="w-full h-auto transform -rotate-6 drop-shadow-[0_0_30px_rgba(168,85,247,0.4)]" 
          />
        </div>
      </div>

      {/* --- HERO CONTENT --- */}
      <div className="w-full max-w-6xl px-6 md:px-10 relative z-10">
        <div className="flex flex-col items-center text-center gap-6">
          {/* On phones the robot sits above the headline instead of behind it */}
          <img
            src={robot}
            alt=""
            aria-hidden="true"
            className="md:hidden w-28 h-auto -rotate-6 -mb-2 drop-shadow-[0_0_24px_rgba(168,85,247,0.4)] pointer-events-none select-none"
          />
          <h1 className="text-[40px] md:text-[68px] leading-[1.1] font-bold text-white drop-shadow-md">
            Apply to Universities <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-300">
              automatically
            </span>
          </h1>
          
          <p className="text-white/70 max-w-xl text-lg md:text-xl font-medium">
            Create an account and AikApply will submit applications 
            to top Pakistani universities on your behalf.
          </p>

          <Link
            to="/login"
            className="mt-6 px-12 py-4 rounded-full bg-white text-[#0B0620] font-extrabold text-lg hover:bg-purple-100 transition-all shadow-[0_0_20px_rgba(255,255,255,0.2)] active:scale-95"
          >
            Get Started
          </Link>
        </div>
      </div>

      {/* --- ABOUT SECTION --- */}
      <section id="about" className="w-full mt-32 bg-white/5 py-24 backdrop-blur-sm border-y border-white/10 scroll-mt-24">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-8">About Us</h2>
          <p className="text-white/80 leading-relaxed text-lg md:text-xl">
            AikApply is a unified platform designed to simplify and streamline the university
            admission process for students across Pakistan. Our mission is to eliminate the
            complexity of applying to multiple universities by offering a single, smart form that
            gathers your academic details, preferences, and documents—just once.
          </p>
        </div>
      </section>

      {/* --- CONTACT SECTION --- */}
<section id="contact" className="w-full bg-gradient-to-b from-[#0B0620] to-[#1A012E] py-20 px-6 md:px-12 lg:px-20 scroll-mt-24">
  <div className="max-w-6xl mx-auto">
    
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-start">
      
      {/* LEFT: Context & Contact Info (33% width) */}
      <div className="lg:col-span-4 space-y-10">
        <div className="space-y-4">
          <h2 className="text-4xl font-bold text-white tracking-tight">Contact Us</h2>
          <p className="text-white/50 leading-relaxed text-sm md:text-base">
            Have a question about the admission process? Our support team is available Monday through Friday to assist you.
          </p>
        </div>

        <div className="space-y-6">
          {/* Phone Item */}
          <div className="flex items-center gap-5 p-1 transition-colors group">
            <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-xl group-hover:border-purple-500/50 transition-all">
              📞
            </div>
            <div>
              <p className="text-[10px] font-bold text-purple-400 uppercase tracking-widest mb-1">Call Support</p>
              <p className="text-white font-medium">+92 310 1416169</p>
            </div>
          </div>

          {/* Email Item */}
          <div className="flex items-center gap-5 p-1 transition-colors group">
            <div className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-xl group-hover:border-purple-500/50 transition-all">
              ✉️
            </div>
            <div>
              <p className="text-[10px] font-bold text-purple-400 uppercase tracking-widest mb-1">Email Inquiry</p>
              <p className="text-white font-medium">aikapply@info.edu.pk</p>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT: Professional Form (66% width) */}
      <div className="lg:col-span-8">
        <div className="bg-white/[0.03] border border-white/10 rounded-[2.5rem] p-8 md:p-12 backdrop-blur-3xl shadow-2xl">
          <form className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-2">
                <label className="text-xs font-bold text-white/40 uppercase tracking-widest ml-1">Full Name</label>
                <input 
                  type="text" 
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 text-white outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all" 
                  placeholder="John Doe"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-bold text-white/40 uppercase tracking-widest ml-1">Email Address</label>
                <input 
                  type="email" 
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 text-white outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all" 
                  placeholder="j.doe@example.com"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-white/40 uppercase tracking-widest ml-1">Your Message</label>
              <textarea 
                rows="4" 
                className="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 text-white outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all resize-none" 
                placeholder="Briefly describe how we can help..."
              />
            </div>

            <div className="pt-2">
              <button 
                type="submit"
                className="px-10 py-4 rounded-xl bg-white text-[#0B0620] font-bold text-sm hover:bg-purple-100 transition-all shadow-xl active:scale-95"
              >
                Send Message
              </button>
            </div>
          </form>
        </div>
      </div>

    </div>
  </div>
</section>
    </section>
  );
}