"""
Recreate database with updated schema
"""
from app import app, db

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables with updated schema...")
    db.create_all()
    print("✅ Database recreated successfully with priority field in interventions!")
