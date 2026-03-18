"""
Student Routes
Handles CRUD for students and viewing profiles.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.controllers import data_controller
from app.controllers.alert_controller import AlertController
from app.models import Student, Alert, Intervention, LMSActivity, BehavioralData, GamificationProfile, Teacher
from app.controllers.gamification_controller import GamificationController
from app.extensions import db
from sqlalchemy import desc
from datetime import datetime

student_bp = Blueprint('student_bp', __name__)


def _normalize_event_date(value):
    """Return a datetime from supported date inputs, or None when invalid."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return None
    return None


def _format_event_date(value):
    """Return a timeline-friendly date string from mixed input types."""
    normalized = _normalize_event_date(value)
    return normalized.strftime('%Y-%m-%d %H:%M') if normalized else 'N/A'


def _teacher_has_student_access(user, student_id):
    """Return True when teacher is actively assigned to the student."""
    if not user.is_teacher or not user.teacher_profile:
        return False

    return TeacherStudentAssignment.query.filter_by(
        teacher_id=user.teacher_profile.id,
        student_id=student_id,
        is_active=True,
    ).first() is not None

@student_bp.route('/')
@login_required
def list_students():
    """Display a list of all students."""
    students = data_controller.get_all_students()
    teachers = Teacher.query.order_by(Teacher.created_at.desc()).all() if current_user.is_admin else []
    return render_template('students.html', students=students, teachers=teachers)

@student_bp.route('/<int:student_id>')
@login_required
def student_profile(student_id):
    """Display enhanced student profile with multi-tab interface."""
    # Security: Only teachers and admins can access detailed student profile tabs.
    if not (current_user.is_teacher or current_user.is_admin):
        flash('Only teachers or administrators can view student profiles.', 'danger')
        return redirect(url_for('auth_bp.student_dashboard'))
    
    student = data_controller.get_student_by_id(student_id)
    
    # Get alerts for this student
    alerts = Alert.query.filter_by(student_id=student_id).order_by(desc(Alert.created_at)).all()
    
    # Get interventions
    interventions = Intervention.query.filter_by(student_id=student_id).order_by(desc(Intervention.created_at)).all()
    
    # Get LMS activities
    lms_activities = LMSActivity.query.filter_by(student_id=student_id).order_by(desc(LMSActivity.activity_date)).limit(20).all()
    
    # Get behavioral data
    behavioral_data = BehavioralData.query.filter_by(student_id=student_id).order_by(desc(BehavioralData.record_date)).limit(20).all()
    
    # Get gamification profile
    gamification_profile = GamificationProfile.query.filter_by(student_id=student_id).first()
    gamification_rank = None
    if gamification_profile:
        gamification_rank = GamificationController.get_student_rank(student_id)
    
    # Build timeline events
    timeline_events = []
    
    # Add prediction events
    if student.latest_prediction:
        timeline_events.append({
            'type': 'Prediction',
            'title': f'Risk Assessment: {student.latest_prediction.risk_category} Risk',
            'description': f'Risk score: {student.latest_prediction.risk_score}%',
            'date': student.latest_prediction.prediction_date,
            'icon': 'fa-brain',
            'color': 'danger' if student.latest_prediction.risk_category == 'High' else ('warning' if student.latest_prediction.risk_category == 'Medium' else 'success')
        })
    
    # Add alert events
    for alert in alerts[:5]:
        timeline_events.append({
            'type': 'Alert',
            'title': f'{alert.alert_type} Alert',
            'description': alert.description,
            'date': alert.created_at,
            'icon': 'fa-bell',
            'color': 'warning'
        })
    
    # Add intervention events
    for intervention in interventions[:5]:
        timeline_events.append({
            'type': 'Intervention',
            'title': f'{intervention.intervention_type} Intervention',
            'description': intervention.description[:100] + '...' if len(intervention.description) > 100 else intervention.description,
            'date': intervention.scheduled_date or intervention.created_at,
            'icon': 'fa-hands-helping',
            'color': 'info'
        })
    
    # Add gamification achievements
    if gamification_profile and gamification_profile.badges:
        for badge in gamification_profile.badges[:3]:
            badge_name = badge.get('name') if isinstance(badge, dict) else badge
            earned_date = badge.get('earned_date') if isinstance(badge, dict) else None
            timeline_events.append({
                'type': 'Achievement',
                'title': f'Earned Badge: {badge_name}',
                'description': 'New badge unlocked!',
                'date': earned_date,
                'icon': 'fa-trophy',
                'color': 'success'
            })
    
    def _timeline_sort_date(event):
        """Normalize timeline date values so mixed types can be sorted safely."""
        return _normalize_event_date(event.get('date')) or datetime.min

    # Sort timeline by date (most recent first)
    timeline_events.sort(key=_timeline_sort_date, reverse=True)

    for event in timeline_events:
        event['display_date'] = _format_event_date(event.get('date'))
    
    return render_template('student_profile.html',
                         student=student,
                         alerts=alerts,
                         interventions=interventions,
                         lms_activities=lms_activities,
                         behavioral_data=behavioral_data,
                         gamification_profile=gamification_profile,
                         gamification_rank=gamification_rank,
                         timeline_events=timeline_events)

