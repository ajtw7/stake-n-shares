import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { CompareForm } from './components/CompareForm'

function App() {
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
      <h1>Stake-n-Shares Frontend MVP</h1>
      <CompareForm />
      <p className="read-the-docs">
        Next: add refinement (validation messages, formatting helpers, persistence).
      </p>
    </>
  )
}

export default App
