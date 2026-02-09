"""
Flask Extension Initializations
This file is a compatibility shim - it imports from the new app.extensions
to maintain backward compatibility with old controllers.
"""
from app.extensions import db

__all__ = ['db']
