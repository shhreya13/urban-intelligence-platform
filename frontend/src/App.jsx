import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Events from './pages/Events.jsx'
import Traffic from './pages/Traffic.jsx'
import PWD from './pages/PWD.jsx'

/**
 * App.jsx
 * Purpose: Top-level layout + route table for the ONE common application.
 * Overview / Traffic / PWD / Events are all views inside this single React
 * app (per the "one common dashboard, department filtering inside it"
 * requirement) — never separate apps.
 *
 * Connects to:
 * - src/main.jsx -> rendered inside BrowserRouter
 * - src/components/Navbar.jsx -> nav links matching these routes
 * - src/pages/* -> one component per route
 */
export default function App() {
  return (
    <div className="min-h-screen bg-base-950">
      <Navbar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/traffic" element={<Traffic />} />
        <Route path="/pwd" element={<PWD />} />
        <Route path="/events" element={<Events />} />
      </Routes>
    </div>
  )
}
