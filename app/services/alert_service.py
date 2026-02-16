"""
Alert Service
Business logic for alert management
"""
from app.repositories import AlertRepository, StudentRepository
from typing import Dict, List, Optional


class AlertService:
    """Business logic for alert operations"""
    
    def __init__(self):
        self.alert_repo = AlertRepository()
        self.student_repo = StudentRepository()
    
    def get_all_active_alerts(self):
        """Get all active alerts"""
        return self.alert_repo.get_active_alerts()
    
    def get_alerts_by_student(self, student_id: int):
        """Get alerts for a student"""
        return self.alert_repo.get_by_student(student_id)
    
    def get_alerts_by_severity(self, severity: str):
        """Get alerts by severity"""
        return self.alert_repo.get_by_severity(severity)
    
    def get_critical_alerts(self):
        """Get critical alerts"""
        return self.alert_repo.get_critical_alerts()
    
    def create_alert(self, data: Dict):
        """Create new alert"""
        return self.alert_repo.create(**data)
    
    def update_alert(self, alert_id: int, data: Dict):
        """Update alert"""
        return self.alert_repo.update(alert_id, **data)
    
    def acknowledge_alert(self, alert_id: int, acknowledged_by: str):
        """Acknowledge an alert"""
        return self.alert_repo.update(
            alert_id,
            status='Acknowledged',
            acknowledged_by=acknowledged_by
        )
    
    def resolve_alert(self, alert_id: int, resolution_notes: str = None):
        """Resolve an alert"""
        return self.alert_repo.update(
            alert_id,
            status='Resolved',
            resolution_notes=resolution_notes
        )
