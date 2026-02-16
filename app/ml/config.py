"""
ML Configuration
Centralized configuration for ML models and pipeline
"""
import os

# Paths
ML_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(ML_DIR, 'models')
DATASET_PATH = os.path.join(os.path.dirname(ML_DIR), 'dataset.csv')

# Model files
RANDOM_FOREST_PATH = os.path.join(MODEL_DIR, 'random_forest_model.pkl')
GRADIENT_BOOST_PATH = os.path.join(MODEL_DIR, 'gradient_boosting_model.pkl')
NEURAL_NET_PATH = os.path.join(MODEL_DIR, 'neural_network_model.pkl')
ENSEMBLE_PATH = os.path.join(MODEL_DIR, 'ensemble_model.pkl')
CURRENT_MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')  # Active model

# Features (8 features matching our trained model)
FEATURE_COLUMNS = [
    'previous_qualification',
    'age_at_enrollment',
    'scholarship_holder',
    'debtor',
    'tuition_fees_up_to_date',
    'curricular_units_1st_sem_grade',
    'curricular_units_2nd_sem_grade',
    'gdp'
]

TARGET_COLUMN = 'target'

# Model hyperparameters
RANDOM_FOREST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 15,
    'min_samples_split': 5,
    'random_state': 42,
    'class_weight': 'balanced'
}

GRADIENT_BOOST_PARAMS = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 5,
    'random_state': 42
}

NEURAL_NET_PARAMS = {
    'hidden_layer_sizes': (64, 32),
    'activation': 'relu',
    'max_iter': 500,
    'random_state': 42
}

# Risk thresholds
RISK_THRESHOLDS = {
    'low': 30.0,      # 0-30%
    'medium': 60.0,   # 30-60%
    'high': 100.0     # 60-100%
}

def get_risk_category(risk_score: float) -> str:
    """Convert risk score to category"""
    if risk_score < RISK_THRESHOLDS['low']:
        return 'Low'
    elif risk_score < RISK_THRESHOLDS['medium']:
        return 'Medium'
    else:
        return 'High'
