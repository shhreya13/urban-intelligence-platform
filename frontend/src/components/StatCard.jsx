/**
 * components/StatCard.jsx
 * Purpose: One KPI tile (Potholes, Vehicles, Buses, Traffic Level, etc).
 * Used across Overview, Traffic, and PWD views for consistent stat display.
 *
 * Connects to:
 * - src/pages/Dashboard.jsx -> Potholes / Vehicles / Buses / Traffic Level
 * - src/pages/Traffic.jsx   -> vehicle-class counts
 * - src/pages/PWD.jsx       -> pothole counts
 */
export default function StatCard({ label, value, accent = 'cyan', sublabel }) {
  const accentClass = {
    cyan: 'text-signal-cyan border-signal-cyan/30',
    amber: 'text-signal-amber border-signal-amber/30',
    red: 'text-signal-red border-signal-red/30',
    green: 'text-signal-green border-signal-green/30',
  }[accent]

  return (
    <div className={`rounded-xl border bg-base-900/80 p-4 ${accentClass}`}>
      <div className="font-mono text-[11px] uppercase tracking-wider text-slate-400">
        {label}
      </div>
      <div className="mt-1 font-display text-3xl font-semibold text-slate-100">
        {value}
      </div>
      {sublabel && (
        <div className="mt-0.5 text-xs text-slate-500">{sublabel}</div>
      )}
    </div>
  )
}
