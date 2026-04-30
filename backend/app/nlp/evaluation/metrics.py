from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd
from sklearn.metrics import (
	accuracy_score,
	classification_report,
	confusion_matrix,
	f1_score,
	precision_score,
	recall_score,
)


class MetricsError(ValueError):
	pass


def _to_numpy(values: Iterable[object]) -> np.ndarray:
	if isinstance(values, pd.Series):
		return values.to_numpy()
	if isinstance(values, list):
		return np.asarray(values)
	if isinstance(values, tuple):
		return np.asarray(values)
	if isinstance(values, np.ndarray):
		return values
	return np.asarray(list(values))


def _resolve_label_ids(
	y_true: Sequence[object],
	y_pred: Sequence[object],
	label_ids: Optional[Sequence[object]],
) -> List[object]:
	if label_ids is not None:
		return list(label_ids)

	if len(y_true) == 0 and len(y_pred) == 0:
		return []

	values = list(y_true) + list(y_pred)
	if not values:
		return []
	unique = np.unique(np.asarray(values, dtype=object))
	return [value for value in unique.tolist()]


def evaluate_predictions(
	y_true: Iterable[object],
	y_pred: Iterable[object],
	*,
	label_ids: Optional[Sequence[object]] = None,
	label_names: Optional[Sequence[str]] = None,
	zero_division: int = 0,
) -> dict[str, object]:
	true_values = _to_numpy(y_true)
	pred_values = _to_numpy(y_pred)

	if true_values.size == 0:
		raise MetricsError("y_true is empty.")
	if pred_values.size == 0:
		raise MetricsError("y_pred is empty.")
	if true_values.shape[0] != pred_values.shape[0]:
		raise MetricsError("y_true and y_pred must have the same length.")

	labels = _resolve_label_ids(true_values.tolist(), pred_values.tolist(), label_ids)
	if label_names is not None and len(label_names) != len(labels):
		raise MetricsError("label_names length must match label_ids length.")

	metrics = {
		"accuracy": float(accuracy_score(true_values, pred_values)),
		"precision_macro": float(
			precision_score(true_values, pred_values, average="macro", zero_division=zero_division)
		),
		"recall_macro": float(
			recall_score(true_values, pred_values, average="macro", zero_division=zero_division)
		),
		"f1_macro": float(
			f1_score(true_values, pred_values, average="macro", zero_division=zero_division)
		),
		"f1_weighted": float(
			f1_score(true_values, pred_values, average="weighted", zero_division=zero_division)
		),
		"labels": labels,
	}

	metrics["confusion_matrix"] = confusion_matrix(
		true_values,
		pred_values,
		labels=labels,
	).tolist()
	metrics["report"] = classification_report(
		true_values,
		pred_values,
		labels=labels,
		target_names=list(label_names) if label_names is not None else None,
		output_dict=True,
		zero_division=zero_division,
	)
	return metrics


def evaluate_dataframe(
	df: pd.DataFrame,
	*,
	true_column: str = "label",
	pred_column: str = "prediction",
	label_ids: Optional[Sequence[object]] = None,
	label_names: Optional[Sequence[str]] = None,
	zero_division: int = 0,
) -> dict[str, object]:
	if true_column not in df.columns or pred_column not in df.columns:
		raise MetricsError(
			"Dataframe must contain both true and prediction columns. "
			f"Missing: {[col for col in [true_column, pred_column] if col not in df.columns]}"
		)

	return evaluate_predictions(
		df[true_column],
		df[pred_column],
		label_ids=label_ids,
		label_names=label_names,
		zero_division=zero_division,
	)
