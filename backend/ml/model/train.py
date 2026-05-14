import torch
import torch.nn as nn
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from torch.optim import AdamW
import random
import numpy as np
from pathlib import Path
import json
from tqdm import tqdm
from typing import Dict, Tuple
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') 
from ml.model.config import (
    MODEL_NAME,
    CHECKPOINT_DIR,
    DEVICE,
    LEARNING_RATE,
    NUM_EPOCHS,
    RANDOM_SEED,
    LABEL_MAP,
    PLOTS_DIR,
    METRICS_DIR,
)
from ml.model.dataset import create_train_dataloader, create_valid_dataloader, compute_class_weights


def set_seed(seed: int = RANDOM_SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_model():
    num_labels = len(LABEL_MAP)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels,
        ignore_mismatched_sizes=True
    )
    model.to(DEVICE)
    return model


def get_loss_fn(class_weights):
    return nn.CrossEntropyLoss(weight=class_weights)


def train_one_epoch(model, train_loader, optimizer, loss_fn) -> float:
    model.train()
    total_loss = 0.0
    
    progress_bar = tqdm(train_loader, desc="Training")
    for batch in progress_bar:
        input_ids = batch["input_ids"].to(DEVICE)
        attention_mask = batch["attention_mask"].to(DEVICE)
        labels = batch["labels"].to(DEVICE)
        
        optimizer.zero_grad()
        
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )
        
        logits = outputs.logits
        loss = loss_fn(logits, labels)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        progress_bar.set_postfix({"loss": loss.item()})
    
    avg_loss = total_loss / len(train_loader)
    return avg_loss


def validate(model, valid_loader) -> Tuple[float, float, float, float, float]:
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_labels = []
    
    loss_fn = nn.CrossEntropyLoss()
    
    with torch.no_grad():
        for batch in tqdm(valid_loader, desc="Validating"):
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )
            
            logits = outputs.logits
            loss = loss_fn(logits, labels)
            
            total_loss += loss.item()
            
            preds = torch.argmax(logits, dim=1)
            all_preds.extend(preds.cpu().numpy().tolist())
            all_labels.extend(labels.cpu().numpy().tolist())
    
    avg_loss = total_loss / len(valid_loader)
    accuracy = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, average="macro", zero_division=0)
    recall = recall_score(all_labels, all_preds, average="macro", zero_division=0)
    f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    
    return avg_loss, accuracy, precision, recall, f1


def save_checkpoint(model, tokenizer):
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    
    model.save_pretrained(CHECKPOINT_DIR)
    tokenizer.save_pretrained(CHECKPOINT_DIR)
    
    print(f"Model saved to: {CHECKPOINT_DIR}")


def plot_loss_curve(training_history: Dict):
    plt.figure(figsize=(10, 6))
    plt.plot(training_history["epochs"], training_history["train_losses"], label="Training Loss", marker='o')
    plt.plot(training_history["epochs"], training_history["val_losses"], label="Validation Loss", marker='s')
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training and Validation Loss Curve")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_path = PLOTS_DIR / "loss_curve.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Loss curve saved to: {output_path}")


def plot_accuracy_curve(training_history: Dict):
    plt.figure(figsize=(10, 6))
    plt.plot(training_history["epochs"], training_history["val_accuracies"], label="Validation Accuracy", marker='o', color='green')
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Validation Accuracy Curve")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_path = PLOTS_DIR / "accuracy_curve.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Accuracy curve saved to: {output_path}")


def plot_f1_curve(training_history: Dict):
    plt.figure(figsize=(10, 6))
    plt.plot(training_history["epochs"], training_history["val_f1_scores"], label="Validation F1 Score (Macro)", marker='o', color='orange')
    plt.xlabel("Epoch")
    plt.ylabel("F1 Score")
    plt.title("Validation F1 Score Curve (Macro)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_path = PLOTS_DIR / "f1_curve.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"F1 curve saved to: {output_path}")


