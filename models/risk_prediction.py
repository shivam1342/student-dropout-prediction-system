"""
Risk Prediction Model
Represents dropout risk predictions for students
"""
from extensions import db
from datetime import datetime


class RiskPrediction(db.Model):
    """Dropout risk predictions for students"""
    __tablename__ = 'risk_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Prediction results
    risk_score = db.Column(db.Float, nullable=False)  # 0-100%
    risk_category = db.Column(db.String(20), nullable=False)  # Low, Medium, High
    dropout_probability = db.Column(db.Float)  # 0-1 probability for dropout
    prediction_result = db.Column(db.String(20))  # Dropout, Graduate, Enrolled
    
    # Feature importance (top 3 contributing factors)
    top_feature_1 = db.Column(db.String(50))
    top_feature_1_value = db.Column(db.Float)
    top_feature_2 = db.Column(db.String(50))
    top_feature_2_value = db.Column(db.Float)
    top_feature_3 = db.Column(db.String(50))
    top_feature_3_value = db.Column(db.Float)
    top_risk_factors = db.Column(db.JSON)  # JSON array of all risk factors
    
    def __repr__(self):
        return f'<RiskPrediction {self.student_id}: {self.risk_score}%>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'prediction_date': self.prediction_date.isoformat(),
            'risk_score': self.risk_score,
            'risk_category': self.risk_category,
            'top_features': [
                {'name': self.top_feature_1, 'value': self.top_feature_1_value},
                {'name': self.top_feature_2, 'value': self.top_feature_2_value},
                {'name': self.top_feature_3, 'value': self.top_feature_3_value}
            ]
        }
