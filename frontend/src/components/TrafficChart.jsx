import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

/**
 * components/TrafficChart.jsx
 * Purpose: Bar chart of vehicle counts by class (cars/motorcycles/buses/
 * trucks), fed by GET /traffic. Designed to keep working unchanged once
 * Person 1's real vehicle-counter output replaces the seeded baseline —
 * only the numbers change, not this component.
 *
 * Connects to:
 * - src/pages/Dashboard.jsx -> Overview traffic snapshot
 * - src/pages/Traffic.jsx   -> full Traffic view
 * - Data comes from services/api.js -> getTraffic()
 */
export default function TrafficChart({ traffic }) {
  if (!traffic) return null

  const data = [
    { name: 'Cars', count: traffic.cars },
    { name: 'Motorcycles', count: traffic.motorcycles },
    { name: 'Buses', count: traffic.buses },
    { name: 'Trucks', count: traffic.trucks },
  ]

  return (
    <div className="rounded-xl border border-base-700 bg-base-900/60 p-4">
      <div className="mb-3 font-mono text-[11px] uppercase tracking-wider text-slate-400">
        Vehicle Composition
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#212a3d" vertical={false} />
          <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} />
          <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
          <Tooltip
            contentStyle={{
              background: '#161d2c',
              border: '1px solid #31405a',
              borderRadius: 8,
              color: '#e2e8f0',
              fontSize: 12,
            }}
          />
          <Bar dataKey="count" fill="#3ddcd6" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
