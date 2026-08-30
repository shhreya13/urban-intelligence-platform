/**
 * components/Loading.jsx
 * Purpose: Small reusable loading indicator shown while any page/hook is
 * fetching (events, traffic, buses). Kept tiny and dependency-free.
 *
 * Connects to:
 * - src/pages/Dashboard.jsx, Events.jsx, Traffic.jsx, PWD.jsx -> shown while
 *   useEvents()/getTraffic()/getBuses() are loading
 */
export default function Loading({ label = 'Loading data…' }) {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-slate-400">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-600 border-t-signal-cyan" />
      <span className="font-mono text-sm">{label}</span>
    </div>
  )
}
