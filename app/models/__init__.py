"""
Database Models Package
"""
from app.models.student import Student
from app.models.risk_prediction import RiskPrediction
from app.models.counselling_log import CounsellingLog
from app.models.lms_activity import LMSActivity
from app.models.behavioral_data import BehavioralData
from app.models.alert import Alert
from app.models.intervention import Intervention
from app.models.gamification import GamificationProfile

__all__ = [
    'Student',
    'RiskPrediction',
    'CounsellingLog',
    'LMSActivity',
    'BehavioralData',
    'Alert',
    'Intervention',
    'GamificationProfile'
]
