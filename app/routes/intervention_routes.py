"""
Intervention Routes Blueprint
Handles all intervention management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Intervention, Student, Alert
from controllers.intervention_controller import InterventionController
from app.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func

intervention_bp = Blueprint('intervention_bp', __name__)

@intervention_bp.route('/')
def interventions_list():
    """Main interventions list page with filters"""
    # Get filter parameters
    status_filter = request.args.get('status', 'All')
    type_filter = request.args.get('intervention_type', '')
    priority_filter = request.args.get('priority', '')
    student_id = request.args.get('student_id', '')
    
    # Base query
    query = Intervention.query
    
    # Apply filters
    if status_filter != 'All':
        query = query.filter(Intervention.status == status_filter)
    if type_filter:
        query = query.filter(Intervention.intervention_type == type_filter)
    if priority_filter:
        query = query.filter(Intervention.priority == priority_filter)
    if student_id:
        query = query.filter(Intervention.student_id == int(student_id))
    
    # Order by scheduled date
    interventions = query.order_by(Intervention.scheduled_date.desc()).all()
    
    # Get statistics
    stats = InterventionController.get_intervention_statistics()
    
    # Get all students for filter dropdown
    students = Student.query.order_by(Student.name).all()
    
    return render_template('interventions_list.html',
                         interventions=interventions,
                         stats=stats,
                         students=students,
                         status_filter=status_filter,
                         type_filter=type_filter,
                         priority_filter=priority_filter,
                         student_id=student_id)

@intervention_bp.route('/create', methods=['GET', 'POST'])
def create_intervention():
    """Create new intervention (manual)"""
    if request.method == 'POST':
        try:
            # Get form data
            student_id = request.form.get('student_id')
            intervention_type = request.form.get('intervention_type')
            priority = request.form.get('priority')
            scheduled_date_str = request.form.get('scheduled_date')
            description = request.form.get('description')
            assigned_to = request.form.get('assigned_to')
            
            # Parse scheduled date
            scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d')
            
            # Create intervention
            intervention = InterventionController.create_intervention(
                student_id=int(student_id),
                intervention_type=intervention_type,
                priority=priority,
                description=description,
                scheduled_date=scheduled_date,
                assigned_to=assigned_to
            )
            
            flash(f'Intervention created successfully for {intervention.student.name}', 'success')
            return redirect(url_for('intervention_bp.intervention_detail', intervention_id=intervention.id))
        
        except Exception as e:
            flash(f'Error creating intervention: {str(e)}', 'danger')
            return redirect(url_for('intervention_bp.create_intervention'))
    
    # GET request - show form
    students = Student.query.order_by(Student.name).all()
    return render_template('intervention_form.html', students=students, intervention=None)

@intervention_bp.route('/create-from-alert/<int:alert_id>', methods=['GET', 'POST'])
def create_from_alert(alert_id):
    """Create intervention from an alert"""
    alert = Alert.query.get_or_404(alert_id)
    
    if request.method == 'POST':
        try:
            intervention_type = request.form.get('intervention_type')
            priority = request.form.get('priority')
            scheduled_date_str = request.form.get('scheduled_date')
            description = request.form.get('description')
            assigned_to = request.form.get('assigned_to')
            
            scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d')
            
            # Create intervention linked to alert
            intervention = InterventionController.create_intervention(
                student_id=alert.student_id,
                intervention_type=intervention_type,
                priority=priority,
                description=description,
                scheduled_date=scheduled_date,
                assigned_to=assigned_to,
                alert_id=alert.id
            )
            
            flash(f'Intervention created from alert for {alert.student.name}', 'success')
            return redirect(url_for('intervention_bp.intervention_detail', intervention_id=intervention.id))
        
        except Exception as e:
            flash(f'Error creating intervention: {str(e)}', 'danger')
            return redirect(url_for('intervention_bp.create_from_alert', alert_id=alert_id))
    
    # Pre-fill form with alert data
    return render_template('intervention_form.html',
                         students=None,
                         intervention=None,
                         alert=alert,
                         prefill={
                             'student_id': alert.student_id,
                             'description': f"Intervention for alert: {alert.title}",
                             'intervention_type': alert.alert_type,
                             'priority': alert.severity
                         })

@intervention_bp.route('/<int:intervention_id>')
def intervention_detail(intervention_id):
    """Intervention detail page"""
    intervention = Intervention.query.get_or_404(intervention_id)
    
    # Get student's other interventions
    other_interventions = Intervention.query.filter(
        Intervention.student_id == intervention.student_id,
        Intervention.id != intervention_id
    ).order_by(Intervention.scheduled_date.desc()).limit(5).all()
    
    return render_template('intervention_detail.html',
                         intervention=intervention,
                         other_interventions=other_interventions)

@intervention_bp.route('/<int:intervention_id>/complete', methods=['GET', 'POST'])
def complete_intervention(intervention_id):
    """Complete an intervention"""
    intervention = Intervention.query.get_or_404(intervention_id)
    
    if request.method == 'POST':
        try:
            outcome = request.form.get('outcome')
            effectiveness_rating = int(request.form.get('effectiveness_rating'))
            notes = request.form.get('notes')
            follow_up_required = request.form.get('follow_up_required') == 'on'
            follow_up_date_str = request.form.get('follow_up_date')
            
            follow_up_date = None
            if follow_up_required and follow_up_date_str:
                follow_up_date = datetime.strptime(follow_up_date_str, '%Y-%m-%d')
            
            # Complete intervention
            InterventionController.complete_intervention(
                intervention_id=intervention_id,
                outcome=outcome,
                effectiveness_rating=effectiveness_rating,
                notes=notes,
                follow_up_required=follow_up_required,
                follow_up_date=follow_up_date
            )
            
            flash(f'Intervention completed successfully', 'success')
            return redirect(url_for('intervention_bp.intervention_detail', intervention_id=intervention_id))
        
        except Exception as e:
            flash(f'Error completing intervention: {str(e)}', 'danger')
            return redirect(url_for('intervention_bp.complete_intervention', intervention_id=intervention_id))
    
    # GET request - show form
    return render_template('intervention_complete.html', intervention=intervention)

@intervention_bp.route('/<int:intervention_id>/edit', methods=['GET', 'POST'])
def edit_intervention(intervention_id):
    """Edit an intervention"""
    intervention = Intervention.query.get_or_404(intervention_id)
    
    if request.method == 'POST':
        try:
            intervention.intervention_type = request.form.get('intervention_type')
            intervention.priority = request.form.get('priority')
            intervention.scheduled_date = datetime.strptime(request.form.get('scheduled_date'), '%Y-%m-%d')
            intervention.description = request.form.get('description')
            intervention.assigned_to = request.form.get('assigned_to')
            
            db.session.commit()
            
            flash('Intervention updated successfully', 'success')
            return redirect(url_for('intervention_bp.intervention_detail', intervention_id=intervention_id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating intervention: {str(e)}', 'danger')
    
    students = Student.query.order_by(Student.name).all()
    return render_template('intervention_form.html',
                         students=students,
                         intervention=intervention)

@intervention_bp.route('/calendar')
def calendar_view():
    """Calendar view of scheduled interventions"""
    # Get month/year from query params or use current
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    # Get interventions for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    interventions = Intervention.query.filter(
        Intervention.scheduled_date >= start_date,
        Intervention.scheduled_date < end_date
    ).all()
    
    # Group by date
    interventions_by_date = {}
    for intervention in interventions:
        date_key = intervention.scheduled_date.strftime('%Y-%m-%d')
        if date_key not in interventions_by_date:
            interventions_by_date[date_key] = []
        interventions_by_date[date_key].append(intervention)
    
    return render_template('interventions_calendar.html',
                         interventions_by_date=interventions_by_date,
                         month=month,
                         year=year)

@intervention_bp.route('/upcoming-widget')
def upcoming_widget():
    """Get upcoming interventions (for widget/AJAX)"""
    days = request.args.get('days', 7, type=int)
    
    end_date = datetime.now() + timedelta(days=days)
    
    interventions = Intervention.query.filter(
        Intervention.scheduled_date >= datetime.now(),
        Intervention.scheduled_date <= end_date,
        Intervention.status == 'Scheduled'
    ).order_by(Intervention.scheduled_date).limit(10).all()
    
    return render_template('widgets/upcoming_interventions.html',
                         interventions=interventions,
                         days=days)

@intervention_bp.route('/reminders')
def follow_up_reminders():
    """Display follow-up reminders"""
    # Get interventions needing follow-up
    reminders = Intervention.query.filter(
        Intervention.follow_up_required == True,
        Intervention.follow_up_date <= datetime.now() + timedelta(days=7),
        Intervention.status == 'Completed'
    ).order_by(Intervention.follow_up_date).all()
    
    return render_template('intervention_reminders.html', 
                         reminders=reminders,
                         now=datetime.now())

@intervention_bp.route('/api/stats')
def intervention_stats_api():
    """API endpoint for intervention statistics"""
    stats = InterventionController.get_intervention_statistics()
    return jsonify(stats)

@intervention_bp.route('/api/calendar-data')
def calendar_data_api():
    """API endpoint for calendar data (JSON)"""
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    interventions = Intervention.query.filter(
        Intervention.scheduled_date >= start_date,
        Intervention.scheduled_date < end_date
    ).all()
    
    events = []
    for intervention in interventions:
        events.append({
            'id': intervention.id,
            'title': f"{intervention.student.name} - {intervention.intervention_type}",
            'start': intervention.scheduled_date.strftime('%Y-%m-%d'),
            'className': f'priority-{intervention.priority.lower()}',
            'url': url_for('intervention_bp.intervention_detail', intervention_id=intervention.id)
        })
    
    return jsonify(events)
