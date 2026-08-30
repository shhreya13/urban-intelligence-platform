import { useState, useMemo } from 'react'
import useEvents from '../hooks/useEvents.js'
import EventTable from '../components/EventTable.jsx'
import EventDetails from '../components/EventDetails.jsx'
import Loading from '../components/Loading.jsx'

/**
 * pages/Events.jsx
 * Purpose: "All events" view with filtering by type, department, and bus.
 * This is the general-purpose event browser referenced in the integration
 * plan's STEP 5 (department filtering) and the shared EventTable/Details
 * components used everywhere else.
 *
 * Connects to:
 * - src/hooks/useEvents.js -> refetches whenever filters change
 * - src/components/EventTable.jsx, EventDetails.jsx
 */
const EVENT_TYPES = [
  'POTHOLE',
  'ROAD_DEFECT',
  'VEHICLE',
  'TRAFFIC_DENSITY',
  'CONGESTION',
  'INCIDENT',
  'PEDESTRIAN',
]

export default function Events() {
  const [eventType, setEventType] = useState('')
  const [department, setDepartment] = useState('')
  const [busId, setBusId] = useState('')
  const [selectedEvent, setSelectedEvent] = useState(null)

  const filters = useMemo(() => {
    const f = {}
    if (eventType) f.event_type = eventType
    if (department) f.department = department
    if (busId) f.bus_id = busId
    return f
  }, [eventType, department, busId])

  const { events, loading, error, isMock, refresh } = useEvents(filters)

  return (
    <div className="mx-auto max-w-7xl space-y-5 p-6">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl font-semibold text-slate-100">Events</h1>
        <button
          onClick={refresh}
          className="rounded-lg border border-base-600 px-3 py-1.5 font-mono text-xs text-slate-300 hover:bg-base-800"
        >
          Refresh
        </button>
      </div>

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

      <div className="flex flex-wrap gap-3">
        <Select
          label="Event Type"
          value={eventType}
          onChange={setEventType}
          options={['', ...EVENT_TYPES]}
        />
        <Select
          label="Department"
          value={department}
          onChange={setDepartment}
          options={['', 'PWD', 'TRAFFIC']}
        />
        <input
          placeholder="Bus ID (e.g. BUS-001)"
          value={busId}
          onChange={(e) => setBusId(e.target.value)}
          className="rounded-lg border border-base-600 bg-base-900 px-3 py-1.5 font-mono text-sm text-slate-200 placeholder:text-slate-600 focus:border-signal-cyan focus:outline-none"
        />
      </div>

      {loading ? <Loading /> : <EventTable events={events} onSelect={setSelectedEvent} />}

      <EventDetails event={selectedEvent} onClose={() => setSelectedEvent(null)} />
    </div>
  )
}

function Select({ label, value, onChange, options }) {
  return (
    <label className="flex flex-col gap-1">
      <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500">
        {label}
      </span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-lg border border-base-600 bg-base-900 px-3 py-1.5 font-mono text-sm text-slate-200 focus:border-signal-cyan focus:outline-none"
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt || 'All'}
          </option>
        ))}
      </select>
    </label>
  )
}
