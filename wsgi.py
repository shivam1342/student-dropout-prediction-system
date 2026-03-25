"""Production WSGI entrypoint for container platforms (Railway, etc.)."""
from app import create_app

# Force production config for hosted environments.
app = create_app("production")
