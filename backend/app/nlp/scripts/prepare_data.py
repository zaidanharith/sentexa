from __future__ import annotations

from pathlib import Path

from app.nlp.data.labeling import (
	DEFAULT_LABEL_TO_ID,
	DataLabelingError,
	auto_label_dataframe,
	build_label_mapping,
	normalize_label_column,
	validate_supported_labels,
)
from app.nlp.data.loaders import DataLoaderError, load_labeled_dataset, load_unlabeled_dataset
from app.nlp.data.split import (
	DataSplitError,
	split_train_test,
	split_train_validation_test,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = PROJECT_ROOT / "app" / "nlp" / "data" / "raw" / "dataset.tsv"
OUTPUT_DIR = PROJECT_ROOT / "app" / "nlp" / "data" / "processed"
TEXT_COLUMN = "text"
LABEL_COLUMN = "label"
SPLIT_MODE = "train-val-test"
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.1
RANDOM_STATE = 42
ENCODING = "utf-8"
SHEET_NAME: int | str = 0
LOWERCASE_TEXT = False
NO_STRATIFY = False
KEEP_DUPLICATES = False
AUTO_LABEL = False
ALLOW_CUSTOM_LABELS = False


def main() -> int:
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

	try:
		if AUTO_LABEL:
			dataset = load_unlabeled_dataset(
				INPUT_PATH,
				text_column=TEXT_COLUMN,
				drop_duplicates=not KEEP_DUPLICATES,
				lowercase_text=LOWERCASE_TEXT,
				encoding=ENCODING,
				sheet_name=SHEET_NAME,
			)
			dataset = auto_label_dataframe(dataset)
		else:
			dataset = load_labeled_dataset(
				INPUT_PATH,
				text_column=TEXT_COLUMN,
				label_column=LABEL_COLUMN,
				drop_duplicates=not KEEP_DUPLICATES,
				lowercase_text=LOWERCASE_TEXT,
				encoding=ENCODING,
				sheet_name=SHEET_NAME,
			)
			dataset = normalize_label_column(dataset)

		if ALLOW_CUSTOM_LABELS:
			label_to_id = build_label_mapping(
				dataset["label"],
				preferred_order=["negative", "neutral", "positive"],
			).label_to_id
		else:
			is_supported, unknown = validate_supported_labels(dataset["label"])
			if not is_supported:
				raise DataLabelingError(
					"Unsupported labels found: "
					f"{unknown}. Use --allow-custom-labels to keep non-standard classes."
				)
			label_to_id = dict(DEFAULT_LABEL_TO_ID)

		dataset["label_id"] = dataset["label"].map(label_to_id)

		stratify = not NO_STRATIFY
		if SPLIT_MODE == "train-test":
			train_df, test_df = split_train_test(
				dataset,
				test_size=TEST_SIZE,
				random_state=RANDOM_STATE,
				stratify_by_label=stratify,
			)
			split_payload = {
				"train": train_df,
				"test": test_df,
			}
		else:
			train_df, val_df, test_df = split_train_validation_test(
				dataset,
				test_size=TEST_SIZE,
				validation_size=VALIDATION_SIZE,
				random_state=RANDOM_STATE,
				stratify_by_label=stratify,
			)
			split_payload = {
				"train": train_df,
				"validation": val_df,
				"test": test_df,
			}

		dataset.to_csv(OUTPUT_DIR / "dataset_prepared.csv", index=False)
		for split_name, split_df in split_payload.items():
			split_df.to_csv(OUTPUT_DIR / f"{split_name}.csv", index=False)

	except (DataLoaderError, DataLabelingError, DataSplitError) as exc:
		print(f"[prepare_data] Error: {exc}")
		return 1

	print(f"[prepare_data] Completed. Output saved to: {OUTPUT_DIR}")
	print(f"[prepare_data] Total rows: {len(dataset)}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
