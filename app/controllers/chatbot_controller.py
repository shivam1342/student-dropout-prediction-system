from flask import Blueprint, request, jsonify
import pickle
import numpy as np
import subprocess
import os
from models import Student, RiskPrediction

chatbot_bp = Blueprint('chatbot', __name__)

# --- Layer 1: Rule-Based Responses ---
rule_based_responses = {
    "hello": "Hi there! How can I help you today?",
    "hi": "Hi there! How can I help you today?",
    "fees": "If you're facing financial issues, you can apply for aid through the counselling portal.",
    "attendance": "Make sure to maintain above 75% to stay safe from dropout risk.",
    "stress": "It's okay to feel stressed. Take a short break or talk to a mentor.",
    "study": "To improve your study habits, try creating a study schedule, breaking down topics into smaller chunks, and taking regular breaks. Consider joining a study group for better engagement.",
    "weak": "To identify your weak areas, review your past assessments and grades. Focus on subjects where you're scoring lower. Consider seeking help from mentors or tutors for those specific areas.",
    "how should i study": "Create a regular study schedule, find a quiet place to study, break down complex topics into smaller parts, use active recall techniques, and take regular breaks. Remember to review previous material regularly.",
    "where i am weak": "To identify your weak areas, check your grades and performance records. Review subjects where you've scored lower. You can also seek help from mentors or use the counselling portal for personalized guidance.",
    "bye": "Goodbye! Remember, support is always here."
}

def rule_based_reply(user_input):
    user_input_lower = user_input.lower()
    for key, response in rule_based_responses.items():
        if key in user_input_lower:
            return response
    return None

# --- Layer 2: ML Intent Classifier ---
# Load model and vectorizer
vectorizer = None
model = None
try:
    # Construct absolute paths to model files
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    vectorizer_path = os.path.join(base_dir, 'ml', 'vectorizer.pkl')
    model_path = os.path.join(base_dir, 'ml', 'intent_model.pkl')
    
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("WARNING: Chatbot ML model/vectorizer not found. The ML layer will be skipped.")

intent_responses = {
    "financial_help": "You may qualify for scholarships or fee waivers. Visit the financial aid section.",
    "academic_support": "Consider joining a study group or requesting a mentor session.",
    "mental_health": "It’s important to take care of your mind. Try our counselling resources.",
    "greeting": "Hey there! How can I help you today?",
    "farewell": "Goodbye! Take care of yourself.",
    "gratitude": "You’re welcome! Glad to help."
}

def get_academic_performance_reply(student_id):
    student = Student.query.get(student_id)
    if not student:
        return "I couldn't find your records. Please ensure you are logged in correctly."
    
    return f"Your performance has been recorded. 1st semester grade: {student.curricular_units_1st_sem_grade}, 2nd semester grade: {student.curricular_units_2nd_sem_grade}."

def get_risk_factors_reply(student_id):
    prediction = RiskPrediction.query.filter_by(student_id=student_id).order_by(RiskPrediction.prediction_date.desc()).first()
    if not prediction:
        return "No risk assessment has been performed for you yet."

    features = [prediction.top_feature_1, prediction.top_feature_2, prediction.top_feature_3]
    non_null_features = [f for f in features if f is not None]
    
    if not non_null_features:
        return f"Your current risk score is {prediction.risk_score:.2f}%, which is considered {prediction.risk_category}. No specific factors are highlighted at the moment."

    factors_str = ", ".join(non_null_features)
    return f"Your risk score is {prediction.risk_score:.2f}% ({prediction.risk_category}). The main contributing factors are: {factors_str}."

