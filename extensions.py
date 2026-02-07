"""
Flask Extension Initializations
This file is used to initialize Flask extensions to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize the database extension
db = SQLAlchemy()
