import argparse
import pandas as pd
from pathlib import Path
import json
from sklearn.model_selection import train_test_split
from ml.preprocessing.cleaning import clean_text
from ml.preprocessing.normalization import normalize_text
from ml.preprocessing.stopwords import remove_stopwords_tokens
from ml.model.config import LABEL_MAP, PROCESSED_DATA_DIR, RAW_DATA_DIR


TEXT_COLUMN_CANDIDATES = ["text", "review", "content", "sentence"]
LABEL_COLUMN_CANDIDATES = ["label", "sentiment", "target"]
MIN_LABEL_COUNT_WARNING = 50
MIN_LABEL_COUNT_HARD_FAIL = 10


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


def load_csv_file(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    sep = ','
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        header = f.readline()
        if '\t' in header:
            sep = '\t'
    
    return pd.read_csv(file_path, sep=sep)


def load_raw_data() -> pd.DataFrame:
    dfs = []
    
    for split in ['train', 'valid', 'test']:
        csv_path = RAW_DATA_DIR / f"{split}.csv"
        tsv_path = RAW_DATA_DIR / f"{split}.tsv"
        
        path = csv_path if csv_path.exists() else tsv_path if tsv_path.exists() else None
        
        if path:
            df = load_csv_file(path)
            text_col = detect_text_column(df)
            label_col = detect_label_column(df)
            
            print(f"Loaded {split}: {len(df)} samples")
            print(f"  Text column: {text_col}, Label column: {label_col}")
            print(f"  Distribution: {df[label_col].value_counts().to_dict()}")
            
            dfs.append(df[[text_col, label_col]].rename(columns={text_col: 'text', label_col: 'label'}).copy())
    
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        print(f"\nCombined: {len(combined)} samples")
        print(f"Distribution: {combined['label'].value_counts().to_dict()}")
        return combined
    else:
        raise FileNotFoundError("No raw data files found in {RAW_DATA_DIR}")


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess text data (assumes columns are already named 'text' and 'label')"""
    df = df.dropna(subset=['text', 'label'])
    df = df[df['text'].str.strip() != ""].copy()
    
    print("Cleaning text...")
    df['text'] = df['text'].apply(lambda x: clean_text(str(x)))
    
    print("Normalizing text...")
    df['text'] = df['text'].apply(lambda x: normalize_text(str(x)))
    
    print("Removing stopwords...")
    df['text'] = df['text'].apply(
        lambda x: " ".join(remove_stopwords_tokens(x.split(), use_default_stopwords=True))
    )
    
    df = df[df['text'].str.strip() != ""].copy()
    return df


def encode_labels(df: pd.DataFrame) -> pd.DataFrame:
    print("Encoding labels...")
    df = df.copy()
    df['label'] = df['label'].str.lower().str.strip()
    
    for label_text, label_id in LABEL_MAP.items():
        mask = df['label'] == label_text
        if mask.any():
            df.loc[mask, 'label'] = label_id
    
    invalid = df[~df['label'].isin(LABEL_MAP.values())]
    if not invalid.empty:
        invalid_labels = set(invalid['label'].unique())
        print(f"Warning: Unknown labels {invalid_labels}, removing them")
        df = df[df['label'].isin(LABEL_MAP.values())]
    
    df['label'] = df['label'].astype(int)
    return df


def validate_split_distribution(df: pd.DataFrame, split_name: str) -> None:
    """Validate minimum label distribution for a split.

    - Hard fail when one or more labels are too scarce.
    - Warn when all labels exist but one is still relatively small.
    """
    expected_labels = set(LABEL_MAP.values())
    counts = df['label'].value_counts().to_dict()
    present_labels = set(counts.keys())
    missing_labels = sorted(expected_labels - present_labels)

    if missing_labels:
        label_names = {v: k for k, v in LABEL_MAP.items()}
        missing_names = [label_names.get(x, str(x)) for x in missing_labels]
        raise ValueError(
            f"{split_name} split missing labels: {missing_names}. "
            "Please review source data or split ratios."
        )

    low_hard_fail = sorted([k for k, v in counts.items() if v < MIN_LABEL_COUNT_HARD_FAIL])
    if low_hard_fail:
        label_names = {v: k for k, v in LABEL_MAP.items()}
        low_hard_fail_names = [f"{label_names.get(x, x)}={counts[x]}" for x in low_hard_fail]
        raise ValueError(
            f"{split_name} split has too few samples for labels: {', '.join(low_hard_fail_names)}. "
            f"Minimum hard-fail threshold is {MIN_LABEL_COUNT_HARD_FAIL}."
        )

    low_warning = sorted([k for k, v in counts.items() if v < MIN_LABEL_COUNT_WARNING])
    if low_warning:
        label_names = {v: k for k, v in LABEL_MAP.items()}
        low_warning_names = [f"{label_names.get(x, x)}={counts[x]}" for x in low_warning]
        print(
            f"Warning: {split_name} split has low label counts: {', '.join(low_warning_names)}. "
            f"Recommended minimum is {MIN_LABEL_COUNT_WARNING}."
        )


def create_stratified_split(df: pd.DataFrame, 
                           train_ratio: float = 0.7,
                           valid_ratio: float = 0.15,
                           test_ratio: float = 0.15):
    print(f"\nCreating stratified split: train={train_ratio}, valid={valid_ratio}, test={test_ratio}")
    
    train_df, temp_df = train_test_split(
        df,
        test_size=(1 - train_ratio),
        stratify=df['label'],
        random_state=42
    )
    
    valid_size = valid_ratio / (1 - train_ratio)
    valid_df, test_df = train_test_split(
        temp_df,
        test_size=(1 - valid_size),
        stratify=temp_df['label'],
        random_state=42
    )
    
    return train_df, valid_df, test_df


def save_splits(train_df, valid_df, test_df) -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    validate_split_distribution(train_df, "train")
    validate_split_distribution(valid_df, "valid")
    validate_split_distribution(test_df, "test")
    
    for name, df in [('train', train_df), ('valid', valid_df), ('test', test_df)]:
        output_path = PROCESSED_DATA_DIR / f"{name}.csv"
        df_copy = df.copy()
        df_copy.columns = ['text', 'label']
        df_copy.to_csv(output_path, index=False)
        
        label_dist = df['label'].value_counts().sort_index().to_dict()
        label_names = {v: k for k, v in LABEL_MAP.items()}
        label_dist_named = {label_names.get(k, k): v for k, v in label_dist.items()}
        print(f"Saved {name}: {len(df)} samples, distribution: {label_dist_named}")


def save_label_map() -> None:
    label_map_path = PROCESSED_DATA_DIR / "label_map.json"
    with open(label_map_path, "w") as f:
        json.dump(LABEL_MAP, f, indent=2)
    print(f"Label map saved to {label_map_path}")
    
    checkpoint_dir = Path(__file__).parent.parent / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_label_map_path = checkpoint_dir / "label_map.json"
    with open(checkpoint_label_map_path, "w") as f:
        json.dump(LABEL_MAP, f, indent=2)
    print(f"Label map saved to {checkpoint_label_map_path}")


def prepare_data() -> None:
    print("="*60)
    print("DATA PREPARATION: COMBINED RAW SPLITS + STRATIFIED SPLIT")
    print("="*60)
    
    df = load_raw_data()
    print("\nPreprocessing data...")
    df = preprocess_dataframe(df)
    df = encode_labels(df)
    
    train_df, valid_df, test_df = create_stratified_split(df)
    save_splits(train_df, valid_df, test_df)
    
    print("\n" + "="*60)
    print("Data preparation complete!")
    print("="*60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare data for sentiment analysis")
    parser.parse_args()

    save_label_map()

    prepare_data()


if __name__ == "__main__":
    main()
