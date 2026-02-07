# User Model Database Schema
**Date:** February 7, 2026  
**Purpose:** Multi-role authentication system for EduCare

---

## 1. USER MODEL (New Table: `users`)

```sql
CREATE TABLE users (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    username            VARCHAR(50) UNIQUE NOT NULL,
    email               VARCHAR(100) UNIQUE NOT NULL,
    password_hash       VARCHAR(256) NOT NULL,
    role                VARCHAR(20) NOT NULL,  -- 'student', 'teacher', 'admin', 'counselor'
    full_name           VARCHAR(100) NOT NULL,
    department          VARCHAR(100),  -- For teachers/counselors/admin
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login          DATETIME,
    profile_picture_url VARCHAR(255),
    phone               VARCHAR(20)
);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

### Fields Explanation:
- **id**: Primary key, auto-increment
- **username**: Unique login identifier (e.g., "student001", "teacher.john")
- **email**: Unique email for password recovery
- **password_hash**: Hashed password (Werkzeug's generate_password_hash)
- **role**: User role - determines dashboard and permissions
- **full_name**: Display name (e.g., "John Doe")
- **department**: For teachers (e.g., "Computer Science"), counselors (e.g., "Student Affairs")
- **is_active**: Soft delete flag (deactivate users without deleting)
- **created_at**: Account creation timestamp
- **last_login**: Track user activity
- **profile_picture_url**: Optional profile image
- **phone**: Optional contact number

---

## 2. TEACHER MODEL (New Table: `teachers`)

```sql
CREATE TABLE teachers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER UNIQUE NOT NULL,
    employee_id     VARCHAR(50) UNIQUE,
    department      VARCHAR(100) NOT NULL,
    subjects        TEXT,  -- JSON array: ["Math", "Physics"]
    office_location VARCHAR(100),
    office_hours    TEXT,  -- JSON: {"Monday": "10:00-12:00", ...}
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_teachers_user_id ON teachers(user_id);
CREATE INDEX idx_teachers_department ON teachers(department);
```

---

## 3. COUNSELOR MODEL (New Table: `counselors`)

```sql
CREATE TABLE counselors (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER UNIQUE NOT NULL,
    employee_id             VARCHAR(50) UNIQUE,
    department              VARCHAR(100) NOT NULL,
    specialization          VARCHAR(100),  -- e.g., "Academic", "Career", "Mental Health"
    availability_schedule   TEXT,  -- JSON: {"Monday": ["09:00-12:00", "14:00-17:00"], ...}
    max_students_per_day    INTEGER DEFAULT 10,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_counselors_user_id ON counselors(user_id);
CREATE INDEX idx_counselors_specialization ON counselors(specialization);
```

---

## 4. TEACHER-STUDENT ASSIGNMENT (New Table: `teacher_student_assignments`)

```sql
CREATE TABLE teacher_student_assignments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id      INTEGER NOT NULL,
    student_id      INTEGER NOT NULL,
    course_name     VARCHAR(100),
    semester        VARCHAR(20),  -- e.g., "Fall 2026", "Spring 2026"
    academic_year   VARCHAR(20),  -- e.g., "2025-2026"
    assigned_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active       BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    
    UNIQUE(teacher_id, student_id, course_name, semester)  -- Prevent duplicates
);

CREATE INDEX idx_tsa_teacher ON teacher_student_assignments(teacher_id);
CREATE INDEX idx_tsa_student ON teacher_student_assignments(student_id);
CREATE INDEX idx_tsa_active ON teacher_student_assignments(is_active);
```

**Why separate assignment table?**
- Many-to-many relationship (one teacher → many students, one student → many teachers)
- Allows historical tracking (past assignments)
- Course-specific assignments

---

## 5. UPDATED EXISTING MODELS

### 5.1 Student Model (UPDATE `students` table)
```sql
-- Add new column
ALTER TABLE students ADD COLUMN user_id INTEGER UNIQUE;
ALTER TABLE students ADD CONSTRAINT fk_student_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

CREATE INDEX idx_students_user_id ON students(user_id);
```

**Note:** `user_id` is NULLABLE initially for backward compatibility with existing student records. During migration, we'll create user accounts for existing students.

---

### 5.2 Alert Model (UPDATE `alerts` table)
```sql
-- Add columns for tracking
ALTER TABLE alerts ADD COLUMN created_by_user_id INTEGER;
ALTER TABLE alerts ADD COLUMN assigned_to_user_id INTEGER;

ALTER TABLE alerts ADD CONSTRAINT fk_alert_creator 
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL;
    
ALTER TABLE alerts ADD CONSTRAINT fk_alert_assignee 
    FOREIGN KEY (assigned_to_user_id) REFERENCES users(id) ON DELETE SET NULL;

CREATE INDEX idx_alerts_creator ON alerts(created_by_user_id);
CREATE INDEX idx_alerts_assignee ON alerts(assigned_to_user_id);
```

**Changes:**
- `created_by_user_id`: Who generated the alert (admin/system)
- `assigned_to_user_id`: Teacher/counselor assigned to handle it
- Keep `acknowledged_by` and `resolved_by` as text for now (can be names or external references)

---

### 5.3 Intervention Model (UPDATE `interventions` table)
```sql
-- Add columns for user tracking
ALTER TABLE interventions ADD COLUMN created_by_user_id INTEGER;
ALTER TABLE interventions ADD COLUMN assigned_to_user_id INTEGER;

ALTER TABLE interventions ADD CONSTRAINT fk_intervention_creator 
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL;
    
ALTER TABLE interventions ADD CONSTRAINT fk_intervention_assignee 
    FOREIGN KEY (assigned_to_user_id) REFERENCES users(id) ON DELETE SET NULL;

