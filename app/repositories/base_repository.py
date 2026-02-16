"""
Base Repository
Provides common database operations for all repositories
"""
from app.extensions import db
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError


class BaseRepository:
    """Base repository with common CRUD operations"""
    
    def __init__(self, model):
        self.model = model
        self.db = db
    
    def get_all(self) -> List:
        """Get all records"""
        return self.model.query.all()
    
    def get_by_id(self, id: int) -> Optional[Any]:
        """Get record by ID"""
        return self.model.query.get(id)
    
    def filter_by(self, **kwargs) -> List:
        """Filter records by criteria"""
        return self.model.query.filter_by(**kwargs).all()
    
    def create(self, **kwargs) -> Any:
        """Create new record"""
        try:
            instance = self.model(**kwargs)
            self.db.session.add(instance)
            self.db.session.commit()
            return instance
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e
    
    def update(self, id: int, **kwargs) -> Optional[Any]:
        """Update record by ID"""
        try:
            instance = self.get_by_id(id)
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                self.db.session.commit()
            return instance
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e
    
    def delete(self, id: int) -> bool:
        """Delete record by ID"""
        try:
            instance = self.get_by_id(id)
            if instance:
                self.db.session.delete(instance)
                self.db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e
    
    def count(self) -> int:
        """Count total records"""
        return self.model.query.count()
    
    def exists(self, id: int) -> bool:
        """Check if record exists"""
        return self.get_by_id(id) is not None