def ml_intent_reply(user_input, student_id=None):
    if not model or not vectorizer:
        return None

    try:
        X = vectorizer.transform([user_input])
        intent = model.predict(X)[0]
        
        if hasattr(model, 'predict_proba'):
            prob = np.max(model.predict_proba(X))
            if prob < 0.6: # Use a slightly higher threshold for confidence
                return None
        
        # Handle personalized intents (only if student_id is provided)
        if intent == "academic_performance":
            if student_id:
                return get_academic_performance_reply(student_id)
            else:
                return "I can help you with academic performance information, but I need your student ID to provide personalized details. Please access the chatbot through your student profile."
        if intent == "risk_factors":
            if student_id:
                return get_risk_factors_reply(student_id)
            else:
                return "I can help you understand your risk factors, but I need your student ID to provide personalized information. Please access the chatbot through your student profile."
            
        return intent_responses.get(intent)
    except Exception as e:
        print(f"Error in ML intent reply: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Layer 3: Fallback to Local LLM (Ollama) ---
def ollama_reply(prompt):
    try:
        # Command to run Ollama with the Mistral model
        command = [
            "ollama", "run", "mistral",
            f"You are a friendly and supportive student counsellor. Keep your response concise (2-3 sentences). User's message: '{prompt}'"
        ]
        
        result = subprocess.run(
            command,
            capture_output=True, text=True, check=True, encoding='utf-8',
            timeout=30  # Add timeout to prevent hanging
        )
        response = result.stdout.strip()
        if not response:
            raise ValueError("Empty response from Ollama")
        return response
    except FileNotFoundError:
        print("ERROR: 'ollama' command not found. Make sure Ollama is installed and in your PATH.")
        # Provide a helpful generic response based on common keywords
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['study', 'learn', 'exam', 'grade', 'academic']):
            return "For academic support, I recommend creating a study schedule, reviewing your notes regularly, and seeking help from mentors or study groups. You can also check your performance through the student portal."
        elif any(word in prompt_lower for word in ['weak', 'poor', 'bad', 'fail', 'struggle']):
            return "It's normal to have areas where you need improvement. Focus on identifying specific topics, practice regularly, and don't hesitate to ask for help from teachers or mentors."
        elif any(word in prompt_lower for word in ['stress', 'anxious', 'worried', 'pressure']):
            return "Managing stress is important. Take breaks, practice relaxation techniques, and remember that it's okay to ask for help. Consider using our counselling resources."
        else:
            return "I'm here to help with academic support, study tips, and general guidance. Could you provide more details about what you need help with?"
    except subprocess.TimeoutExpired:
        print("ERROR: Ollama request timed out.")
        return "I'm taking longer than expected to respond. Please try rephrasing your question or try again in a moment."
    except subprocess.CalledProcessError as e:
        print(f"Ollama process error: {e.stderr}")
        return "I'm facing a technical issue. Please try rephrasing your question or contact support if the issue persists."
    except Exception as e:
        print(f"An unexpected error occurred with Ollama: {e}")
        import traceback
        traceback.print_exc()
        return "I encountered an unexpected issue. Please try rephrasing your question."

# --- Main Chat Route ---
@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"reply": "Please provide a message."}), 400
            
        user_input = data.get('message', '').strip()
        student_id = data.get('student_id')  # student_id is optional
        
        # Convert empty string to None
        if student_id == '':
            student_id = None
        # Convert string ID to int if provided
        elif student_id and isinstance(student_id, str) and student_id.isdigit():
            try:
                student_id = int(student_id)
            except ValueError:
                student_id = None

        if not user_input:
            return jsonify({"reply": "Please provide a message."}), 400

        # 1️⃣ Try rule-based layer first
        reply = rule_based_reply(user_input)
        if reply:
            return jsonify({"reply": reply})

        # 2️⃣ If no rule matches, try ML intent classifier
        reply = ml_intent_reply(user_input, student_id)
        if reply:
            return jsonify({"reply": reply})

        # 3️⃣ If intent confidence is low, fallback to Ollama LLM or generic response
        reply = ollama_reply(user_input)
        return jsonify({"reply": reply})
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"reply": f"An error occurred: {str(e)}"}), 500

