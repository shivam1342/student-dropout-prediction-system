"""
Gamification Repository
Database operations for GamificationProfile model
"""
from app.repositories.base_repository import BaseRepository
from app.models import GamificationProfile
from sqlalchemy import desc


class GamificationRepository(BaseRepository):
    """Repository for gamification data access"""
    
    def __init__(self):
        super().__init__(GamificationProfile)
    
    def get_leaderboard(self, limit: int = 10):
        """Get top students by points"""
        return (
            GamificationProfile.query
            .order_by(desc(GamificationProfile.total_points))
            .limit(limit)
            .all()
        )
    
    def get_by_student(self, student_id: int):
        """Get gamification profile for student"""
        return GamificationProfile.query.filter_by(student_id=student_id).first()
    
    def get_student_rank(self, student_id: int):
        """Get student's rank on leaderboard"""
        profile = self.get_by_student(student_id)
        if not profile:
            return None
        
        rank = (
            GamificationProfile.query
            .filter(GamificationProfile.total_points > profile.total_points)
            .count()
        )
        return rank + 1
