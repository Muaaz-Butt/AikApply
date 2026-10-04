import React from "react";
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    /* py-4 for a slightly more comfortable slim height */
    <footer className="w-full bg-[#0B0620] border-t border-white/10 py-4 mt-auto">
      {/* w-full and px-12 ensures it reaches the edges but has safe breathing room */}
      <div className="w-full px-6 md:px-12 flex flex-col md:flex-row justify-between items-center gap-6">
        
        {/* LEFT: Brand & Rights */}
        <div className="flex items-center gap-5">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded bg-white flex items-center justify-center text-[#0B0620] font-bold text-xs">1</div>
            <span className="text-base font-bold text-white tracking-tight">Apply</span>
          </div>
          <span className="hidden md:inline h-4 w-px bg-white/20" /> {/* Vertical Divider */}
          <p className="text-xs font-semibold text-white/40 uppercase tracking-wider">
            © 2025 AIK Apply
          </p>
        </div>

        {/* CENTER: Contact Info (Increased size and contrast) */}
        <div className="flex items-center gap-10">
          <a href="mailto:aikapply@info.edu.pk" className="text-sm font-medium text-white/70 hover:text-purple-400 transition flex items-center gap-2">
            <span className="text-lg">✉️</span> aikapply@info.edu.pk
          </a>
          <a href="tel:+923101416169" className="text-sm font-medium text-white/70 hover:text-purple-400 transition flex items-center gap-2">
            <span className="text-lg">📞</span> +92 310 1416169
          </a>
        </div>

        {/* RIGHT: Legal Links (Clean and readable) */}
        <div className="flex gap-8 text-xs font-bold text-white/50 uppercase tracking-widest">
          <Link to="/privacy" className="hover:text-white transition decoration-purple-500/50 hover:underline underline-offset-4">
            Privacy Policy
          </Link>
          <Link to="/terms" className="hover:text-white transition decoration-purple-500/50 hover:underline underline-offset-4">
            Terms of Service
          </Link>
        </div>
        
      </div>
    </footer>
  );
};

export default Footer;