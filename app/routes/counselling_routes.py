"""
Counselling Routes
Dashboard for viewing recommendations.
"""
from flask import Blueprint, render_template
from controllers import data_controller, counselling_controller
from app.models import Student, RiskPrediction
from sqlalchemy import desc

counselling_bp = Blueprint('counselling_bp', __name__)

@counselling_bp.route('/')
def dashboard():
    """Show high-risk students and their counselling recommendations."""
    high_risk_students = (
        Student.query
        .join(RiskPrediction)
        .filter(RiskPrediction.risk_category == 'High')
        .order_by(desc(RiskPrediction.risk_score))
        .all()
    )
    
    counselling_data = []
    for student in high_risk_students:
        latest_prediction = RiskPrediction.query.filter_by(student_id=student.id).order_by(desc(RiskPrediction.prediction_date)).first()
        if latest_prediction:
            top_features = [
                {'name': latest_prediction.top_feature_1, 'value': latest_prediction.top_feature_1_value},
                {'name': latest_prediction.top_feature_2, 'value': latest_prediction.top_feature_2_value},
                {'name': latest_prediction.top_feature_3, 'value': latest_prediction.top_feature_3_value}
            ]
            # Filter out None features
            top_features = [f for f in top_features if f['name'] is not None]
            
            recommendations = counselling_controller.generate_recommendations(top_features)
            counselling_data.append({
                'student': student,
                'prediction': latest_prediction,
                'recommendations': recommendations
            })
            
    return render_template('counselling.html', counselling_data=counselling_data)
