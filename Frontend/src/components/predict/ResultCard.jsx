export default function ResultCard({ result }) {
  if (!result) {
    return (
      <section className="card result-card">
        <h2>Result</h2>
        <p className="muted">Prediction appears here after you submit symptoms.</p>
      </section>
    );
  }

  const prediction = result?.data;
  const top = prediction?.top_predictions || [];

  return (
    <section className="card result-card">
      <h2>Result</h2>

      <div className="result-main">
        <p className="result-label">Predicted Disease</p>
        <h3>{prediction?.predicted_disease || "-"}</h3>
        <p className="result-confidence">
          Confidence: {prediction?.confidence ? `${(prediction.confidence * 100).toFixed(1)}%` : "N/A"}
        </p>
      </div>

      <div className="remedy-box">
        <p className="result-label">Suggested Remedy</p>
        <p>{prediction?.remedy || "No remedy available."}</p>
      </div>

      {top.length > 0 && (
        <div className="top-predictions">
          <p className="result-label">Other Possible Diseases</p>
          <ul>
            {top.slice(1).map((item) => (
              <li key={item.disease}>
                <span>{item.disease}</span>
                <span>{(item.confidence * 100).toFixed(1)}%</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
