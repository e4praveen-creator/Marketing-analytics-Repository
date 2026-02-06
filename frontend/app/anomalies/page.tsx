import { apiGet } from '../../lib/api'

export default async function AnomaliesPage() {
  const anomalies = await apiGet('/anomalies')
  return <div className="card"><h2>Anomaly Center</h2><table><thead><tr><th>ID</th><th>Severity</th><th>Status</th><th>Metric</th><th>Explanation</th></tr></thead><tbody>{anomalies.map((a:any)=><tr key={a.id}><td>{a.id}</td><td>{a.severity}</td><td>{a.status}</td><td>{a.metric}</td><td>{a.explanation}</td></tr>)}</tbody></table></div>
}
