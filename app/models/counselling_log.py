"""
Counselling Log Model
Represents counselling interventions and recommendations
"""
from app.extensions import db
from datetime import datetime


class CounsellingLog(db.Model):
    """Counselling interventions and recommendations"""
    __tablename__ = 'counselling_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    log_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Counselling details
    intervention_type = db.Column(db.String(50), nullable=False)  # Academic, Financial, Engagement
    recommendation = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, In Progress, Completed
    counsellor_notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<CounsellingLog {self.student_id}: {self.intervention_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'log_date': self.log_date.isoformat(),
            'intervention_type': self.intervention_type,
            'recommendation': self.recommendation,
            'status': self.status,
            'counsellor_notes': self.counsellor_notes
        }
