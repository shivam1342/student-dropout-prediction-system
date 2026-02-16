"""
Data Loader
Load and prepare data for ML training
"""
import pandas as pd
import re
from typing import Tuple
from sklearn.model_selection import train_test_split
from app.ml.config import DATASET_PATH, FEATURE_COLUMNS, TARGET_COLUMN


class DataLoader:
    """Load and prepare data for training"""
    
    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Clean column names to lowercase with underscores"""
        new_cols = []
        for col in df.columns:
            clean_col = re.sub(r'[^A-Za-z0-9_]+', '', col.lower().strip().replace(' ', '_'))
            new_cols.append(clean_col)
        df.columns = new_cols
        return df
    
    @staticmethod
    def load_data() -> pd.DataFrame:
        """Load dataset from CSV"""
        print(f"Loading data from {DATASET_PATH}...")
        df = pd.read_csv(DATASET_PATH)
        df = DataLoader.clean_column_names(df)
        print(f"✅ Loaded {len(df)} records")
        return df
    
    @staticmethod
    def preprocess_target(df: pd.DataFrame) -> pd.DataFrame:
        """Convert target to binary (1=Dropout, 0=Graduate/Enrolled)"""
        df[TARGET_COLUMN] = df[TARGET_COLUMN].apply(
            lambda x: 1 if x == 'Dropout' else 0
        )
        return df
    
    @staticmethod
    def split_data(df: pd.DataFrame, test_size: float = 0.2) -> Tuple:
        """Split into train and test sets"""
        X = df[FEATURE_COLUMNS]
        y = df[TARGET_COLUMN]
        
        return train_test_split(
            X, y, 
            test_size=test_size, 
            random_state=42, 
            stratify=y
        )
    
    @staticmethod
    def load_and_prepare() -> Tuple:
        """Full pipeline: load, clean, split"""
        df = DataLoader.load_data()
        df = DataLoader.preprocess_target(df)
        X_train, X_test, y_train, y_test = DataLoader.split_data(df)
        
        print(f"✅ Training set: {len(X_train)} samples")
        print(f"✅ Test set: {len(X_test)} samples")
        
        return X_train, X_test, y_train, y_test
