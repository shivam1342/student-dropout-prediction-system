# Foreign Key Relationships Design
**Date:** February 7, 2026  
**Purpose:** Complete FK mapping for multi-role authentication

---

## RELATIONSHIP TYPES

### 1. ONE-TO-ONE Relationships

| Parent Table | Child Table | FK Column      | Explanation |
|--------------|-------------|----------------|-------------|
| `users`      | `students`  | `user_id`      | Each student has one user account |
| `users`      | `teachers`  | `user_id`      | Each teacher has one user account |
| `users`      | `counselors`| `user_id`      | Each counselor has one user account |

**Implementation:**
```python
# In Student model
user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=True)
user = db.relationship('User', backref=db.backref('student_profile', uselist=False))

# In Teacher model
user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
user = db.relationship('User', backref=db.backref('teacher_profile', uselist=False))

# In Counselor model
user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
user = db.relationship('User', backref=db.backref('counselor_profile', uselist=False))
```

---

### 2. ONE-TO-MANY Relationships

| Parent (One)    | Child (Many)        | FK Column          | Explanation |
|-----------------|---------------------|-------------------|-------------|
| `students`      | `alerts`            | `student_id`      | One student → many alerts (EXISTING) |
| `students`      | `interventions`     | `student_id`      | One student → many interventions (EXISTING) |
| `students`      | `risk_predictions`  | `student_id`      | One student → many predictions (EXISTING) |
| `students`      | `counselling_logs`  | `student_id`      | One student → many sessions (EXISTING) |
| `students`      | `behavioral_data`   | `student_id`      | One student → many behavior records (EXISTING) |
| `students`      | `lms_activities`    | `student_id`      | One student → many LMS activities (EXISTING) |
| `users`         | `alerts` (created)  | `created_by_user_id` | One user → many alerts created (NEW) |
| `users`         | `interventions` (created) | `created_by_user_id` | One user → many interventions created (NEW) |

**Implementation:**
```python
# In Alert model
created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
creator = db.relationship('User', foreign_keys=[created_by_user_id], 
                         backref='alerts_created')

# In Intervention model
created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
creator = db.relationship('User', foreign_keys=[created_by_user_id], 
                         backref='interventions_created')
```

---

### 3. MANY-TO-MANY Relationships

| Entity A   | Entity B  | Junction Table | Explanation |
|------------|-----------|----------------|-------------|
| `teachers` | `students`| `teacher_student_assignments` | Teachers teach multiple students; students have multiple teachers |

**Implementation:**
```python
# Junction table model
class TeacherStudentAssignment(db.Model):
    __tablename__ = 'teacher_student_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_name = db.Column(db.String(100))
    semester = db.Column(db.String(20))
    
    teacher = db.relationship('Teacher', backref='student_assignments')
    student = db.relationship('Student', backref='teacher_assignments')

# In Teacher model
students = db.relationship('Student', secondary='teacher_student_assignments',
                          backref='teachers', lazy='dynamic')

# Usage:
# teacher.students - Get all students assigned to this teacher
# student.teachers - Get all teachers for this student
```

---

### 4. SELF-REFERENCING Relationships (Future Enhancement)

| Table    | FK Column    | Purpose |
|----------|--------------|---------|
| `users`  | `mentor_id`  | Student → Student mentorship |
| `users`  | `supervisor_id` | Teacher → Department Head |

**Not implementing in MVP, but design consideration:**
```python
# Future: User mentorship
mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
mentor = db.relationship('User', remote_side=[id], backref='mentees')
```

---

## COMPLETE FK MAPPING BY TABLE

### USERS Table (New)
```python
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    # ... other fields ...
    
    # Relationships (One-to-One)
    student_profile = db.relationship('Student', backref='user', uselist=False)
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False)
    counselor_profile = db.relationship('Counselor', backref='user', uselist=False)
    
    # Relationships (One-to-Many) - Things created by this user
    alerts_created = db.relationship('Alert', foreign_keys='Alert.created_by_user_id',
                                     backref='creator', lazy='dynamic')
    interventions_created = db.relationship('Intervention', 
                                           foreign_keys='Intervention.created_by_user_id',
                                           backref='creator', lazy='dynamic')
    counselling_sessions = db.relationship('CounsellingLog',
                                          foreign_keys='CounsellingLog.counselor_user_id',
                                          backref='counselor', lazy='dynamic')
```

---

### STUDENTS Table (Existing - Add FK)
```python
class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # NEW: Link to user account
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=True)
    
    # EXISTING: One-to-Many relationships (student is parent)
    predictions = db.relationship('RiskPrediction', backref='student', lazy=True)
    counselling_logs = db.relationship('CounsellingLog', backref='student', lazy=True)
    lms_activities = db.relationship('LMSActivity', backref='student', lazy=True)
    behavioral_data = db.relationship('BehavioralData', backref='student', lazy=True)
    alerts = db.relationship('Alert', backref='student', lazy=True)
    interventions = db.relationship('Intervention', backref='student', lazy=True)
    gamification_profile = db.relationship('GamificationProfile', backref='student', uselist=False)
    
    # NEW: Many-to-Many with teachers
    teachers = db.relationship('Teacher', secondary='teacher_student_assignments',
                              backref='students', lazy='dynamic')
```

