import { useState } from 'react'
import useEvents from '../hooks/useEvents.js'
import StatCard from '../components/StatCard.jsx'
import EventTable from '../components/EventTable.jsx'
import EventDetails from '../components/EventDetails.jsx'
import Loading from '../components/Loading.jsx'
import MapView from '../map/MapView.jsx'

/**
 * pages/PWD.jsx
 * Purpose: Department view for the Public Works Department — pothole
 * count, high-confidence potholes, recent potholes, and pothole map
 * markers only (STEP 4 of the integration plan).
 *
 * Connects to:
 * - src/hooks/useEvents.js -> filtered to department=PWD
 * - src/map/MapView.jsx -> pothole/road-defect markers only
 */
export default function PWD() {
  const { events, loading, error, isMock } = useEvents({ department: 'PWD' })
  const [selectedEvent, setSelectedEvent] = useState(null)

  const highConfidence = events.filter((e) => e.confidence >= 0.85)

  return (
    <div className="mx-auto max-w-7xl space-y-5 p-6">
      <h1 className="font-display text-2xl font-semibold text-slate-100">
        Public Works Department
      </h1>

      {isMock && (
        <div className="rounded-lg border border-signal-amber/30 bg-signal-amber/10 px-4 py-2 font-mono text-xs text-signal-amber">
          Backend unavailable — using demo data
        </div>
      )}
      {error && (
        <div className="rounded-lg border border-signal-red/30 bg-signal-red/10 px-4 py-2 font-mono text-xs text-signal-red">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total Potholes" value={events.length} accent="amber" />
        <StatCard label="High Confidence (≥85%)" value={highConfidence.length} accent="amber" />
      </div>

      {loading ? (
        <Loading />
      ) : (
        <MapView events={events} buses={[]} onSelectEvent={setSelectedEvent} height={380} />
      )}

      <div>
        <div className="mb-2 font-mono text-[11px] uppercase tracking-wider text-slate-400">
          Recent Potholes
        </div>
        <EventTable
          events={events}
          onSelect={setSelectedEvent}
          emptyLabel="No potholes reported yet."
        />
      </div>

      <EventDetails event={selectedEvent} onClose={() => setSelectedEvent(null)} />
    </div>
  )
}