def plot_precision_recall_curves(training_history: Dict):
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(training_history["epochs"], training_history["val_precisions"], label="Validation Precision (Macro)", marker='o', color='blue')
    plt.xlabel("Epoch")
    plt.ylabel("Precision")
    plt.title("Validation Precision Curve (Macro)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.plot(training_history["epochs"], training_history["val_recalls"], label="Validation Recall (Macro)", marker='o', color='red')
    plt.xlabel("Epoch")
    plt.ylabel("Recall")
    plt.title("Validation Recall Curve (Macro)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_path = PLOTS_DIR / "precision_recall_curves.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Precision/Recall curves saved to: {output_path}")


def save_training_metrics(metrics: Dict, output_path: Path = None):
    if output_path is None:
        output_path = METRICS_DIR / "training_metrics.json"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Training metrics saved to: {output_path}")


def train():
    set_seed()
    
    print("\n" + "="*60)
    print("IndoBERT Fine-tuning for Sentiment Analysis")
    print("="*60)
    print(f"Device: {DEVICE}")
    print(f"Epochs: {NUM_EPOCHS}")
    print(f"Learning Rate: {LEARNING_RATE}")
    print(f"Batch Size: 16")
    print("="*60 + "\n")
    
    model = load_model()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    class_weights = compute_class_weights().to(DEVICE)
    loss_fn = get_loss_fn(class_weights)
    
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    
    train_loader = create_train_dataloader()
    valid_loader = create_valid_dataloader()
    
    best_f1 = 0.0
    best_epoch = 0
    training_history = {
        "epochs": [],
        "train_losses": [],
        "val_losses": [],
        "val_accuracies": [],
        "val_precisions": [],
        "val_recalls": [],
        "val_f1_scores": []
    }
    
    for epoch in range(NUM_EPOCHS):
        print(f"\nEpoch {epoch+1}/{NUM_EPOCHS}")
        print("-"*60)
        
        train_loss = train_one_epoch(model, train_loader, optimizer, loss_fn)
        print(f"Training Loss: {train_loss:.4f}")
        
        val_loss, val_acc, val_prec, val_rec, val_f1 = validate(model, valid_loader)
        print(f"Validation Loss: {val_loss:.4f}")
        print(f"Validation Accuracy: {val_acc:.4f}")
        print(f"Validation Precision (Macro): {val_prec:.4f}")
        print(f"Validation Recall (Macro): {val_rec:.4f}")
        print(f"Validation F1 Score (Macro): {val_f1:.4f}")
        
        training_history["epochs"].append(epoch + 1)
        training_history["train_losses"].append(train_loss)
        training_history["val_losses"].append(val_loss)
        training_history["val_accuracies"].append(val_acc)
        training_history["val_precisions"].append(val_prec)
        training_history["val_recalls"].append(val_rec)
        training_history["val_f1_scores"].append(val_f1)
        
        if val_f1 > best_f1:
            best_f1 = val_f1
            best_epoch = epoch + 1
            print(f"\n* New best Macro F1 score: {val_f1:.4f}")
            save_checkpoint(model, tokenizer)
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"Best Epoch: {best_epoch}")
    print(f"Best Macro F1 Score: {best_f1:.4f}")
    print("="*60 + "\n")
    
    final_metrics = {
        "best_epoch": best_epoch,
        "best_f1_macro": best_f1,
        "best_accuracy": training_history["val_accuracies"][best_epoch-1],
        "best_precision_macro": training_history["val_precisions"][best_epoch-1],
        "best_recall_macro": training_history["val_recalls"][best_epoch-1],
        "num_epochs": NUM_EPOCHS,
        "learning_rate": LEARNING_RATE,
        "training_history": training_history
    }
    
    save_training_metrics(final_metrics)
    
    print("\nGenerating plots...")
    plot_loss_curve(training_history)
    plot_accuracy_curve(training_history)
    plot_f1_curve(training_history)
    plot_precision_recall_curves(training_history)
    print("All plots saved successfully!")


def main():
    try:
        train()
    except Exception as e:
        print(f"Error during training: {str(e)}")
        raise


if __name__ == "__main__":
    main()
