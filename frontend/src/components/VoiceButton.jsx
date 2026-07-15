export default function VoiceButton({ isListening, isSpeaking, onClick }) {
  return (
    <button
      onClick={onClick}
      title={isListening ? "Stop listening" : "Start voice input"}
      className={`relative w-12 h-12 rounded-full flex items-center justify-center transition-all flex-shrink-0 ${
        isListening
          ? "bg-red-600 hover:bg-red-500 scale-110"
          : isSpeaking
          ? "bg-indigo-700 cursor-default"
          : "bg-gray-700 hover:bg-gray-600"
      }`}
    >
      {/* Pulse ring when listening */}
      {isListening && (
        <span className="absolute inset-0 rounded-full bg-red-500 opacity-30 animate-ping" />
      )}
      
      {isListening ? (
        /* Stop icon */
        <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
          <rect x="6" y="6" width="12" height="12" rx="2" />
        </svg>
      ) : (
        /* Mic icon */
        <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8" />
        </svg>
      )}
    </button>
  );
}
