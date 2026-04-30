from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Iterable, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

from app.nlp.features.tfidf import (
	TfidfFeatureError,
	tfidf_fit_transform_dataframe,
	tfidf_transform_dataframe,
)


class BaselineTrainingError(ValueError):
	pass


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = PROJECT_ROOT / "app" / "nlp" / "data" / "processed"
PREPROCESSED_PATH = PROCESSED_DIR / "dataset_preprocessed.csv"
TRAIN_PATH = PROCESSED_DIR / "train.csv"
VALIDATION_PATH = PROCESSED_DIR / "validation.csv"
TEST_PATH = PROCESSED_DIR / "test.csv"
OUTPUT_DIR = PROCESSED_DIR / "models" / "baseline"

TEXT_COLUMN = "text"
LABEL_COLUMN = "label"
LABEL_ID_COLUMN = "label_id"
STEMS_COLUMN = "stems"
PARSED_STEMS_COLUMN = "stems_parsed"


def _is_missing(value: object) -> bool:
	if value is None:
		return True
	if isinstance(value, float):
		return np.isnan(value)
	return False


def _parse_tokens(value: object) -> List[str]:
	if _is_missing(value):
		return []
	if isinstance(value, list):
		return [str(item) for item in value]
	if isinstance(value, tuple):
		return [str(item) for item in value]
	if isinstance(value, set):
		return [str(item) for item in value]
	if isinstance(value, str):
		text = value.strip()
		if text.startswith("[") and text.endswith("]"):
			try:
				parsed = ast.literal_eval(text)
			except (ValueError, SyntaxError):
				parsed = None
			if isinstance(parsed, list):
				return [str(item) for item in parsed]
		return text.split()
	if isinstance(value, Iterable):
		return [str(item) for item in value]
	return str(value).split()


def _load_csv(path: Path) -> pd.DataFrame:
	if not path.exists():
		raise BaselineTrainingError(f"Dataset file not found: {path}")
	return pd.read_csv(path, encoding="utf-8")


def _ensure_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
	missing = [column for column in required if column not in df.columns]
	if missing:
		raise BaselineTrainingError(
			f"Missing required columns: {missing}. Available columns: {list(df.columns)}"
		)


def _attach_parsed_stems(df: pd.DataFrame) -> pd.DataFrame:
	result = df.copy()
	result[PARSED_STEMS_COLUMN] = result[STEMS_COLUMN].apply(_parse_tokens)
	return result


def _merge_split(split_df: pd.DataFrame, pre_df: pd.DataFrame) -> pd.DataFrame:
	join_columns = [TEXT_COLUMN, LABEL_COLUMN, LABEL_ID_COLUMN]
	join_columns = [col for col in join_columns if col in split_df.columns and col in pre_df.columns]
	if not join_columns:
		raise BaselineTrainingError("No shared columns to merge split with preprocessed data.")

	merged = split_df.merge(pre_df, on=join_columns, how="left")
	if STEMS_COLUMN not in merged.columns:
		raise BaselineTrainingError("Column 'stems' not found after merging split data.")

	missing = int(merged[STEMS_COLUMN].isna().sum())
	if missing:
		raise BaselineTrainingError(
			f"{missing} rows could not be matched with preprocessed stems."
		)

	if len(merged) != len(split_df):
		raise BaselineTrainingError(
			"Split merge changed row count. Check for duplicates in split or preprocessed data."
		)

	return merged


