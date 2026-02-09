"""
Student Model
Represents student information and academic data
"""
from app.extensions import db
from datetime import datetime


class Student(db.Model):
    """Student information and academic data"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Demographic and Academic Data (from dataset)
    age_at_enrollment = db.Column(db.Integer, nullable=False)
    previous_qualification = db.Column(db.Integer, default=1)
    
    # Financial & Scholarship Status
    scholarship_holder = db.Column(db.Boolean, default=False)
    debtor = db.Column(db.Boolean, default=False)
    tuition_fees_up_to_date = db.Column(db.Boolean, default=True)
    
    # Academic Performance
    curricular_units_1st_sem_grade = db.Column(db.Float, default=0.0)
    curricular_units_2nd_sem_grade = db.Column(db.Float, default=0.0)
    
    # Economic Context
    gdp = db.Column(db.Float, default=0.0)
    
    # Relationships
    predictions = db.relationship('RiskPrediction', backref='student', lazy=True, cascade='all, delete-orphan')
    counselling_logs = db.relationship('CounsellingLog', backref='student', lazy=True, cascade='all, delete-orphan')
    lms_activities = db.relationship('LMSActivity', backref='student', lazy=True, cascade='all, delete-orphan')
    behavioral_data = db.relationship('BehavioralData', backref='student', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='student', lazy=True, cascade='all, delete-orphan')
    interventions = db.relationship('Intervention', backref='student', lazy=True, cascade='all, delete-orphan')
    gamification_profile = db.relationship('GamificationProfile', backref='student', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.name}>'
    
    def to_dict(self):
        """Convert student to dictionary for prediction"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age_at_enrollment': self.age_at_enrollment,
            'previous_qualification': self.previous_qualification,
            'scholarship_holder': 1 if self.scholarship_holder else 0,
            'debtor': 1 if self.debtor else 0,
            'tuition_fees_up_to_date': 1 if self.tuition_fees_up_to_date else 0,
            'curricular_units_1st_sem_grade': self.curricular_units_1st_sem_grade,
            'curricular_units_2nd_sem_grade': self.curricular_units_2nd_sem_grade,
            'gdp': self.gdp
        }
