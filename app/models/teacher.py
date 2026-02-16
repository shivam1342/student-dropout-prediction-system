"""
Teacher Model
Represents teacher profiles with course and student management
"""
from app.extensions import db
from datetime import datetime
import json


class Teacher(db.Model):
    """Teacher profile and information"""
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    employee_id = db.Column(db.String(50), unique=True)
    department = db.Column(db.String(100), nullable=False)
    subjects = db.Column(db.Text)  # JSON array: ["Math", "Physics"]
    office_location = db.Column(db.String(100))
    office_hours = db.Column(db.Text)  # JSON: {"Monday": "10:00-12:00", ...}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student_assignments = db.relationship('TeacherStudentAssignment', backref='teacher', lazy=True, cascade='all, delete-orphan')
    
    def set_subjects(self, subject_list):
        """Set subjects as JSON"""
        self.subjects = json.dumps(subject_list)
    
    def get_subjects(self):
        """Get subjects as Python list"""
        return json.loads(self.subjects) if self.subjects else []
    
    def set_office_hours(self, hours_dict):
        """Set office hours as JSON"""
        self.office_hours = json.dumps(hours_dict)
    
    def get_office_hours(self):
        """Get office hours as Python dict"""
        return json.loads(self.office_hours) if self.office_hours else {}
    
    def __repr__(self):
        return f'<Teacher {self.employee_id}>'
    
    def to_dict(self):
        """Convert teacher to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'department': self.department,
            'subjects': self.get_subjects(),
            'office_location': self.office_location,
            'office_hours': self.get_office_hours(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TeacherStudentAssignment(db.Model):
    """Many-to-many relationship between teachers and students"""
    __tablename__ = 'teacher_student_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    course_name = db.Column(db.String(100))
    semester = db.Column(db.String(20))  # e.g., "Fall 2026"
    academic_year = db.Column(db.String(20))  # e.g., "2025-2026"
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Relationships
    student = db.relationship('Student', backref='teacher_assignments')
    
    __table_args__ = (
        db.UniqueConstraint('teacher_id', 'student_id', 'course_name', 'semester', name='unique_assignment'),
    )
    
    def __repr__(self):
        return f'<Assignment T:{self.teacher_id} S:{self.student_id}>'
    
    def to_dict(self):
        """Convert assignment to dictionary"""
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id,
            'course_name': self.course_name,
            'semester': self.semester,
            'academic_year': self.academic_year,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'is_active': self.is_active
        }
