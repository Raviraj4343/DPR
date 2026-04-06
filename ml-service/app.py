from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import joblib
from flask import Flask, jsonify, request


CURRENT_DIR = Path(__file__).resolve().parent
MODEL_DIR = CURRENT_DIR / "model"
PROJECT_ROOT = CURRENT_DIR

if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from utils.preprocess import get_feature_columns, preprocess_user_input  # noqa: E402


MODEL_PATH = MODEL_DIR / "model.pkl"
ENCODER_PATH = MODEL_DIR / "encoder.pkl"
METADATA_PATH = MODEL_DIR / "metadata.json"


app = Flask(__name__)


model = None
encoder = None
metadata: Dict[str, Any] = {}
feature_columns: List[str] = list(get_feature_columns())


def load_artifacts() -> None:
	"""Load trained model artifacts into memory."""
	global model, encoder, metadata, feature_columns

	missing = [
		str(path)
		for path in (MODEL_PATH, ENCODER_PATH, METADATA_PATH)
		if not path.exists()
	]
	if missing:
		raise FileNotFoundError(
			"Missing model artifacts. Train the model first. Missing: "
			+ ", ".join(missing)
		)

	model = joblib.load(MODEL_PATH)
	encoder = joblib.load(ENCODER_PATH)

	metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
	feature_columns = metadata.get("feature_columns") or list(get_feature_columns())


def ensure_artifacts_loaded() -> None:
	if model is None or encoder is None:
		load_artifacts()


def build_top_predictions(probabilities) -> List[Dict[str, Any]]:
	"""Return top-3 predictions with remedies for UI display."""
	classes = list(encoder.classes_)
	remedy_map = metadata.get("remedy_map", {})

	ranked_indices = sorted(
		range(len(probabilities)), key=lambda idx: probabilities[idx], reverse=True
	)[:3]

	top = []
	for idx in ranked_indices:
		disease = classes[idx]
		top.append(
			{
				"disease": disease,
				"confidence": round(float(probabilities[idx]), 4),
				"remedy": remedy_map.get(disease, "Consult a doctor for proper guidance."),
			}
		)
	return top


@app.get("/")
def index():
	return jsonify(
		{
			"service": "disease-prediction-api",
			"status": "running",
			"endpoints": ["GET /health", "GET /features", "POST /predict"],
		}
	)


@app.get("/health")
def health():
	try:
		ensure_artifacts_loaded()
		return jsonify(
			{
				"status": "ok",
				"model_loaded": True,
				"classes": list(encoder.classes_),
			}
		)
	except Exception as exc:  # pragma: no cover
		return jsonify({"status": "error", "model_loaded": False, "error": str(exc)}), 500


@app.get("/features")
def features():
	return jsonify({"feature_columns": feature_columns})


@app.post("/predict")
def predict():
	try:
		ensure_artifacts_loaded()
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500

	payload = request.get_json(silent=True)
	if not isinstance(payload, dict):
		return jsonify({"error": "Invalid JSON body. Send a JSON object."}), 400

	try:
		model_input = preprocess_user_input(payload)
	except ValueError as exc:
		return jsonify({"error": str(exc)}), 400

	model_input = model_input.reindex(columns=feature_columns, fill_value=0)

	encoded_prediction = model.predict(model_input)[0]
	predicted_disease = encoder.inverse_transform([encoded_prediction])[0]

	remedy_map = metadata.get("remedy_map", {})
	remedy = remedy_map.get(predicted_disease, "Consult a doctor for proper guidance.")

	response: Dict[str, Any] = {
		"predicted_disease": predicted_disease,
		"remedy": remedy,
		"input": model_input.iloc[0].to_dict(),
	}

	if hasattr(model, "predict_proba"):
		probabilities = model.predict_proba(model_input)[0]
		top_predictions = build_top_predictions(probabilities)
		response["confidence"] = top_predictions[0]["confidence"]
		response["top_predictions"] = top_predictions

	return jsonify(response)


if __name__ == "__main__":
	try:
		ensure_artifacts_loaded()
	except Exception as exc:
		print(f"Warning: {exc}")
		print("Run train_model.py first to create model artifacts.")

	app.run(host="0.0.0.0", port=5000, debug=True)

