from __future__ import annotations

from typing import Dict, Optional, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from .loaders import DataLoaderError


class DataSplitError(DataLoaderError):
	"""Raised when dataset splitting fails."""


def _validate_dataframe(df: pd.DataFrame, require_label: bool = True) -> None:
	if df.empty:
		raise DataSplitError("Cannot split an empty dataset.")

	if "text" not in df.columns:
		raise DataSplitError("Expected dataframe with 'text' column.")

	if require_label and "label" not in df.columns:
		raise DataSplitError("Expected dataframe with 'label' column for stratified split.")


def _validate_split_sizes(test_size: float, validation_size: Optional[float] = None) -> None:
	if not 0 < test_size < 1:
		raise DataSplitError("test_size must be between 0 and 1.")

	if validation_size is not None:
		if not 0 < validation_size < 1:
			raise DataSplitError("validation_size must be between 0 and 1.")
		if test_size + validation_size >= 1:
			raise DataSplitError("test_size + validation_size must be less than 1.")


def split_train_test(
	df: pd.DataFrame,
	*,
	test_size: float = 0.2,
	random_state: int = 42,
	stratify_by_label: bool = True,
	shuffle: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
	"""Split standardized dataframe into train and test sets."""
	_validate_dataframe(df, require_label=stratify_by_label)
	_validate_split_sizes(test_size)

	stratify = df["label"] if stratify_by_label else None

	try:
		train_df, test_df = train_test_split(
			df,
			test_size=test_size,
			random_state=random_state,
			stratify=stratify,
			shuffle=shuffle,
		)
	except ValueError as exc:
		raise DataSplitError(f"Failed to split dataset: {exc}") from exc

	return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def split_train_validation_test(
	df: pd.DataFrame,
	*,
	test_size: float = 0.2,
	validation_size: float = 0.1,
	random_state: int = 42,
	stratify_by_label: bool = True,
	shuffle: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
	"""Split standardized dataframe into train, validation, and test sets."""
	_validate_dataframe(df, require_label=stratify_by_label)
	_validate_split_sizes(test_size, validation_size)

	stratify_full = df["label"] if stratify_by_label else None

	try:
		train_val_df, test_df = train_test_split(
			df,
			test_size=test_size,
			random_state=random_state,
			stratify=stratify_full,
			shuffle=shuffle,
		)

		adjusted_validation_size = validation_size / (1 - test_size)
		stratify_train_val = train_val_df["label"] if stratify_by_label else None

		train_df, validation_df = train_test_split(
			train_val_df,
			test_size=adjusted_validation_size,
			random_state=random_state,
			stratify=stratify_train_val,
			shuffle=shuffle,
		)
	except ValueError as exc:
		raise DataSplitError(f"Failed to split dataset: {exc}") from exc

	return (
		train_df.reset_index(drop=True),
		validation_df.reset_index(drop=True),
		test_df.reset_index(drop=True),
	)


def get_label_distribution(df: pd.DataFrame) -> Dict[str, float]:
	"""Return normalized label distribution as a mapping of label -> percentage."""
	if "label" not in df.columns:
		raise DataSplitError("Expected dataframe with 'label' column.")

	if df.empty:
		return {}

	distribution = df["label"].value_counts(normalize=True).sort_index()
	return {str(label): float(value) for label, value in distribution.items()}
