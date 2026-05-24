import os
from dotenv import load_dotenv
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from huggingface_hub import login
from ml.model.config import CHECKPOINT_DIR, MODEL_NAME, LABEL_MAP, ID_TO_LABEL

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
REPO_NAME = "zaidanharith/sentexa-indobert"


def main():
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN is not set")

    if not CHECKPOINT_DIR.exists():
        raise FileNotFoundError(f"Checkpoint not found: {CHECKPOINT_DIR}")

    login(token=HF_TOKEN)

    model = AutoModelForSequenceClassification.from_pretrained(str(CHECKPOINT_DIR))

    model.config.id2label = ID_TO_LABEL
    model.config.label2id = LABEL_MAP

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model.push_to_hub(REPO_NAME)
    tokenizer.push_to_hub(REPO_NAME)

    print(f"Pushed model to {REPO_NAME}")


if __name__ == "__main__":
    main()