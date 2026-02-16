"""
Student Routes
Handles CRUD for students and viewing profiles.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers import data_controller
from app.models import Student, Alert, Intervention, LMSActivity, BehavioralData, GamificationProfile
from app.controllers.gamification_controller import GamificationController
from app.extensions import db
from sqlalchemy import desc

student_bp = Blueprint('student_bp', __name__)

@student_bp.route('/')
def list_students():
    """Display a list of all students."""
    students = data_controller.get_all_students()
    return render_template('students.html', students=students)

@student_bp.route('/<int:student_id>')
def student_profile(student_id):
    """Display enhanced student profile with multi-tab interface."""
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
    
    # Sort timeline by date (most recent first)
    timeline_events.sort(key=lambda x: x['date'] if x['date'] else '', reverse=True)
    
    return render_template('student_profile.html',
                         student=student,
                         alerts=alerts,
                         interventions=interventions,
                         lms_activities=lms_activities,
                         behavioral_data=behavioral_data,
                         gamification_profile=gamification_profile,
                         gamification_rank=gamification_rank,
                         timeline_events=timeline_events)

@student_bp.route('/<int:student_id>/chatbot')
def student_chatbot(student_id):
    """Renders the chatbot page for a specific student."""
    student = Student.query.get_or_404(student_id)
    return render_template('chatbot.html', student=student)

@student_bp.route('/add', methods=['GET', 'POST'])
def add_student():
    """Add a new student."""
    if request.method == 'POST':
        data_controller.add_student(request.form)
        flash('Student added successfully!', 'success')
        return redirect(url_for('student_bp.list_students'))
    return render_template('student_form.html', form_action='Add Student')

@student_bp.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    """Edit an existing student."""
    student = data_controller.get_student_by_id(student_id)
    if request.method == 'POST':
        data_controller.update_student(student_id, request.form)
        flash('Student updated successfully!', 'success')
        return redirect(url_for('student_bp.student_profile', student_id=student_id))
    return render_template('student_form.html', student=student, form_action='Edit Student')

@student_bp.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    """Delete a student."""
    data_controller.delete_student(student_id)
    flash('Student deleted successfully.', 'danger')
    return redirect(url_for('student_bp.list_students'))
