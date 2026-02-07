"""
Database Models
Defines Student, RiskPrediction, and CounsellingLog tables
"""
from extensions import db
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
    
    # Economic Context (example)
    gdp = db.Column(db.Float, default=0.0)
    
    # Relationships
    predictions = db.relationship('RiskPrediction', backref='student', lazy=True, cascade='all, delete-orphan')
    counselling_logs = db.relationship('CounsellingLog', backref='student', lazy=True, cascade='all, delete-orphan')
    
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

class RiskPrediction(db.Model):
    """Dropout risk predictions for students"""
    __tablename__ = 'risk_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Prediction results
    risk_score = db.Column(db.Float, nullable=False)  # 0-100%
    risk_category = db.Column(db.String(20), nullable=False)  # Low, Medium, High
    
    # Feature importance (top 3 contributing factors)
    top_feature_1 = db.Column(db.String(50))
    top_feature_1_value = db.Column(db.Float)
    top_feature_2 = db.Column(db.String(50))
    top_feature_2_value = db.Column(db.Float)
    top_feature_3 = db.Column(db.String(50))
    top_feature_3_value = db.Column(db.Float)
    
    def __repr__(self):
        return f'<RiskPrediction {self.student_id}: {self.risk_score}%>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'prediction_date': self.prediction_date.isoformat(),
            'risk_score': self.risk_score,
            'risk_category': self.risk_category,
            'top_features': [
                {'name': self.top_feature_1, 'value': self.top_feature_1_value},
                {'name': self.top_feature_2, 'value': self.top_feature_2_value},
                {'name': self.top_feature_3, 'value': self.top_feature_3_value}
            ]
        }

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
