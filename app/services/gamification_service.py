"""
Gamification Service
Business logic for gamification features
"""
from app.repositories import GamificationRepository, StudentRepository
from typing import Dict, List


class GamificationService:
    """Business logic for gamification operations"""
    
    def __init__(self):
        self.gamification_repo = GamificationRepository()
        self.student_repo = StudentRepository()
    
    def get_leaderboard(self, limit: int = 10):
        """Get leaderboard""" 
        return self.gamification_repo.get_leaderboard(limit)
    
    def get_student_profile(self, student_id: int):
        """Get gamification profile for student"""
        profile = self.gamification_repo.get_by_student(student_id)
        if profile:
            rank = self.gamification_repo.get_student_rank(student_id)
            return {
                'profile': profile,
                'rank': rank
            }
        return None
    
    def add_points(self, student_id: int, points: int, reason: str):
        """Add points to student"""
        profile = self.gamification_repo.get_by_student(student_id)
        if profile:
            new_points = profile.total_points + points
            return self.gamification_repo.update(
                profile.id,
                total_points=new_points
            )
        return None
    
    def award_badge(self, student_id: int, badge_name: str):
        """Award badge to student"""
        profile = self.gamification_repo.get_by_student(student_id)
        if profile:
            badges = profile.badges_earned or []
            if badge_name not in badges:
                badges.append(badge_name)
                return self.gamification_repo.update(
                    profile.id,
                    badges_earned=badges
                )
        return None
    
    def update_streak(self, student_id: int, streak: int):
        """Update login streak"""
        profile = self.gamification_repo.get_by_student(student_id)
        if profile:
            return self.gamification_repo.update(
                profile.id,
                current_streak=streak
            )
        return None
