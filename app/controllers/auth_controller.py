"""
Authentication Controller
Handles user authentication, login, logout, and registration
"""
from flask import flash, redirect, url_for
from flask_login import login_user, logout_user, current_user
from app.models import User, Student, Teacher
from app.extensions import db
from datetime import datetime


class AuthController:
    """Handles authentication logic"""
    
    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticate user by username/email and password
        Returns: (success:bool, user:User|None, message:str)
        """
        # Try to find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return False, None, "Invalid username or email"
        
        if not user.is_active:
            return False, None, "Account is deactivated. Contact administrator."
        
        if not user.check_password(password):
            return False, None, "Invalid password"
        
        # Update last login
        user.update_last_login()
        
        return True, user, "Login successful"
    
    @staticmethod
    def login(username, password, remember=False):
        """
        Login user and redirect to appropriate dashboard
        Returns: (success:bool, redirect_route:str, message:str)
        """
        success, user, message = AuthController.authenticate_user(username, password)
        
        if not success:
            return False, None, message
        
        login_user(user, remember=remember)
        
        # Redirect based on role
        if user.is_teacher:
            redirect_route = 'auth_bp.teacher_dashboard'
        elif user.is_student:
            redirect_route = 'auth_bp.student_dashboard'
        elif user.is_admin:
            redirect_route = 'main_bp.dashboard'  # Admin sees main dashboard
        elif user.is_counselor:
            redirect_route = 'counselling_bp.counselling'
        else:
            redirect_route = 'main_bp.dashboard'
        
        return True, redirect_route, f"Welcome back, {user.full_name}!"
    
    @staticmethod
    def logout():
        """Logout current user"""
        logout_user()
        return True, 'auth_bp.login', "You have been logged out successfully."
    
    @staticmethod
    def register_user(username, email, password, full_name, role='student', **kwargs):
        """
        Register a new user
        Returns: (success:bool, user:User|None, message:str)
        """
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return False, None, "Username already exists"
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return False, None, "Email already registered"
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            department=kwargs.get('department'),
            phone=kwargs.get('phone')
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.flush()  # Get user.id without committing
            
            # Create role-specific profile
            if role == 'student':
                student = Student(
                    user_id=user.id,
                    name=full_name,
                    email=email,
                    age_at_enrollment=kwargs.get('age', 18),
                    previous_qualification=kwargs.get('previous_qualification', 1)
                )
                db.session.add(student)
            
            elif role == 'teacher':
                teacher = Teacher(
                    user_id=user.id,
                    employee_id=kwargs.get('employee_id'),
                    department=kwargs.get('department', 'General'),
                    subjects=kwargs.get('subjects', '[]')
                )
                db.session.add(teacher)
            
            db.session.commit()
            return True, user, "Registration successful!"
        
        except Exception as e:
            db.session.rollback()
            return False, None, f"Registration failed: {str(e)}"
    
    @staticmethod
    def get_user_dashboard_data(user):
        """Get dashboard data based on user role"""
        if user.is_teacher:
            return AuthController._get_teacher_dashboard_data(user)
        elif user.is_student:
            return AuthController._get_student_dashboard_data(user)
        return {}
    
    @staticmethod
    def _get_teacher_dashboard_data(user):
        """Get teacher-specific dashboard data"""
        if not user.teacher_profile:
            return {}
        
        from app.models import TeacherStudentAssignment, RiskPrediction
        
        # Get assigned students
        assignments = TeacherStudentAssignment.query.filter_by(
            teacher_id=user.teacher_profile.id,
            is_active=True
        ).all()
        
        students = [assignment.student for assignment in assignments]
        
        # Get high-risk students
        high_risk_students = []
        for student in students:
            latest_prediction = RiskPrediction.query.filter_by(
                student_id=student.id
            ).order_by(RiskPrediction.prediction_date.desc()).first()
            
            if latest_prediction and latest_prediction.risk_category == 'High':
                high_risk_students.append({
                    'student': student,
                    'prediction': latest_prediction
                })
        
        return {
            'total_students': len(students),
            'students': students,
            'high_risk_students': high_risk_students,
            'high_risk_count': len(high_risk_students),
            'assignments': assignments
        }
    
    @staticmethod
    def _get_student_dashboard_data(user):
        """Get student-specific dashboard data"""
        if not user.student_profile:
            return {}
        
        from app.models import RiskPrediction, Alert, Intervention, GamificationProfile
        
        student = user.student_profile
        
        # Get latest prediction
        latest_prediction = RiskPrediction.query.filter_by(
            student_id=student.id
        ).order_by(RiskPrediction.prediction_date.desc()).first()
        
        # Get active alerts
        active_alerts = Alert.query.filter_by(
            student_id=student.id,
            status='pending'
        ).all()
        
        # Get active interventions
        active_interventions = Intervention.query.filter_by(
            student_id=student.id,
            status='in_progress'
        ).all()
        
        # Get gamification profile
        gamification = GamificationProfile.query.filter_by(
            student_id=student.id
        ).first()
        
        return {
            'student': student,
            'latest_prediction': latest_prediction,
            'active_alerts': active_alerts,
            'active_interventions': active_interventions,
            'gamification': gamification,
            'alert_count': len(active_alerts),
            'intervention_count': len(active_interventions)
        }
