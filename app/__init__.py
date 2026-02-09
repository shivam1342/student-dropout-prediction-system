"""
EduCare Flask Application
AI-Based Dropout Prediction and Counselling System
"""
from flask import Flask, render_template
import os
from app.extensions import db
from app.config import config


def create_app(config_name='default'):
    """Application factory pattern"""
    # Define template and static folders relative to app directory
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure instance folder exists
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Import models to register them with SQLAlchemy
    from app.models import (
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
    from app.routes.main_routes import main_bp
    from app.routes.student_routes import student_bp
    from app.routes.api_routes import api_bp
    from app.routes.counselling_routes import counselling_bp
    from app.routes.favicon_routes import favicon_bp
    from app.routes.alert_routes import alert_bp
    from app.routes.intervention_routes import intervention_bp
    from app.routes.gamification_routes import gamification_bp
    # Note: chatbot_bp temporarily imported from old location
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
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
    
    # CLI Commands
    from controllers.db_utils import seed_db

    @app.cli.command("db-create")
    def create_database_command():
        """Creates database tables."""
        with app.app_context():
            db.create_all()
            print("[OK] Database tables created successfully.")

    @app.cli.command("seed-db")
    def seed_database_command():
        """Seeds the database with initial data."""
        with app.app_context():
            db.create_all()
            seed_db()
    
    # Create database tables automatically
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
