import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from pathlib import Path
import json
import numpy as np
from typing import Dict
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    
)
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
from ml.model.config import CHECKPOINT_DIR, DEVICE, MODEL_NAME, ID_TO_LABEL, PLOTS_DIR, METRICS_DIR
from ml.model.dataset import create_test_dataloader


def load_model():
    if not CHECKPOINT_DIR.exists():
        raise FileNotFoundError(f"Checkpoint directory not found: {CHECKPOINT_DIR}")
    
    model = AutoModelForSequenceClassification.from_pretrained(CHECKPOINT_DIR)
    model.to(DEVICE)
    model.eval()
    return model


def evaluate_model(dataloader) -> Dict:
    model = load_model()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )
            
            logits = outputs.logits
            preds = torch.argmax(logits, dim=1)
            
            all_preds.extend(preds.cpu().numpy().tolist())
            all_labels.extend(labels.cpu().numpy().tolist())
    
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    
    accuracy = accuracy_score(all_labels, all_preds)
    precision_macro = precision_score(all_labels, all_preds, average="macro", zero_division=0)
    recall_macro = recall_score(all_labels, all_preds, average="macro", zero_division=0)
    f1_macro = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    
    conf_matrix = confusion_matrix(all_labels, all_preds)
    class_report = classification_report(
        all_labels,
        all_preds,
        target_names=[ID_TO_LABEL[i] for i in sorted(ID_TO_LABEL.keys())],
        zero_division=0,
        output_dict=True
    )
    
    results = {
        "accuracy": float(accuracy),
        "precision_macro": float(precision_macro),
        "recall_macro": float(recall_macro),
        "f1_macro": float(f1_macro),
        "confusion_matrix": conf_matrix.tolist(),
        "classification_report": class_report,
    }
    
    return results


def plot_confusion_matrix(results: Dict) -> None:
    conf_matrix = np.array(results["confusion_matrix"])
    labels = [ID_TO_LABEL[i] for i in sorted(ID_TO_LABEL.keys())]
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        conf_matrix,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=labels,
        yticklabels=labels,
        cbar_kws={'label': 'Count'}
    )
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    
    output_path = PLOTS_DIR / "confusion_matrix.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Confusion matrix saved to: {output_path}")


def print_metrics(results: Dict) -> None:
    print("\n" + "="*50)
    print("EVALUATION METRICS")
    print("="*50)
    print(f"Accuracy:         {results['accuracy']:.4f}")
    print(f"Precision (Macro): {results['precision_macro']:.4f}")
    print(f"Recall (Macro):    {results['recall_macro']:.4f}")
    print(f"F1 Score (Macro):  {results['f1_macro']:.4f}")
    print("\n" + "-"*50)
    print("CLASSIFICATION REPORT")
    print("-"*50)
    
    report = results["classification_report"]
    for label, metrics in report.items():
        if label not in ["accuracy", "macro avg", "weighted avg"]:
            print(f"\n{label}:")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall:    {metrics['recall']:.4f}")
            print(f"  F1-Score:  {metrics['f1-score']:.4f}")
    
    print("\n" + "-"*50)
    print("CONFUSION MATRIX")
    print("-"*50)
    conf_matrix = np.array(results["confusion_matrix"])
    print(conf_matrix)
    print("\n" + "="*50)


def save_metrics(results: Dict, output_path: Path = None) -> None:
    if output_path is None:
        output_path = METRICS_DIR / "test_metrics.json"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Metrics saved to: {output_path}")


def save_classification_report(results: Dict, output_path: Path = None) -> None:
    if output_path is None:
        output_path = METRICS_DIR / "classification_report.json"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    report = results["classification_report"]
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Classification report saved to: {output_path}")


def main():
    try:
        print("Loading test dataloader...")
        test_dataloader = create_test_dataloader()
        
        print("Evaluating model...")
        results = evaluate_model(test_dataloader)
        
        print_metrics(results)
        
        print("\nSaving metrics and reports...")
        save_metrics(results)
        save_classification_report(results)
        
        print("\nGenerating plots...")
        plot_confusion_matrix(results)
        print("All plots and reports saved successfully!")
        
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
        raise


if __name__ == "__main__":
    main()