CREATE INDEX idx_interventions_creator ON interventions(created_by_user_id);
CREATE INDEX idx_interventions_assignee ON interventions(assigned_to_user_id);
```

**Note:** Keep the existing `assigned_to` text field for backward compatibility. New code should use `assigned_to_user_id`.

---

### 5.4 Counselling Log Model (UPDATE `counselling_logs` table)
```sql
-- Add counselor tracking
ALTER TABLE counselling_logs ADD COLUMN counselor_user_id INTEGER;
ALTER TABLE counselling_logs ADD COLUMN session_status VARCHAR(20) DEFAULT 'scheduled';
    -- Values: 'scheduled', 'in_progress', 'completed', 'cancelled', 'no_show'

ALTER TABLE counselling_logs ADD CONSTRAINT fk_counselling_counselor 
    FOREIGN KEY (counselor_user_id) REFERENCES users(id) ON DELETE SET NULL;

CREATE INDEX idx_counselling_counselor ON counselling_logs(counselor_user_id);
CREATE INDEX idx_counselling_session_status ON counselling_logs(session_status);
```

---

## 6. RELATIONSHIPS DIAGRAM

```
┌─────────────────┐
│     USERS       │
│  (Central Hub)  │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    │         │         │          │
    ▼         ▼         ▼          ▼
┌────────┐ ┌──────────┐ ┌───────┐ ┌──────────┐
│Student │ │ Teacher  │ │ Admin │ │Counselor │
│(1-to-1)│ │(1-to-1)  │ │(role) │ │(1-to-1)  │
└───┬────┘ └────┬─────┘ └───────┘ └────┬─────┘
    │           │                       │
    │           │                       │
    │      ┌────┴─────────┐            │
    │      │  Teacher-    │            │
    │      │  Student     │            │
    │      │ Assignments  │            │
    │      │ (Many-Many)  │            │
    │      └──────────────┘            │
    │                                  │
    ├──────────────┬───────────────────┤
    │              │                   │
    ▼              ▼                   ▼
┌─────────┐  ┌──────────────┐  ┌──────────────┐
│ Alerts  │  │Interventions │  │ Counselling  │
│         │  │              │  │    Logs      │
└─────────┘  └──────────────┘  └──────────────┘
   ▲ ▲            ▲ ▲               ▲
   │ │            │ │               │
   │ └────────────┘ └───────────────┘
   │   created_by    assigned_to
   │   (Teacher/Admin/Counselor)
   │
   └─── student_id (existing)
```

---

## 7. USER ROLES & PERMISSIONS MATRIX

| Feature                  | Student | Teacher | Counselor | Admin |
|--------------------------|---------|---------|-----------|-------|
| View own profile         | ✓       | ✓       | ✓         | ✓     |
| View all students        | ✗       | Own only| All       | All   |
| Edit student data        | Own     | ✗       | ✗         | All   |
| Create interventions     | ✗       | Own students | All  | All   |
| View alerts              | Own     | Own students | All  | All   |
| Create alerts            | ✗       | ✗       | ✓         | ✓     |
| View ML predictions      | Own     | Own students | All  | All   |
| Manage users             | ✗       | ✗       | ✗         | ✓     |
| View gamification        | Own     | Own students | All  | All   |
| Counselling sessions     | Own     | Refer   | Manage    | View  |
| System settings          | ✗       | ✗       | ✗         | ✓     |

---

## 8. SAMPLE DATA STRUCTURE

### Example User Records:
```python
# Admin
{
    "username": "admin",
    "email": "admin@educare.edu",
    "password_hash": "hashed_password",
    "role": "admin",
    "full_name": "System Administrator",
    "department": "IT"
}

# Teacher
{
    "username": "teacher.john",
    "email": "john.doe@educare.edu",
    "password_hash": "hashed_password",
    "role": "teacher",
    "full_name": "John Doe",
    "department": "Computer Science"
}

# Student
{
    "username": "student001",
    "email": "student001@educare.edu",
    "password_hash": "hashed_password",
    "role": "student",
    "full_name": "Alice Johnson",
    "department": None  # Students don't have departments
}

# Counselor
{
    "username": "counselor.jane",
    "email": "jane.smith@educare.edu",
    "password_hash": "hashed_password",
    "role": "counselor",
    "full_name": "Jane Smith",
    "department": "Student Affairs"
}
```

---

## 9. AUTHENTICATION FLOW

```
User Login → Verify credentials → Load user record → Check role
                    ↓
            Session created with:
            - user_id
            - username
            - role
            - full_name
                    ↓
            Redirect to role-specific dashboard:
            - student → /student/dashboard
            - teacher → /teacher/dashboard
            - counselor → /counselor/dashboard
            - admin → /admin/dashboard
```

---

## 10. SECURITY CONSIDERATIONS

1. **Password Hashing**: Use Werkzeug's `generate_password_hash()` with default settings
2. **Session Security**: 
   - Set `SECRET_KEY` in environment variables
   - Use `SESSION_COOKIE_SECURE = True` in production
   - Set `SESSION_COOKIE_HTTPONLY = True`
3. **SQL Injection Prevention**: SQLAlchemy ORM handles parameterization
4. **Role Verification**: Every route must check user role via decorators
5. **Foreign Key Constraints**: Use `ON DELETE CASCADE` or `SET NULL` appropriately

---

## 11. MIGRATION NOTES

**Backward Compatibility:**
- All new foreign key columns are NULLABLE
- Existing records won't break
- Migration script will:
  1. Create new tables (users, teachers, counselors, assignments)
  2. Add columns to existing tables
  3. Create user accounts for existing students
  4. Link existing records to new user accounts

**Rollback Plan:**
- Backup database before migration
- Keep migration script reversible
- Test on copy of database first

---

**End of Schema Document**
