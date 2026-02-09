"""
Alert Model
System-generated alerts for at-risk students
"""
from app.extensions import db
from datetime import datetime


class Alert(db.Model):
    """Real-time alerts for at-risk students"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Alert details
    alert_type = db.Column(db.String(50), nullable=False)  # Academic, Behavioral, Financial, Psychological
    severity = db.Column(db.String(20), nullable=False)  # Low, Medium, High, Critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Triggering factors
    trigger_factors = db.Column(db.JSON)  # Factors that triggered the alert
    recommended_actions = db.Column(db.JSON)  # Suggested intervention steps
    
    # Status tracking
    status = db.Column(db.String(20), default='Active')  # Active, Acknowledged, Resolved, Dismissed
    acknowledged_at = db.Column(db.DateTime)
    acknowledged_by = db.Column(db.String(100))  # Mentor/Admin name
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.String(100))  # Who resolved it
    
    # Action taken
    action_taken = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Alert {self.student_id}: {self.alert_type} - {self.severity}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'created_at': self.created_at.isoformat(),
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'trigger_factors': self.trigger_factors,
            'recommended_actions': self.recommended_actions,
            'status': self.status,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'acknowledged_by': self.acknowledged_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'action_taken': self.action_taken,
            'notes': self.notes
        }