---

### TEACHERS Table (New)
```python
class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Many-to-Many with students
    students = db.relationship('Student', secondary='teacher_student_assignments',
                              backref='assigned_teachers', lazy='dynamic')
```

---

### COUNSELORS Table (New)
```python
class Counselor(db.Model):
    __tablename__ = 'counselors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # One-to-Many: counselor → sessions (via User relationship)
```

---

### ALERTS Table (Existing - Add FKs)
```python
class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # EXISTING FK
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # NEW FKs for tracking
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
```

---

### INTERVENTIONS Table (Existing - Add FKs)
```python
class Intervention(db.Model):
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # EXISTING FK
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.id'), nullable=True)
    
    # NEW FKs for tracking
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Keep existing 'assigned_to' text field for backward compatibility
```

---

### COUNSELLING_LOGS Table (Existing - Add FK)
```python
class CounsellingLog(db.Model):
    __tablename__ = 'counselling_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # EXISTING FK
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # NEW FK
    counselor_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
```

---

## CASCADE RULES

### DELETE Cascades
| Parent → Child | Cascade Rule | Reason |
|----------------|--------------|---------|
| `users` → `students` | CASCADE | If user deleted, student profile should be deleted |
| `users` → `teachers` | CASCADE | If user deleted, teacher profile should be deleted |
| `users` → `counselors` | CASCADE | If user deleted, counselor profile should be deleted |
| `students` → `alerts` | CASCADE | If student deleted, their alerts should be deleted |
| `students` → `interventions` | CASCADE | If student deleted, their interventions should be deleted |
| `students` → `predictions` | CASCADE | If student deleted, their predictions should be deleted |
| `students` → `counselling_logs` | CASCADE | If student deleted, their sessions should be deleted |
| `teachers` → `assignments` | CASCADE | If teacher deleted, their assignments should be deleted |

### SET NULL Rules
| Parent → Child | Cascade Rule | Reason |
|----------------|--------------|---------|
| `users` → `alerts.created_by` | SET NULL | Keep alert even if creator deleted |
| `users` → `interventions.created_by` | SET NULL | Keep intervention even if creator deleted |
| `users` → `alerts.assigned_to` | SET NULL | Keep alert even if assignee deleted |
| `users` → `interventions.assigned_to` | SET NULL | Keep intervention even if assignee deleted |

**Implementation:**
```python
# CASCADE example
user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

# SET NULL example
created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
```

---

## QUERIES ENABLED BY FKs

### 1. Get all students for a teacher
```python
# Via relationship
teacher = Teacher.query.filter_by(user_id=current_user.id).first()
students = teacher.students.all()

# Via join
students = db.session.query(Student)\
    .join(TeacherStudentAssignment)\
    .filter(TeacherStudentAssignment.teacher_id == teacher.id)\
    .all()
```

### 2. Get all alerts created by a user
```python
alerts = Alert.query.filter_by(created_by_user_id=user.id).all()
# Or via relationship
alerts = user.alerts_created.all()
```

### 3. Get student's user account
```python
student = Student.query.get(student_id)
user = student.user  # Direct access via relationship
```

### 4. Get all interventions assigned to a counselor
```python
interventions = Intervention.query.filter_by(assigned_to_user_id=counselor_user.id).all()
```

### 5. Get all counselling sessions for a counselor
```python
sessions = CounsellingLog.query.filter_by(counselor_user_id=counselor_user.id).all()
# Or via relationship
sessions = counselor_user.counselling_sessions.all()
```

---

## INTEGRITY CONSTRAINTS

### UNIQUE Constraints
```python
# User model
username = db.Column(db.String(50), unique=True, nullable=False)
email = db.Column(db.String(100), unique=True, nullable=False)

# Teacher model
user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)

# Student model  
user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)

# Assignment table
__table_args__ = (
    db.UniqueConstraint('teacher_id', 'student_id', 'course_name', 'semester'),
)
```

### CHECK Constraints
```python
# User role validation
role = db.Column(db.String(20), nullable=False)
# In application code:
assert role in ['student', 'teacher', 'counselor', 'admin']

# Session status validation
session_status = db.Column(db.String(20), default='scheduled')
# Valid values: 'scheduled', 'in_progress', 'completed', 'cancelled', 'no_show'
```

---

## MIGRATION STRATEGY

1. **Create new tables first** (users, teachers, counselors, assignments)
2. **Add nullable FK columns** to existing tables
3. **Populate user accounts** for existing students
4. **Link existing records** to new user accounts
5. **Add indexes** for performance
6. **Test queries** to verify relationships work

---

**End of FK Relationships Document**
