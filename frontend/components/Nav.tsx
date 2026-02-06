import Link from 'next/link'

export default function Nav() {
  const links = ['cockpit', 'anomalies', 'chat', 'admin/metrics', 'audit']
  return (
    <nav style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
      {links.map((l) => (
        <Link key={l} href={`/${l}`}>{l}</Link>
      ))}
    </nav>
  )
}
