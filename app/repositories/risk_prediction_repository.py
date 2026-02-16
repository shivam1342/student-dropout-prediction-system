"""
Risk Prediction Repository
Database operations for RiskPrediction model
"""
from app.repositories.base_repository import BaseRepository
from app.models import RiskPrediction
from sqlalchemy import desc


class RiskPredictionRepository(BaseRepository):
    """Repository for risk prediction data access"""
    
    def __init__(self):
        super().__init__(RiskPrediction)
    
    def get_latest_for_student(self, student_id: int):
        """Get latest prediction for a student"""
        return (
            RiskPrediction.query
            .filter_by(student_id=student_id)
            .order_by(desc(RiskPrediction.prediction_date))
            .first()
        )
    
    def get_all_for_student(self, student_id: int):
        """Get all predictions for a student"""
        return (
            RiskPrediction.query
            .filter_by(student_id=student_id)
            .order_by(desc(RiskPrediction.prediction_date))
            .all()
        )
    
    def get_high_risk_predictions(self):
        """Get all high risk predictions"""
        return (
            RiskPrediction.query
            .filter(RiskPrediction.risk_category.in_(['High', 'Critical']))
            .order_by(desc(RiskPrediction.risk_score))
            .all()
        )
