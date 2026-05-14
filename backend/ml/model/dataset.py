import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from ml.model.config import (
    PROCESSED_DATA_DIR,
    TRAIN_FILE,
    VALID_FILE,
    TEST_FILE,
    MODEL_NAME,
    MAX_LENGTH,
    BATCH_SIZE,
)


class SentimentDataset(Dataset):
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        text = self.texts[idx]
        label = self.labels[idx]
        
        encoded = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoded["input_ids"].squeeze(0),
            "attention_mask": encoded["attention_mask"].squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long)
        }


_tokenizer = None


def load_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    return _tokenizer


def load_dataframe(csv_path: Path) -> pd.DataFrame:
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    if df.empty:
        raise ValueError(f"CSV file is empty: {csv_path}")
    
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError(f"CSV must have 'text' and 'label' columns. Got: {df.columns.tolist()}")
    
    return df


def create_dataset(csv_path: Path) -> SentimentDataset:
    df = load_dataframe(csv_path)
    tokenizer = load_tokenizer()
    
    texts = df["text"].tolist()
    labels = df["label"].astype(int).tolist()
    
    return SentimentDataset(texts, labels, tokenizer, MAX_LENGTH)


def create_train_dataset() -> SentimentDataset:
    return create_dataset(TRAIN_FILE)


def create_valid_dataset() -> SentimentDataset:
    return create_dataset(VALID_FILE)


def create_test_dataset() -> SentimentDataset:
    return create_dataset(TEST_FILE)


def create_dataloader(dataset: SentimentDataset, shuffle: bool = False) -> DataLoader:
    return DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=shuffle)


def create_train_dataloader() -> DataLoader:
    dataset = create_train_dataset()
    return create_dataloader(dataset, shuffle=True)


def create_valid_dataloader() -> DataLoader:
    dataset = create_valid_dataset()
    return create_dataloader(dataset, shuffle=False)


def create_test_dataloader() -> DataLoader:
    dataset = create_test_dataset()
    return create_dataloader(dataset, shuffle=False)


def create_all_dataloaders() -> Tuple[DataLoader, DataLoader, DataLoader]:
    train_loader = create_train_dataloader()
    valid_loader = create_valid_dataloader()
    test_loader = create_test_dataloader()
    return train_loader, valid_loader, test_loader


def compute_class_weights() -> torch.Tensor:
    df = load_dataframe(TRAIN_FILE)
    labels = df["label"].astype(int).tolist()
    
    unique_labels = np.unique(labels)
    num_samples = len(labels)
    num_classes = len(unique_labels)
    
    weights = []
    for label_id in sorted(unique_labels):
        count = (np.array(labels) == label_id).sum()
        weight = num_samples / (num_classes * count)
        weights.append(weight)
    
    weights = torch.tensor(weights, dtype=torch.float32)
    return weights
