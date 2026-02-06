'use client'

import { useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ChatPage() {
  const [message, setMessage] = useState('CTR last 7 days')
  const [response, setResponse] = useState<any>(null)

  async function send() {
    const res = await fetch(`${API_URL}/chat/message`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message })
    })
    setResponse(await res.json())
  }

  return (
    <div className="card">
      <h2>Chat Analyst</h2>
      <input style={{ width: '80%' }} value={message} onChange={(e) => setMessage(e.target.value)} />
      <button onClick={send}>Send</button>
      {response && (
        <div>
          <h3>{response.answer}</h3>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
