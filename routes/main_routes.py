"""
Main Routes
Handles dashboard, home, and about pages.
"""
from flask import Blueprint, render_template
from models import Student, RiskPrediction, GamificationProfile
from controllers.alert_controller import AlertController
from controllers.intervention_controller import InterventionController
from controllers.gamification_controller import GamificationController
from sqlalchemy import desc
import os
import json

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def dashboard():
    """Enhanced Dashboard with comprehensive stats from all modules."""
    total_students = Student.query.count()
    
    # Get students with high-risk predictions
    high_risk_students = Student.query.join(RiskPrediction).filter(RiskPrediction.risk_category == 'High').count()
    at_risk_percentage = (high_risk_students / total_students * 100) if total_students > 0 else 0
    
    # For chart data (simplified)
    risk_trend = RiskPrediction.query.order_by(RiskPrediction.prediction_date).limit(10).all()
    chart_labels = [p.prediction_date.strftime('%b %d') for p in risk_trend]
    chart_data = [p.risk_score for p in risk_trend]
    
    # Top 5 high-risk students
    top_high_risk = (
        Student.query
        .join(RiskPrediction)
        .filter(RiskPrediction.risk_category == 'High')
        .order_by(desc(RiskPrediction.risk_score))
        .limit(5)
        .all()
    )
    # Attach latest prediction to each student
    for student in top_high_risk:
        student.latest_prediction = RiskPrediction.query.filter_by(student_id=student.id).order_by(desc(RiskPrediction.prediction_date)).first()

    # Get Alert Statistics
    alert_stats = AlertController.get_alert_statistics()
    
    # Get Intervention Statistics
    intervention_stats = InterventionController.get_intervention_statistics()
    
    # Get Gamification Statistics (Top 5 Leaderboard)
    top_gamification = GamificationProfile.query.order_by(desc(GamificationProfile.total_points)).limit(5).all()
    
    # Load ML Model Comparison
    model_comparison = {}
    comparison_path = os.path.join('ml', 'model_comparison.json')
    if os.path.exists(comparison_path):
        with open(comparison_path, 'r') as f:
            model_comparison = json.load(f)

    stats = {
        'total_students': total_students,
        'at_risk_percentage': round(at_risk_percentage, 2),
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
def chatbot_page():
    """Renders the chatbot interface page."""
    return render_template('chatbot.html')
@main_bp.route('/evaluation')
def evaluation():
    """ML Model Evaluation Dashboard with comprehensive metrics and visualizations."""
    # Load model comparison data
    comparison_path = os.path.join('ml', 'model_comparison.json')
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