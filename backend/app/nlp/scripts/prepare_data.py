from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd

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
	get_label_distribution,
	split_train_test,
	split_train_validation_test,
)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Prepare NLP dataset for model training.")
	parser.add_argument("--input", required=True, help="Path to input dataset file (csv/tsv/xls/xlsx).")
	parser.add_argument(
		"--output-dir",
		default="app/nlp/data/processed",
		help="Output directory for prepared dataset files.",
	)
	parser.add_argument("--text-column", default="text", help="Text column name in source dataset.")
	parser.add_argument(
		"--label-column",
		default="label",
		help="Label column name in source dataset for labeled data.",
	)
	parser.add_argument(
		"--split-mode",
		choices=["train-test", "train-val-test"],
		default="train-val-test",
		help="Split strategy to apply.",
	)
	parser.add_argument("--test-size", type=float, default=0.2, help="Test split ratio.")
	parser.add_argument("--validation-size", type=float, default=0.1, help="Validation split ratio.")
	parser.add_argument("--random-state", type=int, default=42, help="Random state for reproducibility.")
	parser.add_argument("--encoding", default="utf-8", help="File encoding for CSV/TSV input.")
	parser.add_argument(
		"--sheet-name",
		default="0",
		help="Excel sheet name/index (ignored for CSV/TSV). Use index number or sheet name.",
	)
	parser.add_argument(
		"--lowercase-text",
		action="store_true",
		help="Convert all text to lowercase during loading.",
	)
	parser.add_argument(
		"--no-stratify",
		action="store_true",
		help="Disable stratified split by label.",
	)
	parser.add_argument(
		"--keep-duplicates",
		action="store_true",
		help="Keep duplicate rows instead of dropping them.",
	)
	parser.add_argument(
		"--auto-label",
		action="store_true",
		help="Treat dataset as unlabeled and create labels using keyword-based rules.",
	)
	parser.add_argument(
		"--allow-custom-labels",
		action="store_true",
		help="Allow labels outside negative/neutral/positive and build dynamic label mapping.",
	)
	return parser.parse_args()


def _parse_sheet_name(raw_value: str) -> int | str:
	try:
		return int(raw_value)
	except ValueError:
		return raw_value


def _resolve_label_to_id(labels: Iterable[object], allow_custom_labels: bool) -> Dict[str, int]:
	if allow_custom_labels:
		mapping = build_label_mapping(labels, preferred_order=["negative", "neutral", "positive"])
		return mapping.label_to_id

	is_supported, unknown = validate_supported_labels(labels)
	if not is_supported:
		raise DataLabelingError(
			"Unsupported labels found: "
			f"{unknown}. Use --allow-custom-labels to keep non-standard classes."
		)
	return dict(DEFAULT_LABEL_TO_ID)


def _save_dataframe(df: pd.DataFrame, output_path: Path) -> None:
	output_path.parent.mkdir(parents=True, exist_ok=True)
	df.to_csv(output_path, index=False)


def main() -> int:
	args = parse_args()
	input_path = Path(args.input)
	output_dir = Path(args.output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	sheet_name = _parse_sheet_name(args.sheet_name)
	drop_duplicates = not args.keep_duplicates

	try:
		if args.auto_label:
			dataset = load_unlabeled_dataset(
				input_path,
				text_column=args.text_column,
				drop_duplicates=drop_duplicates,
				lowercase_text=args.lowercase_text,
				encoding=args.encoding,
				sheet_name=sheet_name,
			)
			dataset = auto_label_dataframe(dataset)
		else:
			dataset = load_labeled_dataset(
				input_path,
				text_column=args.text_column,
				label_column=args.label_column,
				drop_duplicates=drop_duplicates,
				lowercase_text=args.lowercase_text,
				encoding=args.encoding,
				sheet_name=sheet_name,
			)
			dataset = normalize_label_column(dataset)

		label_to_id = _resolve_label_to_id(
			dataset["label"],
			allow_custom_labels=args.allow_custom_labels,
		)
		dataset["label_id"] = dataset["label"].map(label_to_id)

		stratify = not args.no_stratify
		if args.split_mode == "train-test":
			train_df, test_df = split_train_test(
				dataset,
				test_size=args.test_size,
				random_state=args.random_state,
				stratify_by_label=stratify,
			)
			split_payload = {
				"train": train_df,
				"test": test_df,
			}
		else:
			train_df, val_df, test_df = split_train_validation_test(
				dataset,
				test_size=args.test_size,
				validation_size=args.validation_size,
				random_state=args.random_state,
				stratify_by_label=stratify,
			)
			split_payload = {
				"train": train_df,
				"validation": val_df,
				"test": test_df,
			}

		_save_dataframe(dataset, output_dir / "dataset_prepared.csv")
		for split_name, split_df in split_payload.items():
			_save_dataframe(split_df, output_dir / f"{split_name}.csv")

		metadata = {
			"input_file": str(input_path),
			"num_rows": int(len(dataset)),
			"split_mode": args.split_mode,
			"label_to_id": label_to_id,
			"distribution": get_label_distribution(dataset),
			"splits": {
				split_name: {
					"rows": int(len(split_df)),
					"distribution": get_label_distribution(split_df),
				}
				for split_name, split_df in split_payload.items()
			},
		}

		with (output_dir / "metadata.json").open("w", encoding="utf-8") as file_obj:
			json.dump(metadata, file_obj, indent=2)

	except (DataLoaderError, DataLabelingError, DataSplitError) as exc:
		print(f"[prepare_data] Error: {exc}")
		return 1

	print(f"[prepare_data] Completed. Output saved to: {output_dir}")
	print(f"[prepare_data] Total rows: {len(dataset)}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
