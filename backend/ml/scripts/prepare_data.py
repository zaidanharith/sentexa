import pandas as pd
from pathlib import Path
import json
from ml.preprocessing.cleaning import clean_text
from ml.preprocessing.normalization import normalize_text
from ml.preprocessing.stopwords import remove_stopwords_tokens
from ml.model.config import LABEL_MAP, PROCESSED_DATA_DIR, RAW_DATA_DIR


TEXT_COLUMN_CANDIDATES = ["text", "review", "content", "sentence"]
LABEL_COLUMN_CANDIDATES = ["label", "sentiment", "target"]


def detect_text_column(df: pd.DataFrame) -> str:
    for col in TEXT_COLUMN_CANDIDATES:
        if col in df.columns:
            return col
    raise ValueError(f"Text column not found. Available: {list(df.columns)}")


def detect_label_column(df: pd.DataFrame) -> str:
    for col in LABEL_COLUMN_CANDIDATES:
        if col in df.columns:
            return col
    raise ValueError(f"Label column not found. Available: {list(df.columns)}")


def validate_dataset(df: pd.DataFrame, file_name: str) -> None:
    if df.empty:
        raise ValueError(f"{file_name} is empty")
    
    text_col = detect_text_column(df)
    label_col = detect_label_column(df)
    
    if df[text_col].isnull().all() or df[label_col].isnull().all():
        raise ValueError(f"{file_name} has all null values")


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    text_col = detect_text_column(df)
    label_col = detect_label_column(df)
    
    df = df.dropna(subset=[text_col, label_col])
    df = df[df[text_col].str.strip() != ""].copy()
    
    print("Cleaning text...")
    df[text_col] = df[text_col].apply(lambda x: clean_text(str(x)))
    
    print("Normalizing text...")
    df[text_col] = df[text_col].apply(lambda x: normalize_text(str(x)))
    
    print("Removing stopwords...")
    df[text_col] = df[text_col].apply(
        lambda x: " ".join(remove_stopwords_tokens(x.split(), use_default_stopwords=True))
    )
    
    df = df[df[text_col].str.strip() != ""].copy()
    
    return df[[text_col, label_col]]


def encode_labels(df: pd.DataFrame) -> pd.DataFrame:
    print("Encoding labels...")
    label_col = df.columns[1]
    
    df = df.copy()
    df[label_col] = df[label_col].str.lower().str.strip()
    
    for label_text, label_id in LABEL_MAP.items():
        mask = df[label_col] == label_text
        if mask.any():
            df.loc[mask, label_col] = label_id
    
    invalid = df[~df[label_col].isin(LABEL_MAP.values())]
    if not invalid.empty:
        invalid_labels = set(invalid[label_col].unique())
        raise ValueError(f"Unknown labels: {invalid_labels}")
    
    df[label_col] = df[label_col].astype(int)
    
    return df


def save_processed_data(df: pd.DataFrame, output_path: Path) -> None:
    print(f"Saving to {output_path}...")
    df.columns = ["text", "label"]
    df.to_csv(output_path, index=False)


def save_label_map() -> None:
    label_map_path = PROCESSED_DATA_DIR / "label_map.json"
    with open(label_map_path, "w") as f:
        json.dump(LABEL_MAP, f, indent=2)
    print(f"Label map saved to {label_map_path}")
    
    checkpoint_dir = Path(__file__).parent.parent / "model" / "checkpoint"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_label_map_path = checkpoint_dir / "label_map.json"
    with open(checkpoint_label_map_path, "w") as f:
        json.dump(LABEL_MAP, f, indent=2)
    print(f"Label map saved to {checkpoint_label_map_path}")


def prepare_split(split_name: str) -> None:
    input_path = RAW_DATA_DIR / f"{split_name}.csv"
    output_path = PROCESSED_DATA_DIR / f"{split_name}.csv"
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    print(f"\nPreparing {split_name} dataset...")
    df = pd.read_csv(input_path)
    
    validate_dataset(df, split_name)
    df = preprocess_dataframe(df)
    df = encode_labels(df)
    save_processed_data(df, output_path)
    print(f"{split_name} dataset ready")


def main() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Starting data preparation pipeline...")
    
    prepare_split("train")
    prepare_split("valid")
    prepare_split("test")
    
    save_label_map()
    print("\nData preparation complete!")


if __name__ == "__main__":
    main()
