import json
import os
from pathlib import Path
from typing import Dict, List, Optional, cast

import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from ml.model.config import CHECKPOINT_DIR, HF_MODEL, DEVICE, MAX_LENGTH, LABEL_MAP
from ml.preprocessing.cleaning import clean_text
from ml.preprocessing.normalization import normalize_text
from ml.preprocessing.stopwords import remove_stopwords_tokens


model = None
tokenizer = None
label_map = None
HF_CACHE_DIR = Path(os.getenv("HF_HOME", "/tmp/sentexa/huggingface"))
HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)

class PredictionError(ValueError):
    pass


def _checkpoint_is_ready() -> bool:
    config_path = CHECKPOINT_DIR / "config.json"
    model_safetensors = CHECKPOINT_DIR / "model.safetensors"
    model_bin = CHECKPOINT_DIR / "pytorch_model.bin"

    return config_path.exists() and (model_safetensors.exists() or model_bin.exists())


def _save_model_artifacts(model_instance) -> None:
    try:
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        model_instance.save_pretrained(CHECKPOINT_DIR)
        print(f"Saved model artifacts to {CHECKPOINT_DIR}")
    except Exception as e:
        print(f"Warning: could not save model artifacts to {CHECKPOINT_DIR}: {e}")


def _save_tokenizer_artifacts(tokenizer_instance) -> None:
    try:
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        tokenizer_instance.save_pretrained(CHECKPOINT_DIR)
        print(f"Saved tokenizer artifacts to {CHECKPOINT_DIR}")
    except Exception as e:
        print(f"Warning: could not save tokenizer artifacts to {CHECKPOINT_DIR}: {e}")


def load_model():
    global model
    if model is None:
        local_error = None
        try:
            if _checkpoint_is_ready():
                try:
                    model = AutoModelForSequenceClassification.from_pretrained(CHECKPOINT_DIR)
                    print(f"Loaded model from checkpoint directory: {CHECKPOINT_DIR}")
                except Exception as e:
                    local_error = e
                    print(f"Error loading model from checkpoint directory {CHECKPOINT_DIR}: {e}")

            if model is None:
                model = AutoModelForSequenceClassification.from_pretrained(
                    HF_MODEL,
                    cache_dir=str(HF_CACHE_DIR),
                )
                print(f"Loaded model from Hugging Face Hub: {HF_MODEL}")
                _save_model_artifacts(model)
        except Exception as e:
            raise FileNotFoundError(
                f"Unable to load model from {HF_MODEL} or {CHECKPOINT_DIR}: {e}"
            ) from e

        model.to(DEVICE)
        model.eval()
    
    return model


def load_tokenizer():
    global tokenizer
    if tokenizer is None:
        local_error = None
        try:
            if _checkpoint_is_ready():
                try:
                    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT_DIR)
                except Exception as e:
                    local_error = e
                    print(f"Error loading tokenizer from checkpoint directory {CHECKPOINT_DIR}: {e}")

            if tokenizer is None:
                tokenizer = AutoTokenizer.from_pretrained(
                    HF_MODEL,
                    cache_dir=str(HF_CACHE_DIR),
                )
                _save_tokenizer_artifacts(tokenizer)
        except Exception as e:
            raise FileNotFoundError(
                f"Unable to load tokenizer from {HF_MODEL} or {CHECKPOINT_DIR}: {e}"
            ) from e
    
    return tokenizer


def load_label_map() -> Dict[int, str]:
    global label_map
    if label_map is None:
        model_instance = load_model()
        model_id2label = getattr(model_instance.config, "id2label", None)
        if model_id2label:
            # Avoid generic labels like LABEL_0 when custom mapping is available elsewhere.
            values = [str(v) for v in model_id2label.values()]
            if not all(v.startswith("LABEL_") for v in values):
                label_map = {int(k): str(v) for k, v in model_id2label.items()}
                return label_map

        checkpoint_label_map_path = CHECKPOINT_DIR / "label_map.json"
        processed_label_map_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "label_map.json"
        
        label_map_path = None
        if checkpoint_label_map_path.exists():
            label_map_path = checkpoint_label_map_path
        elif processed_label_map_path.exists():
            label_map_path = processed_label_map_path
        
        if label_map_path and label_map_path.exists():
            with open(label_map_path, "r") as f:
                loaded_map = json.load(f)
                label_map = {v: k for k, v in loaded_map.items()}
        else:
            label_map = {v: k for k, v in LABEL_MAP.items()}
    
    return label_map


