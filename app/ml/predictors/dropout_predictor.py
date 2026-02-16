"""
Dropout Predictor
Main predictor for dropout risk prediction
"""
from app.ml.predictors.base_predictor import BasePredictor
from app.ml.config import CURRENT_MODEL_PATH
from typing import Dict


class DropoutPredictor(BasePredictor):
    """Predictor for dropout risk using the current best model"""
    
    _instance = None  # Singleton instance
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            super().__init__(CURRENT_MODEL_PATH)
            self.initialized = True
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def predict_with_explanation(self, features: Dict) -> Dict:
        """Predict with feature importance explanation"""
        # Get base prediction
        result = self.predict(features)
        
        # Get feature importance
        feature_importance = self.get_feature_importance()
        
        # Get top 3 features for this student
        top_features = []
        for feat in feature_importance[:3]:
            feat_name = feat['name']
            feat_value = features.get(feat_name, 0)
            top_features.append({
                'name': feat_name,
                'value': float(feat_value),
                'importance': feat['importance']
            })
        
        result['top_features'] = top_features
        result['feature_importance'] = feature_importance
        
        return result