def _load_splits(pre_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
	if TRAIN_PATH.exists() and VALIDATION_PATH.exists() and TEST_PATH.exists():
		train_df = _merge_split(_load_csv(TRAIN_PATH), pre_df)
		val_df = _merge_split(_load_csv(VALIDATION_PATH), pre_df)
		test_df = _merge_split(_load_csv(TEST_PATH), pre_df)
		return train_df, val_df, test_df

	stratify_col = LABEL_ID_COLUMN if LABEL_ID_COLUMN in pre_df.columns else LABEL_COLUMN
	stratify_values = pre_df[stratify_col] if stratify_col in pre_df.columns else None
	train_df, temp_df = train_test_split(
		pre_df,
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
	return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)


def _resolve_labels(df: pd.DataFrame) -> pd.Series:
	if LABEL_ID_COLUMN in df.columns:
		return df[LABEL_ID_COLUMN].astype(int)
	if LABEL_COLUMN in df.columns:
		return df[LABEL_COLUMN].astype(str)
	raise BaselineTrainingError("Label columns not found in dataset.")


def _build_label_map(df: pd.DataFrame) -> dict[int, str]:
	if LABEL_ID_COLUMN not in df.columns or LABEL_COLUMN not in df.columns:
		return {}

	mapping: dict[int, str] = {}
	for label_id, label in df[[LABEL_ID_COLUMN, LABEL_COLUMN]].dropna().drop_duplicates().values:
		mapping[int(label_id)] = str(label)
	return mapping


def _evaluate(
	model: LogisticRegression,
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


def main() -> int:
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

	try:
		pre_df = _load_csv(PREPROCESSED_PATH)
		if pre_df.empty:
			raise BaselineTrainingError("Preprocessed dataset is empty.")
		_ensure_columns(pre_df, [TEXT_COLUMN, LABEL_COLUMN, LABEL_ID_COLUMN, STEMS_COLUMN])

		train_df, val_df, test_df = _load_splits(pre_df)
		train_df = _attach_parsed_stems(train_df)
		val_df = _attach_parsed_stems(val_df)
		test_df = _attach_parsed_stems(test_df)

		vectorizer, X_train = tfidf_fit_transform_dataframe(
			train_df,
			text_column=PARSED_STEMS_COLUMN,
			pretokenized=True,
			max_features=5000,
			ngram_range=(1, 2),
			min_df=1,
			max_df=1.0,
			use_idf=True,
			smooth_idf=True,
			sublinear_tf=False,
			norm="l2",
			stop_words=None,
			token_pattern=None,
		)

		X_val = tfidf_transform_dataframe(
			vectorizer,
			val_df,
			text_column=PARSED_STEMS_COLUMN,
			pretokenized=True,
		)
		X_test = tfidf_transform_dataframe(
			vectorizer,
			test_df,
			text_column=PARSED_STEMS_COLUMN,
			pretokenized=True,
		)

		y_train = _resolve_labels(train_df)
		y_val = _resolve_labels(val_df)
		y_test = _resolve_labels(test_df)

		model = LogisticRegression(
			max_iter=1000,
			class_weight="balanced",
			random_state=42,
		)
		model.fit(X_train, y_train)

		label_map = _build_label_map(pre_df)
		label_ids = sorted(label_map.keys()) if label_map else sorted(np.unique(y_train).tolist())
		label_names = [label_map[label_id] for label_id in label_ids] if label_map else None

		metrics = {
			"train": _evaluate(model, X_train, y_train, label_ids=label_ids, label_names=label_names),
			"validation": _evaluate(model, X_val, y_val, label_ids=label_ids, label_names=label_names),
			"test": _evaluate(model, X_test, y_test, label_ids=label_ids, label_names=label_names),
			"label_map": label_map,
			"feature": "tfidf",
			"train_rows": int(len(train_df)),
			"validation_rows": int(len(val_df)),
			"test_rows": int(len(test_df)),
		}

		joblib.dump(model, OUTPUT_DIR / "baseline_model.joblib")
		joblib.dump(vectorizer, OUTPUT_DIR / "tfidf_vectorizer.joblib")
		_save_json(OUTPUT_DIR / "label_map.json", label_map)
		_save_json(OUTPUT_DIR / "metrics.json", metrics)

	except (BaselineTrainingError, FileNotFoundError, TfidfFeatureError, ValueError) as exc:
		print(f"[train_baseline] Error: {exc}")
		return 1

	print(f"[train_baseline] Completed. Output saved to: {OUTPUT_DIR}")
	print(f"[train_baseline] Train rows: {len(train_df)}")
	print(f"[train_baseline] Validation rows: {len(val_df)}")
	print(f"[train_baseline] Test rows: {len(test_df)}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
