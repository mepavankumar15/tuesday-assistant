export default function YoutubePlayer({ videoId, title, onClose }) {
  return (
    <div className="bg-gray-900 border-b border-gray-800 px-4 py-3">
      <div className="max-w-3xl mx-auto flex gap-4 items-start">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-indigo-400 font-medium uppercase tracking-wider">Now playing</span>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-white text-xs transition-colors"
            >
              ✕ Close
            </button>
          </div>
          <p className="text-sm text-white font-medium truncate mb-3">{title}</p>
          <div className="relative w-full rounded-xl overflow-hidden" style={{ paddingBottom: "30%", maxWidth: "480px" }}>
            <iframe
              className="absolute inset-0 w-full h-full"
              src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`}
              title={title}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        </div>
      </div>
    </div>
  );
}
