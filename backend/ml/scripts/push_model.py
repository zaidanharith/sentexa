import os
from dotenv import load_dotenv
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from huggingface_hub import login
from ml.model.config import CHECKPOINT_DIR

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_PATH = CHECKPOINT_DIR
REPO_NAME = "zaidanharith/sentexa-indobert"


def main():
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN is not set. Please set it in your environment or .env file.")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Checkpoint directory not found: {MODEL_PATH}")

    login(token=HF_TOKEN)

    model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_PATH))
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))

    model.push_to_hub(REPO_NAME)
    tokenizer.push_to_hub(REPO_NAME)


if __name__ == "__main__":
    main()