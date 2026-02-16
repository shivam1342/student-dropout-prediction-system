"""
Student Service
Business logic for student operations
"""
from app.repositories import (
    StudentRepository,
    AlertRepository,
    InterventionRepository,
    RiskPredictionRepository,
    GamificationRepository
)
from typing import Dict, List, Optional


class StudentService:
    """Business logic for student operations"""
    
    def __init__(self):
        self.student_repo = StudentRepository()
        self.alert_repo = AlertRepository()
        self.intervention_repo = InterventionRepository()
        self.prediction_repo = RiskPredictionRepository()
        self.gamification_repo = GamificationRepository()
    
    def get_all_students(self) -> List:
        """Get all students"""
        return self.student_repo.get_all()
    
    def get_student_by_id(self, student_id: int):
        """Get student by ID"""
        return self.student_repo.get_by_id(student_id)
    
    def get_student_profile(self, student_id: int) -> Optional[Dict]:
        """Get complete student profile with related data"""
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return None
        
        return {
            'student': student,
            'alerts': self.alert_repo.get_by_student(student_id),
            'interventions': self.intervention_repo.get_by_student(student_id),
            'latest_prediction': self.prediction_repo.get_latest_for_student(student_id),
            'gamification': self.gamification_repo.get_by_student(student_id),
        }
    
    def create_student(self, data: Dict):
        """Create new student"""
        return self.student_repo.create(**data)
    
    def update_student(self, student_id: int, data: Dict):
        """Update student"""
        return self.student_repo.update(student_id, **data)
    
    def delete_student(self, student_id: int):
        """Delete student"""
        return self.student_repo.delete(student_id)
    
    def search_students(self, query: str):
        """Search students"""
        return self.student_repo.search(query)
    
    def get_high_risk_students(self, limit: int = 10):
        """Get high risk students"""
        return self.student_repo.get_high_risk_students(limit)
