from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class EvaluationReport:
	model_name: str
	metrics: Dict[str, Any]
	created_at: str
	feature_type: Optional[str] = None
	dataset_path: Optional[str] = None
	metadata: Optional[Dict[str, Any]] = None

	def to_dict(self) -> Dict[str, Any]:
		return asdict(self)


class ReportError(ValueError):
	pass


def create_report(
	model_name: str,
	metrics: Dict[str, Any],
	*,
	feature_type: Optional[str] = None,
	dataset_path: Optional[str] = None,
	metadata: Optional[Dict[str, Any]] = None,
) -> EvaluationReport:
	if not model_name:
		raise ReportError("model_name is required.")
	if not isinstance(metrics, dict) or not metrics:
		raise ReportError("metrics must be a non-empty dict.")

	created_at = datetime.now(timezone.utc).isoformat()
	return EvaluationReport(
		model_name=model_name,
		metrics=metrics,
		created_at=created_at,
		feature_type=feature_type,
		dataset_path=dataset_path,
		metadata=metadata,
	)


def save_report(report: EvaluationReport, output_path: str | Path) -> Path:
	path = Path(output_path)
	path.parent.mkdir(parents=True, exist_ok=True)

	with path.open("w", encoding="utf-8") as file_obj:
		json.dump(report.to_dict(), file_obj, ensure_ascii=True, indent=2)

	return path


def load_report(report_path: str | Path) -> EvaluationReport:
	path = Path(report_path)
	if not path.exists():
		raise ReportError(f"Report file not found: {path}")

	with path.open("r", encoding="utf-8") as file_obj:
		payload = json.load(file_obj)

	if "model_name" not in payload or "metrics" not in payload or "created_at" not in payload:
		raise ReportError("Invalid report format.")

	return EvaluationReport(
		model_name=str(payload["model_name"]),
		metrics=dict(payload["metrics"]),
		created_at=str(payload["created_at"]),
		feature_type=payload.get("feature_type"),
		dataset_path=payload.get("dataset_path"),
		metadata=payload.get("metadata"),
	)
