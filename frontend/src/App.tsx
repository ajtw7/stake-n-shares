import { useState, type JSX } from "react";
import { CompareForm } from "./components/CompareForm";
import ResultCard from "./components/ResultCard";
import { ErrorBoundary } from './components/ErrorBoundary'
import './App.css'
import './styles.css'

export default function App(): JSX.Element {
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <ErrorBoundary>
      <div className="app-root">
        <header className="topbar">
          <div className="brand">
            <h1>Stake &amp; Shares</h1>
            <span className="tag">Compare stock vs sportsbook in one view</span>
          </div>
        </header>

        <main className="container">
          <section className="panel panel-form">
            <h2>Run a comparison</h2>
            <p className="muted">Pick equity range, allocate %, and a single bet. Results show combined outcome and odds metadata.</p>

            <CompareForm
              onSubmit={async (payload, params) => {
                setError(null);
                setLoading(true);
                setResult(null);
                try {
                  const q = new URLSearchParams({ start: params.start, end: params.end });
                  if (params.odds_date) q.set("odds_date", params.odds_date);
                  const res = await fetch(`/api/v1/compare?${q.toString()}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                  });
                  if (!res.ok) {
                    const txt = await res.text();
                    throw new Error(txt || res.statusText);
                  }
                  const json = await res.json();
                  setResult(json);
                } catch (err: any) {
                  setError(err.message || "Request failed");
                } finally {
                  setLoading(false);
                }
              }}
              submitting={loading}
            />

            {error && <div className="alert error">{error}</div>}
          </section>

          <section className="panel panel-result">
            <h2>Result</h2>
            {!result && <div className="muted">No run yet — submit the form to see results here.</div>}
            {result && <ResultCard data={result} />}
          </section>
        </main>
      </div>
    </ErrorBoundary>
  )
}
