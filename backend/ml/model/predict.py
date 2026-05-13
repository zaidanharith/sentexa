import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from pathlib import Path
import json
from typing import Dict, List, Optional
import pandas as pd
from ml.model.config import CHECKPOINT_DIR, MODEL_NAME, DEVICE, MAX_LENGTH, LABEL_MAP
from ml.preprocessing.cleaning import clean_text
from ml.preprocessing.normalization import normalize_text


model = None
tokenizer = None
label_map = None


class PredictionError(ValueError):
    pass


def load_model():
    global model
    if model is None:
        config_path = CHECKPOINT_DIR / "config.json"
        model_safetensors = CHECKPOINT_DIR / "model.safetensors"
        model_bin = CHECKPOINT_DIR / "pytorch_model.bin"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Model config not found in {CHECKPOINT_DIR}")
        
        if not model_safetensors.exists() and not model_bin.exists():
            raise FileNotFoundError(f"Model weights not found in {CHECKPOINT_DIR} (looking for model.safetensors or pytorch_model.bin)")
        
        model = AutoModelForSequenceClassification.from_pretrained(CHECKPOINT_DIR)
        model.to(DEVICE)
        model.eval()
    
    return model


def load_tokenizer():
    global tokenizer
    if tokenizer is None:
        try:
            tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT_DIR)
        except:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    return tokenizer


def load_label_map() -> Dict[int, str]:
    global label_map
    if label_map is None:
        checkpoint_label_map_path = CHECKPOINT_DIR / "label_map.json"
        processed_label_map_path = Path(__file__).resolve().parents[2] / "data" / "processed" / "label_map.json"
        
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
            inverse_map = {v: k for k, v in LABEL_MAP.items()}
            label_map = {v: k for k, v in inverse_map.items()}
    
    return label_map


def preprocess_text(text: str) -> str:
    if text is None or not isinstance(text, str):
        raise PredictionError("Input must be a non-empty string")
    
    text = text.strip()
    if not text:
        raise PredictionError("Input text cannot be empty")
    
    cleaned = clean_text(text)
    normalized = normalize_text(cleaned)
    
    return normalized


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
    confidence = api_result["score"]
    
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


def predict_csv(input_csv: str, output_csv: str = None):
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
