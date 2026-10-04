import React, { useState, useRef, useEffect } from "react";
import robotImage from "../assets/robot.png";

export default function ChatbotNew() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your educational assistant. Ask me about university admissions, study tips, or deadlines.",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;

    const userMsg = { id: Date.now(), text: input, sender: "user", timestamp: new Date() };
    setMessages([...messages, userMsg]);
    setInput("");
    setIsTyping(true);

    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: "I am analyzing the latest admission data for you. Do you have a specific university in mind?",
        sender: "bot",
        timestamp: new Date()
      }]);
      setIsTyping(false);
    }, 1200);
  };

  return (
    /* 1. OUTER WRAPPER: Matches the background and spacing of your Profile/Dashboard */
    <section className="min-h-screen bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] flex flex-col items-center">
      
      {/* 2. SPACING: Clears your fixed Navbar */}
      <div className="h-24 w-full" />

      {/* 3. MAIN CONTENT: Fluid width that prevents "cramming" */}
      <div className="w-full max-w-[1400px] px-6 md:px-12 flex flex-col h-[calc(100vh-10rem)]">
        
        {/* HEADER: Sleek, horizontal, and professional */}
        <div className="bg-white/10 border border-white/20 rounded-3xl p-5 mb-6 flex items-center justify-between backdrop-blur-xl shadow-2xl">
          <div className="flex items-center gap-4">
            <div className="relative">
              <img src={robotImage} alt="AI Bot" className="w-14 h-14 rounded-2xl object-cover border border-white/30 shadow-2xl" />
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-[#1A012E] rounded-full shadow-lg animate-pulse"></div>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Educational AI</h1>
              <p className="text-[10px] font-bold text-purple-400 uppercase tracking-[0.3em]">Institutional Knowledge Base</p>
            </div>
          </div>
          <div className="hidden md:block px-6 py-2 rounded-full bg-white/5 border border-white/10">
            <span className="text-xs font-semibold text-white/40 italic">Informed by AikApply Admissions Data</span>
          </div>
        </div>

        {/* MESSAGES VIEWPORT: This now expands to fill the full height */}
        <div className="flex-1 bg-white/[0.03] border border-white/10 rounded-[2.5rem] p-6 md:p-12 flex flex-col overflow-hidden backdrop-blur-3xl shadow-inner">
          
          {/* Scrollable List */}
          <div className="flex-1 overflow-y-auto space-y-8 mb-6 pr-4 custom-scrollbar">
            {messages.map((m) => (
              <div key={m.id} className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`flex gap-4 max-w-[80%] md:max-w-[65%] ${m.sender === "user" ? "flex-row-reverse" : "flex-row"}`}>
                  
                  {/* Avatar Icons */}
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border border-white/10 text-lg shadow-xl ${m.sender === "user" ? "bg-white text-black" : "bg-purple-600 text-white"}`}>
                    {m.sender === "user" ? "👤" : "🤖"}
                  </div>

                  <div className="space-y-2">
                    <div className={`p-5 rounded-3xl shadow-2xl text-base leading-relaxed ${
                      m.sender === "user" 
                      ? "bg-white text-[#0B0620] font-medium rounded-tr-none" 
                      : "bg-white/10 text-white border border-white/10 rounded-tl-none backdrop-blur-md"
                    }`}>
                      {m.text}
                    </div>
                    <p className={`text-[10px] font-black text-white/20 uppercase tracking-widest ${m.sender === "user" ? "text-right" : "text-left"}`}>
                      {m.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex gap-2 ml-14">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* INPUT SECTION: Clean and centered */}
          <form onSubmit={handleSend} className="relative mt-auto group">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about universities, subjects, or deadlines..."
              className="w-full pl-8 pr-40 py-6 rounded-[2rem] bg-white text-black text-lg outline-none focus:ring-4 focus:ring-purple-500/20 transition-all shadow-2xl placeholder-black/30"
            />
            <button
              type="submit"
              disabled={!input.trim() || isTyping}
              className="absolute right-4 top-1/2 -translate-y-1/2 px-10 py-3.5 rounded-[1.5rem] bg-[#0B0620] text-white font-bold text-sm hover:bg-purple-900 transition-all shadow-xl active:scale-95 disabled:opacity-20"
            >
              Send Message
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}