def preprocess_text(text: str) -> str:
    if text is None or not isinstance(text, str):
        raise PredictionError("Input must be a non-empty string")
    
    text = text.strip()
    if not text:
        raise PredictionError("Input text cannot be empty")
    
    cleaned = clean_text(text)
    normalized = normalize_text(cleaned)
    removed_stopwords = remove_stopwords_tokens(normalized)

    if isinstance(removed_stopwords, list):
        return " ".join(str(token) for token in removed_stopwords if str(token).strip())

    return str(removed_stopwords)


def _ensure_text(value: object, *, index: Optional[int] = None) -> str:
    if value is None:
        message = "Text is required."
    else:
        text = str(value)
        if text.strip():
            return text
        message = "Text is empty."

    if index is not None:
        message = f"Text at index {index} is empty."

    raise PredictionError(message)


def _build_scores_map(probs: torch.Tensor, label_decoder: Dict[int, str]) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    for idx, score in enumerate(probs):
        label = label_decoder.get(idx, str(idx))
        scores[label] = float(score)
    return scores


def predict_text(text: object, *, include_scores: bool = True) -> Dict[str, object]:
    validated = _ensure_text(text)
    processed_text = preprocess_text(validated)
    
    model_instance = load_model()
    tok = load_tokenizer()
    label_decoder = load_label_map()
    
    encoded = tok(
        processed_text,
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
        return_tensors="pt"
    )
    
    input_ids = encoded["input_ids"].to(DEVICE)
    attention_mask = encoded["attention_mask"].to(DEVICE)
    
    with torch.no_grad():
        outputs = model_instance(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )
        logits = outputs.logits
    
    probs = torch.softmax(logits, dim=1)[0]
    pred_id = int(torch.argmax(logits, dim=1).item())
    confidence = float(probs[pred_id].item())
    predicted_label = label_decoder.get(pred_id, "unknown")
    
    result: Dict[str, object] = {
        "label": predicted_label,
        "label_id": pred_id,
        "score": confidence,
    }
    if include_scores:
        result["scores"] = _build_scores_map(probs, label_decoder)
    
    return result


def predict_texts(texts: List[object], *, include_scores: bool = True) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for idx, text in enumerate(texts):
        validated = _ensure_text(text, index=idx)
        results.append(predict_text(validated, include_scores=include_scores))
    return results


def predict(text: str) -> Dict:
    if text is None or not isinstance(text, str):
        raise PredictionError("Input must be a non-empty string")
    
    text = text.strip()
    if not text:
        raise PredictionError("Input text cannot be empty")
    
    original_text = text
    processed_text = preprocess_text(text)
    
    api_result = predict_text(original_text, include_scores=True)
    pred_id = api_result["label_id"]
    predicted_label = api_result["label"]
    confidence = cast(float, api_result["score"])
    
    return {
        "text": original_text,
        "processed_text": processed_text,
        "predicted_label": predicted_label,
        "predicted_id": pred_id,
        "confidence": round(float(confidence), 4)
    }


def predict_batch(texts: List[str]) -> List[Dict]:
    results = []
    for text in texts:
        try:
            result = predict(text)
            results.append(result)
        except Exception as e:
            results.append({
                "text": text,
                "error": str(e)
            })
    
    return results


def predict_csv(input_csv: str, output_csv: Optional[str] = None):
    input_path = Path(input_csv)
    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")
    
    df = pd.read_csv(input_path)
    
    if "text" not in df.columns:
        raise ValueError("CSV must have 'text' column")
    
    predictions = []
    for idx, text in enumerate(df["text"]):
        try:
            pred = predict(str(text))
            predictions.append(pred)
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{len(df)} rows...")
        except Exception as e:
            predictions.append({
                "text": text,
                "predicted_label": None,
                "predicted_id": None,
                "confidence": None,
                "error": str(e)
            })
    
    pred_df = pd.DataFrame(predictions)
    
    if output_csv is None:
        output_csv = str(input_path.stem) + "_predictions.csv"
    
    pred_df.to_csv(output_csv, index=False)
    print(f"Predictions saved to: {output_csv}")


def main():
    print("\n" + "="*60)
    print("IndoBERT Sentiment Predictor")
    print("="*60)
    
    try:
        while True:
            user_input = input("\nEnter text (or 'quit' to exit): ").strip()
            
            if user_input.lower() == "quit":
                print("Exiting...")
                break
            
            if not user_input:
                print("Please enter a valid text")
                continue
            
            result = predict(user_input)
            
            print("\n" + "-"*60)
            print(f"Original:    {result['text']}")
            print(f"Processed:   {result['processed_text']}")
            print(f"Sentiment:   {result['predicted_label'].upper()}")
            print(f"Confidence:  {result['confidence']:.2%}")
            print("-"*60)
    
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
