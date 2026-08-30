import { useState, useEffect } from 'react'
import useEvents from '../hooks/useEvents.js'
import { getTraffic, getBuses } from '../services/api.js'
import StatCard from '../components/StatCard.jsx'
import EventTable from '../components/EventTable.jsx'
import EventDetails from '../components/EventDetails.jsx'
import TrafficChart from '../components/TrafficChart.jsx'
import Loading from '../components/Loading.jsx'
import MapView from '../map/MapView.jsx'

/**
 * pages/Dashboard.jsx
 * Purpose: The "Overview" landing page — command-center summary showing
 * Potholes / Vehicles / Buses / Traffic Level stat cards, the full GIS map,
 * a traffic snapshot chart, and a recent-events panel. This is the page
 * from STEP 1-4 of the integration plan, combined into one view.
 *
 * Connects to:
 * - src/hooks/useEvents.js -> all events (for map + recent events + counts)
 * - src/services/api.js    -> getTraffic(), getBuses()
 * - src/components/*       -> StatCard, EventTable, EventDetails, TrafficChart, Loading
 * - src/map/MapView.jsx    -> GIS map
 */
export default function Dashboard() {
  const { events, loading: eventsLoading, error, isMock: eventsMock } = useEvents()
  const [traffic, setTraffic] = useState(null)
  const [buses, setBuses] = useState([])
  const [busesLoading, setBusesLoading] = useState(true)
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [banner, setBanner] = useState(false)

  useEffect(() => {
    getTraffic().then(({ data, isMock }) => {
      setTraffic(data)
      if (isMock) setBanner(true)
    })
    getBuses().then(({ data, isMock }) => {
      setBuses(data)
      setBusesLoading(false)
      if (isMock) setBanner(true)
    })
  }, [])

  const potholeCount = events.filter((e) => e.department === 'PWD').length
  const recentEvents = events.slice(0, 6)

  if (eventsLoading || busesLoading) return <Loading label="Loading dashboard…" />

  return (
    <div className="mx-auto max-w-7xl space-y-5 p-6">
      {(banner || eventsMock) && (
        <div className="rounded-lg border border-signal-amber/30 bg-signal-amber/10 px-4 py-2 font-mono text-xs text-signal-amber">
          Backend unavailable — using demo data
        </div>
      )}
      {error && (
        <div className="rounded-lg border border-signal-red/30 bg-signal-red/10 px-4 py-2 font-mono text-xs text-signal-red">
          {error}
        </div>
      )}

      <div>
        <h1 className="font-display text-2xl font-semibold text-slate-100">
          Urban Intelligence Platform
        </h1>
        <p className="mt-0.5 text-sm text-slate-500">
          Live sensing from the public bus fleet — SIH26124
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Potholes" value={potholeCount} accent="amber" />
        <StatCard label="Vehicles Tracked" value={traffic?.total_vehicles ?? '—'} accent="cyan" />
        <StatCard label="Active Buses" value={buses.length} accent="green" />
        <StatCard label="Traffic Level" value={traffic?.traffic_level ?? '—'} accent="red" />
      </div>

      <MapView events={events} buses={buses} onSelectEvent={setSelectedEvent} height={420} />

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <TrafficChart traffic={traffic} />
        </div>
        <div className="lg:col-span-2">
          <div className="mb-2 font-mono text-[11px] uppercase tracking-wider text-slate-400">
            Recent Events
          </div>
          <EventTable events={recentEvents} onSelect={setSelectedEvent} />
        </div>
      </div>

      <EventDetails event={selectedEvent} onClose={() => setSelectedEvent(null)} />
    </div>
  )
}
