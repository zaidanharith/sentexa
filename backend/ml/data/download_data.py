import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path, override=False)

import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi


DATASET_NAME = "alvinhanafie/dataset-for-indonesian-sentiment-analysis"
FILE_MAPPING = {
	"train_preprocess_ori.tsv": "train.csv",
	"valid_preprocess.tsv": "valid.csv",
	"test_preprocess_masked_label.tsv": "test.csv",
}


def main(force_download: bool = False) -> int:
	raw_dir = Path(__file__).resolve().parent / "raw"
	raw_dir.mkdir(parents=True, exist_ok=True)

	target_files = [raw_dir / name for name in FILE_MAPPING.values()]
	if not force_download and all(path.exists() for path in target_files):
		print("All CSV files already exist. Skipping download.")
		return 0

	username = os.getenv("KAGGLE_USERNAME")
	key = os.getenv("KAGGLE_KEY")
	if not username or not key:
		raise ValueError("Set KAGGLE_USERNAME and KAGGLE_KEY in backend/.env")

	print("Authenticating with Kaggle...")
	os.environ["KAGGLE_USERNAME"] = username
	os.environ["KAGGLE_KEY"] = key
	api = KaggleApi()
	api.authenticate()

	tmp_dir = Path(tempfile.mkdtemp(prefix="kaggle_download_"))
	try:
		print("Downloading dataset...")
		api.dataset_download_files(DATASET_NAME, path=str(tmp_dir), unzip=False)

		print("Extracting dataset...")
		extract_dir = tmp_dir / "extracted"
		extract_dir.mkdir(parents=True, exist_ok=True)
		for zip_path in tmp_dir.glob("*.zip"):
			with zipfile.ZipFile(zip_path, "r") as zip_ref:
				zip_ref.extractall(extract_dir)

		print("Validating files...")
		found = {}
		for name in FILE_MAPPING.keys():
			matches = list(extract_dir.rglob(name))
			if matches:
				found[name] = matches[0]
		
		missing = [n for n in FILE_MAPPING.keys() if n not in found]
		if missing:
			raise FileNotFoundError(f"Missing files: {', '.join(missing)}")

		print("Converting TSV to CSV...")
		for source_name, target_name in FILE_MAPPING.items():
			df = pd.read_csv(found[source_name], sep="\t")
			target_path = raw_dir / target_name
			df.to_csv(target_path, index=False)
			print(f"Saved: {target_path}")

		print("Download complete.")
		return 0
	finally:
		shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
	raise SystemExit(main())
