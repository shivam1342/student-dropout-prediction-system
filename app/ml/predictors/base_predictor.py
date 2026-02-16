"""
Base Predictor
Base class for all ML predictors
"""
import joblib
import pandas as pd
import numpy as np
from typing import Dict, List
from app.ml.config import FEATURE_COLUMNS, get_risk_category


class BasePredictor:
    """Base class for ML predictors"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load model from disk"""
        try:
            self.model = joblib.load(self.model_path)
            print(f"✅ Model loaded: {self.model_path}")
        except FileNotFoundError:
            print(f"⚠️ Model not found: {self.model_path}")
            self.model = None
    
    def prepare_features(self, features: Dict) -> pd.DataFrame:
        """Convert feature dict to DataFrame"""
        # Ensure all required features are present
        feature_values = []
        for col in FEATURE_COLUMNS:
            if col not in features:
                raise ValueError(f"Missing feature: {col}")
            feature_values.append(features[col])
        
        # Create DataFrame with proper column names
        df = pd.DataFrame([feature_values], columns=FEATURE_COLUMNS)
        return df
    
    def predict(self, features: Dict) -> Dict:
        """Make prediction"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        # Prepare features
        X = self.prepare_features(features)
        
        # Get prediction probability
        pred_proba = self.model.predict_proba(X)[0]
        dropout_prob = pred_proba[1]  # Probability of class 1 (Dropout)
        
        # Convert to risk score (0-100)
        risk_score = float(dropout_prob * 100)
        risk_category = get_risk_category(risk_score)
        
        return {
            'risk_score': risk_score,
            'risk_category': risk_category,
            'dropout_probability': float(dropout_prob),
            'confidence': float(max(pred_proba))
        }
    
    def get_feature_importance(self) -> List[Dict]:
        """Get feature importance from model"""
        if self.model is None or not hasattr(self.model, 'feature_importances_'):
            return []
        
        importances = self.model.feature_importances_
        features = []
        for i, importance in enumerate(importances):
            features.append({
                'name': FEATURE_COLUMNS[i],
                'importance': float(importance)
            })
        
        # Sort by importance
        features.sort(key=lambda x: x['importance'], reverse=True)
        return features
