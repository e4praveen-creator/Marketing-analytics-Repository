import Link from 'next/link'
import { apiGet, apiPost } from '../../lib/api'

export default async function CockpitPage() {
  const campaigns = await apiGet('/campaigns')
  const spend = await apiPost('/metrics/query', {
    metric: 'spend', dimensions: ['campaign'], filters: {}, date_range: { start: '2024-01-01', end: '2030-01-01' }
  })
  const clicks = await apiPost('/metrics/query', {
    metric: 'clicks', dimensions: ['campaign'], filters: {}, date_range: { start: '2024-01-01', end: '2030-01-01' }
  })

  const totalSpend = spend.rows.reduce((a: number, r: any) => a + (r.spend || 0), 0)
  const totalClicks = clicks.rows.reduce((a: number, r: any) => a + (r.clicks || 0), 0)

  return (
    <div>
      <div className="kpi-grid">
        <div className="card"><b>Spend</b><div>${totalSpend.toFixed(2)}</div></div>
        <div className="card"><b>Clicks</b><div>{totalClicks}</div></div>
        <div className="card"><b>Campaigns</b><div>{campaigns.length}</div></div>
        <div className="card"><b>Data freshness</b><div>{spend.metadata.freshness.slice(0, 19)}</div></div>
      </div>
      <div className="card">
        <h3>Cross-channel performance</h3>
        <table>
          <thead><tr><th>Campaign</th><th>Channel</th><th>Status</th><th>Budget Daily</th><th>Details</th></tr></thead>
          <tbody>
            {campaigns.map((c: any) => (
              <tr key={c.id}><td>{c.name}</td><td>{c.channel}</td><td>{c.status}</td><td>{c.budget_daily}</td><td><Link href={`/campaign/${c.id}`}>View</Link></td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
