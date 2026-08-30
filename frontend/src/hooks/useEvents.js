import { useState, useEffect, useCallback } from 'react'
import { getEvents } from '../services/api.js'

/**
 * hooks/useEvents.js
 * Purpose: Fetches events (with optional filters) and exposes
 * { events, loading, error, isMock, refresh }. Every page that needs event
 * data (Dashboard, Events, Traffic, PWD) uses this hook instead of calling
 * services/api.js directly, so loading/error handling stays consistent.
 *
 * Connects to:
 * - src/services/api.js -> getEvents()
 * - src/pages/Dashboard.jsx, Events.jsx, Traffic.jsx, PWD.jsx -> consumers
 */
export default function useEvents(filters = {}) {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isMock, setIsMock] = useState(false)

  // Stringify filters so the effect only re-runs when filter *values* change,
  // not on every re-render (a new {} object would otherwise loop forever).
  const filterKey = JSON.stringify(filters)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { data, isMock: mockFlag } = await getEvents(JSON.parse(filterKey))
      setEvents(data)
      setIsMock(mockFlag)
    } catch (err) {
      setError(err.message || 'Failed to load events')
    } finally {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterKey])

  useEffect(() => {
    refresh()
  }, [refresh])

  return { events, loading, error, isMock, refresh }
}
