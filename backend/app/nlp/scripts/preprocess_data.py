from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from app.nlp.preprocessing.cleaning import TextCleaningError, clean_dataframe
from app.nlp.preprocessing.normalization import TextNormalizationError, normalize_dataframe
from app.nlp.preprocessing.stopwords import StopwordError, remove_stopwords_dataframe
from app.nlp.preprocessing.stemming import TextStemmingError, stem_tokens_dataframe
from app.nlp.preprocessing.tokenization import TokenizationError, tokenize_dataframe


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = PROJECT_ROOT / "app" / "nlp" / "data" / "processed" / "dataset_prepared.csv"
OUTPUT_DIR = PROJECT_ROOT / "app" / "nlp" / "data" / "processed"
OUTPUT_FILENAME = "dataset_preprocessed.csv"

TEXT_COLUMN = "text"
WORK_COLUMN = "text_preprocessed"
TOKENS_COLUMN = "tokens"
STEMS_COLUMN = "stems"


def _get_file_signature(path: Path) -> dict[str, float | int]:
	stat = path.stat()
	return {
		"mtime": stat.st_mtime,
		"size": stat.st_size,
	}


def _load_cache(path: Path) -> dict[str, object] | None:
	if not path.exists():
		return None
	with path.open("r", encoding="utf-8") as file_obj:
		return json.load(file_obj)


def _save_cache(path: Path, payload: dict[str, object]) -> None:
	with path.open("w", encoding="utf-8") as file_obj:
		json.dump(payload, file_obj)


def main() -> int:
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	output_path = OUTPUT_DIR / OUTPUT_FILENAME
	cache_path = OUTPUT_DIR / ".preprocess_cache.json"
	output_columns = ["text", "label", "label_id", STEMS_COLUMN]

	try:
		signature = _get_file_signature(INPUT_PATH)
		cache = _load_cache(cache_path)
		if output_path.exists() and cache:
			if cache.get("input_path") == str(INPUT_PATH):
				if cache.get("input_mtime") == signature["mtime"]:
					if cache.get("input_size") == signature["size"]:
						if cache.get("output_columns") == output_columns:
							print(
								f"[preprocess_data] Cached output is up to date: {output_path}"
							)
							return 0

		df = pd.read_csv(INPUT_PATH, encoding="utf-8")
		if TEXT_COLUMN not in df.columns:
			raise ValueError(
				f"Text column '{TEXT_COLUMN}' not found. Available columns: {list(df.columns)}"
			)

		if WORK_COLUMN != TEXT_COLUMN:
			df[WORK_COLUMN] = df[TEXT_COLUMN]

		df = clean_dataframe(
			df,
			text_column=WORK_COLUMN,
			inplace=True,
			lowercase=True,
			remove_html=True,
			remove_urls=True,
			remove_mentions=True,
			hashtag_mode="keep",
			remove_emojis=True,
			remove_punctuation=True,
			remove_numbers=False,
			reduce_repeated_chars=True,
			normalize_whitespace=True,
		)

		df = normalize_dataframe(
			df,
			text_column=WORK_COLUMN,
			inplace=True,
			lowercase=True,
			strip_accents=True,
			use_default_slang_map=True,
			reduce_repeated_chars=True,
			max_repeat=2,
			normalize_whitespace=True,
		)

		df = remove_stopwords_dataframe(
			df,
			text_column=WORK_COLUMN,
			inplace=True,
			use_default_stopwords=True,
			lowercase=True,
			normalize_whitespace=True,
		)

		df = tokenize_dataframe(
			df,
			text_column=WORK_COLUMN,
			output_column=TOKENS_COLUMN,
			inplace=True,
			lowercase=True,
			keep_numbers=True,
			min_token_length=1,
			custom_pattern=None,
		)

		df = stem_tokens_dataframe(
			df,
			tokens_column=TOKENS_COLUMN,
			output_column=STEMS_COLUMN,
			lowercase=True,
			drop_empty=True,
		)

		selected_columns = [col for col in output_columns if col in df.columns]
		if not selected_columns:
			raise ValueError("No expected output columns found after preprocessing.")
		df = df[selected_columns].copy()

		df.to_csv(output_path, index=False)
		_save_cache(
			cache_path,
			{
				"input_path": str(INPUT_PATH),
				"input_mtime": signature["mtime"],
				"input_size": signature["size"],
				"output_path": str(output_path),
				"output_columns": output_columns,
			},
		)

	except (
		FileNotFoundError,
		ValueError,
		TextCleaningError,
		TextNormalizationError,
		StopwordError,
		TokenizationError,
		TextStemmingError,
	) as exc:
		print(f"[preprocess_data] Error: {exc}")
		return 1

	print(f"[preprocess_data] Completed. Output saved to: {output_path}")
	print(f"[preprocess_data] Total rows: {len(df)}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
