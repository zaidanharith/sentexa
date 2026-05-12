from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC


class ClassifierTrainingError(ValueError):
	pass


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FEATURES_DIR = PROCESSED_DIR / "features"
PREPROCESSED_PATH = PROCESSED_DIR / "dataset_preprocessed.csv"
TRAIN_PATH = PROCESSED_DIR / "train.csv"
VALIDATION_PATH = PROCESSED_DIR / "validation.csv"
TEST_PATH = PROCESSED_DIR / "test.csv"
OUTPUT_DIR = PROCESSED_DIR / "models" / "classifier"

TEXT_COLUMN = "text"
LABEL_COLUMN = "label"
LABEL_ID_COLUMN = "label_id"


def _load_csv(path: Path) -> pd.DataFrame:
	if not path.exists():
		raise ClassifierTrainingError(f"Dataset file not found: {path}")
	return pd.read_csv(path, encoding="utf-8")


def _ensure_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
	missing = [column for column in required if column not in df.columns]
	if missing:
		raise ClassifierTrainingError(f"Missing required columns: {missing}. Available columns: {list(df.columns)}")


def _resolve_key_columns(df: pd.DataFrame) -> List[str]:
	columns = []
	if TEXT_COLUMN in df.columns:
		columns.append(TEXT_COLUMN)
	if LABEL_ID_COLUMN in df.columns:
		columns.append(LABEL_ID_COLUMN)
	if LABEL_COLUMN in df.columns:
		columns.append(LABEL_COLUMN)
	if len(columns) < 2:
		raise ClassifierTrainingError("Insufficient columns to match splits with preprocessed data.")
	return columns


def _normalize_key_columns(df: pd.DataFrame, key_columns: Sequence[str]) -> pd.DataFrame:
	result = df.copy()
	if TEXT_COLUMN in key_columns:
		result[TEXT_COLUMN] = result[TEXT_COLUMN].astype(str)
	if LABEL_COLUMN in key_columns:
		result[LABEL_COLUMN] = result[LABEL_COLUMN].astype(str)
	if LABEL_ID_COLUMN in key_columns:
		result[LABEL_ID_COLUMN] = result[LABEL_ID_COLUMN].astype(int)
	return result


def _attach_dup_index(df: pd.DataFrame, key_columns: Sequence[str]) -> pd.DataFrame:
	result = df.copy()
	result["__dup_index"] = result.groupby(list(key_columns)).cumcount()
	return result


def _resolve_row_ids(split_df: pd.DataFrame, base_df: pd.DataFrame) -> List[int]:
	key_columns = _resolve_key_columns(base_df)
	base_keyed = _attach_dup_index(_normalize_key_columns(base_df, key_columns), key_columns)
	split_keyed = _attach_dup_index(_normalize_key_columns(split_df, key_columns), key_columns)

	merge_columns = list(key_columns) + ["__dup_index"]
	merged = split_keyed.merge(
		base_keyed[merge_columns + ["__row_id"]],
		on=merge_columns,
		how="left",
	)

	if merged["__row_id"].isna().any():
		missing = int(merged["__row_id"].isna().sum())
		raise ClassifierTrainingError(f"{missing} rows could not be matched with preprocessed dataset.")

	return merged["__row_id"].astype(int).tolist()


def _load_splits(base_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List[int], List[int], List[int]]:
	if TRAIN_PATH.exists() and VALIDATION_PATH.exists() and TEST_PATH.exists():
		train_df = _load_csv(TRAIN_PATH)
		val_df = _load_csv(VALIDATION_PATH)
		test_df = _load_csv(TEST_PATH)
		train_ids = _resolve_row_ids(train_df, base_df)
		val_ids = _resolve_row_ids(val_df, base_df)
		test_ids = _resolve_row_ids(test_df, base_df)
		return train_df, val_df, test_df, train_ids, val_ids, test_ids

	stratify_col = LABEL_ID_COLUMN if LABEL_ID_COLUMN in base_df.columns else LABEL_COLUMN
	stratify_values = base_df[stratify_col] if stratify_col in base_df.columns else None
	train_df, temp_df = train_test_split(
		base_df,
		test_size=0.3,
		random_state=42,
		stratify=stratify_values,
	)
	stratify_temp = temp_df[stratify_col] if stratify_col in temp_df.columns else None
	val_df, test_df = train_test_split(
		temp_df,
		test_size=0.5,
		random_state=42,
		stratify=stratify_temp,
	)
	return (
		train_df.reset_index(drop=True),
		val_df.reset_index(drop=True),
		test_df.reset_index(drop=True),
		train_df.index.astype(int).tolist(),
		val_df.index.astype(int).tolist(),
		test_df.index.astype(int).tolist(),
	)


def _resolve_labels(df: pd.DataFrame) -> pd.Series:
	if LABEL_ID_COLUMN in df.columns:
		return df[LABEL_ID_COLUMN].astype(int)
	if LABEL_COLUMN in df.columns:
		return df[LABEL_COLUMN].astype(str)
	raise ClassifierTrainingError("Label columns not found in dataset.")


