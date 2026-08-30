import { Marker, Popup } from 'react-leaflet'
import L from 'leaflet'

/**
 * map/BusMarker.jsx
 * Purpose: One marker per bus, showing its route name and last GPS update.
 * Uses a small custom divIcon (a bus emoji in a circle) rather than
 * Leaflet's default pin, so buses are visually distinct from event markers.
 *
 * Connects to:
 * - map/MapView.jsx -> rendered once per bus in the `buses` array
 * - Data comes from services/api.js -> getBuses()
 */
const busIcon = L.divIcon({
  className: '',
  html: `<div style="
      background:#161d2c;border:2px solid #3ddcd6;border-radius:9999px;
      width:28px;height:28px;display:flex;align-items:center;justify-content:center;
      font-size:14px;box-shadow:0 0 0 3px rgba(61,220,214,0.15);
    ">🚌</div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
})

export default function BusMarker({ bus }) {
  if (bus.last_latitude == null || bus.last_longitude == null) return null

  return (
    <Marker position={[bus.last_latitude, bus.last_longitude]} icon={busIcon}>
      <Popup>
        <div className="space-y-1">
          <div className="font-semibold">{bus.bus_id}</div>
          {bus.route_name && <div className="text-xs text-slate-400">{bus.route_name}</div>}
          <div className="text-xs text-slate-500">Status: {bus.status}</div>
          {bus.last_updated && (
            <div className="text-xs text-slate-500">
              Updated {new Date(bus.last_updated).toLocaleTimeString()}
            </div>
          )}
        </div>
      </Popup>
    </Marker>
  )
}
