"""
Authentication Routes
Handles login, logout, registration, and role-based dashboards
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from app.controllers.auth_controller import AuthController


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
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard'))
    
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
            return render_template('/register.html')
        
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
    
    return render_template('auth/register.html')


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
