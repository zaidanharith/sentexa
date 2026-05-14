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


def prepare_combine_mode() -> None:
    print("="*60)
    print("DATA PREPARATION: COMBINE + STRATIFIED SPLIT")
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


def prepare_process_mode() -> None:
    print("="*60)
    print("DATA PREPARATION: PROCESS INDIVIDUAL SPLITS")
    print("="*60)
    
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    for split_name in ["train", "valid", "test"]:
        input_path = RAW_DATA_DIR / f"{split_name}.csv"
        output_path = PROCESSED_DATA_DIR / f"{split_name}.csv"
        
        if not input_path.exists():
            print(f"Skipping {split_name}: file not found")
            continue
        
        print(f"\nPreparing {split_name}...")
        df = load_csv_file(input_path)
        
        if df.empty:
            raise ValueError(f"{split_name} is empty")
        
        # Detect and rename columns
        text_col = detect_text_column(df)
        label_col = detect_label_column(df)
        df = df[[text_col, label_col]].rename(columns={text_col: 'text', label_col: 'label'}).copy()
        
        df = preprocess_dataframe(df)
        df = encode_labels(df)
        
        df.to_csv(output_path, index=False)
        
        label_dist = df['label'].value_counts().sort_index().to_dict()
        label_names = {v: k for k, v in LABEL_MAP.items()}
        label_dist_named = {label_names.get(k, k): v for k, v in label_dist.items()}
        print(f"Saved {split_name}: {len(df)} samples, distribution: {label_dist_named}")
    
    print("\n" + "="*60)
    print("Data preparation complete!")
    print("="*60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare data for sentiment analysis")
    parser.add_argument(
        "--combine",
        action="store_true",
        help="Combine all raw data and create stratified train/valid/test split"
    )
    
    args = parser.parse_args()
    
    save_label_map()
    
    if args.combine:
        prepare_combine_mode()
    else:
        prepare_process_mode()


if __name__ == "__main__":
    main()
