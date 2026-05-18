import torch
import torch.nn as nn
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)
from transformers.trainer_callback import TrainerCallback
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import pandas as pd
import json
from pathlib import Path
import optuna
from optuna.pruners import MedianPruner
from datasets import Dataset
import shutil

from ml.model.config import (
    MODEL_NAME,
    DEVICE,
    BATCH_SIZE,
    MAX_LENGTH,
    LEARNING_RATE,
    WEIGHT_DECAY,
    NUM_EPOCHS,
    WARMUP_RATIO,
    LABEL_MAP,
    PROCESSED_DATA_DIR,
    METRICS_DIR,
    BASE_DIR
)
from ml.model.dataset import load_dataframe


TUNING_OUTPUT_DIR = BASE_DIR / "ml" / "model" / "tuning_output"
train_df = None
valid_df = None
train_dataset = None
valid_dataset = None
class_weights = None
tokenizer = None


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


def prepare_dataset_cached(df, tok, max_length):
    texts = df["text"].tolist()
    labels = df["label"].astype(int).tolist()
    
    encodings = tok(
        texts,
        truncation=True,
        padding="max_length",
        max_length=max_length,
    )
    
    dataset = Dataset.from_dict({
        "input_ids": encodings["input_ids"],
        "attention_mask": encodings["attention_mask"],
        "labels": labels,
    })
    
    return dataset


def initialize_globals():
    global train_df, valid_df, train_dataset, valid_dataset, class_weights, tokenizer
    
    print("Loading data...")
    train_df = load_dataframe(PROCESSED_DATA_DIR / "train.csv")
    valid_df = load_dataframe(PROCESSED_DATA_DIR / "valid.csv")
    
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    print("Preparing datasets...")
    train_dataset = prepare_dataset_cached(train_df, tokenizer, MAX_LENGTH)
    valid_dataset = prepare_dataset_cached(valid_df, tokenizer, MAX_LENGTH)
    
    print("Computing class weights...")
    labels = train_df["label"].astype(int).tolist()
    unique_labels = np.unique(labels)
    weights = compute_class_weight(
        "balanced",
        classes=unique_labels,
        y=labels
    )
    class_weights = torch.tensor(weights, dtype=torch.float32).to(DEVICE)


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


class OptunaCallback(TrainerCallback):
    def __init__(self, trial):
        self.trial = trial

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if metrics is None:
            return
        
        metric_value = metrics.get("eval_f1_macro", 0.0)
        self.trial.report(metric_value, step=int(state.epoch))
        
        if self.trial.should_prune():
            raise optuna.TrialPruned()


def objective(trial):
    assert train_dataset is not None
    assert valid_dataset is not None
    assert class_weights is not None

    learning_rate = trial.suggest_float("learning_rate", 8e-6, 5e-5, log=True)
    batch_size = trial.suggest_categorical(
        "batch_size",
        sorted({max(4, BATCH_SIZE // 2), BATCH_SIZE}),
    )
    num_epochs = trial.suggest_categorical(
        "num_epochs",
        [max(1, NUM_EPOCHS - 1), NUM_EPOCHS],
    )
    weight_decay = trial.suggest_float("weight_decay", 0.0, 0.05)
    warmup_ratio = trial.suggest_float("warmup_ratio", 0.02, 0.1)
    
    id2label = {v: k for k, v in LABEL_MAP.items()}
    config = AutoConfig.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABEL_MAP),
        id2label=id2label,
        label2id=LABEL_MAP,
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        config=config,
        ignore_mismatched_sizes=True,
    )
    
    output_dir = TUNING_OUTPUT_DIR / f"trial_{trial.number}"
    
    steps_per_epoch = max(1, len(train_dataset) // batch_size)
    total_steps = max(1, steps_per_epoch * num_epochs)
    warmup_steps = max(1, int(total_steps * warmup_ratio))

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        warmup_steps=warmup_steps,
        eval_strategy="epoch",
        logging_strategy="epoch",
        save_strategy="epoch",
        logging_steps=500,
        report_to="none",
        load_best_model_at_end=True,
        metric_for_best_model="eval_f1_macro",
        greater_is_better=True,
        seed=42,
        data_seed=42,
        fp16=torch.cuda.is_available(),
        disable_tqdm=True,
    )
    
    trainer = WeightedTrainer(
        class_weights=class_weights,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        compute_metrics=compute_metrics,
        callbacks=[
            EarlyStoppingCallback(
                early_stopping_patience=2,
                early_stopping_threshold=0.0,
            ),
            OptunaCallback(trial),
        ],
    )
    
    try:
        trainer.train()
    except optuna.TrialPruned:
        raise optuna.TrialPruned()
    
    eval_result = trainer.evaluate()
    f1_macro = eval_result.get("eval_f1_macro", 0.0)
    
    if output_dir.exists():
        shutil.rmtree(output_dir, ignore_errors=True)
    
    return f1_macro


def run_tuning():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    TUNING_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    initialize_globals()
    
    print("\nStarting Optuna hyperparameter tuning...\n")
    
    sampler = optuna.samplers.TPESampler(seed=42)
    pruner = MedianPruner(n_startup_trials=3, n_warmup_steps=2)
    
    study = optuna.create_study(
        direction="maximize",
        sampler=sampler,
        pruner=pruner,
    )
    
    study.optimize(objective, n_trials=6, show_progress_bar=True)
    
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
    
    if TUNING_OUTPUT_DIR.exists():
        shutil.rmtree(TUNING_OUTPUT_DIR, ignore_errors=True)
    
    print("\n" + "="*70)
    print("OPTUNA HYPERPARAMETER TUNING RESULTS")
    print("="*70)
    print(f"Best Trial Score (Macro F1): {best_score:.4f}")
    print(f"Total Trials Completed: {len(study.trials)}")
    print("\nBest Hyperparameters:")
    for key, value in best_hyperparameters.items():
        print(f"  {key}: {value}")
    print("="*70 + "\n")
    
    print(f"Results saved:")
    print(f"  - Best hyperparameters: {best_hyperparameters_path}")
    print(f"  - All trial results: {trials_csv_path}\n")


if __name__ == "__main__":
    run_tuning()

