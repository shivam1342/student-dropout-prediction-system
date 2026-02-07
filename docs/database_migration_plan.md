# Database Migration Plan
**Date:** February 7, 2026  
**Target:** Migrate from single-user to multi-role authentication system  
**Estimated Time:** Day 2 (1 hour)

---

## MIGRATION OVERVIEW

### Current State
- ✅ 8 existing tables: students, alerts, interventions, counselling_logs, risk_predictions, behavioral_data, lms_activities, gamification_profiles
- ✅ No authentication system
- ✅ No user roles
- ✅ ~50 student records (seeded)

### Target State
- ✅ All existing tables preserved
- ✅ 3 new tables: users, teachers, counselors
- ✅ 1 new junction table: teacher_student_assignments
- ✅ New FK columns in existing tables
- ✅ User accounts for all students, teachers, admin
- ✅ Working authentication system

---

## MIGRATION STEPS

### STEP 1: BACKUP DATABASE (5 minutes)
**CRITICAL: Do this FIRST!**

```bash
# Create backup directory
mkdir backups

# Copy entire instance folder
cp -r instance/ backups/instance_backup_$(date +%Y%m%d_%H%M%S)/

# Alternative: SQLite specific backup
sqlite3 instance/educare.db ".backup 'backups/educare_$(date +%Y%m%d_%H%M%S).db'"
```

**Verification:**
```bash
# Check backup exists
ls -lh backups/

# Test backup file
sqlite3 backups/educare_YYYYMMDD_HHMMSS.db "SELECT COUNT(*) FROM students;"
```

---

### STEP 2: CREATE NEW TABLES (10 minutes)

**File:** `utils/migrate_to_multiuser.py`

```python
"""
Database Migration Script: Add Multi-User Authentication
Run this ONCE to add user authentication tables
"""
from app import app, db
from models import Student, Alert, Intervention, CounsellingLog
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_new_tables():
    """Create users, teachers, counselors, and assignment tables"""
    
    with app.app_context():
        print("🔄 Creating new tables...")
        
        # This will create all tables defined in models
        # including the new User, Teacher, Counselor models
        db.create_all()
        
        print("✅ New tables created successfully")

if __name__ == '__main__':
    create_new_tables()
```

**What this does:**
- Creates `users` table
- Creates `teachers` table
- Creates `counselors` table
- Creates `teacher_student_assignments` table
- Does NOT touch existing tables

---

### STEP 3: ADD FOREIGN KEY COLUMNS (10 minutes)

```python
def add_foreign_key_columns():
    """Add FK columns to existing tables"""
    
    with app.app_context():
        print("🔄 Adding foreign key columns...")
        
        # Get database connection
        with db.engine.connect() as conn:
            
            # Add user_id to students (nullable for now)
            conn.execute(db.text("""
                ALTER TABLE students 
                ADD COLUMN user_id INTEGER UNIQUE
            """))
            
            # Add tracking columns to alerts
            conn.execute(db.text("""
                ALTER TABLE alerts 
                ADD COLUMN created_by_user_id INTEGER
            """))
            
            conn.execute(db.text("""
                ALTER TABLE alerts 
                ADD COLUMN assigned_to_user_id INTEGER
            """))
            
            # Add tracking columns to interventions
            conn.execute(db.text("""
                ALTER TABLE interventions 
                ADD COLUMN created_by_user_id INTEGER
            """))
            
            conn.execute(db.text("""
                ALTER TABLE interventions 
                ADD COLUMN assigned_to_user_id INTEGER
            """))
            
            # Add counselor tracking to counselling_logs
            conn.execute(db.text("""
                ALTER TABLE counselling_logs 
                ADD COLUMN counselor_user_id INTEGER
            """))
            
            conn.execute(db.text("""
                ALTER TABLE counselling_logs 
                ADD COLUMN session_status VARCHAR(20) DEFAULT 'scheduled'
            """))
            
            conn.commit()
        
        print("✅ Foreign key columns added successfully")
```

---

### STEP 4: SEED DEFAULT USERS (15 minutes)

```python
def seed_default_users():
    """Create default admin, teacher, and student users"""
    
    with app.app_context():
        from models.user import User
        
        print("🔄 Creating default users...")
        
        # 1. Create Admin User
        admin = User(
            username='admin',
            email='admin@educare.edu',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            full_name='System Administrator',
            department='IT Administration'
        )
        db.session.add(admin)
        
        # 2. Create Teacher Users
        teachers_data = [
            {
                'username': 'teacher.john',
                'email': 'john.doe@educare.edu',
                'password': 'teacher123',
                'full_name': 'John Doe',
                'department': 'Computer Science',
                'subjects': ['Programming', 'Data Structures']
            },
            {
                'username': 'teacher.sarah',
                'email': 'sarah.wilson@educare.edu',
                'password': 'teacher123',
                'full_name': 'Sarah Wilson',
                'department': 'Mathematics',
                'subjects': ['Calculus', 'Statistics']
            }
        ]
        
        for teacher_data in teachers_data:
            user = User(
                username=teacher_data['username'],
                email=teacher_data['email'],
                password_hash=generate_password_hash(teacher_data['password']),
                role='teacher',
                full_name=teacher_data['full_name'],
                department=teacher_data['department']
            )
            db.session.add(user)
            db.session.flush()  # Get user.id
            
            # Create teacher profile
            from models.teacher import Teacher
            teacher = Teacher(
                user_id=user.id,
                department=teacher_data['department'],
                subjects=teacher_data['subjects']
            )
            db.session.add(teacher)
        
        db.session.commit()
        print("✅ Default users created")
```

