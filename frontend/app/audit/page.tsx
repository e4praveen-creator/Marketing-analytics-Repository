import { apiGet } from '../../lib/api'

export default async function AuditPage() {
  const logs = await apiGet('/audit/actions')
  return <div className="card"><h2>Audit Trail</h2><table><thead><tr><th>ID</th><th>Type</th><th>Target</th><th>Time</th></tr></thead><tbody>{logs.map((l:any)=><tr key={l.id}><td>{l.id}</td><td>{l.action_type}</td><td>{l.target_id}</td><td>{l.timestamp}</td></tr>)}</tbody></table></div>
}
