"""
Behavioral Data Model
Tracks student behavioral and psychological indicators
"""
from extensions import db
from datetime import datetime


class BehavioralData(db.Model):
    """Student behavioral and psychological tracking"""
    __tablename__ = 'behavioral_data'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Attendance metrics
    attendance_rate = db.Column(db.Float, default=100.0)  # Percentage
    late_arrivals = db.Column(db.Integer, default=0)
    early_departures = db.Column(db.Integer, default=0)
    
    # Academic behavior
    assignment_completion_rate = db.Column(db.Float, default=100.0)
    submission_timeliness = db.Column(db.Float, default=100.0)  # % on time
    participation_score = db.Column(db.Float, default=0.0)  # 0-100
    
    # Social indicators
    peer_interaction_level = db.Column(db.String(20), default='Normal')  # Low, Normal, High
    mentor_meeting_frequency = db.Column(db.Integer, default=0)
    help_seeking_behavior = db.Column(db.Integer, default=0)  # Times asked for help
    
    # Psychological indicators
    stress_level = db.Column(db.Integer, default=5)  # 1-10 scale
    motivation_level = db.Column(db.Integer, default=5)  # 1-10 scale
    confidence_level = db.Column(db.Integer, default=5)  # 1-10 scale
    
    # Sentiment analysis (if available)
    sentiment_score = db.Column(db.Float)  # -1 to 1, negative to positive
    
    # Overall behavioral risk score
    behavioral_risk_score = db.Column(db.Float, default=0.0)  # 0-100
    
    def __repr__(self):
        return f'<BehavioralData {self.student_id}: {self.record_date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'record_date': self.record_date.isoformat(),
            'attendance_rate': self.attendance_rate,
            'late_arrivals': self.late_arrivals,
            'early_departures': self.early_departures,
            'assignment_completion_rate': self.assignment_completion_rate,
            'submission_timeliness': self.submission_timeliness,
            'participation_score': self.participation_score,
            'peer_interaction_level': self.peer_interaction_level,
            'mentor_meeting_frequency': self.mentor_meeting_frequency,
            'help_seeking_behavior': self.help_seeking_behavior,
            'stress_level': self.stress_level,
            'motivation_level': self.motivation_level,
            'confidence_level': self.confidence_level,
            'sentiment_score': self.sentiment_score,
            'behavioral_risk_score': self.behavioral_risk_score
        }
