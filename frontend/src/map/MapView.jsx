import { MapContainer, TileLayer } from 'react-leaflet'
import EventMarker from './EventMarker.jsx'
import BusMarker from './BusMarker.jsx'

/**
 * map/MapView.jsx
 * Purpose: The GIS map itself — dark-themed Leaflet tiles centered on
 * Chennai, rendering event markers (potholes/traffic) and bus markers.
 * All markers come from live backend/mock data — nothing is hardcoded here.
 *
 * Connects to:
 * - src/pages/Dashboard.jsx, Events.jsx, Traffic.jsx, PWD.jsx -> pass
 *   filtered `events` / `buses` arrays as props
 * - map/EventMarker.jsx, map/BusMarker.jsx -> per-item marker rendering
 * - components/EventDetails.jsx -> opened via onSelectEvent
 */
const CHENNAI_CENTER = [13.0827, 80.2707]

export default function MapView({ events = [], buses = [], onSelectEvent, height = 420 }) {
  return (
    <div
      className="overflow-hidden rounded-xl border border-base-700"
      style={{ height }}
    >
      <MapContainer
        center={CHENNAI_CENTER}
        zoom={12}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        {events
          .filter((e) => isValidCoord(e.latitude, e.longitude))
          .map((e) => (
            <EventMarker key={e.event_id} event={e} onSelect={onSelectEvent} />
          ))}
        {buses.map((b) => (
          <BusMarker key={b.bus_id} bus={b} />
        ))}
      </MapContainer>
    </div>
  )
}

function isValidCoord(lat, lon) {
  return (
    typeof lat === 'number' &&
    typeof lon === 'number' &&
    lat >= -90 &&
    lat <= 90 &&
    lon >= -180 &&
    lon <= 180
  )
}
