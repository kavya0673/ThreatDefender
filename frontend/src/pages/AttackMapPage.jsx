import { Globe2, Zap, MapPin, Activity, Layers } from 'lucide-react'
import { useAppStore } from '../store/useAppStore.jsx'

const originEvents = [
  { id: 1, location: 'Moscow, RU', type: 'Botnet', asset: 'auth.corp.local', severity: 'High' },
  { id: 2, location: 'Seoul, KR', type: 'API brute force', asset: 'api.corp.local', severity: 'Medium' },
  { id: 3, location: 'Frankfurt, DE', type: 'Scanner probe', asset: 'portal.corp.local', severity: 'Low' },
]

export default function AttackMapPage() {
  const assets = useAppStore((state) => state.assets)

  return (
    <div className="page-shell">
      <div className="page-head">
        <div>
          <p className="eyebrow">Attack Surface Analytics</p>
          <h1>Global Threat Map</h1>
          <p>Track live attack origins, geo-IP intelligence, and threat vectors in a SOC-ready interface.</p>
        </div>
        <div className="hero-pill blue">Geo-IP insights</div>
      </div>

      <div className="grid-2">
        <section className="glass-card map-card">
          <div className="card-head">
            <div>
              <h2>Interactive Attack Map</h2>
              <p>Live threat origin tracking and animated attack routes.</p>
            </div>
          </div>
          <div className="world-map">
            <div className="map-pin pin-1"><MapPin size={16} /><span>RU</span></div>
            <div className="map-pin pin-2"><MapPin size={16} /><span>KR</span></div>
            <div className="map-pin pin-3"><MapPin size={16} /><span>DE</span></div>
            <div className="connection-line line-1" />
            <div className="connection-line line-2" />
            <div className="connection-line line-3" />
          </div>
        </section>

        <section className="glass-card threat-feed-card">
          <div className="card-head">
            <div>
              <h2>Live Event Feed</h2>
              <p>Latest inbound threats and asset targeting summary.</p>
            </div>
            <span className="tag">Realtime</span>
          </div>
          <ul className="event-feed">
            {originEvents.map((event) => (
              <li key={event.id}>
                <div>
                  <strong>{event.type}</strong>
                  <p>{event.asset} targeted from {event.location}</p>
                </div>
                <span className={`badge ${event.severity.toLowerCase()}`}>{event.severity}</span>
              </li>
            ))}
          </ul>
          <div className="connection-summary">
            <div><Zap size={16} /><span>Threat origins</span><strong>3</strong></div>
            <div><Layers size={16} /><span>Assets impacted</span><strong>{assets.length}</strong></div>
            <div><Activity size={16} /><span>Events in last hour</span><strong>14</strong></div>
          </div>
        </section>
      </div>

      <section className="glass-card analysis-card">
        <div className="card-head">
          <div>
            <h2>Country Threat Overview</h2>
            <p>Aggregate geo-threat scoring and top source locations.</p>
          </div>
        </div>
        <div className="country-grid">
          <div><strong>Russia</strong><span>37%</span></div>
          <div><strong>South Korea</strong><span>28%</span></div>
          <div><strong>Germany</strong><span>18%</span></div>
          <div><strong>US</strong><span>9%</span></div>
          <div><strong>Other</strong><span>8%</span></div>
        </div>
      </section>
    </div>
  )
}
