"""
Train Advanced ML Models
Trains multiple models: Random Forest, Gradient Boosting, Neural Networks, and Ensemble
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, confusion_matrix
import joblib
import os
import re
import json

# --- Configuration ---
DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset.csv')
MODEL_DIR = os.path.dirname(__file__)

def load_and_preprocess_data():
    """Loads the dataset, cleans column names, and preprocesses the target variable."""
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
    print("✅ Cleaned column names.")

    # --- Preprocess Target Variable ---
    df['target'] = df['target'].apply(lambda x: 1 if x == 'Dropout' else 0)
    print(f"✅ Target variable preprocessed. Distribution:\n{df['target'].value_counts(normalize=True)}")
    
    return df

def prepare_data(df):
    """Prepare features and target for training."""
    # Use more features for better accuracy
    features = [
        'previous_qualification',
        'age_at_enrollment',
        'scholarship_holder',
        'debtor',
        'tuition_fees_up_to_date',
        'curricular_units_1st_sem_grade',
        'curricular_units_2nd_sem_grade',
        'curricular_units_1st_sem_enrolled',
        'curricular_units_1st_sem_approved',
        'curricular_units_2nd_sem_enrolled',
        'curricular_units_2nd_sem_approved',
        'gdp',
        'unemployment_rate',
        'inflation_rate'
    ]
    
    # Handle missing values
    X = df[features].fillna(df[features].mean())
    y = df['target']
    
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y), features

def train_random_forest(X_train, y_train, X_test, y_test):
    """Train Random Forest model."""
    print("\n" + "="*70)
    print("TRAINING RANDOM FOREST MODEL")
    print("="*70)
    
    model = RandomForestClassifier(
        n_estimators=200,      # Increased from 100
        max_depth=15,          # Increased from 10
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1             # Use all CPU cores for parallel processing
    )
    
    # Train
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    # Cross-validation (reduced folds for speed)
    cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='accuracy', n_jobs=-1)
    
    # Get classification report as dictionary to extract precision and recall
    report_dict = classification_report(y_test, y_pred, target_names=['Graduate/Enrolled', 'Dropout'], output_dict=True)
    precision = report_dict['weighted avg']['precision']
    recall = report_dict['weighted avg']['recall']
    
    print(f"✅ Accuracy: {accuracy:.4f}")
    print(f"✅ AUC-ROC: {auc:.4f}")
    print(f"✅ Precision: {precision:.4f}")
    print(f"✅ Recall: {recall:.4f}")
    print(f"✅ CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Graduate/Enrolled', 'Dropout']))
    
    # Save model
    model_path = os.path.join(MODEL_DIR, 'random_forest_model.pkl')
    joblib.dump(model, model_path)
    print(f"✅ Model saved to {model_path}")
    
    return model, accuracy, auc, precision, recall

def train_gradient_boosting(X_train, y_train, X_test, y_test):
    """Train Gradient Boosting model."""
    print("\n" + "="*70)
    print("TRAINING GRADIENT BOOSTING MODEL")
    print("="*70)
    
    model = GradientBoostingClassifier(
        n_estimators=200,      # Increased from 100
        learning_rate=0.05,    # Reduced for better convergence
        max_depth=6,           # Increased from 5
        min_samples_split=5,
        min_samples_leaf=2,
        subsample=0.8,
        random_state=42
    )
    
    # Train
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    # Cross-validation (reduced folds for speed)
    cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='accuracy')
    
    # Get classification report as dictionary to extract precision and recall
    report_dict = classification_report(y_test, y_pred, target_names=['Graduate/Enrolled', 'Dropout'], output_dict=True)
    precision = report_dict['weighted avg']['precision']
    recall = report_dict['weighted avg']['recall']
    
    print(f"✅ Accuracy: {accuracy:.4f}")
    print(f"✅ AUC-ROC: {auc:.4f}")
    print(f"✅ Precision: {precision:.4f}")
    print(f"✅ Recall: {recall:.4f}")
    print(f"✅ CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Graduate/Enrolled', 'Dropout']))
    
    # Save model
    model_path = os.path.join(MODEL_DIR, 'gradient_boosting_model.pkl')
    joblib.dump(model, model_path)
    print(f"✅ Model saved to {model_path}")
    
    return model, accuracy, auc, precision, recall

def train_neural_network(X_train, y_train, X_test, y_test):
    """Train Neural Network model."""
    print("\n" + "="*70)
    print("TRAINING NEURAL NETWORK MODEL")
    print("="*70)
    
    # Scale features for neural network
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = MLPClassifier(
        hidden_layer_sizes=(128, 64, 32),  # Increased layer sizes
        activation='relu',
        solver='adam',
        alpha=0.0001,                      # Reduced regularization
        batch_size=64,                     # Increased batch size for faster training
        learning_rate='adaptive',
        learning_rate_init=0.001,
        max_iter=300,                      # Reduced iterations with early stopping
        early_stopping=True,
        validation_fraction=0.15,          # Increased validation set
        n_iter_no_change=10,               # Stop if no improvement for 10 iterations
        random_state=42,
        verbose=False                      # Reduce console output
    )
    
    # Train
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    # Get classification report as dictionary to extract precision and recall
    report_dict = classification_report(y_test, y_pred, target_names=['Graduate/Enrolled', 'Dropout'], output_dict=True)
    precision = report_dict['weighted avg']['precision']
    recall = report_dict['weighted avg']['recall']
    
    print(f"✅ Accuracy: {accuracy:.4f}")
    print(f"✅ AUC-ROC: {auc:.4f}")
    print(f"✅ Precision: {precision:.4f}")
    print(f"✅ Recall: {recall:.4f}")
    print(f"✅ Training iterations: {model.n_iter_}")
    print(f"✅ Final loss: {model.loss_:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Graduate/Enrolled', 'Dropout']))
    
    # Save model and scaler
    model_path = os.path.join(MODEL_DIR, 'neural_network_model.pkl')
    scaler_path = os.path.join(MODEL_DIR, 'neural_network_scaler.pkl')
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"✅ Model saved to {model_path}")
    print(f"✅ Scaler saved to {scaler_path}")
    
    return model, scaler, accuracy, auc, precision, recall

def train_ensemble_model(rf_model, gb_model, nn_model, nn_scaler, X_train, y_train, X_test, y_test):
    """Train Ensemble (Voting) model."""
    print("\n" + "="*70)
    print("TRAINING ENSEMBLE MODEL (Voting Classifier)")
    print("="*70)
    
    # For ensemble, we'll use soft voting (averaging probabilities)
    # We'll handle NN scaling separately during prediction
    
    # Create voting classifier with only tree-based models
    ensemble = VotingClassifier(
        estimators=[
            ('rf', rf_model),
            ('gb', gb_model)
        ],
        voting='soft',
        weights=[1, 1]
    )
    
    # Train (this will use the already-trained models)
    ensemble.fit(X_train, y_train)
    
    # Evaluate
    y_pred = ensemble.predict(X_test)
    y_pred_proba = ensemble.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    # Get classification report as dictionary to extract precision and recall
    report_dict = classification_report(y_test, y_pred, target_names=['Graduate/Enrolled', 'Dropout'], output_dict=True)
    precision = report_dict['weighted avg']['precision']
    recall = report_dict['weighted avg']['recall']
    
    print(f"✅ Accuracy: {accuracy:.4f}")
    print(f"✅ AUC-ROC: {auc:.4f}")
    print(f"✅ Precision: {precision:.4f}")
    print(f"✅ Recall: {recall:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Graduate/Enrolled', 'Dropout']))
    
    # Save ensemble model
    model_path = os.path.join(MODEL_DIR, 'ensemble_model.pkl')
    joblib.dump(ensemble, model_path)
    print(f"✅ Ensemble model saved to {model_path}")
    
    return ensemble, accuracy, auc, precision, recall

def save_model_comparison(results):
    """Save model comparison results."""
    comparison_path = os.path.join(MODEL_DIR, 'model_comparison.json')
    
    with open(comparison_path, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"\n✅ Model comparison saved to {comparison_path}")

def main():
    """Main training pipeline."""
    print("="*70)
    print("ADVANCED ML MODELS TRAINING PIPELINE")
    print("="*70)
    
    # Load and prepare data
    df = load_and_preprocess_data()
    (X_train, X_test, y_train, y_test), features = prepare_data(df)
    
    print(f"\n📊 Dataset Split:")
    print(f"   Training samples: {len(X_train)}")
    print(f"   Testing samples: {len(X_test)}")
    print(f"   Features: {len(features)}")
    
    # Train all models
    rf_model, rf_acc, rf_auc, rf_prec, rf_rec = train_random_forest(X_train, y_train, X_test, y_test)
    gb_model, gb_acc, gb_auc, gb_prec, gb_rec = train_gradient_boosting(X_train, y_train, X_test, y_test)
    nn_model, nn_scaler, nn_acc, nn_auc, nn_prec, nn_rec = train_neural_network(X_train, y_train, X_test, y_test)
    ensemble_model, ens_acc, ens_auc, ens_prec, ens_rec = train_ensemble_model(
        rf_model, gb_model, nn_model, nn_scaler,
        X_train, y_train, X_test, y_test
    )
    
    # Model comparison
    results = {
        'Random Forest': {
            'accuracy': float(rf_acc), 
            'auc': float(rf_auc),
            'precision': float(rf_prec),
            'recall': float(rf_rec)
        },
        'Gradient Boosting': {
            'accuracy': float(gb_acc), 
            'auc': float(gb_auc),
            'precision': float(gb_prec),
            'recall': float(gb_rec)
        },
        'Neural Network': {
            'accuracy': float(nn_acc), 
            'auc': float(nn_auc),
            'precision': float(nn_prec),
            'recall': float(nn_rec)
        },
        'Ensemble': {
            'accuracy': float(ens_acc), 
            'auc': float(ens_auc),
            'precision': float(ens_prec),
            'recall': float(ens_rec)
        }
    }
    
    # Print comparison
    print("\n" + "="*70)
    print("MODEL COMPARISON")
    print("="*70)
    print(f"{'Model':<20} {'Accuracy':<12} {'AUC-ROC':<12} {'Precision':<12} {'Recall':<12}")
    print("-"*70)
    for model_name, metrics in results.items():
        print(f"{model_name:<20} {metrics['accuracy']:<12.4f} {metrics['auc']:<12.4f} {metrics['precision']:<12.4f} {metrics['recall']:<12.4f}")
    
    # Find best model
    best_model = max(results.items(), key=lambda x: x[1]['accuracy'])
    print(f"\n🏆 Best Model: {best_model[0]} (Accuracy: {best_model[1]['accuracy']:.4f})")
    
    # Save comparison
    save_model_comparison(results)
    
    # Copy best model to model.pkl for backward compatibility
    if best_model[0] == 'Random Forest':
        best_model_path = os.path.join(MODEL_DIR, 'random_forest_model.pkl')
    elif best_model[0] == 'Gradient Boosting':
        best_model_path = os.path.join(MODEL_DIR, 'gradient_boosting_model.pkl')
    elif best_model[0] == 'Neural Network':
        best_model_path = os.path.join(MODEL_DIR, 'neural_network_model.pkl')
    else:
        best_model_path = os.path.join(MODEL_DIR, 'ensemble_model.pkl')
    
    # Copy best model to model.pkl
    import shutil
    shutil.copy(best_model_path, os.path.join(MODEL_DIR, 'model.pkl'))
    print(f"✅ Best model copied to model.pkl for application use")
    
    print("\n" + "="*70)
    print("✅ TRAINING COMPLETE - ALL MODELS SAVED")
    print("="*70)

if __name__ == '__main__':
    main()
