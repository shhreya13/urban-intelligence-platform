/**
 * data/mockEvents.js
 * Purpose: Static demo data used when VITE_USE_MOCK=true (or when the live
 * backend is unreachable). Shape matches the backend's EventOut / BusOut /
 * traffic-summary responses exactly, so components never need mock-specific
 * branches — only services/api.js decides which source to use.
 *
 * Connects to:
 * - src/services/api.js -> returned instead of a live fetch when mocking
 */

export const mockEvents = [
  {
    id: 1,
    event_id: 'EVT-1001',
    bus_id: 'BUS-001',
    camera_id: 'FRONT-01',
    event_type: 'POTHOLE',
    confidence: 0.93,
    timestamp: '2026-08-30T08:34:18.124',
    latitude: 13.0827,
    longitude: 80.2707,
    frame_id: 101,
    evidence_path: 'events/EVT-1001.jpg',
    department: 'PWD',
  },
  {
    id: 2,
    event_id: 'EVT-1002',
    bus_id: 'BUS-002',
    camera_id: 'FRONT-01',
    event_type: 'POTHOLE',
    confidence: 0.87,
    timestamp: '2026-08-30T08:27:18.124',
    latitude: 13.0604,
    longitude: 80.2496,
    frame_id: 202,
    evidence_path: 'events/EVT-1002.jpg',
    department: 'PWD',
  },
  {
    id: 3,
    event_id: 'EVT-1003',
    bus_id: 'BUS-003',
    camera_id: 'FRONT-02',
    event_type: 'ROAD_DEFECT',
    confidence: 0.78,
    timestamp: '2026-08-30T08:19:18.124',
    latitude: 13.085,
    longitude: 80.2101,
    frame_id: 305,
    evidence_path: 'events/EVT-1003.jpg',
    department: 'PWD',
  },
  {
    id: 4,
    event_id: 'EVT-1004',
    bus_id: 'BUS-004',
    camera_id: 'FRONT-01',
    event_type: 'POTHOLE',
    confidence: 0.95,
    timestamp: '2026-08-30T08:36:18.124',
    latitude: 13.1143,
    longitude: 80.2329,
    frame_id: 410,
    evidence_path: 'events/EVT-1004.jpg',
    department: 'PWD',
  },
  {
    id: 5,
    event_id: 'EVT-2001',
    bus_id: 'BUS-001',
    camera_id: 'FRONT-01',
    event_type: 'TRAFFIC_DENSITY',
    confidence: 0.81,
    timestamp: '2026-08-30T08:31:18.124',
    latitude: 13.07,
    longitude: 80.26,
    frame_id: 150,
    evidence_path: null,
    department: 'TRAFFIC',
  },
  {
    id: 6,
    event_id: 'EVT-2002',
    bus_id: 'BUS-005',
    camera_id: 'FRONT-01',
    event_type: 'CONGESTION',
    confidence: 0.89,
    timestamp: '2026-08-30T08:24:18.124',
    latitude: 13.123,
    longitude: 80.2934,
    frame_id: 220,
    evidence_path: null,
    department: 'TRAFFIC',
  },
  {
    id: 7,
    event_id: 'EVT-2003',
    bus_id: 'BUS-003',
    camera_id: 'FRONT-01',
    event_type: 'TRAFFIC_DENSITY',
    confidence: 0.74,
    timestamp: '2026-08-30T08:14:18.124',
    latitude: 13.09,
    longitude: 80.22,
    frame_id: 260,
    evidence_path: null,
    department: 'TRAFFIC',
  },
]

export const mockBuses = [
  { id: 1, bus_id: 'BUS-001', route_name: 'Route 21G - T.Nagar to Tambaram', status: 'ACTIVE', last_latitude: 13.0827, last_longitude: 80.2707, last_updated: '2026-08-30T08:39:18' },
  { id: 2, bus_id: 'BUS-002', route_name: 'Route 5C - Broadway to Adyar', status: 'ACTIVE', last_latitude: 13.0604, last_longitude: 80.2496, last_updated: '2026-08-30T08:39:18' },
  { id: 3, bus_id: 'BUS-003', route_name: 'Route 102 - Anna Nagar to Velachery', status: 'ACTIVE', last_latitude: 13.085, last_longitude: 80.2101, last_updated: '2026-08-30T08:39:18' },
  { id: 4, bus_id: 'BUS-004', route_name: 'Route 18 - Perambur to Guindy', status: 'ACTIVE', last_latitude: 13.1143, last_longitude: 80.2329, last_updated: '2026-08-30T08:39:18' },
  { id: 5, bus_id: 'BUS-005', route_name: 'Route 47 - Tondiarpet to OMR', status: 'ACTIVE', last_latitude: 13.123, last_longitude: 80.2934, last_updated: '2026-08-30T08:39:18' },
]

export const mockTraffic = {
  total_vehicles: 151,
  cars: 72,
  motorcycles: 41,
  buses: 12,
  trucks: 23,
  traffic_level: 'HIGH',
}
