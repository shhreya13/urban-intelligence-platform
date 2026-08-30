import { NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { getHealth, cameraStart, cameraStop, getCameraStatus } from '../services/api.js'

/**
 * components/Navbar.jsx
 * Purpose: Top navigation for the ONE common application — Overview /
 * Traffic / PWD / Events — plus a live indicator showing whether the app
 * is talking to the real FastAPI backend or running on mock/demo data.
 *
 * Also hosts a Camera button that starts/stops the live webcam demo on the
 * backend (/camera/start + /camera/stop) so it can be triggered right from
 * the dashboard during a presentation.
 *
 * Connects to:
 * - src/App.jsx -> rendered on every route
 * - src/services/api.js -> getHealth(), cameraStart(), cameraStop(),
 *   getCameraStatus()
 */
const USE_MOCK = String(import.meta.env.VITE_USE_MOCK) === 'true'

const links = [
  { to: '/', label: 'Overview', end: true },
  { to: '/traffic', label: 'Traffic' },
  { to: '/pwd', label: 'PWD' },
  { to: '/events', label: 'Events' },
]

export default function Navbar() {
  const [connected, setConnected] = useState(null)
  const [cameraOn, setCameraOn] = useState(false)
  const [cameraBusy, setCameraBusy] = useState(false)

  useEffect(() => {
    if (USE_MOCK) return
    let cancelled = false
    getHealth().then((ok) => {
      if (!cancelled) setConnected(ok)
    })
    const interval = setInterval(async () => {
      const ok = await getHealth()
      if (!cancelled) setConnected(ok)
    }, 15000)
    getCameraStatus().then((running) => {
      if (!cancelled) setCameraOn(running)
    })
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  const toggleCamera = async () => {
    setCameraBusy(true)
    try {
      if (cameraOn) {
        await cameraStop()
        setCameraOn(false)
      } else {
        await cameraStart()
        setCameraOn(true)
      }
    } catch {
      alert('Could not reach backend to control the camera.')
    } finally {
      setCameraBusy(false)
    }
  }

  const statusLabel = USE_MOCK
    ? 'DEMO DATA'
    : connected === null
    ? 'CHECKING…'
    : connected
    ? 'LIVE'
    : 'BACKEND UNAVAILABLE'

  const statusColor = USE_MOCK
    ? 'bg-signal-amber'
    : connected === null
    ? 'bg-slate-500'
    : connected
    ? 'bg-signal-green'
    : 'bg-signal-red'

  return (
    <nav className="sticky top-0 z-[1000] flex items-center justify-between border-b border-base-700 bg-base-950/95 px-6 py-3 backdrop-blur">
      <div className="flex items-center gap-8">
        <span className="font-display text-lg font-semibold tracking-tight text-slate-100">
          URBAN<span className="text-signal-cyan">INTEL</span>
        </span>
        <div className="flex gap-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `rounded-lg px-3 py-1.5 font-mono text-sm transition-colors ${
                  isActive
                    ? 'bg-base-700 text-slate-100'
                    : 'text-slate-400 hover:bg-base-800 hover:text-slate-200'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </div>
      </div>
      <div className="flex items-center gap-3">
        <button
          onClick={toggleCamera}
          disabled={cameraBusy || !connected}
          className={`flex items-center gap-2 rounded-lg px-3 py-1.5 font-mono text-sm transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
            cameraOn
              ? 'bg-signal-green text-base-950'
              : 'bg-base-700 text-slate-200 hover:bg-base-600'
          }`}
          title={
            cameraOn
              ? 'Stop the live camera demo'
              : 'Start the live camera demo (webcam)'
          }
        >
          <span
            className={`h-2 w-2 rounded-full ${
              cameraOn ? 'bg-base-950' : 'bg-signal-cyan'
            }`}
          />
          {cameraBusy
            ? '…'
            : cameraOn
            ? 'CAMERA ON'
            : 'CAMERA'}
        </button>
        <div className="flex items-center gap-2 font-mono text-xs text-slate-400">
          <span className={`h-2 w-2 rounded-full ${statusColor}`} />
          {statusLabel}
        </div>
      </div>
    </nav>
  )
}
