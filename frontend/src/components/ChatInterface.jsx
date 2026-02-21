import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

function ChatInterface() {
    const [messages, setMessages] = useState([
        {
            text: "Hello! 👋 I am KPGU Assistant, here to help you with information about Drs. Kiran & Pallavi Patel Global University (KPGU) in Vadodara. How may I assist you today regarding admissions, courses, fees, or anything else about KPGU? 🎓✨",
            sender: "bot",
            detected_language: "en"
        },
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = { text: input, sender: "user" };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1/chat";
            const response = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: input }),
            });
            const data = await response.json();

            const botMessage = {
                text: data.response,
                sender: "bot",
                sources: data.sources,
                detected_language: data.detected_language
            };
            setMessages((prev) => [...prev, botMessage]);
        } catch (error) {
            setMessages((prev) => [
                ...prev,
                { text: "⚠️ Connection Error: Please ensure the backend is running.", sender: "bot" },
            ]);
        }

        setIsLoading(false);
    };

    return (
        <div
            className="relative flex flex-col h-[100dvh] w-full bg-cover bg-center font-sans text-gray-800"
            style={{ backgroundImage: "url('/campus_bg.jpg')" }}
        >
            {/* Dark Overlay */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-0"></div>

            {/* Main Content Card */}
            <div className="relative z-10 flex flex-col h-full md:h-[90vh] md:w-[90vw] md:max-w-5xl md:mx-auto md:my-auto bg-white/10 backdrop-blur-md md:border border-white/20 md:rounded-2xl shadow-2xl overflow-hidden">

                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 bg-[#003366]/90 border-b border-white/10 text-white">
                    <div className="flex items-center gap-4">
                        {/* Logo Placeholder - User can replace src later */}
                        <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center overflow-hidden border-2 border-[#CC0000]">
                            <img src="/kpgu_logo.png" alt="KPGU" className="object-contain w-10 h-10" onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'block' }} />
                            <span className="hidden text-[#003366] font-bold text-xs text-center leading-tight">ESTD<br />KPGU</span>
                        </div>
                        <div>
                            <h1 className="text-xl font-bold tracking-wide">KPGU Assistant</h1>
                            <p className="text-xs text-gray-300 font-light">Drs. Kiran & Pallavi Patel Global University</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></span>
                        <span className="text-sm font-medium text-white/90">Online</span>
                    </div>
                </div>

                {/* Chat Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-transparent">
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`flex w-full ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                        >
                            <div className={`flex max-w-[85%] md:max-w-[75%] gap-3 ${msg.sender === "user" ? "flex-row-reverse" : "flex-row"}`}>

                                {/* Avatar Icon */}
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-lg border-2 border-white/20
                    ${msg.sender === 'user' ? 'bg-[#CC0000] text-white' : 'bg-[#003366] text-white'}`}>
                                    {msg.sender === 'user' ? (
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                                    ) : (
                                        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V7h2v5z" /></svg>
                                    )}
                                </div>

                                {/* Message Bubble */}
                                <div
                                    className={`relative p-4 rounded-2xl shadow-md text-base leading-relaxed backdrop-blur-sm
                    ${msg.sender === "user"
                                            ? "bg-gradient-to-br from-[#CC0000] to-[#b30000] text-white rounded-tr-none border border-red-800/50"
                                            : "bg-white/95 text-gray-800 rounded-tl-none border border-white/50"
                                        }`}
                                >
                                    <div className="prose prose-sm max-w-none break-words">
                                        <ReactMarkdown
                                            components={{
                                                p: ({ node, ...props }) => <p className={`m-0 ${msg.sender === 'user' ? 'text-white' : 'text-gray-800'}`} {...props} />,
                                                a: ({ node, ...props }) => <a className="underline font-bold hover:text-blue-200" {...props} />,
                                                ul: ({ node, ...props }) => <ul className="list-disc pl-4 space-y-1" {...props} />,
                                                ol: ({ node, ...props }) => <ol className="list-decimal pl-4 space-y-1" {...props} />
                                            }}
                                        >
                                            {msg.text}
                                        </ReactMarkdown>
                                    </div>

                                    {/* Language Tag Badge */}
                                    {msg.sender === 'bot' && (
                                        <div className="mt-3 flex items-center justify-between border-t border-gray-100/50 pt-2">
                                            {msg.detected_language && (
                                                <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded bg-[#003366]/10 text-[#003366] border border-[#003366]/20">
                                                    {msg.detected_language === 'gu' ? 'GUJARATI' : msg.detected_language === 'hi' ? 'HINDI' : 'ENGLISH'}
                                                </span>
                                            )}
                                            {msg.sources && msg.sources.length > 0 && (
                                                <span className="text-[10px] text-gray-400 italic flex items-center gap-1">
                                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 011.414.586l4 4a1 1 0 01.586 1.414V19a2 2 0 01-2 2z" /></svg>
                                                    KPGU Knowledge Base
                                                </span>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex justify-start w-full animate-pulse">
                            <div className="flex max-w-[80%] gap-3 ml-2 md:ml-0">
                                <div className="w-10 h-10 rounded-full bg-[#003366] flex items-center justify-center shrink-0 border-2 border-white/20">
                                    <span className="animate-spin text-white text-xs">⏳</span>
                                </div>
                                <div className="bg-white/90 p-4 rounded-2xl rounded-tl-none border border-white/50 shadow-sm flex items-center gap-1.5">
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></span>
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 bg-white/90 backdrop-blur-md border-t border-gray-200/50">
                    <div className="flex items-center gap-3 max-w-4xl mx-auto">
                        <input
                            type="text"
                            className="flex-1 px-6 py-4 rounded-full border border-gray-300 focus:outline-none focus:border-[#003366] focus:ring-4 focus:ring-[#003366]/10 transition-all placeholder-gray-400 bg-white text-gray-800 shadow-inner font-medium"
                            placeholder="Ask anything about KPGU..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && handleSend()}
                        />
                        <button
                            onClick={handleSend}
                            disabled={isLoading || !input.trim()}
                            className={`p-4 rounded-full shadow-lg transition-all duration-200 flex items-center justify-center group
                ${isLoading || !input.trim()
                                    ? "bg-gray-200 cursor-not-allowed text-gray-400"
                                    : "bg-gradient-to-r from-[#CC0000] to-[#990000] text-white hover:scale-105 active:scale-95 hover:shadow-xl"
                                }`}
                        >
                            <svg className="w-6 h-6 ml-0.5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ChatInterface;
