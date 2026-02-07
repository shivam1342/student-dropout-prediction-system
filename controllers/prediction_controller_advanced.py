"""
Advanced Prediction Controller
Handles multiple ML models and provides model comparison
"""
import joblib
import pandas as pd
import shap
import os
import json

# --- Model Paths ---
MODEL_DIR = 'ml'
RF_MODEL_PATH = os.path.join(MODEL_DIR, 'random_forest_model.pkl')
GB_MODEL_PATH = os.path.join(MODEL_DIR, 'gradient_boosting_model.pkl')
NN_MODEL_PATH = os.path.join(MODEL_DIR, 'neural_network_model.pkl')
NN_SCALER_PATH = os.path.join(MODEL_DIR, 'neural_network_scaler.pkl')
ENSEMBLE_MODEL_PATH = os.path.join(MODEL_DIR, 'ensemble_model.pkl')
COMPARISON_PATH = os.path.join(MODEL_DIR, 'model_comparison.json')
DEFAULT_MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')

class MLModelManager:
    """Manages multiple ML models for dropout prediction."""
    
    def __init__(self):
        self.models = {}
        self.nn_scaler = None
        self.explainers = {}
        self.comparison = {}
        self.load_all_models()
    
    def load_all_models(self):
        """Load all available models."""
        # Load Random Forest
        if os.path.exists(RF_MODEL_PATH):
            self.models['random_forest'] = joblib.load(RF_MODEL_PATH)
            self.explainers['random_forest'] = shap.TreeExplainer(self.models['random_forest'])
            print("✅ Random Forest model loaded")
        
        # Load Gradient Boosting
        if os.path.exists(GB_MODEL_PATH):
            self.models['gradient_boosting'] = joblib.load(GB_MODEL_PATH)
            self.explainers['gradient_boosting'] = shap.TreeExplainer(self.models['gradient_boosting'])
            print("✅ Gradient Boosting model loaded")
        
        # Load Neural Network
        if os.path.exists(NN_MODEL_PATH) and os.path.exists(NN_SCALER_PATH):
            self.models['neural_network'] = joblib.load(NN_MODEL_PATH)
            self.nn_scaler = joblib.load(NN_SCALER_PATH)
            print("✅ Neural Network model loaded")
        
        # Load Ensemble
        if os.path.exists(ENSEMBLE_MODEL_PATH):
            self.models['ensemble'] = joblib.load(ENSEMBLE_MODEL_PATH)
            print("✅ Ensemble model loaded")
        
        # Load default model for backward compatibility
        if os.path.exists(DEFAULT_MODEL_PATH) and 'random_forest' not in self.models:
            self.models['default'] = joblib.load(DEFAULT_MODEL_PATH)
            self.explainers['default'] = shap.TreeExplainer(self.models['default'])
            print("✅ Default model loaded")
        
        # Load model comparison
        if os.path.exists(COMPARISON_PATH):
            with open(COMPARISON_PATH, 'r') as f:
                self.comparison = json.load(f)
            print("✅ Model comparison loaded")
        
        if not self.models:
            print("⚠️  No models found. Please train models first.")
    
    def predict_with_model(self, student_data, model_name='random_forest'):
        """
        Predict dropout risk using a specific model.
        
        Args:
            student_data (dict): Student features
            model_name (str): Model to use ('random_forest', 'gradient_boosting', 'neural_network', 'ensemble')
        
        Returns:
            tuple: (risk_score, risk_category, top_features)
        """
        if model_name not in self.models:
            # Fallback to default or first available model
            if 'default' in self.models:
                model_name = 'default'
            else:
                model_name = list(self.models.keys())[0]
        
        model = self.models[model_name]
        
        # Prepare features
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
        
        features_df = pd.DataFrame([student_data])[feature_columns]
        
        # Scale features for neural network
        if model_name == 'neural_network' and self.nn_scaler:
            features_scaled = self.nn_scaler.transform(features_df)
            prediction_proba = model.predict_proba(features_scaled)[:, 1]
        else:
            prediction_proba = model.predict_proba(features_df)[:, 1]
        
        risk_score = round(prediction_proba[0] * 100, 2)
        
        # Categorization
        if risk_score >= 70:
            risk_category = 'High'
        elif risk_score >= 40:
            risk_category = 'Medium'
        else:
            risk_category = 'Low'
        
        # Explainability (SHAP for tree-based models)
        top_features = []
        if model_name in self.explainers:
            explainer = self.explainers[model_name]
            shap_values = explainer.shap_values(features_df)
            
            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                shap_values_for_dropout = shap_values[1]
            else:
                shap_values_for_dropout = shap_values
            
            # Get feature importance
            feature_importance = pd.DataFrame(
                list(zip(feature_columns, shap_values_for_dropout[0])),
                columns=['feature', 'shap_value']
            )
            feature_importance['abs_shap'] = feature_importance['shap_value'].abs()
            feature_importance = feature_importance.sort_values(by='abs_shap', ascending=False)
            
            # Top 3 features
            for _, row in feature_importance.head(3).iterrows():
                top_features.append({
                    'name': row['feature'].replace('_', ' ').title(),
                    'value': student_data[row['feature']],
                    'shap_value': round(row['shap_value'], 4)
                })
        
        return risk_score, risk_category, top_features
    
    def predict_with_all_models(self, student_data):
        """
        Predict using all available models and return comparison.
        
        Args:
            student_data (dict): Student features
        
        Returns:
            dict: Predictions from all models
        """
        predictions = {}
        
        for model_name in self.models.keys():
            risk_score, risk_category, top_features = self.predict_with_model(student_data, model_name)
            predictions[model_name] = {
                'risk_score': risk_score,
                'risk_category': risk_category,
                'top_features': top_features
            }
        
        # Calculate average prediction
        if predictions:
            avg_score = sum(p['risk_score'] for p in predictions.values()) / len(predictions)
            if avg_score >= 70:
                avg_category = 'High'
            elif avg_score >= 40:
                avg_category = 'Medium'
            else:
                avg_category = 'Low'
            
            predictions['average'] = {
                'risk_score': round(avg_score, 2),
                'risk_category': avg_category,
                'top_features': []
            }
        
        return predictions
    
    def get_best_model(self):
        """Get the best performing model based on accuracy."""
        if not self.comparison:
            return 'random_forest'  # Default
        
        best_model = max(self.comparison.items(), key=lambda x: x[1]['accuracy'])
        return best_model[0].lower().replace(' ', '_')
    
    def get_model_metrics(self):
        """Get performance metrics for all models."""
        return self.comparison

# Initialize global model manager
model_manager = MLModelManager()

def predict_dropout_risk(student_data, model_name='random_forest'):
    """
    Main prediction function (backward compatible).
    
    Args:
        student_data (dict): Student features
        model_name (str): Model to use
    
    Returns:
        tuple: (risk_score, risk_category, top_features)
    """
    return model_manager.predict_with_model(student_data, model_name)

def predict_with_all_models(student_data):
    """
    Predict with all models and return comparison.
    
    Args:
        student_data (dict): Student features
    
    Returns:
        dict: Predictions from all models
    """
    return model_manager.predict_with_all_models(student_data)

def get_available_models():
    """Get list of available models."""
    return list(model_manager.models.keys())

def get_best_model():
    """Get the best performing model."""
    return model_manager.get_best_model()

def get_model_comparison():
    """Get model performance comparison."""
    return model_manager.get_model_metrics()
