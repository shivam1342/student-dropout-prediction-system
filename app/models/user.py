"""
User Model
Represents system users with role-based access (student, teacher, admin, counselor)
"""
from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """User authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # 'student', 'teacher', 'admin', 'counselor'
    full_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))  # For teachers/counselors/admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    profile_picture_url = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    
    # Relationships
    student_profile = db.relationship('Student', backref='user_account', uselist=False, foreign_keys='Student.user_id')
    teacher_profile = db.relationship('Teacher', backref='user_account', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_teacher(self):
        return self.role == 'teacher'
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_counselor(self):
        return self.role == 'counselor'
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'department': self.department,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
