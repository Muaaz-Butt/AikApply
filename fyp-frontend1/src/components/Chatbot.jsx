import React, { useState, useRef, useEffect } from "react";
import robotImage from "../assets/robot.png";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Send, User, Bot, Loader2, Copy, Check } from "lucide-react";
import useProfilePhoto from "../utils/useProfilePhoto";
import { API_BASE } from "../config";

export default function Chatbot() {
  const userPhoto = useProfilePhoto();
  const [photoFailed, setPhotoFailed] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your Career Consultant and University Advisor. How can I help you today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initialize or retrieve Session ID for persistent chat context
    let storedSession = localStorage.getItem("chat_session_id");
    if (!storedSession) {
      storedSession = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2) + Date.now().toString(36);
      localStorage.setItem("chat_session_id", storedSession);
    }
    setSessionId(storedSession);
  }, []);

  useEffect(() => {
    // Fetch History using backend endpoint
    if (sessionId) {
      axios.get(`${API_BASE}/api_tools/chat/?session_id=${sessionId}`)
        .then(res => {
           if (res.data.messages && res.data.messages.length > 0) {
             const history = res.data.messages.map(m => ({
               id: m.id,
               text: m.text,
               sender: m.role,
               timestamp: new Date(m.timestamp)
             }));
             setMessages(history);
           }
        })
        .catch(err => {
           console.error("History fetch error:", err);
        });
    }
  }, [sessionId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text).then(() => {
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    });
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;

    const userMessage = {
      id: Date.now(),
      text: input.trim(),
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await axios.post(`${API_BASE}/api_tools/chat/`, {
        session_id: sessionId,
        message: userMessage.text
      });

      const botMessage = {
        id: Date.now() + 1,
        text: response.data.reply,
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      let errorMessage = "Sorry, I am currently unable to connect to my knowledge base. Please ensure the backend server is running.";
      if (error.response && error.response.data && error.response.data.error) {
        errorMessage = `System Error: ${error.response.data.error}`;
      }
      
      const botMessage = {
        id: Date.now() + 1,
        text: errorMessage,
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev.filter(msg => !msg.isTyping), botMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    //   <section className="min-h-screen bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] flex flex-col items-center pt-28 pb-10 px-4 md:px-10 lg:px-20">
      
    //     <div className="w-full max-w-[1400px] flex flex-col flex-1" style={{ maxHeight: "calc(100vh - 8rem)" }}>
        
    //       {/* HEADER */}
    //       <div className="bg-white/10 border border-white/20 rounded-3xl p-5 mb-6 flex shrink-0 items-center justify-between backdrop-blur-xl shadow-2xl">
    //         <div className="flex items-center gap-4">
    //           <div className="relative">
    //             <img src={robotImage} alt="AI Bot" className="w-14 h-14 rounded-2xl object-cover border border-white/30 shadow-2xl" />
    //             <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-[#1A012E] rounded-full shadow-lg animate-pulse"></div>
    //           </div>
    //           <div>
    //             <h1 className="text-2xl font-bold text-white tracking-tight">Career Consultant AI</h1>
    //             <p className="text-[10px] font-bold text-purple-400 uppercase tracking-[0.3em]">University Advisor Mode</p>
    //           </div>
    //         </div>
    //         <div className="hidden md:block px-6 py-2 rounded-full bg-white/5 border border-white/10 italic text-xs text-white/40">
    //           Powered by Gemini
    //         </div>
    //       </div>

    //       {/* MESSAGES BOX */}
    //       <div className="flex-1 bg-white/[0.03] border border-white/10 rounded-[2.5rem] p-6 md:p-10 flex flex-col overflow-hidden backdrop-blur-3xl shadow-2xl h-full relative">
          
    //         <div className="flex-1 overflow-y-auto space-y-8 mb-6 pr-4 custom-scrollbar">
    //           {messages.map((m) => (
    //             <div key={m.id} className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}>
    //               <div className={`flex gap-4 max-w-[90%] md:max-w-[80%] ${m.sender === "user" ? "flex-row-reverse" : "flex-row"}`}>
                  
    //                 {/* Avatars */}
    //                 <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border border-white/10 shadow-xl ${m.sender === "user" ? "bg-white text-[#0B0620]" : "bg-purple-600 text-white"}`}>
    //                   {m.sender === "user" ? <User size={20} /> : <Bot size={20} />}
    //                 </div>

    //                 <div className="space-y-2 group relative">
    //                   <div className={`p-5 rounded-3xl shadow-2xl text-base leading-relaxed relative ${
    //                     m.sender === "user" 
    //                     ? "bg-white text-[#0B0620] font-medium rounded-tr-none px-6" 
    //                     : "bg-[#180A2D] text-gray-200 border border-white/10 rounded-tl-none markdown-body prose prose-invert max-w-none"
    //                   }`}>
    //                     {m.sender === "bot" ? (
    //                       <ReactMarkdown remarkPlugins={[remarkGfm]}>
    //                         {m.text}
    //                       </ReactMarkdown>
    //                     ) : (
    //                       m.text
    //                     )}
                      
    //                     {/* Copy Button Hover Overlay */}
    //                     <button 
    //                       onClick={() => handleCopy(m.id, m.text)}
    //                       className={`absolute ${m.sender === 'user' ? 'left-[-40px]' : 'right-[-40px]'} top-2 p-2 rounded-full bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/20 text-white`}
    //                       title="Copy message"
    //                     >
    //                        {copiedId === m.id ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
    //                     </button>

    //                   </div>
    //                   <p className={`text-[10px] font-black text-white/20 uppercase tracking-widest ${m.sender === "user" ? "text-right" : "text-left"}`}>
    //                     {m.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
    //                   </p>
    //                 </div>
    //               </div>
    //             </div>
    //           ))}
            
    //           {isTyping && (
    //             <div className="flex gap-2 ml-14">
    //               <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border border-white/10 shadow-xl bg-purple-600 text-white">
    //                   <Loader2 size={20} className="animate-spin" />
    //               </div>
    //               <div className="bg-[#180A2D] border border-white/10 rounded-3xl rounded-tl-none p-5 flex items-center gap-2 shadow-2xl">
    //                   <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
    //                   <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
    //                   <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
    //               </div>
    //             </div>
    //           )}
    //           <div ref={messagesEndRef} />
    //         </div>

    //         {/* INPUT BAR */}
    //         <div className="shrink-0 pt-2">
    //           <form onSubmit={handleSend} className="relative group flex items-center">
    //             <input
    //               type="text"
    //               value={input}
    //               onChange={(e) => setInput(e.target.value)}
    //               placeholder="Ask about careers, universities, or your study path..."
    //               className="w-full pl-8 pr-[140px] py-6 rounded-[2rem] bg-white text-black text-lg outline-none focus:ring-4 focus:ring-purple-500/20 transition-all shadow-2xl placeholder-black/30 bg-opacity-95 backdrop-blur"
    //               disabled={isTyping}
    //             />
    //             <button
    //               type="submit"
    //               disabled={!input.trim() || isTyping}
    //               className="absolute right-3 px-8 py-4 rounded-[1.5rem] bg-[#0B0620] text-white font-bold flex items-center gap-2 hover:bg-black transition-all shadow-xl active:scale-95 disabled:opacity-30"
    //             >
    //               <Send size={18} /> Send
    //             </button>
    //           </form>
    //         </div>
    //       </div>
    //     </div>

    //     <style jsx="true">{`
    //       .markdown-body table {
    //         width: 100%;
    //         border-collapse: collapse;
    //         margin: 15px 0;
    //       }
    //       .markdown-body th, .markdown-body td {
    //         border: 1px solid rgba(255, 255, 255, 0.2);
    //         padding: 10px;
    //         text-align: left;
    //       }
    //       .markdown-body th {
    //         background-color: rgba(255, 255, 255, 0.05);
    //         font-weight: bold;
    //         color: #fff;
    //       }
    //       .markdown-body tr:nth-child(even) {
    //         background-color: rgba(255, 255, 255, 0.02);
    //       }
    //       .markdown-body a {
    //         color: #a855f7;
    //         text-decoration: underline;
    //       }
    //       .markdown-body ul {
    //         list-style-type: disc;
    //         margin-left: 20px;
    //         margin-bottom: 15px;
    //       }
    //       .markdown-body ol {
    //         list-style-type: decimal;
    //         margin-left: 20px;
    //         margin-bottom: 15px;
    //       }
    //       .markdown-body strong {
    //         color: #fff;
    //       }
    //     `}</style>
    //   </section>
    // );
    <section className="h-full w-full bg-gradient-to-b from-[#0B0620] via-[#200136] to-[#2A013D] rounded-[2.5rem] p-4 md:p-6 flex flex-col">
  
  {/* MAIN CONTAINER */}
  <div className="w-full h-full flex flex-col">

    {/* HEADER */}
    <div className="bg-white/10 border border-white/20 rounded-3xl p-4 mb-4 flex shrink-0 items-center justify-between backdrop-blur-xl shadow-xl">
      <div className="flex items-center gap-3">
        <div className="relative">
          <img
            src={robotImage}
            alt="AI Bot"
            className="w-12 h-12 rounded-xl object-cover border border-white/30"
          />
          <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 border-2 border-[#1A012E] rounded-full animate-pulse"></div>
        </div>
        <div>
          <h1 className="text-lg font-bold text-white">Career Consultant AI</h1>
          <p className="text-[10px] font-bold text-purple-400 uppercase tracking-widest">
            University Advisor
          </p>
        </div>
      </div>

      <div className="hidden md:block px-4 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-white/40">
        Powered by Gemini
      </div>
    </div>

    {/* CHAT BOX */}
    <div className="flex-1 flex flex-col bg-white/[0.04] backdrop-blur-2xl border border-white/10 rounded-[2rem] p-4 md:p-6 overflow-hidden shadow-inner">

      {/* MESSAGES */}
      <div className="flex-1 overflow-y-auto space-y-6 pr-2 scroll-smooth">

        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"} animate-[fadeIn_0.3s_ease]`}
          >
            <div className={`flex gap-3 max-w-[85%] ${m.sender === "user" ? "flex-row-reverse" : ""}`}>

              {/* AVATAR */}
              {m.sender === "user" && userPhoto && !photoFailed ? (
                <img
                  src={userPhoto}
                  alt="You"
                  onError={() => setPhotoFailed(true)}
                  className="w-9 h-9 rounded-full object-cover shrink-0 border border-white/10 shadow-lg"
                />
              ) : (
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 border border-white/10 shadow-lg
                  ${m.sender === "user" ? "bg-white text-black" : "bg-purple-600 text-white"}`}>
                  {m.sender === "user" ? <User size={18} /> : <Bot size={18} />}
                </div>
              )}

              {/* MESSAGE */}
              <div className="group relative space-y-1">
                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed shadow-lg relative
                  ${m.sender === "user"
                    ? "bg-white text-black font-medium rounded-tr-none"
                    : "bg-gradient-to-br from-[#1A0B2E] to-[#140822] text-gray-200 border border-white/10 rounded-tl-none markdown-body"
                  }`}
                >
                  {m.sender === "bot" ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {m.text}
                    </ReactMarkdown>
                  ) : (
                    m.text
                  )}

                  {/* COPY BUTTON */}
                  <button
                    onClick={() => handleCopy(m.id, m.text)}
                    className={`absolute ${m.sender === "user" ? "-left-10" : "-right-10"} top-2 p-2 rounded-full bg-white/10 opacity-0 group-hover:opacity-100 transition hover:bg-white/20`}
                  >
                    {copiedId === m.id ? (
                      <Check size={14} className="text-green-400" />
                    ) : (
                      <Copy size={14} />
                    )}
                  </button>
                </div>

                <p className="text-[10px] text-white/20">
                  {m.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            </div>
          </div>
        ))}

        {/* TYPING INDICATOR */}
        {isTyping && (
          <div className="flex gap-2 ml-12">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center bg-purple-600 text-white">
              <Loader2 size={16} className="animate-spin" />
            </div>
            <div className="bg-[#180A2D] border border-white/10 rounded-2xl p-4 flex gap-1">
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce delay-150"></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce delay-300"></div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* INPUT BAR */}
      <div className="sticky bottom-0 pt-4 bg-gradient-to-t from-[#0B0620] via-transparent to-transparent">
        <form onSubmit={handleSend} className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about universities, careers..."
            className="w-full pl-4 sm:pl-6 pr-16 sm:pr-28 py-4 rounded-2xl bg-white text-black text-sm outline-none focus:ring-2 focus:ring-purple-500 shadow-xl"
            disabled={isTyping}
          />

          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            aria-label="Send"
            className="absolute right-2 px-3.5 sm:px-6 py-3 rounded-xl bg-[#0B0620] text-white font-semibold flex items-center gap-2 hover:bg-black transition active:scale-95 disabled:opacity-30"
          >
            <Send size={16} />
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</section>
  );
  
}