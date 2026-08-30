import { CircleMarker, Popup } from 'react-leaflet'

/**
 * map/EventMarker.jsx
 * Purpose: One marker per event on the Leaflet GIS map — color-coded by
 * department (amber = PWD/pothole, cyan = TRAFFIC). Clicking the marker's
 * popup "View details" opens the shared EventDetails modal via onSelect.
 *
 * Connects to:
 * - map/MapView.jsx -> rendered once per event in the `events` array
 * - components/EventDetails.jsx -> opened via onSelect callback
 */
const colorForDept = {
  PWD: '#e8a33d',
  TRAFFIC: '#3ddcd6',
}

export default function EventMarker({ event, onSelect }) {
  const color = colorForDept[event.department] || '#94a3b8'

  return (
    <CircleMarker
      center={[event.latitude, event.longitude]}
      radius={8}
      pathOptions={{ color, fillColor: color, fillOpacity: 0.7, weight: 2 }}
    >
      <Popup>
        <div className="space-y-1">
          <div className="font-semibold">{event.event_type}</div>
          <div className="text-xs text-slate-400">
            {event.bus_id} · {(event.confidence * 100).toFixed(0)}% confidence
          </div>
          <button
            onClick={() => onSelect?.(event)}
            className="mt-1 rounded bg-base-700 px-2 py-1 text-xs text-slate-100 hover:bg-base-600"
          >
            View details
          </button>
        </div>
      </Popup>
    </CircleMarker>
  )
}
