# DAY 1: Foundation & Core Restructuring - Detailed Checklist

## Overview
Today we'll set up the new structure and implement the Repository pattern. Everything will be tested on localhost after each major step.

---

## PHASE 1: Setup New Structure (30 min)

### Step 1.1: Create Directory Structure
```powershell
# Run these commands in terminal
New-Item -ItemType Directory -Path app
New-Item -ItemType Directory -Path app/models
New-Item -ItemType Directory -Path app/repositories
New-Item -ItemType Directory -Path app/services
New-Item -ItemType Directory -Path app/routes
New-Item -ItemType Directory -Path app/ml
New-Item -ItemType Directory -Path app/ml/models
New-Item -ItemType Directory -Path app/ml/pipeline
New-Item -ItemType Directory -Path app/ml/predictors
New-Item -ItemType Directory -Path app/utils
New-Item -ItemType Directory -Path app/cli
```

### Step 1.2: Create __init__.py Files
Create empty `__init__.py` in:
- [ ] app/
- [ ] app/models/
- [ ] app/repositories/
- [ ] app/services/
- [ ] app/routes/
- [ ] app/ml/
- [ ] app/ml/pipeline/
- [ ] app/ml/predictors/
- [ ] app/utils/
- [ ] app/cli/

### Step 1.3: Move Existing Files
- [ ] Move `models/*.py` → `app/models/`
- [ ] Move `routes/*.py` → `app/routes/`
- [ ] Move `static/` → `app/static/`
- [ ] Move `templates/` → `app/templates/`
- [ ] Move `ml/*.pkl` → `app/ml/models/`
- [ ] Move `ml/*.py` → `app/ml/` (we'll reorganize later)
- [ ] Keep `instance/` at root level

### Step 1.4: Create New Entry Point (run.py)
- [ ] Create `run.py` at root
- [ ] Simple 10-line file that imports and runs app

### Step 1.5: TEST CHECKPOINT ✅
```powershell
python run.py
```
**Expected**: Flask starts, but may have import errors (we'll fix next)

---

## PHASE 2: Configuration & Extensions (15 min)

### Step 2.1: Update Configuration
- [ ] Move `app_config.py` → `app/config.py`
- [ ] Add ML configuration section
- [ ] Add logging configuration
- [ ] Remove all Unicode emoji from configs

### Step 2.2: Update Extensions
- [ ] Move `extensions.py` → `app/extensions.py`
- [ ] Add Flask-Login setup
- [ ] Add any other extensions needed

### Step 2.3: Update App Factory
- [ ] Create `app/__init__.py` with `create_app()` function
- [ ] Import from new locations
- [ ] Register blueprints from new locations
- [ ] Clean up all Unicode characters

### Step 2.4: TEST CHECKPOINT ✅
```powershell
python run.py
```
**Expected**: Flask starts successfully, no errors
**Test**: Visit http://127.0.0.1:5000 - should see homepage

---

## PHASE 3: Repository Layer (45 min)

### Step 3.1: Create Base Repository
- [ ] Create `app/repositories/base_repository.py`
- [ ] Implement: `get_by_id()`, `get_all()`, `create()`, `update()`, `delete()`
- [ ] Add error handling for each method

**Template:**
```python
from app.extensions import db
from typing import List, Optional, Type, TypeVar

T = TypeVar('T', bound=db.Model)

class BaseRepository:
    """Base repository with common CRUD operations"""
    model: Type[T] = None  # Override in subclass
    
    def __init__(self):
        if self.model is None:
            raise NotImplementedError("Subclass must define 'model' attribute")
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get a single record by ID"""
        return self.model.query.get(id)
    
    def get_all(self) -> List[T]:
        """Get all records"""
        return self.model.query.all()
    
    def create(self, **kwargs) -> T:
        """Create a new record"""
        obj = self.model(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update an existing record"""
        obj = self.get_by_id(id)
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            db.session.commit()
        return obj
    
    def delete(self, id: int) -> bool:
        """Delete a record by ID"""
        obj = self.get_by_id(id)
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return True
        return False
    
    def filter_by(self, **kwargs) -> List[T]:
        """Filter records by arbitrary fields"""
        return self.model.query.filter_by(**kwargs).all()
```

### Step 3.2: Create Student Repository
- [ ] Create `app/repositories/student_repository.py`
- [ ] Inherit from `BaseRepository`
- [ ] Add custom methods: `get_high_risk_students()`, `search_by_name()`

**Template:**
```python
from app.repositories.base_repository import BaseRepository
from app.models.student import Student
from typing import List

class StudentRepository(BaseRepository):
    """Repository for Student model"""
    model = Student
    
    def get_high_risk_students(self, threshold: float = 0.7) -> List[Student]:
        """Get students with risk score above threshold"""
        # Add custom query logic
        pass
    
    def search_by_name(self, name: str) -> List[Student]:
        """Search students by name (partial match)"""
        return self.model.query.filter(
            self.model.first_name.ilike(f"%{name}%") | 
            self.model.last_name.ilike(f"%{name}%")
        ).all()
    
    def get_with_latest_prediction(self, student_id: int):
        """Get student with their latest risk prediction"""
        # Join with RiskPrediction and return both
        pass
```

### Step 3.3: Create Other Repositories
Create repositories for each model:
- [ ] `app/repositories/alert_repository.py`
- [ ] `app/repositories/intervention_repository.py`
- [ ] `app/repositories/risk_prediction_repository.py`
- [ ] `app/repositories/gamification_repository.py`
- [ ] `app/repositories/counselling_repository.py`

Each repository:
- Inherits from `BaseRepository`
- Sets `model = YourModel`
- Adds 1-2 custom methods specific to that model

### Step 3.4: Create Repository Index
- [ ] Update `app/repositories/__init__.py` to export all repositories

**Template:**
```python
from app.repositories.base_repository import BaseRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.intervention_repository import InterventionRepository
# ... import others

__all__ = [
    'BaseRepository',
    'StudentRepository',
    'AlertRepository',
    'InterventionRepository',
    # ... export others
]
```

### Step 3.5: TEST CHECKPOINT ✅
Create quick test script: `test_repositories.py`
```python
from app import create_app
from app.repositories import StudentRepository

app = create_app()
with app.app_context():
    repo = StudentRepository()
    
    # Test get_all
    students = repo.get_all()
    print(f"[OK] Found {len(students)} students")
    
    # Test get_by_id
    if students:
        student = repo.get_by_id(students[0].id)
        print(f"[OK] Retrieved student: {student.first_name}")
    
    print("[SUCCESS] All repository tests passed!")
```

Run: `python test_repositories.py`

---

## DAY 1 FINAL CHECKLIST

Before ending Day 1, verify:
- [ ] Flask app starts with `python run.py`
- [ ] Homepage loads at http://127.0.0.1:5000
- [ ] No Unicode errors in terminal
- [ ] All models moved to `app/models/`
- [ ] All routes moved to `app/routes/`
- [ ] Repository pattern implemented and tested
- [ ] Can retrieve students using `StudentRepository`

## Git Commit
```bash
git add .
git commit -m "refactor: Day 1 - Implement repository pattern and restructure project"
git push origin main
```

---

## Troubleshooting Common Issues

### Import Errors
- Check all `__init__.py` files exist
- Update imports to use `app.models` instead of `models`
- Update imports to use `app.routes` instead of `routes`

### Database Errors
- Make sure `instance/` folder exists
- Check database URI in config
- Run `db.create_all()` if needed

### Unicode Errors
- Replace all emoji in print statements
- Use ASCII characters only: OK, ERROR, WARNING, INFO

---

## Notes for Tomorrow (Day 2)
- Service layer will use these repositories
- No more direct `Model.query.get()` in routes
- All database access goes through repositories
- ML pipeline will be separate from services
