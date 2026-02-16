"""
Prediction Service
Business logic for risk predictions using ML
"""
from app.repositories import StudentRepository, RiskPredictionRepository
from typing import Dict, Optional


class PredictionService:
    """Business logic for risk predictions"""
    
    def __init__(self):
        self.student_repo = StudentRepository()
        self.prediction_repo = RiskPredictionRepository()
    
    def get_latest_prediction(self, student_id: int):
        """Get latest prediction for student"""
        return self.prediction_repo.get_latest_for_student(student_id)
    
    def get_all_predictions(self, student_id: int):
        """Get all predictions for student"""
        return self.prediction_repo.get_all_for_student(student_id)
    
    def get_high_risk_predictions(self):
        """Get all high risk predictions"""
        return self.prediction_repo.get_high_risk_predictions()
    
    def create_prediction(self, student_id: int, prediction_data: Dict):
        """Create new prediction record"""
        return self.prediction_repo.create(
            student_id=student_id,
            **prediction_data
        )
    
    def prepare_features(self, student) -> Dict:
        """Convert student model to feature dict for ML"""
        return {
            'previous_qualification': student.previous_qualification,
            'age_at_enrollment': student.age_at_enrollment,
            'scholarship_holder': student.scholarship_holder,
            'debtor': student.debtor,
            'tuition_fees_up_to_date': student.tuition_fees_up_to_date,
            'curricular_units_1st_sem_grade': student.curricular_units_1st_sem_grade,
            'curricular_units_2nd_sem_grade': student.curricular_units_2nd_sem_grade,
            'gdp': student.gdp
        }
