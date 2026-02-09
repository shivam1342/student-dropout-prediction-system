"""
Prediction Controller
Handles loading the ML model, making predictions, and interpreting results.
Uses both SHAP and LIME for comprehensive explainability.
Supports attention mechanism visualization for neural networks.
"""
import joblib
import pandas as pd
import shap
import os
import re
import numpy as np
from lime.lime_tabular import LimeTabularExplainer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier

# --- Model & Explainability Artifacts ---
MODEL_PATH = os.path.join('app', 'ml', 'models', 'model.pkl')

# Load the ML model
try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ ML model loaded successfully. Type: {type(model).__name__}")
except FileNotFoundError:
    model = None
    print("⚠️ ML model not found. Please train the model first by running 'ml/train_model.py'.")
except Exception as e:
    model = None
    print(f"⚠️ Error loading ML model: {e}")

# Initialize explainer based on model type
explainer = None
kernel_explainer_cache = None  # Cache for KernelExplainer to avoid recreating it each time
lime_explainer_cache = None  # Cache for LIME explainer

if model:
    # Check if it's a tree-based model
    if isinstance(model, (RandomForestClassifier, GradientBoostingClassifier)):
        explainer = shap.TreeExplainer(model)
        print("✅ Using TreeExplainer for tree-based model.")
    # Check if it's a neural network
    elif isinstance(model, MLPClassifier):
        # For neural networks, we'll use KernelExplainer (initialized on first use)
        explainer = "kernel"  # Marker to use KernelExplainer
        print("✅ Will use KernelExplainer for neural network model.")
    # Check if it's an ensemble
    elif isinstance(model, VotingClassifier):
        explainer = shap.TreeExplainer(model.estimators_[0])  # Use first estimator
        print("✅ Using TreeExplainer for ensemble model.")
    else:
        print(f"⚠️ Unknown model type: {type(model).__name__}. Will use KernelExplainer.")
        explainer = "kernel"
    
    # Initialize LIME explainer
    try:
        dataset_path = 'dataset.csv'
        if os.path.exists(dataset_path):
            background_data = pd.read_csv(dataset_path)
            
            # Clean column names
            def clean_col_names(df):
                cols = df.columns
                new_cols = []
                for col in cols:
                    new_col = re.sub(r'[^A-Za-z0-9_]+', '', col.lower().strip().replace(' ', '_'))
                    new_cols.append(new_col)
                df.columns = new_cols
                return df
            
            background_data = clean_col_names(background_data)
            
            feature_columns = [
                'previous_qualification',
                'age_at_enrollment',
                'scholarship_holder',
                'debtor',
                'tuition_fees_up_to_date',
                'curricular_units_1st_sem_grade',
                'curricular_units_2nd_sem_grade',
                'gdp'
            ]
            
            training_data = background_data[feature_columns].values
            
            lime_explainer_cache = LimeTabularExplainer(
                training_data,
                feature_names=feature_columns,
                class_names=['Graduate/Enrolled', 'Dropout'],
                mode='classification',
                random_state=42
            )
            print("✅ LIME explainer initialized and cached.")
    except Exception as e:
        print(f"⚠️ Could not initialize LIME explainer: {e}")

