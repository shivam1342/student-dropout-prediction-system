"""
Model Trainer
Train and evaluate ML models
"""
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, confusion_matrix
import joblib
import json
import os
from app.ml.config import *
from app.ml.pipeline.data_loader import DataLoader


class ModelTrainer:
    """Train and evaluate ML models"""
    
    def __init__(self):
        self.models = {}
        self.results = {}
    
    def train_random_forest(self, X_train, y_train):
        """Train Random Forest model"""
        print("\n🌲 Training Random Forest...")
        model = RandomForestClassifier(**RANDOM_FOREST_PARAMS)
        model.fit(X_train, y_train)
        self.models['random_forest'] = model
        print("✅ Random Forest trained")
        return model
    
    def train_gradient_boosting(self, X_train, y_train):
        """Train Gradient Boosting model"""
        print("\n📈 Training Gradient Boosting...")
        model = GradientBoostingClassifier(**GRADIENT_BOOST_PARAMS)
        model.fit(X_train, y_train)
        self.models['gradient_boosting'] = model
        print("✅ Gradient Boosting trained")
        return model
    
    def train_neural_network(self, X_train, y_train):
        """Train Neural Network model"""
        print("\n🧠 Training Neural Network...")
        model = MLPClassifier(**NEURAL_NET_PARAMS)
        model.fit(X_train, y_train)
        self.models['neural_network'] = model
        print("✅ Neural Network trained")
        return model
    
    def evaluate_model(self, model, X_test, y_test, model_name: str):
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        result = {
            'model_name': model_name,
            'accuracy': float(accuracy),
            'roc_auc': float(roc_auc),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        self.results[model_name] = result
        
        print(f"\n📊 {model_name} Results:")
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   ROC-AUC: {roc_auc:.4f}")
        
        return result
    
    def train_all_models(self):
        """Train all models and select best one"""
        print("=" * 60)
        print("🚀 TRAINING ML MODELS")
        print("=" * 60)
        
        # Load data
        X_train, X_test, y_train, y_test = DataLoader.load_and_prepare()
        
        # Train models
        rf_model = self.train_random_forest(X_train, y_train)
        gb_model = self.train_gradient_boosting(X_train, y_train)
        nn_model = self.train_neural_network(X_train, y_train)
        
        # Evaluate models
        rf_result = self.evaluate_model(rf_model, X_test, y_test, 'Random Forest')
        gb_result = self.evaluate_model(gb_model, X_test, y_test, 'Gradient Boosting')
        nn_result = self.evaluate_model(nn_model, X_test, y_test, 'Neural Network')
        
        # Save models
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(rf_model, RANDOM_FOREST_PATH)
        joblib.dump(gb_model, GRADIENT_BOOST_PATH)
        joblib.dump(nn_model, NEURAL_NET_PATH)
        
        # Select best model based on accuracy
        best_model_name = max(self.results, key=lambda k: self.results[k]['accuracy'])
        best_model = self.models[best_model_name]
        
        # Save best model as current model
        joblib.dump(best_model, CURRENT_MODEL_PATH)
        
        # Save comparison results
        comparison_path = os.path.join(MODEL_DIR, 'model_comparison.json')
        with open(comparison_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("\n" + "=" * 60)
        print(f"✅ BEST MODEL: {best_model_name}")
        print(f"   Accuracy: {self.results[best_model_name]['accuracy']:.4f}")
        print(f"   Saved to: {CURRENT_MODEL_PATH}")
        print("=" * 60)
        
        return best_model, self.results


if __name__ == '__main__':
    trainer = ModelTrainer()
    trainer.train_all_models()
