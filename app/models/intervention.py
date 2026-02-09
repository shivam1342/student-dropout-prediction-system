"""
Intervention Model
Tracks interventions and support provided to students
"""
from app.extensions import db
from datetime import datetime


class Intervention(db.Model):
    """Student intervention tracking"""
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.id'), nullable=True)  # Link to triggering alert
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Intervention details
    intervention_type = db.Column(db.String(50), nullable=False)  # Academic, Financial, Psychological, Social, Behavioral
    priority = db.Column(db.String(20), default='Medium')  # Critical, High, Medium, Low
    category = db.Column(db.String(50))  # Tutoring, Counselling, Financial Aid, Mentoring, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Scheduling
    scheduled_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    
    # Personnel involved
    assigned_to = db.Column(db.String(100))  # Counsellor/Mentor name
    participants = db.Column(db.JSON)  # List of people involved
    
    # Status and outcome
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, In Progress, Completed, Cancelled
    outcome = db.Column(db.Text)
    effectiveness_rating = db.Column(db.Integer)  # 1-5 rating
    notes = db.Column(db.Text)  # General notes about the intervention
    
    # Follow-up
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.DateTime)
    follow_up_notes = db.Column(db.Text)
    
    # Resources provided
    resources_provided = db.Column(db.JSON)  # List of resources/materials
    
    def __repr__(self):
        return f'<Intervention {self.student_id}: {self.intervention_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'alert_id': self.alert_id,
            'created_at': self.created_at.isoformat(),
            'intervention_type': self.intervention_type,
            'priority': self.priority,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'assigned_to': self.assigned_to,
            'participants': self.participants,
            'status': self.status,
            'outcome': self.outcome,
            'effectiveness_rating': self.effectiveness_rating,
            'notes': self.notes,
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'follow_up_notes': self.follow_up_notes,
            'resources_provided': self.resources_provided
        }