---

### STEP 5: LINK EXISTING STUDENTS (10 minutes)

```python
def link_existing_students():
    """Create user accounts for existing students and link them"""
    
    with app.app_context():
        from models.user import User
        
        print("🔄 Linking existing students to user accounts...")
        
        students = Student.query.all()
        
        for i, student in enumerate(students, 1):
            # Create user account for student
            username = f"student{i:03d}"  # student001, student002, etc.
            
            user = User(
                username=username,
                email=student.email,
                password_hash=generate_password_hash('student123'),  # Default password
                role='student',
                full_name=student.name
            )
            db.session.add(user)
            db.session.flush()  # Get user.id
            
            # Link student to user
            student.user_id = user.id
            
            if i % 10 == 0:
                db.session.commit()
                print(f"  ✅ Linked {i}/{len(students)} students...")
        
        db.session.commit()
        print(f"✅ All {len(students)} students linked to user accounts")
```

---

### STEP 6: ASSIGN STUDENTS TO TEACHERS (10 minutes)

```python
def assign_students_to_teachers():
    """Create teacher-student assignments"""
    
    with app.app_context():
        from models.teacher import Teacher
        from models.teacher_student_assignment import TeacherStudentAssignment
        
        print("🔄 Assigning students to teachers...")
        
        teachers = Teacher.query.all()
        students = Student.query.all()
        
        # Simple assignment: divide students among teachers
        students_per_teacher = len(students) // len(teachers)
        
        for i, teacher in enumerate(teachers):
            start_idx = i * students_per_teacher
            end_idx = start_idx + students_per_teacher
            
            # Last teacher gets remaining students
            if i == len(teachers) - 1:
                end_idx = len(students)
            
            assigned_students = students[start_idx:end_idx]
            
            for student in assigned_students:
                assignment = TeacherStudentAssignment(
                    teacher_id=teacher.id,
                    student_id=student.id,
                    course_name='General Education',
                    semester='Spring 2026',
                    academic_year='2025-2026'
                )
                db.session.add(assignment)
            
            print(f"  ✅ Assigned {len(assigned_students)} students to {teacher.user.full_name}")
        
        db.session.commit()
        print("✅ Student assignments completed")
```

---

### STEP 7: CREATE INDEXES (5 minutes)

```python
def create_indexes():
    """Create indexes for foreign keys"""
    
    with app.app_context():
        print("🔄 Creating indexes...")
        
        with db.engine.connect() as conn:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_creator ON alerts(created_by_user_id)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_assignee ON alerts(assigned_to_user_id)",
                "CREATE INDEX IF NOT EXISTS idx_interventions_creator ON interventions(created_by_user_id)",
                "CREATE INDEX IF NOT EXISTS idx_interventions_assignee ON interventions(assigned_to_user_id)",
                "CREATE INDEX IF NOT EXISTS idx_counselling_counselor ON counselling_logs(counselor_user_id)",
                "CREATE INDEX IF NOT EXISTS idx_teachers_user ON teachers(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_assignments_teacher ON teacher_student_assignments(teacher_id)",
                "CREATE INDEX IF NOT EXISTS idx_assignments_student ON teacher_student_assignments(student_id)"
            ]
            
            for index_sql in indexes:
                conn.execute(db.text(index_sql))
            
            conn.commit()
        
        print("✅ Indexes created")
```

---

### STEP 8: VERIFICATION (5 minutes)

```python
def verify_migration():
    """Verify migration completed successfully"""
    
    with app.app_context():
        print("\n" + "="*70)
        print("MIGRATION VERIFICATION")
        print("="*70)
        
        # Count records
        from models.user import User
        from models.teacher import Teacher
        
        user_count = User.query.count()
        student_count = Student.query.filter(Student.user_id.isnot(None)).count()
        teacher_count = Teacher.query.count()
        assignment_count = db.session.query(TeacherStudentAssignment).count()
        
        print(f"✅ Users created: {user_count}")
        print(f"✅ Students linked: {student_count}")
        print(f"✅ Teachers created: {teacher_count}")
        print(f"✅ Assignments created: {assignment_count}")
        
        # Test a relationship
        test_student = Student.query.filter(Student.user_id.isnot(None)).first()
        if test_student and test_student.user:
            print(f"\n✅ Sample relationship test:")
            print(f"   Student: {test_student.name}")
            print(f"   Username: {test_student.user.username}")
            print(f"   Role: {test_student.user.role}")
        
        # Test teacher-student assignment
        test_teacher = Teacher.query.first()
        if test_teacher:
            assigned_count = db.session.query(TeacherStudentAssignment)\
                .filter_by(teacher_id=test_teacher.id).count()
            print(f"\n✅ Teacher assignment test:")
            print(f"   Teacher: {test_teacher.user.full_name}")
            print(f"   Students assigned: {assigned_count}")
        
        print("\n" + "="*70)
        print("MIGRATION COMPLETED SUCCESSFULLY! 🎉")
        print("="*70)
```

