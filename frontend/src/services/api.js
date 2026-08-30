/**
 * services/api.js
 * Purpose: THE single place every component/hook calls to reach the backend.
 * No component should ever hardcode a fetch URL — everything routes through
 * here so the mock/live switch and the API base URL only exist in one file.
 *
 * Modes:
 * - VITE_USE_MOCK=true  -> always return data from src/data/mockEvents.js
 * - VITE_USE_MOCK=false -> call the FastAPI backend at VITE_API_URL. If the
 *   backend is unreachable, transparently fall back to mock data and flag
 *   `isMock: true` so the UI can show "Backend unavailable — using demo data".
 *
 * Connects to:
 * - src/hooks/useEvents.js -> getEvents(), postEvent()
 * - src/pages/*.jsx        -> getTraffic(), getBuses(), getEvent()
 * - backend/app/api/events.py, traffic.py, buses.py -> the real endpoints
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const USE_MOCK = String(import.meta.env.VITE_USE_MOCK) === 'true'

import { mockEvents, mockBuses, mockTraffic } from '../data/mockEvents.js'

async function safeFetch(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      // response wasn't JSON — keep statusText
    }
    const err = new Error(detail)
    err.status = res.status
    throw err
  }
  return res.json()
}

function applyFilters(events, filters = {}) {
  return events.filter((e) => {
    if (filters.event_type && e.event_type !== filters.event_type) return false
    if (filters.department && e.department !== filters.department) return false
    if (filters.bus_id && e.bus_id !== filters.bus_id) return false
    return true
  })
}

/** GET /events with optional { event_type, department, bus_id } filters. */
export async function getEvents(filters = {}) {
  if (USE_MOCK) {
    return { data: applyFilters(mockEvents, filters), isMock: true }
  }
  try {
    const params = new URLSearchParams(filters).toString()
    const data = await safeFetch(`/events${params ? `?${params}` : ''}`)
    return { data, isMock: false }
  } catch (err) {
    console.warn('Backend unavailable, falling back to mock events:', err.message)
    return { data: applyFilters(mockEvents, filters), isMock: true }
  }
}

/** GET /events/{event_id} — fetch one event's full detail. */
export async function getEvent(eventId) {
  if (USE_MOCK) {
    const found = mockEvents.find((e) => e.event_id === eventId)
    return { data: found || null, isMock: true }
  }
  try {
    const data = await safeFetch(`/events/${eventId}`)
    return { data, isMock: false }
  } catch (err) {
    console.warn('Backend unavailable, falling back to mock event:', err.message)
    const found = mockEvents.find((e) => e.event_id === eventId)
    return { data: found || null, isMock: true }
  }
}

/** POST /events — ingest one event. Used for manual testing from the UI. */
export async function postEvent(event) {
  if (USE_MOCK) {
    return { data: { ...event, id: Date.now(), department: event.event_type }, isMock: true }
  }
  const data = await safeFetch('/events', {
    method: 'POST',
    body: JSON.stringify(event),
  })
  return { data, isMock: false }
}

/** GET /traffic — vehicle-count / traffic-level summary. */
export async function getTraffic() {
  if (USE_MOCK) {
    return { data: mockTraffic, isMock: true }
  }
  try {
    const data = await safeFetch('/traffic')
    return { data, isMock: false }
  } catch (err) {
    console.warn('Backend unavailable, falling back to mock traffic:', err.message)
    return { data: mockTraffic, isMock: true }
  }
}

/** GET /buses — bus identity + last known GPS fix. */
export async function getBuses() {
  if (USE_MOCK) {
    return { data: mockBuses, isMock: true }
  }
  try {
    const data = await safeFetch('/buses')
    return { data, isMock: false }
  } catch (err) {
    console.warn('Backend unavailable, falling back to mock buses:', err.message)
    return { data: mockBuses, isMock: true }
  }
}

/** GET /health — used by the Navbar's live connection indicator. */
export async function getHealth() {
  try {
    await safeFetch('/health')
    return true
  } catch {
    return false
  }
}

/** GET /camera/status — is the live camera demo currently running? */
export async function getCameraStatus() {
  try {
    const data = await safeFetch('/camera/status')
    return !!data.running
  } catch {
    return false
  }
}

/** POST /camera/start — launch the live webcam demo on the backend. */
export async function cameraStart() {
  const data = await safeFetch('/camera/start', { method: 'POST' })
  return data
}

/** POST /camera/stop — terminate the running live webcam demo. */
export async function cameraStop() {
  const data = await safeFetch('/camera/stop', { method: 'POST' })
  return data
}
