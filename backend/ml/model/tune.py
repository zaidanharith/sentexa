import torch
import torch.nn as nn
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import pandas as pd
import json
from pathlib import Path
import optuna
from optuna.pruners import MedianPruner
from datasets import Dataset

from ml.model.config import (
    MODEL_NAME,
    DEVICE,
    LABEL_MAP,
    PROCESSED_DATA_DIR,
    METRICS_DIR,
)
from ml.model.dataset import load_dataframe


class WeightedTrainer(Trainer):
    def __init__(self, class_weights, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        
        loss_fn = nn.CrossEntropyLoss(weight=self.class_weights)
        loss = loss_fn(logits, labels)
        
        return (loss, outputs) if return_outputs else loss


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    accuracy = accuracy_score(labels, predictions)
    precision_macro = precision_score(labels, predictions, average="macro", zero_division=0)
    recall_macro = recall_score(labels, predictions, average="macro", zero_division=0)
    f1_macro = f1_score(labels, predictions, average="macro", zero_division=0)
    
    return {
        "accuracy": accuracy,
        "precision_macro": precision_macro,
        "recall_macro": recall_macro,
        "f1_macro": f1_macro,
    }


def prepare_dataset(csv_path, tokenizer, max_length):
    df = load_dataframe(csv_path)
    texts = df["text"].tolist()
    labels = df["label"].astype(int).tolist()
    
    encodings = tokenizer(
        texts,
        truncation=True,
        padding="max_length",
        max_length=max_length,
        return_tensors="pt"
    )
    
    dataset = Dataset.from_dict({
        "input_ids": encodings["input_ids"],
        "attention_mask": encodings["attention_mask"],
        "labels": labels,
    })
    
    return dataset


def get_class_weights():
    df = load_dataframe(PROCESSED_DATA_DIR / "train.csv")
    labels = df["label"].astype(int).tolist()
    
    unique_labels = np.unique(labels)
    weights = compute_class_weight(
        "balanced",
        classes=unique_labels,
        y=labels
    )
    
    weights_tensor = torch.tensor(weights, dtype=torch.float32).to(DEVICE)
    return weights_tensor


def objective(trial):
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 5e-5, log=True)
    batch_size = trial.suggest_categorical("batch_size", [8, 16])
    num_epochs = trial.suggest_int("num_epochs", 3, 6)
    weight_decay = trial.suggest_float("weight_decay", 0.0, 0.3)
    warmup_ratio = trial.suggest_float("warmup_ratio", 0.0, 0.2)
    max_length = trial.suggest_categorical("max_length", [64, 128, 256])
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABEL_MAP),
        ignore_mismatched_sizes=True
    )
    model.to(DEVICE)
    
    train_dataset = prepare_dataset(
        PROCESSED_DATA_DIR / "train.csv",
        tokenizer,
        max_length
    )
    valid_dataset = prepare_dataset(
        PROCESSED_DATA_DIR / "valid.csv",
        tokenizer,
        max_length
    )
    
    training_args = TrainingArguments(
        output_dir="./ml_tuning_output",
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        warmup_ratio=warmup_ratio,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=100,
        disable_tqdm=False,
        report_to="none",
        load_best_model_at_end=False,
    )
    
    class_weights = get_class_weights()
    
    trainer = WeightedTrainer(
        class_weights=class_weights,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        compute_metrics=compute_metrics,
    )
    
    trainer.train()
    
    eval_result = trainer.evaluate()
    f1_macro = eval_result.get("eval_f1_macro", 0.0)
    
    return f1_macro


def run_tuning():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    
    sampler = optuna.samplers.TPESampler(seed=42)
    pruner = MedianPruner()
    
    study = optuna.create_study(
        direction="maximize",
        sampler=sampler,
        pruner=pruner,
    )
    
    study.optimize(objective, n_trials=20, show_progress_bar=True)
    
    best_trial = study.best_trial
    best_hyperparameters = best_trial.params
    best_score = best_trial.value
    
    best_hyperparameters_path = METRICS_DIR / "best_hyperparameters.json"
    with open(best_hyperparameters_path, "w") as f:
        json.dump(best_hyperparameters, f, indent=2)
    
    trials_data = []
    for trial in study.trials:
        trial_data = {
            "trial_number": trial.number,
            "value": trial.value,
            "state": trial.state.name,
            **trial.params
        }
        trials_data.append(trial_data)
    
    trials_df = pd.DataFrame(trials_data)
    trials_csv_path = METRICS_DIR / "optuna_trials.csv"
    trials_df.to_csv(trials_csv_path, index=False)
    
    print("\n" + "="*60)
    print("OPTUNA HYPERPARAMETER TUNING RESULTS")
    print("="*60)
    print(f"Best Trial Score (Macro F1): {best_score:.4f}")
    print("\nBest Hyperparameters:")
    for key, value in best_hyperparameters.items():
        print(f"  {key}: {value}")
    print("="*60 + "\n")
    
    print(f"Best hyperparameters saved to: {best_hyperparameters_path}")
    print(f"All trials saved to: {trials_csv_path}")


if __name__ == "__main__":
    run_tuning()
