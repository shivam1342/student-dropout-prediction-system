"""
API Routes
Provides REST endpoints for predictions and chatbot.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.controllers import prediction_controller
from app.models import Student, RiskPrediction, TeacherStudentAssignment
from app.extensions import db
from app.services.chatbot import chatbot_reply_from_user

api_bp = Blueprint('api_bp', __name__)


def _teacher_can_access_student(user, student_id):
    """Check whether a teacher is actively assigned to a student."""
    if not user.is_teacher or not user.teacher_profile:
        return False

    return TeacherStudentAssignment.query.filter_by(
        teacher_id=user.teacher_profile.id,
        student_id=student_id,
        is_active=True,
    ).first() is not None


def _can_predict_for_student(user, student_id):
    """Authorize prediction access by role and assignment."""
    if user.is_admin or user.is_counselor:
        return True
    if user.is_teacher:
        return _teacher_can_access_student(user, student_id)
    if user.is_student and user.student_profile:
        return user.student_profile.id == student_id
    return False

@api_bp.route('/predict/<int:student_id>', methods=['POST'])
@login_required
def predict(student_id):
    """Run prediction for a student and save the result."""
    if not _can_predict_for_student(current_user, student_id):
        return jsonify({'error': 'Access denied for this student'}), 403

    student = Student.query.get_or_404(student_id)
    student_data = student.to_dict()

    try:
        risk_score, risk_category, top_features, lime_features = prediction_controller.predict_dropout_risk(student_data)

        # Do not persist placeholder results when the model is unavailable.
        if risk_category == 'N/A':
            return jsonify({'error': 'Prediction model is unavailable. Please train/load the model first.'}), 503

        # Get attention weights if available
        attention_weights = prediction_controller.get_attention_weights(student_data)

        # Save prediction to database
        new_prediction = RiskPrediction(
            student_id=student.id,
            risk_score=risk_score,
            risk_category=risk_category,
            dropout_probability=risk_score / 100.0,  # Convert 0-100 to 0-1
            prediction_result=risk_category,
            top_feature_1=top_features[0]['name'] if len(top_features) > 0 else None,
            top_feature_1_value=top_features[0]['value'] if len(top_features) > 0 else None,
            top_feature_2=top_features[1]['name'] if len(top_features) > 1 else None,
            top_feature_2_value=top_features[1]['value'] if len(top_features) > 1 else None,
            top_feature_3=top_features[2]['name'] if len(top_features) > 2 else None,
            top_feature_3_value=top_features[2]['value'] if len(top_features) > 2 else None,
            top_risk_factors={
                'shap_explanations': top_features,
                'lime_explanations': lime_features,
                'attention_weights': attention_weights,
            }
        )
        db.session.add(new_prediction)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': f'Prediction failed: {exc}'}), 500
    
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
@login_required
def chat():
    """Chatbot endpoint to get a response."""
    if not current_user.is_student:
        return jsonify({'error': 'Chatbot is available for students only'}), 403

    payload = request.get_json(silent=True) or {}
    user_message = payload.get('message')
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    bot_response = chatbot_reply_from_user(user_message, current_user)
    return jsonify({'response': bot_response})
