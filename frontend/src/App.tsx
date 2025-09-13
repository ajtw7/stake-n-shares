import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <button
        onClick={async () => {
          try {
            const q = new URLSearchParams({ start: '2025-01-01', end: '2025-02-01' });
            const eventId = '0123456789abcdef0123456789abcdef'; // 32-char hex
            const res = await fetch(`${import.meta.env.VITE_API_BASE}/api/v1/compare?${q}`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                starting_capital: 1000,
                equity_symbol: 'AAPL',
                equity_weight: 0.7,
                bet: {
                  league: 'NFL',
                  event_id: eventId,
                  stake: 100,
                  odds: 150,
                  outcome: 'win'
                }
              })
            });
            let body;
            try { body = await res.json(); } catch { body = await res.text(); }
            console.log('Compare status', res.status);
            console.log('Compare body', body);
          } catch (e) {
            console.error(e);
          }
        }}
      >
        Test Compare
      </button>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
