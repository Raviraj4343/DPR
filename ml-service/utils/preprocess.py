from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import pandas as pd


# Symptom fields expected from dataset and UI input.
SYMPTOM_COLUMNS = [
	"cough",
	"fever",
	"headache",
	"vomiting",
	"diarrhea",
	"fatigue",
	"body_pain",
	"sore_throat",
	"runny_nose",
	"breathlessness",
	"chest_pain",
	"abdominal_pain",
	"rash",
	"joint_pain",
	"loss_of_taste_smell",
]

TARGET_DISEASE = "disease"
TARGET_REMEDIES = "remedies"

REQUIRED_COLUMNS = SYMPTOM_COLUMNS + [TARGET_DISEASE, TARGET_REMEDIES]


@dataclass(frozen=True)
class PreprocessedData:
	"""Container returned by training-data preprocessing."""

	X: pd.DataFrame
	y_disease: pd.Series
	y_remedies: pd.Series


def _to_binary(value: object) -> int:
	"""Convert common truthy/falsy representations to 0 or 1."""
	if pd.isna(value):
		return 0

	if isinstance(value, bool):
		return int(value)

	if isinstance(value, (int, float)):
		return 1 if float(value) >= 1 else 0

	text = str(value).strip().lower()
	if text in {"1", "yes", "y", "true", "t", "on", "present"}:
		return 1
	if text in {"0", "no", "n", "false", "f", "off", "absent"}:
		return 0

	raise ValueError(f"Cannot convert symptom value '{value}' to binary.")


def _validate_columns(df: pd.DataFrame) -> None:
	missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
	if missing:
		raise ValueError(
			"Dataset is missing required columns: " + ", ".join(missing)
		)


def load_dataset(csv_path: str) -> pd.DataFrame:
	"""
	Load the raw dataset from CSV.

	Parameters
	----------
	csv_path:
		Path to dataset CSV.
	"""
	df = pd.read_csv(csv_path)
	if df.empty:
		raise ValueError("Dataset is empty. Add rows before training.")
	_validate_columns(df)
	return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
	"""
	Clean and normalize a raw disease dataset.

	Steps:
	1. Keep only required columns.
	2. Normalize symptom columns to 0/1.
	3. Normalize text targets.
	4. Drop invalid rows and duplicates.
	"""
	_validate_columns(df)

	clean = df[REQUIRED_COLUMNS].copy()

	for col in SYMPTOM_COLUMNS:
		clean[col] = clean[col].map(_to_binary).astype("int8")

	clean[TARGET_DISEASE] = (
		clean[TARGET_DISEASE]
		.astype(str)
		.str.strip()
		.replace({"": pd.NA, "nan": pd.NA, "none": pd.NA})
	)
	clean[TARGET_REMEDIES] = (
		clean[TARGET_REMEDIES]
		.astype(str)
		.str.strip()
		.replace({"": pd.NA, "nan": pd.NA, "none": pd.NA})
	)

	clean = clean.dropna(subset=[TARGET_DISEASE, TARGET_REMEDIES])
	clean = clean.drop_duplicates().reset_index(drop=True)

	if clean.empty:
		raise ValueError("All rows were dropped during cleaning.")

	return clean


def preprocess_training_data(csv_path: str) -> PreprocessedData:
	"""
	Load, clean, and split dataset into model inputs and targets.

	Returns
	-------
	PreprocessedData
		X: symptom features
		y_disease: disease label
		y_remedies: remedy text
	"""
	raw = load_dataset(csv_path)
	clean = clean_dataset(raw)

	X = clean[SYMPTOM_COLUMNS].copy()
	y_disease = clean[TARGET_DISEASE].copy()
	y_remedies = clean[TARGET_REMEDIES].copy()

	return PreprocessedData(X=X, y_disease=y_disease, y_remedies=y_remedies)


def preprocess_user_input(user_input: Dict[str, object]) -> pd.DataFrame:
	"""
	Convert UI symptom payload into a single-row model input DataFrame.

	Unknown keys are ignored, missing symptoms default to 0.

	Example accepted values: 0/1, true/false, yes/no, y/n, on/off.
	"""
	row = {}
	for symptom in SYMPTOM_COLUMNS:
		row[symptom] = _to_binary(user_input.get(symptom, 0))

	return pd.DataFrame([row], columns=SYMPTOM_COLUMNS).astype("int8")


def get_feature_columns() -> Iterable[str]:
	"""Return feature column names in model input order."""
	return tuple(SYMPTOM_COLUMNS)

