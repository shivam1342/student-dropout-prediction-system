"""
Intervention Service
Business logic for intervention management
"""
from app.repositories import InterventionRepository, StudentRepository, AlertRepository
from typing import Dict, List
from datetime import datetime


class InterventionService:
    """Business logic for intervention operations"""
    
    def __init__(self):
        self.intervention_repo = InterventionRepository()
        self.student_repo = StudentRepository()
        self.alert_repo = AlertRepository()
    
    def get_all_interventions(self):
        """Get all interventions"""
        return self.intervention_repo.get_all()
    
    def get_intervention_by_id(self, intervention_id: int):
        """Get intervention by ID"""
        return self.intervention_repo.get_by_id(intervention_id)
    
    def get_interventions_by_student(self, student_id: int):
        """Get interventions for a student"""
        return self.intervention_repo.get_by_student(student_id)
    
    def get_upcoming_interventions(self, limit: int = 5):
        """Get upcoming interventions"""
        return self.intervention_repo.get_upcoming(limit)
    
    def get_interventions_by_status(self, status: str):
        """Get interventions by status"""
        return self.intervention_repo.get_by_status(status)
    
    def create_intervention(self, data: Dict):
        """Create new intervention"""
        return self.intervention_repo.create(**data)
    
    def update_intervention(self, intervention_id: int, data: Dict):
        """Update intervention"""
        return self.intervention_repo.update(intervention_id, **data)
    
    def complete_intervention(self, intervention_id: int, outcome_notes: str = None):
        """Mark interventiont as completed"""
        return self.intervention_repo.update(
            intervention_id,
            status='Completed',
            completion_date=datetime.utcnow(),
            outcome_notes=outcome_notes
        )
    
    def cancel_intervention(self, intervention_id: int, reason: str = None):
        """Cancel intervention"""
        return self.intervention_repo.update(
            intervention_id,
            status='Cancelled',
            outcome_notes=reason
        )