def _build_label_map(df: pd.DataFrame) -> dict[int, str]:
	if LABEL_ID_COLUMN not in df.columns or LABEL_COLUMN not in df.columns:
		return {}

	mapping: dict[int, str] = {}
	for label_id, label in df[[LABEL_ID_COLUMN, LABEL_COLUMN]].dropna().drop_duplicates().values:
		mapping[int(label_id)] = str(label)
	return mapping


def _evaluate(
	model: LinearSVC,
	features,
	labels: pd.Series,
	*,
	label_ids: Optional[List[int]] = None,
	label_names: Optional[List[str]] = None,
) -> dict[str, object]:
	preds = model.predict(features)
	metrics = {
		"accuracy": float(accuracy_score(labels, preds)),
		"f1_macro": float(f1_score(labels, preds, average="macro")),
		"f1_weighted": float(f1_score(labels, preds, average="weighted")),
	}
	report = classification_report(
		labels,
		preds,
		labels=label_ids,
		target_names=label_names,
		output_dict=True,
		zero_division=0,
	)
	metrics["report"] = report
	metrics["confusion_matrix"] = confusion_matrix(labels, preds, labels=label_ids).tolist()
	return metrics


def _save_json(path: Path, payload: object) -> None:
	with path.open("w", encoding="utf-8") as file_obj:
		json.dump(payload, file_obj, ensure_ascii=True, indent=2)


def _load_features(path: Path, *, sparse_matrix: bool) -> np.ndarray | sparse.spmatrix:
	if not path.exists():
		raise ClassifierTrainingError(f"Feature file not found: {path}")
	if sparse_matrix:
		return sparse.load_npz(path)
	return np.load(path)


def _slice_features(features, row_ids: List[int]):
	return features[row_ids]


def main() -> int:
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

	try:
		base_df = _load_csv(PREPROCESSED_PATH)
		if base_df.empty:
			raise ClassifierTrainingError("Preprocessed dataset is empty.")
		_ensure_columns(base_df, [TEXT_COLUMN, LABEL_COLUMN, LABEL_ID_COLUMN])
		base_df = base_df.copy()
		base_df["__row_id"] = np.arange(len(base_df))

		train_df, val_df, test_df, train_ids, val_ids, test_ids = _load_splits(base_df)
		y_train = _resolve_labels(train_df)
		y_val = _resolve_labels(val_df)
		y_test = _resolve_labels(test_df)

		label_map = _build_label_map(base_df)
		label_ids = sorted(label_map.keys()) if label_map else sorted(np.unique(y_train).tolist())
		label_names = [label_map[label_id] for label_id in label_ids] if label_map else None

		tfidf_path = FEATURES_DIR / "tfidf_features.npz"
		if not tfidf_path.exists():
			raise ClassifierTrainingError(
				"TF-IDF features not found. Run feature_extraction before training classifier."
			)

		features = _load_features(tfidf_path, sparse_matrix=True)
		if features.shape[0] != len(base_df):
			raise ClassifierTrainingError(
				f"Feature rows ({features.shape[0]}) do not match dataset rows ({len(base_df)})."
			)

		X_train = _slice_features(features, train_ids)
		X_val = _slice_features(features, val_ids)
		X_test = _slice_features(features, test_ids)

		model = LinearSVC(
			class_weight="balanced",
			dual="auto",
			max_iter=5000,
			random_state=42,
		)
		model.fit(X_train, y_train)

		metrics = {
			"train": _evaluate(model, X_train, y_train, label_ids=label_ids, label_names=label_names),
			"validation": _evaluate(model, X_val, y_val, label_ids=label_ids, label_names=label_names),
			"test": _evaluate(model, X_test, y_test, label_ids=label_ids, label_names=label_names),
		}
		best_feature = "tfidf"
		best_score = float(metrics["validation"]["f1_macro"])

		metadata = {
			"best_feature": best_feature,
			"label_map": label_map,
			"train_rows": int(len(train_df)),
			"validation_rows": int(len(val_df)),
			"test_rows": int(len(test_df)),
			"metrics": {"tfidf": metrics},
			"feature_paths": {
				"tfidf": str(tfidf_path),
			},
			"artifact_paths": {
				"tfidf_vectorizer": str(FEATURES_DIR / "tfidf_vectorizer.joblib"),
			},
		}

		joblib.dump(model, OUTPUT_DIR / "classifier_model.joblib")
		_save_json(OUTPUT_DIR / "classifier_metadata.json", metadata)

	except (ClassifierTrainingError, FileNotFoundError, ValueError) as exc:
		print(f"[train_classifier] Error: {exc}")
		return 1

	print(f"[train_classifier] Completed. Output saved to: {OUTPUT_DIR}")
	print(f"[train_classifier] Best feature: {best_feature}")
	print(f"[train_classifier] Validation F1: {best_score:.4f}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
