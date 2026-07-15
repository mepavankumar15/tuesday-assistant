const STATUS_CONFIG = {
  idle:      { label: "Ready",    color: "bg-gray-600" },
  listening: { label: "Listening…", color: "bg-red-500 animate-pulse" },
  thinking:  { label: "Thinking…", color: "bg-yellow-500 animate-pulse" },
  speaking:  { label: "Speaking…", color: "bg-indigo-500 animate-pulse" },
};

export default function StatusBar({ status }) {
  const { label, color } = STATUS_CONFIG[status] || STATUS_CONFIG.idle;
  
  return (
    <div className="flex items-center gap-2 text-xs text-gray-400">
      <span className={`w-2 h-2 rounded-full ${color}`} />
      {label}
    </div>
  );
}
