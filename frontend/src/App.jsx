/**
 * Root App component. Manages global chat state, voice I/O, 
 * YouTube player visibility, and API communication.
 */
import { useState, useRef, useCallback, useEffect } from "react";
import ChatInterface from "./components/ChatInterface";
import YoutubePlayer from "./components/YoutubePlayer";
import StatusBar from "./components/StatusBar";
import VoiceButton from "./components/VoiceButton";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Web Speech API setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const synth = window.speechSynthesis;

export default function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hey! I'm Grok Assistant. Ask me anything, play music, check weather or forex rates. How can I help?" }
  ]);
  const [input, setInput] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [status, setStatus] = useState("idle"); // idle | listening | thinking | speaking
  const [youtubeVideoId, setYoutubeVideoId] = useState(null);
  const [youtubeTitle, setYoutubeTitle] = useState("");
  const [ttsEnabled, setTtsEnabled] = useState(true);

  const recognitionRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Text-to-speech
  const speak = useCallback((text) => {
    if (!ttsEnabled || !synth) return;
    
    // Strip JSON blocks and markdown from spoken text
    const cleanText = text
      .replace(/\{.*?\}/gs, "")
      .replace(/[*_`#]/g, "")
      .trim();
    
    synth.cancel();
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    // Use a natural-sounding voice if available
    const voices = synth.getVoices();
    const preferred = voices.find(v => 
      v.name.includes("Google") || v.name.includes("Natural") || v.lang === "en-US"
    );
    if (preferred) utterance.voice = preferred;
    
    utterance.onstart = () => { setIsSpeaking(true); setStatus("speaking"); };
    utterance.onend = () => { setIsSpeaking(false); setStatus("idle"); };
    utterance.onerror = () => { setIsSpeaking(false); setStatus("idle"); };
    
    synth.speak(utterance);
  }, [ttsEnabled]);

  // Send message to backend
  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;
    
    const userMsg = { role: "user", content: text };
    const updatedHistory = [...messages, userMsg];
    setMessages(updatedHistory);
    setInput("");
    setIsLoading(true);
    setStatus("thinking");

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: messages.slice(-10), // last 10 messages
        }),
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);
      
      const data = await response.json();
      const assistantMsg = { role: "assistant", content: data.response };
      
      setMessages(prev => [...prev, assistantMsg]);
      
      // Handle YouTube playback
      if (data.youtube_action?.video_id) {
        setYoutubeVideoId(data.youtube_action.video_id);
        setYoutubeTitle(data.youtube_action.title || "Now playing");
      }
      
      // Speak the response
      speak(data.response);
      
    } catch (err) {
      const errMsg = { role: "assistant", content: "Sorry, I couldn't connect to the server. Please check your connection." };
      setMessages(prev => [...prev, errMsg]);
      speak(errMsg.content);
    } finally {
      setIsLoading(false);
      if (!isSpeaking) setStatus("idle");
    }
  }, [messages, isLoading, speak, isSpeaking]);

  // Voice recognition
  const startListening = useCallback(() => {
    if (!SpeechRecognition) {
      alert("Your browser doesn't support voice input. Try Chrome.");
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      setStatus("idle");
      return;
    }

    synth.cancel(); // stop speaking if user interrupts

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.continuous = false;

    recognition.onstart = () => { setIsListening(true); setStatus("listening"); };
    recognition.onend = () => { setIsListening(false); };
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      setStatus("thinking");
      sendMessage(transcript);
    };
    
    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setIsListening(false);
      setStatus("idle");
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, [isListening, sendMessage]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-white font-sans">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800 bg-gray-900">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-sm font-bold">G</div>
          <h1 className="text-lg font-semibold tracking-tight">Grok Assistant</h1>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => { setTtsEnabled(v => !v); synth.cancel(); }}
            className={`text-xs px-3 py-1 rounded-full border transition-colors ${
              ttsEnabled ? "border-indigo-500 text-indigo-400" : "border-gray-600 text-gray-500"
            }`}
          >
            {ttsEnabled ? "🔊 Voice on" : "🔇 Voice off"}
          </button>
          <StatusBar status={status} />
        </div>
      </header>

      {/* YouTube Player (shown when a video is active) */}
      {youtubeVideoId && (
        <YoutubePlayer
          videoId={youtubeVideoId}
          title={youtubeTitle}
          onClose={() => setYoutubeVideoId(null)}
        />
      )}

      {/* Chat messages */}
      <ChatInterface messages={messages} isLoading={isLoading}>
        <div ref={messagesEndRef} />
      </ChatInterface>

      {/* Input row */}
      <div className="border-t border-gray-800 bg-gray-900 px-4 py-4">
        <div className="flex items-center gap-3 max-w-3xl mx-auto">
          <VoiceButton
            isListening={isListening}
            isSpeaking={isSpeaking}
            onClick={startListening}
          />
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything, or press the mic…"
            disabled={isLoading || isListening}
            className="flex-1 bg-gray-800 text-white placeholder-gray-500 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-indigo-500 border border-gray-700 disabled:opacity-50"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || isLoading}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white px-4 py-3 rounded-xl text-sm font-medium transition-colors"
          >
            Send
          </button>
        </div>
        <p className="text-center text-gray-600 text-xs mt-2">
          Try: "Play lofi hip hop" · "Weather in Tokyo" · "100 USD to INR"
        </p>
      </div>
    </div>
  );
}