---

## COMPLETE MIGRATION SCRIPT

**File:** `utils/migrate_to_multiuser.py`

```python
"""
Complete Database Migration Script
Adds multi-user authentication to EduCare system
"""
from app import app, db
from models import Student, Alert, Intervention, CounsellingLog
from werkzeug.security import generate_password_hash
from datetime import datetime
import sys

def main():
    """Run complete migration"""
    
    print("\n" + "="*70)
    print("EDUCARE DATABASE MIGRATION TO MULTI-USER SYSTEM")
    print("="*70)
    print("\n⚠️  WARNING: This will modify your database!")
    print("Make sure you have backed up your database first.\n")
    
    response = input("Continue with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        sys.exit(0)
    
    try:
        # Step 1: Create new tables
        create_new_tables()
        
        # Step 2: Add FK columns
        add_foreign_key_columns()
        
        # Step 3: Seed default users
        seed_default_users()
        
        # Step 4: Link existing students
        link_existing_students()
        
        # Step 5: Assign students to teachers
        assign_students_to_teachers()
        
        # Step 6: Create indexes
        create_indexes()
        
        # Step 7: Verify
        verify_migration()
        
        print("\n✅ Migration completed successfully!")
        print("\n📝 Default credentials:")
        print("   Admin: admin / admin123")
        print("   Teacher: teacher.john / teacher123")
        print("   Teacher: teacher.sarah / teacher123")
        print("   Students: student001 / student123 (and so on)")
        print("\n⚠️  IMPORTANT: Change these passwords in production!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Rolling back changes...")
        db.session.rollback()
        print("Please restore from backup and check the error.")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

---

## RUNNING THE MIGRATION

### Command Line
```bash
# 1. Backup database
cp -r instance/ backups/instance_backup_$(date +%Y%m%d)/

# 2. Run migration
python utils/migrate_to_multiuser.py

# 3. Verify
python -c "from app import app, db; from models.user import User; \
           app.app_context().push(); print(f'Users: {User.query.count()}')"
```

---

## ROLLBACK PLAN

If migration fails:

```bash
# 1. Stop the application
# Kill Flask process

# 2. Restore backup
rm -rf instance/
cp -r backups/instance_backup_YYYYMMDD/ instance/

# 3. Restart application
python app.py
```

---

## POST-MIGRATION CHECKLIST

- [ ] Backup created and verified
- [ ] Migration script ran without errors
- [ ] User count matches expected (1 admin + 2 teachers + N students)
- [ ] Students linked to user accounts
- [ ] Teacher-student assignments created
- [ ] Can log in as admin (admin/admin123)
- [ ] Can log in as teacher (teacher.john/teacher123)
- [ ] Can log in as student (student001/student123)
- [ ] Existing student data intact
- [ ] Existing alerts/interventions intact
- [ ] ML predictions still work

---

## TROUBLESHOOTING

### Issue: "Table already exists"
**Solution:** Tables were already created. Skip Step 2 or drop tables first.

### Issue: "Foreign key constraint failed"
**Solution:** Check that parent records exist before adding FKs.

### Issue: "Column already exists"
**Solution:** Columns were already added. This is safe to ignore.

### Issue: "Cannot add NOT NULL column"
**Solution:** All new FK columns are NULLABLE. Check migration script.

### Issue: "Duplicate username"
**Solution:** Clear existing users first or use unique username generation.

---

## ESTIMATED TIME

| Step | Task | Time |
|------|------|------|
| 1 | Backup database | 5 min |
| 2 | Create new tables | 10 min |
| 3 | Add FK columns | 10 min |
| 4 | Seed default users | 15 min |
| 5 | Link existing students | 10 min |
| 6 | Assign students to teachers | 10 min |
| 7 | Create indexes | 5 min |
| 8 | Verification | 5 min |
| **TOTAL** | | **70 min** |

*Fits within Day 2's 1-hour window if no issues*

---

## TESTING PLAN

After migration, test these scenarios:

1. **Authentication:**
   - [ ] Admin can log in
   - [ ] Teacher can log in
   - [ ] Student can log in
   - [ ] Wrong password fails
   - [ ] Sessions persist across page reloads

2. **Relationships:**
   - [ ] Student has linked user account
   - [ ] Teacher can see assigned students
   - [ ] Admin can see all users

3. **Data Integrity:**
   - [ ] All existing students preserved
   - [ ] All alerts preserved
   - [ ] All interventions preserved
   - [ ] ML predictions still accessible

4. **Queries:**
   - [ ] Can get students by teacher
   - [ ] Can get alerts by student
   - [ ] Can filter by user role

---

**END OF MIGRATION PLAN**

✅ Ready for Day 2 implementation!
