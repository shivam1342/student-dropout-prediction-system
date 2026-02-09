"""
EduCare Application Entry Point
Run with: python run.py
"""
from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("Starting AI-Based Dropout Prediction System...")
    print("Dashboard available at: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