@student_bp.route('/<int:student_id>/request-counselling', methods=['POST'])
@login_required
def request_counselling(student_id):
    """Allow students to request counselling help - creates an alert."""
    # Security: Students can only request counselling for themselves
    if current_user.is_student:
        if not current_user.student_profile or current_user.student_profile.id != student_id:
            flash('You can only request counselling for yourself.', 'danger')
            return redirect(url_for('student_bp.student_profile', student_id=current_user.student_profile.id))
    
    student = Student.query.get_or_404(student_id)
    
    # Check if student already has an active counselling request alert
    existing_alert = Alert.query.filter_by(
        student_id=student_id,
        alert_type='Psychological',
        status='Active'
    ).filter(Alert.title.contains('Counselling Request')).first()
    
    if existing_alert:
        flash('You already have an active counselling request. A counselor will contact you soon.', 'info')
    else:
        # Create a counselling request alert
        alert = Alert(
            student_id=student_id,
            alert_type='Psychological',
            severity='High',
            title='Student Counselling Request',
            description=f'{student.name} has requested counselling support.',
            context={'student_requested': True, 'request_date': datetime.utcnow().isoformat()},
            recommended_actions=['Schedule counselling session', 'Contact student within 24 hours', 'Assess student needs'],
            status='Active'
        )
        db.session.add(alert)
        db.session.commit()
        
        flash('Your counselling request has been submitted successfully. A counselor will contact you soon.', 'success')
    
    return redirect(url_for('student_bp.student_profile', student_id=student_id))

@student_bp.route('/<int:student_id>/chatbot')
@login_required
def student_chatbot(student_id):
    """Renders the chatbot page for a specific student - Students only."""
    # Only students can access chatbot
    if not current_user.is_student:
        flash('Chatbot is only available for students.', 'warning')
        return redirect(url_for('student_bp.student_profile', student_id=student_id))
    
    # Students can only access their own chatbot
    if current_user.student_profile and current_user.student_profile.id != student_id:
        flash('You can only access your own chatbot.', 'danger')
        return redirect(url_for('student_bp.student_profile', student_id=current_user.student_profile.id))
    
    student = Student.query.get_or_404(student_id)
    return render_template('chatbot.html', student=student)

@student_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add a new student - Teachers and Admins only."""
    if not (current_user.is_teacher or current_user.is_admin):
        flash('Only teachers and administrators can add students.', 'danger')
        return redirect(url_for('student_bp.list_students'))
    
    if request.method == 'POST':
        data_controller.add_student(request.form)
        flash('Student added successfully!', 'success')
        return redirect(url_for('student_bp.list_students'))
    return render_template('student_form.html', form_action='Add Student')

@student_bp.route('/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    """Edit an existing student - Teachers and Admins only."""
    if not (current_user.is_teacher or current_user.is_admin):
        flash('Only teachers and administrators can edit student information.', 'danger')
        return redirect(url_for('student_bp.student_profile', student_id=student_id))

    if current_user.is_teacher and not _teacher_has_student_access(current_user, student_id):
        flash('You can only edit students assigned to you.', 'danger')
        return redirect(url_for('auth_bp.teacher_dashboard'))
    
    student = data_controller.get_student_by_id(student_id)
    if request.method == 'POST':
        data_controller.update_student(student_id, request.form)
        flash('Student updated successfully!', 'success')
        return redirect(url_for('student_bp.student_profile', student_id=student_id))
    return render_template('student_form.html', student=student, form_action='Edit Student')

@student_bp.route('/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    """Delete a student - Admins only."""
    if not current_user.is_admin:
        flash('Only administrators can delete students.', 'danger')
        return redirect(url_for('student_bp.list_students'))
    
    data_controller.delete_student(student_id)
    flash('Student deleted successfully.', 'danger')
    return redirect(url_for('student_bp.list_students'))
