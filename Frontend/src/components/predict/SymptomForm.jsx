import { useMemo, useState } from "react";

import { SYMPTOMS } from "../../constants/symptoms";

function buildInitialState() {
  return SYMPTOMS.reduce((acc, item) => {
    acc[item.key] = 0;
    return acc;
  }, {});
}

export default function SymptomForm({ onSubmit, loading }) {
  const [values, setValues] = useState(buildInitialState);
  const [error, setError] = useState("");

  const selectedCount = useMemo(
    () => Object.values(values).filter((value) => value === 1).length,
    [values]
  );

  function toggleSymptom(key) {
    setValues((prev) => ({
      ...prev,
      [key]: prev[key] === 1 ? 0 : 1,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (selectedCount === 0) {
      setError("Select at least one symptom.");
      return;
    }

    setError("");
    await onSubmit(values);
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <div className="card-header">
        <h2>Symptoms</h2>
        <p>Select all symptoms currently present.</p>
      </div>

      <div className="symptom-grid">
        {SYMPTOMS.map((symptom) => (
          <label key={symptom.key} className="symptom-item">
            <input
              type="checkbox"
              checked={values[symptom.key] === 1}
              onChange={() => toggleSymptom(symptom.key)}
            />
            <span>{symptom.label}</span>
          </label>
        ))}
      </div>

      {error && <p className="form-error">{error}</p>}

      <button type="submit" className="btn-primary" disabled={loading}>
        {loading ? "Predicting..." : "Predict Disease"}
      </button>
    </form>
  );
}
