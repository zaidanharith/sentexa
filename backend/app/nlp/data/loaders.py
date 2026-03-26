from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import pandas as pd


class DataLoaderError(ValueError):
	"""Raised when dataset loading or validation fails."""


SUPPORTED_FILE_TYPES = {".csv", ".tsv", ".xls", ".xlsx"}
LABEL_COLUMN_ALIASES = ("label", "sentiment", "sentimen", "target", "class")


def _find_matching_column(df: pd.DataFrame, candidate: str) -> Optional[str]:
	normalized = candidate.strip().lower()
	lookup = {str(col).strip().lower(): str(col) for col in df.columns}
	return lookup.get(normalized)


def _read_dataframe(
	file_path: str | Path,
	*,
	sheet_name: int | str = 0,
	encoding: str = "utf-8",
	**kwargs: Any,
) -> pd.DataFrame:
	path = Path(file_path)

	if not path.exists():
		raise DataLoaderError(f"Dataset file not found: {path}")

	suffix = path.suffix.lower()
	if suffix not in SUPPORTED_FILE_TYPES:
		allowed = ", ".join(sorted(SUPPORTED_FILE_TYPES))
		raise DataLoaderError(
			f"Unsupported file type '{suffix}'. Supported types: {allowed}"
		)

	try:
		if suffix in {".csv", ".tsv"}:
			read_kwargs = dict(kwargs)
			if suffix == ".tsv" and "sep" not in read_kwargs:
				read_kwargs["sep"] = "\t"
			return pd.read_csv(path, encoding=encoding, **read_kwargs)
		return pd.read_excel(path, sheet_name=sheet_name, **kwargs)
	except ImportError as exc:
		raise DataLoaderError(
			f"Failed to read dataset file '{path}': {exc}"
		) from exc
	except Exception as exc:
		raise DataLoaderError(f"Failed to read dataset file '{path}': {exc}") from exc


def _standardize_text_series(series: pd.Series) -> pd.Series:
	return series.astype(str).str.strip()


def load_labeled_dataset(
	file_path: str | Path,
	*,
	text_column: str = "text",
	label_column: str = "label",
	drop_na: bool = True,
	drop_duplicates: bool = True,
	lowercase_text: bool = False,
	sheet_name: int | str = 0,
	encoding: str = "utf-8",
	**kwargs: Any,
) -> pd.DataFrame:
	"""Load a labeled dataset and return standardized columns: text, label."""
	df = _read_dataframe(
		file_path,
		sheet_name=sheet_name,
		encoding=encoding,
		**kwargs,
	)

	text_col = _find_matching_column(df, text_column)
	label_col = _find_matching_column(df, label_column)
	if label_col is None:
		for candidate in LABEL_COLUMN_ALIASES:
			label_col = _find_matching_column(df, candidate)
			if label_col is not None:
				break

	if text_col is None:
		raise DataLoaderError(
			f"Text column '{text_column}' not found. Available columns: {list(df.columns)}"
		)
	if label_col is None:
		raise DataLoaderError(
			f"Label column '{label_column}' not found. Available columns: {list(df.columns)}"
		)

	result = df[[text_col, label_col]].copy()
	result = result.rename(columns={text_col: "text", label_col: "label"})

	if drop_na:
		result = result.dropna(subset=["text", "label"])

	result["text"] = _standardize_text_series(result["text"])
	result["label"] = _standardize_text_series(result["label"])

	if lowercase_text:
		result["text"] = result["text"].str.lower()

	if drop_duplicates:
		result = result.drop_duplicates(subset=["text", "label"])

	result = result.reset_index(drop=True)

	if result.empty:
		raise DataLoaderError("Dataset is empty after preprocessing and validation.")

	return result


def load_unlabeled_dataset(
	file_path: str | Path,
	*,
	text_column: str = "text",
	drop_na: bool = True,
	drop_duplicates: bool = True,
	lowercase_text: bool = False,
	sheet_name: int | str = 0,
	encoding: str = "utf-8",
	**kwargs: Any,
) -> pd.DataFrame:
	"""Load an unlabeled dataset and return standardized column: text."""
	df = _read_dataframe(
		file_path,
		sheet_name=sheet_name,
		encoding=encoding,
		**kwargs,
	)

	text_col = _find_matching_column(df, text_column)
	if text_col is None:
		raise DataLoaderError(
			f"Text column '{text_column}' not found. Available columns: {list(df.columns)}"
		)

	result = df[[text_col]].copy().rename(columns={text_col: "text"})

	if drop_na:
		result = result.dropna(subset=["text"])

	result["text"] = _standardize_text_series(result["text"])

	if lowercase_text:
		result["text"] = result["text"].str.lower()

	if drop_duplicates:
		result = result.drop_duplicates(subset=["text"])

	result = result.reset_index(drop=True)

	if result.empty:
		raise DataLoaderError("Dataset is empty after preprocessing and validation.")

	return result


def to_xy(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
	"""Split standardized dataframe into X (text) and y (label)."""
	required = {"text", "label"}
	missing = required - set(df.columns)
	if missing:
		raise DataLoaderError(
			f"Missing required column(s): {sorted(missing)}. "
			"Expected dataframe with columns: ['text', 'label']."
		)
	return df["text"], df["label"]


def to_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
	"""Convert standardized dataframe to list-of-dict records."""
	if "text" not in df.columns:
		raise DataLoaderError("Expected dataframe with at least 'text' column.")
	return cast(List[Dict[str, Any]], df.to_dict(orient="records"))