def predict_dropout_risk(student_data):
    """
    Predicts dropout risk for a single student.

    Args:
        student_data (dict): A dictionary containing student features.

    Returns:
        tuple: A tuple containing:
            - risk_score (float): The predicted risk score (0-100).
            - risk_category (str): 'Low', 'Medium', or 'High'.
            - top_features (list): A list of dictionaries with the top 3 contributing features.
    """
    if not model:
        return 0, 'N/A', []

    # Convert to DataFrame for model compatibility
    features_df = pd.DataFrame([student_data])
    
    # Ensure columns are in the same order as during training
    # This list MUST match the features used in ml/train_model.py
    feature_columns = [
        'previous_qualification',
        'age_at_enrollment',
        'scholarship_holder',
        'debtor',
        'tuition_fees_up_to_date',
        'curricular_units_1st_sem_grade',
        'curricular_units_2nd_sem_grade',
        'gdp'
    ]
    features_df = features_df[feature_columns]

    # --- Prediction ---
    prediction_proba = model.predict_proba(features_df)[:, 1]  # Probability of class 1 (dropout)
    risk_score = round(prediction_proba[0] * 100, 2)

    # --- Categorization ---
    if risk_score >= 70:
        risk_category = 'High'
    elif risk_score >= 40:
        risk_category = 'Medium'
    else:
        risk_category = 'Low'

    # --- Explainability (SHAP) ---
    if not explainer:
        return risk_score, risk_category, []
    
    # Use appropriate explainer based on model type
    if explainer == "kernel":
        global kernel_explainer_cache
        
        # For neural networks, use KernelExplainer with a small background dataset
        if kernel_explainer_cache is None:
            try:
                dataset_path = 'dataset.csv'
                if os.path.exists(dataset_path):
                    # Load and clean the background data (same as training)
                    background_data = pd.read_csv(dataset_path)
                    
                    # Clean column names (same as train_advanced_models.py)
                    def clean_col_names(df):
                        cols = df.columns
                        new_cols = []
                        for col in cols:
                            new_col = re.sub(r'[^A-Za-z0-9_]+', '', col.lower().strip().replace(' ', '_'))
                            new_cols.append(new_col)
                        df.columns = new_cols
                        return df
                    
                    background_data = clean_col_names(background_data)
                    
                    # Select only the feature columns and sample
                    background_data = background_data[feature_columns]
                    background_data = background_data.sample(n=min(50, len(background_data)), random_state=42)
                    
                    # Create explainer - use a simple predict wrapper to avoid numpy issues
                    def predict_wrapper(X):
                        return model.predict_proba(X)
                    
                    print("Creating KernelExplainer (this may take a moment)...")
                    kernel_explainer_cache = shap.KernelExplainer(predict_wrapper, background_data.values)
                    print("✅ KernelExplainer created and cached.")
                else:
                    print("⚠️ Dataset not found for SHAP explanations.")
                    return risk_score, risk_category, []
            except Exception as e:
                print(f"⚠️ Error creating KernelExplainer: {e}")
                import traceback
                traceback.print_exc()
                return risk_score, risk_category, []
        
        # Use the cached explainer
        try:
            print("Computing SHAP values...")
            shap_values = kernel_explainer_cache.shap_values(features_df.values, nsamples=50)
            print("✅ SHAP values computed.")
        except Exception as e:
            print(f"⚠️ Error computing SHAP values: {e}")
            return risk_score, risk_category, []
    else:
        # Use TreeExplainer for tree-based models
        shap_values = explainer.shap_values(features_df)
    
    # For binary classification, shap_values format depends on the explainer:
    # - TreeExplainer: list of two arrays [class_0_shap, class_1_shap]
    # - KernelExplainer: array of shape (n_samples, n_features, n_classes)
    
    if isinstance(shap_values, list):
        # TreeExplainer format - use class 1 (dropout)
        shap_values_for_dropout = shap_values[1][0]
    elif len(shap_values.shape) == 3:
        # KernelExplainer format (n_samples, n_features, n_classes) - use class 1
        shap_values_for_dropout = shap_values[0, :, 1]
    else:
        # Single class or unknown format - use as is
        shap_values_for_dropout = shap_values[0]

    # Get SHAP feature importance
    feature_importance = pd.DataFrame(
        list(zip(feature_columns, shap_values_for_dropout)),
        columns=['feature', 'shap_value']
    )
    feature_importance['abs_shap'] = feature_importance['shap_value'].abs()
    feature_importance = feature_importance.sort_values(by='abs_shap', ascending=False)

    # Get top 3 SHAP features
    top_features = []
    for _, row in feature_importance.head(3).iterrows():
        top_features.append({
            'name': row['feature'].replace('_', ' ').title(),
            'value': student_data[row['feature']],
            'shap_value': float(row['shap_value'])
        })

    # --- Explainability (LIME) ---
    lime_features = []
    if lime_explainer_cache:
        try:
            print("Computing LIME explanations...")
            
            # LIME expects the same predict_proba function
            lime_explanation = lime_explainer_cache.explain_instance(
                features_df.values[0],
                model.predict_proba,
                num_features=8,  # Explain all features
                top_labels=1  # Focus on top prediction
            )
            
            # Get the explanation for the predicted class
            # For binary classification, LIME uses indices 0 and 1
            # We want to explain the dropout probability (class 1)
            predicted_class = model.predict(features_df)[0]
            lime_values = lime_explanation.as_list(label=predicted_class)
            
            # Sort by absolute importance
            lime_sorted = sorted(lime_values, key=lambda x: abs(x[1]), reverse=True)
            
            # Get top 3 LIME features
            for i, (feature_desc, lime_value) in enumerate(lime_sorted[:3]):
                # Extract feature name from LIME description (e.g., "age_at_enrollment > 22.00")
                feature_name = feature_desc.split()[0] if ' ' in feature_desc else feature_desc
                
                # Find matching feature column
                matching_feature = None
                for feat in feature_columns:
                    if feat in feature_name or feature_name in feat:
                        matching_feature = feat
                        break
                
                if matching_feature:
                    lime_features.append({
                        'name': matching_feature.replace('_', ' ').title(),
                        'value': student_data[matching_feature],
                        'lime_value': float(lime_value),
                        'description': feature_desc
                    })
            
            print("✅ LIME explanations computed.")
        except Exception as e:
            print(f"⚠️ Error computing LIME explanations: {e}")
            import traceback
            traceback.print_exc()

    return risk_score, risk_category, top_features, lime_features


def get_attention_weights(student_data):
    """
    Attention mechanism not available - returns empty list.
    This function exists for backward compatibility.
    """
    return []
