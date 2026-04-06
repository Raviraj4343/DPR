from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


# Enable imports like `from utils.preprocess import ...` when this script is run directly.
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from utils.preprocess import (  # noqa: E402
	TARGET_DISEASE,
	TARGET_REMEDIES,
	get_feature_columns,
	preprocess_training_data,
)


DEFAULT_DATASET = PROJECT_ROOT / "data" / "dataset.csv"
DEFAULT_MODEL_PATH = CURRENT_DIR / "model.pkl"
DEFAULT_ENCODER_PATH = CURRENT_DIR / "encoder.pkl"
DEFAULT_METADATA_PATH = CURRENT_DIR / "metadata.json"


def build_model() -> RandomForestClassifier:
	"""Create the classifier used for disease prediction."""
	return RandomForestClassifier(
		n_estimators=400,
		max_depth=18,
		min_samples_split=4,
		min_samples_leaf=2,
		random_state=42,
		n_jobs=-1,
		class_weight="balanced_subsample",
	)


def make_remedy_map(diseases, remedies) -> Dict[str, str]:
	"""
	Build disease->remedy mapping from dataset targets.

	If duplicates exist, first occurrence is kept (dataset is expected to be consistent).
	"""
	remedy_map: Dict[str, str] = {}
	for disease, remedy in zip(diseases, remedies):
		disease = str(disease).strip()
		remedy = str(remedy).strip()
		if disease and disease not in remedy_map:
			remedy_map[disease] = remedy
	return remedy_map


def train(
	dataset_path: Path,
	model_path: Path,
	encoder_path: Path,
	metadata_path: Path,
	test_size: float = 0.2,
) -> None:
	preprocessed = preprocess_training_data(str(dataset_path))

	X = preprocessed.X
	y_disease = preprocessed.y_disease
	y_remedies = preprocessed.y_remedies

	label_encoder = LabelEncoder()
	y_encoded = label_encoder.fit_transform(y_disease)

	X_train, X_test, y_train, y_test = train_test_split(
		X,
		y_encoded,
		test_size=test_size,
		random_state=42,
		stratify=y_encoded,
	)

	model = build_model()
	model.fit(X_train, y_train)

	y_pred = model.predict(X_test)
	accuracy = accuracy_score(y_test, y_pred)
	report = classification_report(
		y_test,
		y_pred,
		target_names=label_encoder.classes_,
		digits=4,
		zero_division=0,
	)

	remedy_map = make_remedy_map(y_disease, y_remedies)

	model_path.parent.mkdir(parents=True, exist_ok=True)
	joblib.dump(model, model_path)
	joblib.dump(label_encoder, encoder_path)

	metadata = {
		"feature_columns": list(get_feature_columns()),
		"target_disease": TARGET_DISEASE,
		"target_remedies": TARGET_REMEDIES,
		"classes": label_encoder.classes_.tolist(),
		"remedy_map": remedy_map,
		"test_size": test_size,
		"accuracy": round(float(accuracy), 6),
		"dataset_path": str(dataset_path),
	}
	metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

	print("Training complete")
	print(f"Dataset: {dataset_path}")
	print(f"Samples: {len(X)}")
	print(f"Features: {len(X.columns)}")
	print(f"Accuracy: {accuracy:.4f}")
	print(f"Saved model: {model_path}")
	print(f"Saved encoder: {encoder_path}")
	print(f"Saved metadata: {metadata_path}")
	print("\nClassification report:")
	print(report)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Train disease prediction model from symptom dataset."
	)
	parser.add_argument(
		"--dataset",
		type=Path,
		default=DEFAULT_DATASET,
		help=f"Path to dataset CSV (default: {DEFAULT_DATASET})",
	)
	parser.add_argument(
		"--model-out",
		type=Path,
		default=DEFAULT_MODEL_PATH,
		help=f"Path to save trained model (default: {DEFAULT_MODEL_PATH})",
	)
	parser.add_argument(
		"--encoder-out",
		type=Path,
		default=DEFAULT_ENCODER_PATH,
		help=f"Path to save label encoder (default: {DEFAULT_ENCODER_PATH})",
	)
	parser.add_argument(
		"--metadata-out",
		type=Path,
		default=DEFAULT_METADATA_PATH,
		help=f"Path to save metadata JSON (default: {DEFAULT_METADATA_PATH})",
	)
	parser.add_argument(
		"--test-size",
		type=float,
		default=0.2,
		help="Test split ratio between 0 and 1 (default: 0.2)",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()

	if not 0 < args.test_size < 1:
		raise ValueError("--test-size must be between 0 and 1.")

	if not args.dataset.exists():
		raise FileNotFoundError(f"Dataset not found: {args.dataset}")

	train(
		dataset_path=args.dataset,
		model_path=args.model_out,
		encoder_path=args.encoder_out,
		metadata_path=args.metadata_out,
		test_size=args.test_size,
	)


if __name__ == "__main__":
	main()

