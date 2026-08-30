/**
 * components/EventDetails.jsx
 * Purpose: Full detail panel for one event — event type, confidence, bus ID,
 * camera ID, timestamp, GPS, frame ID, and evidence image if available.
 * Rendered as a modal overlay; closing is controlled by the parent (onClose).
 *
 * Connects to:
 * - src/pages/Dashboard.jsx, Events.jsx, Traffic.jsx, PWD.jsx -> opened when
 *   an EventTable row or map marker is clicked
 * - Evidence images resolve against VITE_API_URL (backend serves /evidence
 *   as a static path in production; for the MVP a placeholder is shown if
 *   the image fails to load — see the `onError` handler below)
 */
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function EventDetails({ event, onClose }) {
  if (!event) return null

  const evidenceUrl = event.evidence_path
    ? `${API_URL}/${event.evidence_path}`
    : null

  return (
    <div
      className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-xl border border-base-600 bg-base-900 p-5 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between">
          <div>
            <div className="font-mono text-xs text-slate-500">{event.event_id}</div>
            <h3 className="font-display text-xl font-semibold text-slate-100">
              {event.event_type}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg px-2 py-1 text-slate-400 hover:bg-base-800 hover:text-slate-200"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {evidenceUrl && (
          <img
            src={evidenceUrl}
            alt="Evidence"
            className="mt-4 h-40 w-full rounded-lg border border-base-700 object-cover"
            onError={(e) => {
              e.currentTarget.style.display = 'none'
            }}
          />
        )}

        <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 font-mono text-sm">
          <Field label="Confidence" value={`${(event.confidence * 100).toFixed(1)}%`} />
          <Field
            label="Department"
            value={event.department}
            valueClass={event.department === 'PWD' ? 'text-signal-amber' : 'text-signal-cyan'}
          />
          <Field label="Bus ID" value={event.bus_id} />
          <Field label="Camera" value={event.camera_id} />
          <Field label="Timestamp" value={new Date(event.timestamp).toLocaleString()} full />
          <Field label="GPS" value={`${event.latitude.toFixed(5)}, ${event.longitude.toFixed(5)}`} full />
          {event.frame_id != null && <Field label="Frame ID" value={event.frame_id} />}
          {!evidenceUrl && <Field label="Evidence" value="Not available" />}
        </dl>
      </div>
    </div>
  )
}

function Field({ label, value, full, valueClass = 'text-slate-200' }) {
  return (
    <div className={full ? 'col-span-2' : ''}>
      <dt className="text-[11px] uppercase tracking-wider text-slate-500">{label}</dt>
      <dd className={`mt-0.5 ${valueClass}`}>{value}</dd>
    </div>
  )
}
