from __future__ import annotations

import ast
import json
from collections.abc import Iterable as IterableABC
from pathlib import Path
from typing import Iterable, List, Tuple

import joblib
import numpy as np
import pandas as pd
from scipy import sparse

from app.nlp.features.tfidf import (
	TfidfFeatureError,
	get_feature_names as tfidf_feature_names,
	tfidf_fit_transform_dataframe,
)


class FeatureExtractionError(ValueError):
	pass


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = PROJECT_ROOT / "app" / "nlp" / "data" / "processed" / "dataset_preprocessed.csv"
OUTPUT_DIR = PROJECT_ROOT / "app" / "nlp" / "data" / "processed" / "features"

TEXT_COLUMN = "text_preprocessed"
TOKEN_COLUMN = "stems"
USE_PRETOKENIZED = True
LABEL_COLUMNS = ("label", "label_id")


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
	if isinstance(value, IterableABC):
		return [str(item) for item in value]
	return str(value).split()


def _resolve_feature_source(df: pd.DataFrame) -> Tuple[pd.DataFrame, str, bool]:
	if USE_PRETOKENIZED and TOKEN_COLUMN in df.columns:
		parsed_column = f"{TOKEN_COLUMN}_parsed"
		result = df.copy()
		result[parsed_column] = result[TOKEN_COLUMN].apply(_parse_tokens)
		return result, parsed_column, True

	if TEXT_COLUMN in df.columns:
		return df, TEXT_COLUMN, False

	available = ", ".join([str(col) for col in df.columns])
	raise FeatureExtractionError(
		"Feature source column not found. "
		f"Expected '{TOKEN_COLUMN}' or '{TEXT_COLUMN}'. Available columns: {available}"
	)


def _ensure_output_dir() -> None:
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _save_json(path: Path, payload: object) -> None:
	with path.open("w", encoding="utf-8") as file_obj:
		json.dump(payload, file_obj, ensure_ascii=True, indent=2)


def _save_sparse(path: Path, matrix: sparse.spmatrix) -> None:
	sparse.save_npz(path, matrix)


def _save_feature_index(df: pd.DataFrame) -> None:
	columns = [column for column in LABEL_COLUMNS if column in df.columns]
	if not columns:
		return
	(df[columns]).to_csv(OUTPUT_DIR / "feature_index.csv", index=False)


def main() -> int:
	_ensure_output_dir()

	try:
		df = pd.read_csv(INPUT_PATH, encoding="utf-8")
		if df.empty:
			raise FeatureExtractionError("Input dataset is empty.")

		feature_df, feature_column, pretokenized = _resolve_feature_source(df)

		tfidf_vectorizer, tfidf_features = tfidf_fit_transform_dataframe(
			feature_df,
			text_column=feature_column,
			pretokenized=pretokenized,
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
		joblib.dump(tfidf_vectorizer, OUTPUT_DIR / "tfidf_vectorizer.joblib")
		_save_sparse(OUTPUT_DIR / "tfidf_features.npz", tfidf_features)
		_save_json(
			OUTPUT_DIR / "tfidf_feature_names.json",
			tfidf_feature_names(tfidf_vectorizer),
		)

		_save_feature_index(feature_df)
		_save_json(
			OUTPUT_DIR / "feature_manifest.json",
			{
				"input_path": str(INPUT_PATH),
				"rows": int(len(feature_df)),
				"feature_column": feature_column,
				"pretokenized": pretokenized,
				"tfidf_shape": list(tfidf_features.shape),
			},
		)

	except (
		FileNotFoundError,
		FeatureExtractionError,
		TfidfFeatureError,
		ValueError,
	) as exc:
		print(f"[feature_extraction] Error: {exc}")
		return 1

	print(f"[feature_extraction] Completed. Output saved to: {OUTPUT_DIR}")
	print(f"[feature_extraction] Rows: {len(feature_df)}")
	print(f"[feature_extraction] TF-IDF shape: {tfidf_features.shape}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
