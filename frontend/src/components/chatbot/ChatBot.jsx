import { useState, useRef, useEffect } from "react";
import { MessageSquare, X, Send, Bot, User, Sparkles, Loader2 } from "lucide-react";
import chatService from "../../services/chatService";

function getCurrentTime() {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "bot",
      text: "Hello! I am your Solar Safe Assistant. You can ask me about solar panel maintenance, hotspot anomalies, cleaning tips, and safety checks.",
      time: "09:00",
    },
  ]);

  const messagesEndRef = useRef(null);

  const suggestedQuestions = [
    "How should I clean my solar panels?",
    "What does a hotspot mean?",
    "How do I know if my panel is damaged?",
    "Is my solar panel safe?",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (messageToSend) => {
    const text = (messageToSend || inputMessage).trim();
    if (!text || loading) return;

    const time = getCurrentTime();

    setMessages((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        sender: "user",
        text,
        time,
      },
    ]);
    setInputMessage("");
    setLoading(true);

    try {
      const response = await chatService.sendMessage(text);
      setMessages((prev) => [
        ...prev,
        {
          id: prev.length + 1,
          sender: "bot",
          text: response.reply || "I am available to assist with solar panel safety and inspection queries.",
          time: getCurrentTime(),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: prev.length + 1,
          sender: "bot",
          text: `Unable to connect to assistant (${err.message}). Please ensure the Solar Safe backend is running.`,
          isError: true,
          time: getCurrentTime(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-40">
      {/* Floating Action Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="group relative flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-600 to-amber-500 text-white shadow-xl shadow-emerald-700/30 hover:shadow-emerald-600/40 hover:scale-105 active:scale-95 transition-all duration-200"
          aria-label="Open Solar Safe Assistant"
        >
          <MessageSquare className="w-6 h-6" />
          <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-emerald-500 border-2 border-white animate-pulse" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="flex flex-col w-[360px] sm:w-[410px] h-[540px] max-h-[85vh] bg-white rounded-2xl shadow-2xl border border-slate-200/90 overflow-hidden animate-in fade-in slide-in-from-bottom-6 duration-200">
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 bg-gradient-to-r from-emerald-700 to-emerald-600 text-white shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-white/15 flex items-center justify-center backdrop-blur-xs">
                <Bot className="w-5 h-5 text-amber-300" />
              </div>
              <div>
                <h3 className="font-bold text-sm tracking-tight flex items-center gap-1.5">
                  Solar Safe Assistant
                  <span className="text-[10px] bg-emerald-800 text-emerald-100 font-semibold px-1.5 py-0.5 rounded">
                    Rule-Based
                  </span>
                </h3>
                <p className="text-xs text-emerald-100/80">PV safety & maintenance guide</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded-lg hover:bg-white/10 text-white/80 hover:text-white transition"
              aria-label="Close chat"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-slate-50/60">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2.5 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.sender === "bot" && (
                  <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>
                )}
                <div
                  className={`max-w-[78%] rounded-2xl px-4 py-2.5 text-sm shadow-xs ${
                    msg.sender === "user"
                      ? "bg-emerald-600 text-white rounded-tr-xs"
                      : msg.isError
                      ? "bg-rose-50 border border-rose-200 text-rose-800 rounded-tl-xs"
                      : "bg-white border border-slate-200/80 text-slate-800 rounded-tl-xs"
                  }`}
                >
                  <p className="leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                  <span
                    className={`block text-[10px] mt-1 ${
                      msg.sender === "user" ? "text-emerald-100 text-right" : "text-slate-400"
                    }`}
                  >
                    {msg.time}
                  </span>
                </div>
                {msg.sender === "user" && (
                  <div className="w-7 h-7 rounded-lg bg-slate-200 text-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-2.5 items-center text-slate-400 text-xs">
                <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-white border border-slate-200/80 rounded-2xl px-3.5 py-2 flex items-center gap-1.5 shadow-xs">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-emerald-600" />
                  <span>Assistant is thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Quick Questions */}
          <div className="px-3 py-2 bg-white border-t border-slate-100">
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-1 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-amber-500" /> Suggested queries
            </p>
            <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-none">
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(q)}
                  disabled={loading}
                  className="text-xs shrink-0 px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200 border border-transparent transition"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Input Footer */}
          <div className="p-3 bg-white border-t border-slate-200/80">
            <div className="flex items-center gap-2 bg-slate-100 rounded-xl p-1.5 focus-within:ring-2 focus-within:ring-emerald-500 focus-within:bg-white border border-slate-200 transition">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about PV faults, cleaning, safety..."
                disabled={loading}
                className="flex-1 bg-transparent px-2.5 py-1 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-hidden disabled:opacity-50"
              />
              <button
                onClick={() => handleSend()}
                disabled={!inputMessage.trim() || loading}
                className="p-2 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-40 disabled:hover:bg-emerald-600 transition"
                aria-label="Send message"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
