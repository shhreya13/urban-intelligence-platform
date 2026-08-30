import { useState, useEffect } from 'react'
import useEvents from '../hooks/useEvents.js'
import { getTraffic } from '../services/api.js'
import StatCard from '../components/StatCard.jsx'
import EventTable from '../components/EventTable.jsx'
import EventDetails from '../components/EventDetails.jsx'
import TrafficChart from '../components/TrafficChart.jsx'
import Loading from '../components/Loading.jsx'

/**
 * pages/Traffic.jsx
 * Purpose: Department view for Traffic Police — traffic level, vehicle
 * counts, traffic chart, and TRAFFIC-department events only (STEP 4 of the
 * integration plan). Extends the existing pages/ folder without changing
 * the required repository structure.
 *
 * Connects to:
 * - src/services/api.js -> getTraffic()
 * - src/hooks/useEvents.js -> filtered to department=TRAFFIC
 */
export default function Traffic() {
  const [traffic, setTraffic] = useState(null)
  const [selectedEvent, setSelectedEvent] = useState(null)
  const { events, loading, error, isMock } = useEvents({ department: 'TRAFFIC' })

  useEffect(() => {
    getTraffic().then(({ data }) => setTraffic(data))
  }, [])

  return (
    <div className="mx-auto max-w-7xl space-y-5 p-6">
      <h1 className="font-display text-2xl font-semibold text-slate-100">Traffic</h1>

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
        <StatCard label="Traffic Level" value={traffic?.traffic_level ?? '—'} accent="red" />
        <StatCard label="Total Vehicles" value={traffic?.total_vehicles ?? '—'} accent="cyan" />
        <StatCard label="Cars" value={traffic?.cars ?? '—'} accent="cyan" />
        <StatCard label="Motorcycles" value={traffic?.motorcycles ?? '—'} accent="cyan" />
      </div>

      <TrafficChart traffic={traffic} />

      <div>
        <div className="mb-2 font-mono text-[11px] uppercase tracking-wider text-slate-400">
          Traffic Events
        </div>
        {loading ? (
          <Loading />
        ) : (
          <EventTable
            events={events}
            onSelect={setSelectedEvent}
            emptyLabel="No traffic events reported yet."
          />
        )}
      </div>

      <EventDetails event={selectedEvent} onClose={() => setSelectedEvent(null)} />
    </div>
  )
}
