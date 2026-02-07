"""
Main Flask Application Entry Point
AI-Based Dropout Prediction and Counselling System
"""
from flask import Flask, render_template
import os
from extensions import db
from app_config import config

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure instance folder exists (for any file storage needs)
    os.makedirs('instance', exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Import models to register them with SQLAlchemy
    from models import (
        Student, 
        RiskPrediction, 
        CounsellingLog,
        LMSActivity,
        BehavioralData,
        Alert,
        Intervention,
        GamificationProfile
    )
    
    # Register blueprints
    from routes.main_routes import main_bp
    from routes.student_routes import student_bp
    from routes.api_routes import api_bp
    from routes.counselling_routes import counselling_bp
    from routes.favicon_routes import favicon_bp
    from routes.alert_routes import alert_bp
    from routes.intervention_routes import intervention_bp
    from routes.gamification_routes import gamification_bp
    from controllers.chatbot_controller import chatbot_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp, url_prefix='/students')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(counselling_bp, url_prefix='/counselling')
    app.register_blueprint(alert_bp, url_prefix='/alerts')
    app.register_blueprint(intervention_bp, url_prefix='/interventions')
    app.register_blueprint(gamification_bp, url_prefix='/gamification')
    app.register_blueprint(favicon_bp)
    app.register_blueprint(chatbot_bp)
    
    # --- CLI Commands ---
    from controllers.db_utils import seed_db

    @app.cli.command("db-create")
    def create_database_command():
        """Creates database tables."""
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully.")

    @app.cli.command("seed-db")
    def seed_database_command():
        """Seeds the database with initial data."""
        with app.app_context():
            db.create_all() # Ensure tables are created
            seed_db()
    
    # Create database tables automatically if not using CLI
    with app.app_context():
        db.create_all()
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('layout.html', error="Page not found"), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('layout.html', error="Internal server error"), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    print("🚀 Starting AI-Based Dropout Prediction System...")
    print("📊 Dashboard available at: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
