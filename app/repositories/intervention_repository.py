"""
Intervention Repository
Database operations for Intervention model
"""
from app.repositories.base_repository import BaseRepository
from app.models import Intervention
from sqlalchemy import desc
from datetime import datetime


class InterventionRepository(BaseRepository):
    """Repository for intervention data access"""
    
    def __init__(self):
        super().__init__(Intervention)
    
    def get_upcoming(self, limit: int = 5):
        """Get upcoming interventions"""
        return (
            Intervention.query
            .filter(
                Intervention.scheduled_date >= datetime.utcnow(),
                Intervention.status == 'Scheduled'
            )
            .order_by(Intervention.scheduled_date)
            .limit(limit)
            .all()
        )
    
    def get_by_student(self, student_id: int):
        """Get all interventions for a student"""
        return (
            Intervention.query
            .filter_by(student_id=student_id)
            .order_by(desc(Intervention.scheduled_date))
            .all()
        )
    
    def get_by_status(self, status: str):
        """Get interventions by status"""
        return (
            Intervention.query
            .filter_by(status=status)
            .order_by(desc(Intervention.scheduled_date))
            .all()
        )
