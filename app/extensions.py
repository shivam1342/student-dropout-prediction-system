"""
Flask Extension Initializations
This file is used to initialize Flask extensions to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize the database extension
db = SQLAlchemy()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth_bp.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
