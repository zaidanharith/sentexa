from __future__ import annotations

from pathlib import Path
from typing import Callable

from app.nlp.training import train_baseline, train_classifier, tune


class TrainDataError(ValueError):
	pass


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = PROJECT_ROOT / "app" / "nlp" / "data" / "processed"
FEATURES_DIR = PROCESSED_DIR / "features"

RUN_BASELINE = True
RUN_CLASSIFIER = True
RUN_TUNING = False


def _has_feature_files() -> bool:
	if not FEATURES_DIR.exists():
		return False
	feature_files = [
		FEATURES_DIR / "tfidf_features.npz",
	]
	return any(path.exists() for path in feature_files)


def _run_step(name: str, func: Callable[[], int]) -> None:
	print(f"[train_data] Running {name}...")
	result = func()
	if result != 0:
		raise TrainDataError(f"{name} failed with exit code {result}.")


def main() -> int:
	try:
		if RUN_BASELINE:
			_run_step("baseline training", train_baseline.main)

		if RUN_CLASSIFIER:
			if not _has_feature_files():
				raise TrainDataError(
					"No feature files found. Run feature_extraction before classifier training."
				)
			_run_step("classifier training", train_classifier.main)

		if RUN_TUNING:
			if not _has_feature_files():
				raise TrainDataError(
					"No feature files found. Run feature_extraction before tuning."
				)
			_run_step("model tuning", tune.main)

		print("[train_data] Completed.")
		return 0

	except TrainDataError as exc:
		print(f"[train_data] Error: {exc}")
		return 1


if __name__ == "__main__":
	raise SystemExit(main())
