"""
Authentication Routes
Handles login, logout, registration, and role-based dashboards
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from app.controllers.auth_controller import AuthController
from app.models import Student, Teacher, TeacherStudentAssignment
from app.extensions import db
from datetime import datetime


auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        # Redirect already logged-in users to their dashboard
        if current_user.is_teacher:
            return redirect(url_for('auth_bp.teacher_dashboard'))
        elif current_user.is_student:
            return redirect(url_for('auth_bp.student_dashboard'))
        else:
            return redirect(url_for('main_bp.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'
        
        success, redirect_route, message = AuthController.login(username, password, remember)
        
        if success:
            flash(message, 'success')
            return redirect(url_for(redirect_route))
        else:
            flash(message, 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout current user"""
    success, redirect_route, message = AuthController.logout()
    flash(message, 'success')
    return redirect(url_for(redirect_route))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for('main_bp.dashboard'))

    selected_role = request.args.get('role', 'student')
    if selected_role not in ['student', 'teacher']:
        selected_role = 'student'
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'student')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html', selected_role=selected_role)
        
        # Additional fields based on role
        kwargs = {}
        if role == 'teacher':
            kwargs['department'] = request.form.get('department')
            kwargs['employee_id'] = request.form.get('employee_id')
        
        success, user, message = AuthController.register_user(
            username, email, password, full_name, role, **kwargs
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth_bp.login'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/register.html', selected_role=selected_role)


@auth_bp.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    """Teacher dashboard - view assigned students and their risk status"""
    if not current_user.is_teacher:
        flash('Access denied. Teachers only.', 'danger')
        return redirect(url_for('main_bp.dashboard'))
    
    data = AuthController.get_user_dashboard_data(current_user)
    
    return render_template(
        'auth/teacher_dashboard.html',
        teacher=current_user.teacher_profile,
        **data
    )


@auth_bp.route('/teacher/manage-students', methods=['GET', 'POST'])
@login_required
def teacher_manage_students():
    """Teacher page to assign/unassign students"""
    if not current_user.is_teacher:
        flash('Access denied. Teachers only.', 'danger')
        return redirect(url_for('main_bp.dashboard'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'assign':
            student_id = request.form.get('student_id')
            course_name = request.form.get('course_name')
            semester = request.form.get('semester', 'Spring 2026')
            academic_year = request.form.get('academic_year', '2025-2026')
            
            # Check if assignment already exists
            existing = TeacherStudentAssignment.query.filter_by(
                teacher_id=current_user.teacher_profile.id,
                student_id=student_id,
                course_name=course_name,
                semester=semester
            ).first()
            
            if existing:
                if existing.is_active:
                    flash('This student is already assigned to you for this course.', 'info')
                else:
                    existing.is_active = True
                    db.session.commit()
                    flash('Student assignment reactivated successfully!', 'success')
            else:
                # Create new assignment
                assignment = TeacherStudentAssignment(
                    teacher_id=current_user.teacher_profile.id,
                    student_id=student_id,
                    course_name=course_name,
                    semester=semester,
                    academic_year=academic_year,
                    assigned_date=datetime.utcnow(),
                    is_active=True
                )
                db.session.add(assignment)
                db.session.commit()
                flash('Student assigned successfully!', 'success')
        
        elif action == 'unassign':
            assignment_id = request.form.get('assignment_id')
            assignment = TeacherStudentAssignment.query.get_or_404(assignment_id)
            
            # Verify this is the teacher's assignment
            if assignment.teacher_id != current_user.teacher_profile.id:
                flash('You can only unassign your own students.', 'danger')
            else:
                assignment.is_active = False
                db.session.commit()    
                flash('Student unassigned successfully!', 'success')
        
        return redirect(url_for('auth_bp.teacher_manage_students'))
    
    # GET request - show management page
    # Get all students for assignment dropdown
    all_students = Student.query.all()
    
    # Get current assignments
    assignments = TeacherStudentAssignment.query.filter_by(
        teacher_id=current_user.teacher_profile.id,
        is_active=True
    ).all()
    
    # Get students not yet assigned
    assigned_student_ids = [a.student_id for a in assignments]
    unassigned_students = [s for s in all_students if s.id not in assigned_student_ids]
    
    return render_template(
        'auth/teacher_manage_students.html',
        assignments=assignments,
        unassigned_students=unassigned_students,
        all_students=all_students
    )


@auth_bp.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard - view own risk status, alerts, interventions"""
    if not current_user.is_student:
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('main_bp.dashboard'))
    
    data = AuthController.get_user_dashboard_data(current_user)
    
    return render_template(
        'auth/student_dashboard.html',
        **data
    )


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)
