"""
Train ML Model
This script generates dummy data, trains a RandomForestClassifier, and saves the model.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import re

# --- Configuration ---
DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'dataset.csv')
MODEL_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'models', 'model.pkl')

def load_and_preprocess_data():
    """
    Loads the dataset, cleans column names, and preprocesses the target variable.
    """
    print(f"Loading data from {DATASET_PATH}...")
    df = pd.read_csv(DATASET_PATH)

    # --- Clean Column Names ---
    def clean_col_names(df):
        cols = df.columns
        new_cols = []
        for col in cols:
            new_col = re.sub(r'[^A-Za-z0-9_]+', '', col.lower().strip().replace(' ', '_'))
            new_cols.append(new_col)
        df.columns = new_cols
        return df

    df = clean_col_names(df)
    print("Cleaned column names.")

    # --- Preprocess Target Variable ---
    # Map 'Dropout' to 1 and 'Graduate'/'Enrolled' to 0
    df['target'] = df['target'].apply(lambda x: 1 if x == 'Dropout' else 0)
    print(f"Target variable preprocessed. Distribution:\n{df['target'].value_counts(normalize=True)}")
    
    return df

def train_model(df):
    """
    Trains a RandomForestClassifier and evaluates it.
    """
    print("\n--- Training Model ---")
    # --- Feature Selection ---
    # Select features that are most similar to the data collected in the application's Student model.
    features = [
        'previous_qualification',
        'age_at_enrollment',
        'scholarship_holder',
        'debtor',
        'tuition_fees_up_to_date',
        'curricular_units_1st_sem_grade',
        'curricular_units_2nd_sem_grade',
        'gdp'
    ]
    print(f"\nTraining model with {len(features)} selected features.")
    target = 'target'

    X = df[features]
    y = df[target]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")

    # --- Train RandomForest ---
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    # --- Evaluate ---
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    return model

def save_model(model):
    """
    Saves the trained model to a file.
    """
    print(f"\nSaving model to {MODEL_OUTPUT_PATH}...")
    # Ensure the directory exists
    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT_PATH)
    print("✅ Model saved successfully.")

if __name__ == '__main__':
    # Full pipeline
    processed_df = load_and_preprocess_data()
    trained_model = train_model(processed_df)
    save_model(trained_model)
    print("\n🚀 Training pipeline finished. You can now run the Flask application.")
