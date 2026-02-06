import { apiGet } from '../../../lib/api'

export default async function CampaignDetail({ params }: { params: { id: string } }) {
  const data = await apiGet(`/campaigns/${params.id}`)
  return (
    <div className="card">
      <h2>{data.campaign.name}</h2>
      <p>Status: {data.campaign.status} | Channel: {data.campaign.channel} | Objective: {data.campaign.objective}</p>
      <h3>Trend (last records)</h3>
      <table><thead><tr><th>Date</th><th>Impressions</th><th>Clicks</th><th>Spend</th><th>Conversions</th></tr></thead>
      <tbody>{data.metrics.slice(-14).map((m: any) => <tr key={m.id}><td>{m.date}</td><td>{m.impressions}</td><td>{m.clicks}</td><td>{m.spend}</td><td>{m.conversions}</td></tr>)}</tbody></table>
    </div>
  )
}
