import { apiGet } from '../../../lib/api'

export default async function MetricCatalogPage() {
  const defs = await apiGet('/metrics/definitions')
  return <div className="card"><h2>Metric Definitions</h2><table><thead><tr><th>Name</th><th>Formula</th><th>Allowed Dims</th><th>Version</th></tr></thead><tbody>{defs.map((d:any)=><tr key={d.id}><td>{d.metric_name}</td><td>{d.formula}</td><td>{Array.isArray(d.allowed_dims)?d.allowed_dims.join(', '):''}</td><td>{d.version}</td></tr>)}</tbody></table></div>
}
