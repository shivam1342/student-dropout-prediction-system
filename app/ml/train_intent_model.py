import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle
import os
import sys

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import Student, RiskPrediction

def generate_training_data():
    """Generates training data from the database and hardcoded examples."""
    app = create_app('default')
    with app.app_context():
        students = Student.query.all()
        
        # Base data
        data = {
            "text": [
                "I can't pay my fees", "I need financial help", "How can I apply for aid?",
                "I'm failing my exams", "I need study help", "My grades are very low",
                "I'm feeling depressed", "I'm so stressed out", "I can't focus on my studies", "I feel anxious all the time",
                "Thank you for your help", "Thanks", "Bye", "Goodbye", "Hello", "Hi there"
            ],
            "intent": [
                "financial_help", "financial_help", "financial_help",
                "academic_support", "academic_support", "academic_support",
                "mental_health", "mental_health", "mental_health", "mental_health",
                "gratitude", "gratitude", "farewell", "farewell", "greeting", "greeting"
            ]
        }

        # Add personalized intents
        for student in students:
            # Academic performance queries
            data["text"].extend([
                f"How are my grades?",
                f"What is my academic performance?",
                f"Tell me about my grades in the first semester.",
                f"How did I do in the second semester?"
            ])
            data["intent"].extend([
                "academic_performance",
                "academic_performance",
                "academic_performance",
                "academic_performance"
            ])

            # Risk factor queries
            latest_prediction = RiskPrediction.query.filter_by(student_id=student.id).order_by(RiskPrediction.prediction_date.desc()).first()
            if latest_prediction:
                data["text"].extend([
                    f"Why am I at risk?",
                    f"What are my main risk factors?",
                    f"Tell me about my risk score."
                ])
                data["intent"].extend([
                    "risk_factors",
                    "risk_factors",
                    "risk_factors"
                ])

    return pd.DataFrame(data)

def main():
    """Main function to train and save the model."""
    print("🔄 Generating training data from database...")
    df = generate_training_data()
    
    if df.empty:
        print("❌ No data generated. Please ensure your database is populated.")
        return

    print(f"✅ Generated {len(df)} training samples.")

    # Train the pipeline
    print("🤖 Training intent classification model...")
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['text'])
    model = LogisticRegression(class_weight='balanced')
    model.fit(X, df['intent'])

    # Define the directory path
    ml_dir = os.path.dirname(os.path.abspath(__file__))

    # Save the model and vectorizer
    with open(os.path.join(ml_dir, 'intent_model.pkl'), 'wb') as f:
        pickle.dump(model, f)
    with open(os.path.join(ml_dir, 'vectorizer.pkl'), 'wb') as f:
        pickle.dump(vectorizer, f)

    print("✅ Model trained and saved successfully in the 'ml' directory!")

if __name__ == '__main__':
    main()