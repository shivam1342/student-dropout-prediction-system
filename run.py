"""
EduCare Application Entry Point
Run with: python run.py
"""
import time
_run_start = time.time()

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("Starting AI-Based Dropout Prediction System...")
    print("Dashboard available at: http://127.0.0.1:5000")
    print(f"\n✅ App ready in {time.time() - _run_start:.2f}s")
    print("💡 Note: ML model will load on first prediction request\n")
    # use_reloader=False makes startup 2x faster (but disables auto-reload on code changes)
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)
