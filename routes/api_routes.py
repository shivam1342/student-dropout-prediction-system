"""
API Routes
Provides REST endpoints for predictions and chatbot.
"""
from flask import Blueprint, request, jsonify
from controllers import prediction_controller, data_controller, chatbot_controller
from models import Student, RiskPrediction
from extensions import db

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/predict/<int:student_id>', methods=['POST'])
def predict(student_id):
    """Run prediction for a student and save the result."""
    student = Student.query.get_or_404(student_id)
    student_data = student.to_dict()
    
    risk_score, risk_category, top_features, lime_features = prediction_controller.predict_dropout_risk(student_data)
    
    # Get attention weights if available
    attention_weights = prediction_controller.get_attention_weights(student_data)
    
    # Save prediction to database
    new_prediction = RiskPrediction(
        student_id=student.id,
        risk_score=risk_score,
        risk_category=risk_category,
        top_feature_1=top_features[0]['name'] if len(top_features) > 0 else None,
        top_feature_1_value=top_features[0]['value'] if len(top_features) > 0 else None,
        top_feature_2=top_features[1]['name'] if len(top_features) > 1 else None,
        top_feature_2_value=top_features[1]['value'] if len(top_features) > 1 else None,
        top_feature_3=top_features[2]['name'] if len(top_features) > 2 else None,
        top_feature_3_value=top_features[2]['value'] if len(top_features) > 2 else None
    )
    db.session.add(new_prediction)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'prediction_id': new_prediction.id,
        'risk_score': risk_score,
        'risk_category': risk_category,
        'shap_explanations': top_features,
        'lime_explanations': lime_features,
        'attention_weights': attention_weights
    })

@api_bp.route('/chatbot', methods=['POST'])
def chat():
    """Chatbot endpoint to get a response."""
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    bot_response = chatbot_controller.get_bot_response(user_message)
    return jsonify({'response': bot_response})
