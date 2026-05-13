from pathlib import Path
import torch

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "ml" / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CHECKPOINT_DIR = BASE_DIR / "ml" / "model" / "checkpoint"
REPORTS_DIR = BASE_DIR / "ml" / "reports"
PLOTS_DIR = REPORTS_DIR / "plots"
METRICS_DIR = REPORTS_DIR / "metrics"

CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_FILE = PROCESSED_DATA_DIR / "train.csv"
VALID_FILE = PROCESSED_DATA_DIR / "valid.csv"
TEST_FILE = PROCESSED_DATA_DIR / "test.csv"

MODEL_NAME = "indobenchmark/indobert-base-p1"

MAX_LENGTH = 128
BATCH_SIZE = 16
LEARNING_RATE = 2e-5
NUM_EPOCHS = 5
RANDOM_SEED = 42

LABEL_MAP = {
    "negative": 0,
    "neutral": 1,
    "positive": 2,
}

ID_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
