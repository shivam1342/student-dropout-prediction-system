"""
Favicon Route
Provides a simple favicon to avoid 404 errors
"""
from flask import Blueprint, send_from_directory, current_app
import os

favicon_bp = Blueprint('favicon_bp', __name__)

@favicon_bp.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    try:
        return send_from_directory(
            os.path.join(current_app.root_path, 'static', 'images'), 
            'logo.png', 
            mimetype='image/x-icon'
        )
    except FileNotFoundError:
        return '', 204