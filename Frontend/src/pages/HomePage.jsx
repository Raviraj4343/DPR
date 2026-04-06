import { useState } from "react";

import SymptomForm from "../components/predict/SymptomForm";
import ResultCard from "../components/predict/ResultCard";
import { predictDisease } from "../services/api";

export default function HomePage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function handleRefresh() {
    setResult(null);
    setError("");
  }

  async function handlePredict(payload) {
    setLoading(true);
    setError("");

    try {
      const response = await predictDisease(payload);
      setResult(response);
    } catch (err) {
      const message = err?.response?.data?.message || "Prediction failed. Please try again.";
      setError(message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <header className="page-header">
        <h1>Disease Prediction</h1>
        <p>Choose symptoms and get likely disease with remedy suggestions.</p>
      </header>

      <section className="layout-grid">
        <SymptomForm onSubmit={handlePredict} onRefresh={handleRefresh} loading={loading} />
        <ResultCard result={result} />
      </section>

      {error && <p className="api-error">{error}</p>}
    </main>
  );
}
