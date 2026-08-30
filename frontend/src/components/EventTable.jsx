/**
 * components/EventTable.jsx
 * Purpose: Tabular list of events (used on Dashboard "Recent Events" panel,
 * Events page, Traffic page, and PWD page). Clicking a row opens
 * EventDetails via the onSelect callback — the table itself has no modal
 * logic, keeping it dumb/reusable.
 *
 * Connects to:
 * - src/pages/Dashboard.jsx, Events.jsx, Traffic.jsx, PWD.jsx -> renders
 *   the `events` array from useEvents()
 * - src/components/EventDetails.jsx -> opened by the parent on row click
 */
const typeColor = {
  POTHOLE: 'text-signal-amber',
  ROAD_DEFECT: 'text-signal-amber',
  TRAFFIC_DENSITY: 'text-signal-cyan',
  CONGESTION: 'text-signal-cyan',
  VEHICLE: 'text-slate-300',
  INCIDENT: 'text-signal-red',
  PEDESTRIAN: 'text-signal-red',
}

export default function EventTable({ events, onSelect, emptyLabel = 'No events yet.' }) {
  if (!events || events.length === 0) {
    return (
      <div className="rounded-xl border border-base-700 bg-base-900/60 p-8 text-center text-sm text-slate-500">
        {emptyLabel}
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-xl border border-base-700">
      <table className="w-full text-left text-sm">
        <thead className="bg-base-800 font-mono text-[11px] uppercase tracking-wider text-slate-400">
          <tr>
            <th className="px-4 py-2.5">Event</th>
            <th className="px-4 py-2.5">Type</th>
            <th className="px-4 py-2.5">Bus</th>
            <th className="px-4 py-2.5">Confidence</th>
            <th className="px-4 py-2.5">Time</th>
            <th className="px-4 py-2.5">Dept</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-base-700 bg-base-900/60">
          {events.map((e) => (
            <tr
              key={e.event_id}
              onClick={() => onSelect?.(e)}
              className="cursor-pointer transition-colors hover:bg-base-800"
            >
              <td className="px-4 py-2.5 font-mono text-slate-300">{e.event_id}</td>
              <td className={`px-4 py-2.5 font-medium ${typeColor[e.event_type] || 'text-slate-300'}`}>
                {e.event_type}
              </td>
              <td className="px-4 py-2.5 text-slate-400">{e.bus_id}</td>
              <td className="px-4 py-2.5 text-slate-400">{(e.confidence * 100).toFixed(0)}%</td>
              <td className="px-4 py-2.5 text-slate-500">
                {new Date(e.timestamp).toLocaleTimeString()}
              </td>
              <td className="px-4 py-2.5">
                <span
                  className={`rounded-full px-2 py-0.5 text-[11px] font-mono ${
                    e.department === 'PWD'
                      ? 'bg-signal-amber/10 text-signal-amber'
                      : 'bg-signal-cyan/10 text-signal-cyan'
                  }`}
                >
                  {e.department}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
