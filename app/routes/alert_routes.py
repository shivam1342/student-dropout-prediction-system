"""
Alert Routes
Routes for alert dashboard and management
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Alert, Student
from app.controllers.alert_controller import AlertController
from app.extensions import db

alert_bp = Blueprint('alert_bp', __name__)


def _can_manage_alerts(user):
    """Allow only staff roles to mutate alert state."""
    return user.is_teacher or user.is_admin or user.is_counselor


@alert_bp.route('/')
@login_required
def alerts_dashboard():
    """Alert dashboard with filtering"""
    # Get filter parameters
    severity = request.args.get('severity')
    alert_type = request.args.get('type')
    status = request.args.get('status', 'Active')
    
    # Get alerts with filters
    alerts = AlertController.get_active_alerts(
        severity=severity,
        alert_type=alert_type
    )
    
    # Additional filtering by status
    if status and status != 'All':
        alerts = [a for a in alerts if a.status == status]

    # De-duplicate legacy redundant alerts by keeping the newest per key.
    deduped = {}
    for alert in alerts:
        dedupe_key = (alert.student_id, alert.alert_type, alert.severity, alert.title.strip())
        if dedupe_key not in deduped:
            deduped[dedupe_key] = alert
            continue

        current = deduped[dedupe_key]
        if (alert.created_at or 0) > (current.created_at or 0):
            deduped[dedupe_key] = alert
    alerts = sorted(deduped.values(), key=lambda a: a.created_at or 0, reverse=True)
    
    # Get statistics
    stats = AlertController.get_alert_statistics()
    
    return render_template(
        'alerts_dashboard.html',
        alerts=alerts,
        stats=stats,
        current_severity=severity,
        current_type=alert_type,
        current_status=status
    )


@alert_bp.route('/<int:alert_id>')
@login_required
def alert_detail(alert_id):
    """Alert detail page"""
    alert = Alert.query.get_or_404(alert_id)
    student = Student.query.get(alert.student_id)
    
    return render_template(
        'alert_detail.html',
        alert=alert,
        student=student
    )


@alert_bp.route('/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    if not _can_manage_alerts(current_user):
        flash('Access denied. Only staff can manage alerts.', 'danger')
        return redirect(url_for('main_bp.dashboard'))

    acknowledged_by = request.form.get('acknowledged_by', 'System Admin')
    notes = request.form.get('notes', '')
    
    alert = AlertController.acknowledge_alert(alert_id, acknowledged_by, notes)
    
    if alert:
        flash(f'Alert #{alert_id} acknowledged successfully', 'success')
    else:
        flash(f'Failed to acknowledge alert #{alert_id}', 'danger')
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': alert is not None,
            'alert_id': alert_id,
            'status': alert.status if alert else None
        })
    
    return redirect(request.referrer or url_for('alert_bp.alerts_dashboard'))


@alert_bp.route('/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """Resolve an alert"""
    if not _can_manage_alerts(current_user):
        flash('Access denied. Only staff can manage alerts.', 'danger')
        return redirect(url_for('main_bp.dashboard'))

    resolved_by = request.form.get('resolved_by', 'System Admin')
    action_taken = request.form.get('action_taken', '')
    notes = request.form.get('notes', '')
    
    if not action_taken:
        flash('Please provide the action taken', 'warning')
        return redirect(request.referrer or url_for('alert_bp.alerts_dashboard'))
    
    alert = AlertController.resolve_alert(alert_id, resolved_by, action_taken, notes)
    
    if alert:
        flash(f'Alert #{alert_id} resolved successfully', 'success')
    else:
        flash(f'Failed to resolve alert #{alert_id}', 'danger')
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': alert is not None,
            'alert_id': alert_id,
            'status': alert.status if alert else None
        })
    
    return redirect(request.referrer or url_for('alert_bp.alerts_dashboard'))


@alert_bp.route('/generate', methods=['POST'])
@login_required
def generate_alerts():
    """Generate alerts for all students (batch operation)"""
    if not _can_manage_alerts(current_user):
        flash('Access denied. Only staff can generate alerts.', 'danger')
        return redirect(url_for('main_bp.dashboard'))

    result = AlertController.batch_generate_alerts()
    
    flash(f"Generated alerts for {result['total_students_checked']} students. "
          f"Total alerts: {result['total_alerts_generated']}", 'info')
    
    return redirect(url_for('alert_bp.alerts_dashboard'))


@alert_bp.route('/api/stats')
@login_required
def alert_stats_api():
    """API endpoint for alert statistics"""
    stats = AlertController.get_alert_statistics()
    return jsonify(stats)
