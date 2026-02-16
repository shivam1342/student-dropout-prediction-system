"""
Student Repository
Database operations for Student model
"""
from app.repositories.base_repository import BaseRepository
from app.models import Student
from sqlalchemy import desc


class StudentRepository(BaseRepository):
    """Repository for student data access"""
    
    def __init__(self):
        super().__init__(Student)
    
    def get_high_risk_students(self, limit: int = 10):
        """Get students with highest risk scores"""
        from app.models import RiskPrediction
        return (
            Student.query
            .join(RiskPrediction)
            .filter(RiskPrediction.risk_category.in_(['High', 'Critical']))
            .order_by(desc(RiskPrediction.risk_score))
            .limit(limit)
            .all()
        )
    
    def search(self, query: str):
        """Search students by name or email"""
        search_term = f"%{query}%"
        return (
            Student.query
            .filter(
                (Student.name.ilike(search_term)) |
                (Student.email.ilike(search_term))
            )
            .all()
        )
    
    def get_by_email(self, email: str):
        """Get student by email"""
        return Student.query.filter_by(email=email).first()
