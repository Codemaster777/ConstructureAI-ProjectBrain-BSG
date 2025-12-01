"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Database, FileText, Hammer, Bot, User } from "lucide-react";

// LOGIN COMPONENT
function LoginScreen({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState("");
  return (
    <div className="flex h-screen items-center justify-center bg-slate-100 font-sans">
      <form 
        onSubmit={(e) => {
          e.preventDefault();
          if(email === "testingcheckuser1234@gmail.com") onLogin();
          else alert("Use the test email: testingcheckuser1234@gmail.com");
        }} 
        className="bg-white p-8 rounded-xl shadow-lg w-96 border border-slate-200"
      >
        <div className="mb-6 flex justify-center">
            <div className="bg-blue-600 p-3 rounded-lg">
                <Hammer className="text-white w-6 h-6" />
            </div>
        </div>
        <h2 className="text-xl font-bold mb-2 text-center text-slate-800">Constructure AI</h2>
        <p className="text-sm text-slate-500 text-center mb-6">36-Hour Technical Challenge</p>
        <input
          type="email"
          className="w-full bg-slate-50 border border-slate-300 p-3 rounded-lg mb-4 outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter test email..."
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <button className="w-full bg-blue-600 text-white p-3 rounded-lg font-semibold hover:bg-blue-700 transition">
          Enter Project Brain
        </button>
      </form>
    </div>
  );
}

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState<any[]>([
    { role: "ai", type: "text", content: "Hello! I am Project Brain. Ask me about the construction docs." }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!inputText.trim()) return;

    // 1. ADD USER MSG
    const userMsg = { role: "user", content: inputText };
    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setIsLoading(true);

    // 2. DETERMINE INTENT
    const isExtract = userMsg.content.toLowerCase().includes("schedule") || 
                      userMsg.content.toLowerCase().includes("list");
    
    // 3. PREPARE CALL - ALWAYS USE 'message' KEY
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const endpoint = isExtract ? "/extract" : "/chat";
    
    // THIS FIXES THE 422 ERROR
    const payload = { message: userMsg.content }; 

    try {
      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      
      let aiContent;
      let aiType = "text";

      if (isExtract) {
        aiType = "data";
        aiContent = data.data; 
      } else {
        aiType = "text";
        aiContent = data.answer;
      }

      const aiMsg = {
        role: "ai",
        type: aiType,
        content: aiContent,
        sources: data.sources 
      };
      
      setMessages((prev) => [...prev, aiMsg]);

    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "ai", type: "text", content: "Error: Could not reach the backend. Ensure python Server.py is running." }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isLoggedIn) return <LoginScreen onLogin={() => setIsLoggedIn(true)} />;

  return (
    <div className="flex flex-col h-screen bg-slate-50 text-slate-900 font-sans">
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center gap-3 shadow-sm sticky top-0 z-10">
        <div className="bg-blue-600 p-2 rounded-lg">
          <Hammer className="text-white w-5 h-5" />
        </div>
        <div className="flex-1">
          <h1 className="text-lg font-bold text-slate-800">Constructure Brain</h1>
          <p className="text-xs text-slate-500">36-Hour Challenge</p>
        </div>
        <button 
           onClick={() => fetch('http://localhost:8000/ingest', {method: 'POST'})}
           className="text-xs text-slate-400 hover:text-blue-600 border border-slate-200 px-3 py-1 rounded-md bg-slate-50"
        >
            Reset Ingestion
        </button>
      </header>

      <main className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              msg.role === "user" ? "bg-blue-600" : "bg-emerald-600"
            }`}>
              {msg.role === "user" ? <User size={16} className="text-white"/> : <Bot size={16} className="text-white"/>}
            </div>

            <div className={`max-w-[90%] sm:max-w-[80%] rounded-2xl p-4 shadow-sm ${
              msg.role === "user" ? "bg-white border border-blue-100 rounded-tr-none" : "bg-white border border-slate-200 rounded-tl-none"
            }`}>
              {(!msg.type || msg.type === "text") && (
                <div className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{msg.content}</div>
              )}

              {msg.type === "data" && (
                <div className="overflow-x-auto">
                   <div className="flex items-center gap-2 mb-2">
                      <Database size={14} className="text-emerald-600"/>
                      <span className="text-xs font-bold text-emerald-600 uppercase">Extracted Data</span>
                   </div>
                   {Array.isArray(msg.content) && msg.content.length > 0 ? (
                     <table className="w-full text-xs text-left border border-slate-200 rounded-lg overflow-hidden">
                       <thead className="bg-slate-50 uppercase font-semibold text-slate-500">
                         <tr>
                           {Object.keys(msg.content[0]).map(key => (
                             <th key={key} className="px-3 py-2 border-b border-slate-200 bg-slate-100">{key}</th>
                           ))}
                         </tr>
                       </thead>
                       <tbody>
                         {msg.content.map((row: any, rIdx: number) => (
                           <tr key={rIdx} className="hover:bg-slate-50 border-b border-slate-50 last:border-0">
                             {Object.values(row).map((val: any, cIdx: number) => (
                               <td key={cIdx} className="px-3 py-2">{val}</td>
                             ))}
                           </tr>
                         ))}
                       </tbody>
                     </table>
                   ) : (
                     <p className="text-sm italic text-red-500">No structured data extracted.</p>
                   )}
                </div>
              )}

              {msg.role === "ai" && msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap gap-2">
                  <span className="text-[10px] font-bold text-slate-400 uppercase flex items-center gap-1">
                    <FileText size={10}/> Sources:
                  </span>
                  {msg.sources.map((src: any, k: number) => (
                    <span key={k} className="text-[10px] bg-slate-100 border border-slate-200 px-2 py-0.5 rounded text-slate-600">
                      {src.source || "File"} 
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && <div className="text-xs text-slate-400 animate-pulse ml-12">Processing...</div>}
        <div ref={messagesEndRef} />
      </main>

      <footer className="bg-white border-t border-slate-200 p-4">
        <div className="max-w-4xl mx-auto flex gap-2">
          <input 
            className="flex-1 bg-slate-50 border border-slate-300 rounded-lg p-3 outline-none text-sm focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
            placeholder="e.g. 'Generate a door schedule'..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={isLoading}
          />
          <button 
            onClick={handleSend}
            disabled={isLoading}
            className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition shadow-sm"
          >
            <Send size={18}/>
          </button>
        </div>
      </footer>
    </div>
  );
}