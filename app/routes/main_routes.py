"""
Main Routes
Handles dashboard, home, and about pages.
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Student, RiskPrediction, GamificationProfile
from app.controllers.alert_controller import AlertController
from app.controllers.intervention_controller import InterventionController
from app.controllers.gamification_controller import GamificationController
from sqlalchemy import desc, func
import os
import json

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """Enhanced Dashboard with comprehensive stats from all modules."""
    if current_user.is_student:
        return redirect(url_for('auth_bp.student_dashboard'))

    total_students = Student.query.count()
    
    # Count students by their latest prediction only (prevents duplicate inflation).
    latest_pred_subq = (
        RiskPrediction.query
        .with_entities(
            RiskPrediction.student_id.label('student_id'),
            func.max(RiskPrediction.prediction_date).label('latest_prediction_date'),
        )
        .group_by(RiskPrediction.student_id)
        .subquery()
    )

    high_risk_students = (
        RiskPrediction.query
        .join(
            latest_pred_subq,
            (RiskPrediction.student_id == latest_pred_subq.c.student_id)
            & (RiskPrediction.prediction_date == latest_pred_subq.c.latest_prediction_date),
        )
        .filter(RiskPrediction.risk_category == 'High')
        .count()
    )
    at_risk_percentage = (high_risk_students / total_students * 100) if total_students > 0 else 0
    at_risk_percentage = max(0, min(round(at_risk_percentage, 2), 100))
    
    # For chart data (simplified)
    risk_trend = RiskPrediction.query.order_by(RiskPrediction.prediction_date).limit(10).all()
    chart_labels = [p.prediction_date.strftime('%b %d') for p in risk_trend]
    chart_data = [p.risk_score for p in risk_trend]
    
    # Top 5 high-risk students
    top_high_risk_predictions = (
        RiskPrediction.query
        .join(
            latest_pred_subq,
            (RiskPrediction.student_id == latest_pred_subq.c.student_id)
            & (RiskPrediction.prediction_date == latest_pred_subq.c.latest_prediction_date),
        )
        .filter(RiskPrediction.risk_category == 'High')
        .order_by(desc(RiskPrediction.risk_score))
        .limit(5)
        .all()
    )

    top_high_risk = []
    for prediction in top_high_risk_predictions:
        student = Student.query.get(prediction.student_id)
        if not student:
            continue
        student.latest_prediction = prediction
        top_high_risk.append(student)

    # Get Alert Statistics
    alert_stats = AlertController.get_alert_statistics()
    
    # Get Intervention Statistics
    intervention_stats = InterventionController.get_intervention_statistics()
    
    # Get Gamification Statistics (Top 5 Leaderboard)
    top_gamification = GamificationProfile.query.order_by(desc(GamificationProfile.total_points)).limit(5).all()
    
    # Load ML Model Comparison
    model_comparison = {}
    comparison_path = os.path.join('app', 'ml', 'models', 'model_comparison.json')
    if os.path.exists(comparison_path):
        with open(comparison_path, 'r') as f:
            model_comparison = json.load(f)

    stats = {
        'total_students': total_students,
        'at_risk_percentage': at_risk_percentage,
        'interventions_triggered': high_risk_students,
        'alerts': alert_stats,
        'interventions': intervention_stats,
        'model_comparison': model_comparison
    }
    
    return render_template(
        'index.html', 
        stats=stats, 
        chart_labels=chart_labels, 
        chart_data=chart_data,
        top_high_risk=top_high_risk,
        top_gamification=top_gamification,
        model_comparison=model_comparison
    )

@main_bp.route('/about')
def about():
    """About page for the project."""
    return render_template('about.html')

@main_bp.route('/chatbot')
@login_required
def chatbot_page():
    """Renders the chatbot interface page - Students only."""
    # Only students can access chatbot
    if not current_user.is_student:
        flash('Chatbot is only available for students.', 'warning')
        return redirect(url_for('main_bp.dashboard'))
    return render_template('chatbot.html')
@main_bp.route('/evaluation')
def evaluation():
    """ML Model Evaluation Dashboard with comprehensive metrics and visualizations."""
    # Load model comparison data
    comparison_path = os.path.join('app', 'ml', 'models', 'model_comparison.json')
    model_comparison = {}
    
    if os.path.exists(comparison_path):
        with open(comparison_path, 'r') as f:
            model_comparison = json.load(f)
    
    # Prepare data for charts
    model_names = list(model_comparison.keys())
    accuracies = [model_comparison[m]['accuracy'] * 100 for m in model_names]
    auc_scores = [model_comparison[m]['auc'] for m in model_names]
    
    # Find best model
    best_model = max(model_comparison.items(), key=lambda x: x[1]['accuracy']) if model_comparison else (None, None)
    
    return render_template(
        'evaluation.html',
        model_comparison=model_comparison,
        model_names=model_names,
        accuracies=accuracies,
        auc_scores=auc_scores,
        best_model=best_model
    )


@main_bp.route('/design-system/foundations')
@login_required
def design_system_foundations():
    """Design System Foundations page for the new project-wide UI/UX refresh."""
    return render_template('design_system_foundations.html')


@main_bp.route('/design-system/controls')
@login_required
def design_system_controls():
    """Design System Controls page for component states and form patterns."""
    return render_template('design_system_controls.html')