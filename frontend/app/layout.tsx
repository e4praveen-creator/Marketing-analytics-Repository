import './styles.css'
import Nav from '../components/Nav'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <main style={{ maxWidth: 1100, margin: '20px auto', fontFamily: 'Arial' }}>
          <h1>Marketing Analyst AI Cockpit</h1>
          <Nav />
          {children}
        </main>
      </body>
    </html>
  )
}
