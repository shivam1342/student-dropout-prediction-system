"""
Repository Layer - Database Access
"""
from app.repositories.base_repository import BaseRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.risk_prediction_repository import RiskPredictionRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.intervention_repository import InterventionRepository
from app.repositories.gamification_repository import GamificationRepository

__all__ = [
    'BaseRepository',
    'StudentRepository',
    'RiskPredictionRepository',
    'AlertRepository',
    'InterventionRepository',
    'GamificationRepository'
]
