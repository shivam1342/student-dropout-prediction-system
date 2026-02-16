"""
Alert Repository
Database operations for Alert model
"""
from app.repositories.base_repository import BaseRepository
from app.models import Alert
from sqlalchemy import desc


class AlertRepository(BaseRepository):
    """Repository for alert data access"""
    
    def __init__(self):
        super().__init__(Alert)
    
    def get_active_alerts(self):
        """Get all active alerts"""
        return (
            Alert.query
            .filter_by(status='Active')
            .order_by(desc(Alert.created_at))
            .all()
        )
    
    def get_by_student(self, student_id: int):
        """Get all alerts for a student"""
        return (
            Alert.query
            .filter_by(student_id=student_id)
            .order_by(desc(Alert.created_at))
            .all()
        )
    
    def get_by_severity(self, severity: str):
        """Get alerts by severity level"""
        return (
            Alert.query
            .filter_by(severity=severity, status='Active')
            .order_by(desc(Alert.created_at))
            .all()
        )
    
    def get_critical_alerts(self):
        """Get all critical alerts"""
        return self.get_by_severity('Critical')
