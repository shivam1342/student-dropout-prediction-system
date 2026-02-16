"""
Database Utilities
Includes database seeding and maintenance functions
"""
import random
from datetime import datetime, timedelta
from app.models import Student, LMSActivity, BehavioralData, GamificationProfile, User, Teacher, TeacherStudentAssignment
from app.controllers.alert_controller import AlertController
from app.extensions import db
from faker import Faker

fake = Faker()

def seed_db(num_students=50):
    """
    Seeds the database with dummy student data including LMS activity,
    behavioral data, and generates alerts for at-risk students.
    This function is called by the 'flask seed-db' command.
    """
    # Check if data already exists
    if Student.query.count() > 0:
        print("Database already seeded.")
        return

    print(f"🌱 Seeding database with {num_students} students...")
    
    students_to_add = []
    
    # Create diverse student profiles including at-risk students
    for i in range(num_students):
        # Determine student risk profile (20% high-risk, 30% medium-risk, 50% low-risk)
        risk_level = random.choices(['high', 'medium', 'low'], weights=[0.2, 0.3, 0.5])[0]
        
        # Base student data
        student = Student(
            name=fake.name(),
            email=fake.unique.email(),
            age_at_enrollment=random.randint(18, 25),
            previous_qualification=random.randint(1, 5),
        )
        
        # Configure student based on risk level
        if risk_level == 'high':
            # High-risk: Poor grades, financial issues, low engagement
            student.scholarship_holder = False
            student.debtor = random.choice([True, True, False])  # 67% are debtors
            student.tuition_fees_up_to_date = random.choice([False, False, True])  # 67% behind
            student.curricular_units_1st_sem_grade = round(random.uniform(8, 13), 2)  # Low grades
            student.curricular_units_2nd_sem_grade = round(random.uniform(8, 12), 2)
            student.gdp = round(random.uniform(-2, 0), 2)
            
        elif risk_level == 'medium':
            # Medium-risk: Average grades, some issues
            student.scholarship_holder = random.choice([True, False])
            student.debtor = random.choice([True, False])
            student.tuition_fees_up_to_date = random.choice([True, False])
            student.curricular_units_1st_sem_grade = round(random.uniform(12, 15), 2)
            student.curricular_units_2nd_sem_grade = round(random.uniform(12, 15), 2)
            student.gdp = round(random.uniform(-1, 2), 2)
            
        else:  # low-risk
            # Low-risk: Good grades, no financial issues, high engagement
            student.scholarship_holder = random.choice([True, False])
            student.debtor = False
            student.tuition_fees_up_to_date = True
            student.curricular_units_1st_sem_grade = round(random.uniform(15, 18), 2)
            student.curricular_units_2nd_sem_grade = round(random.uniform(15, 18), 2)
            student.gdp = round(random.uniform(1, 3), 2)
        
        students_to_add.append(student)
        
        # Batch commit every 10 students for better performance
        if (i + 1) % 10 == 0:
            db.session.add_all(students_to_add)
            try:
                db.session.commit()
                print(f"✅ Added {i + 1}/{num_students} students...")
                students_to_add = []
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error adding students: {e}")
                return
    
    # Add remaining students
    if students_to_add:
        db.session.add_all(students_to_add)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding final batch: {e}")
            return
    
    print("✅ Students added successfully.")
    
    # Now seed LMS activity and behavioral data
    print("🌱 Seeding LMS activity and behavioral data...")
    seed_enhanced_data()
    
    # Generate alerts for at-risk students
    print("🚨 Generating alerts for at-risk students...")
    generate_initial_alerts()
    
    print("✅ Database seeding complete.")


def seed_enhanced_data():
    """
    Seeds LMS activity, behavioral data, and gamification profiles for all students.
    """
    students = Student.query.all()
    
    for student in students:
        avg_grade = (student.curricular_units_1st_sem_grade + student.curricular_units_2nd_sem_grade) / 2
        
        # Determine engagement level based on grades
        if avg_grade >= 15:
            engagement_level = 'high'
        elif avg_grade >= 12:
            engagement_level = 'medium'
        else:
            engagement_level = 'low'
        
        # Create LMS Activity
        if engagement_level == 'high':
            lms = LMSActivity(
                student_id=student.id,
                activity_date=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                login_count=random.randint(40, 100),
                assignment_submissions=random.randint(15, 30),
                forum_posts=random.randint(20, 50),
                video_watch_time=round(random.uniform(15, 30), 2),
                quiz_attempts=random.randint(10, 25),
                resource_downloads=random.randint(20, 50),
                engagement_score=round(random.uniform(70, 100), 2)
            )
        elif engagement_level == 'medium':
            lms = LMSActivity(
                student_id=student.id,
                activity_date=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                login_count=random.randint(20, 40),
                assignment_submissions=random.randint(10, 15),
                forum_posts=random.randint(5, 20),
                video_watch_time=round(random.uniform(5, 15), 2),
                quiz_attempts=random.randint(5, 10),
                resource_downloads=random.randint(10, 20),
                engagement_score=round(random.uniform(40, 70), 2)
            )
        else:  # low
            lms = LMSActivity(
                student_id=student.id,
                activity_date=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                login_count=random.randint(5, 20),
                assignment_submissions=random.randint(2, 10),
                forum_posts=random.randint(0, 5),
                video_watch_time=round(random.uniform(0, 5), 2),
                quiz_attempts=random.randint(1, 5),
                resource_downloads=random.randint(0, 10),
                engagement_score=round(random.uniform(10, 40), 2)
            )
        
        db.session.add(lms)
        
        # Create Behavioral Data
        if engagement_level == 'high':
            behavioral = BehavioralData(
                student_id=student.id,
                record_date=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                attendance_rate=round(random.uniform(85, 100), 2),
                late_arrivals=random.randint(0, 2),
                early_departures=random.randint(0, 1),
                assignment_completion_rate=round(random.uniform(85, 100), 2),
                submission_timeliness=round(random.uniform(80, 100), 2),
                participation_score=round(random.uniform(80, 100), 2),
                peer_interaction_level='High',
                mentor_meeting_frequency=random.randint(3, 8),
                help_seeking_behavior=random.randint(2, 5),
                stress_level=random.randint(1, 5),
                motivation_level=random.randint(7, 10),
                confidence_level=random.randint(7, 10),
                sentiment_score=round(random.uniform(0.3, 1.0), 2),
                behavioral_risk_score=round(random.uniform(0, 30), 2)
            )
        elif engagement_level == 'medium':
            behavioral = BehavioralData(
                student_id=student.id,
                record_date=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                attendance_rate=round(random.uniform(65, 85), 2),
                late_arrivals=random.randint(2, 5),
                early_departures=random.randint(1, 3),
                assignment_completion_rate=round(random.uniform(65, 85), 2),
                submission_timeliness=round(random.uniform(60, 80), 2),
                participation_score=round(random.uniform(60, 80), 2),
                peer_interaction_level='Normal',
                mentor_meeting_frequency=random.randint(1, 3),
                help_seeking_behavior=random.randint(1, 3),
                stress_level=random.randint(4, 7),
                motivation_level=random.randint(4, 7),
                confidence_level=random.randint(4, 7),
                sentiment_score=round(random.uniform(-0.2, 0.5), 2),
                behavioral_risk_score=round(random.uniform(30, 60), 2)
            )
        else:  # low
            behavioral = BehavioralData(
                student_id=student.id,
                record_date=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                attendance_rate=round(random.uniform(40, 65), 2),
                late_arrivals=random.randint(5, 15),
                early_departures=random.randint(3, 10),
                assignment_completion_rate=round(random.uniform(30, 65), 2),
                submission_timeliness=round(random.uniform(20, 60), 2),
                participation_score=round(random.uniform(20, 60), 2),
                peer_interaction_level='Low',
                mentor_meeting_frequency=random.randint(0, 1),
                help_seeking_behavior=random.randint(0, 1),
                stress_level=random.randint(7, 10),
                motivation_level=random.randint(1, 4),
                confidence_level=random.randint(1, 4),
                sentiment_score=round(random.uniform(-1.0, 0.0), 2),
                behavioral_risk_score=round(random.uniform(60, 100), 2)
            )
        
        db.session.add(behavioral)
        
        # Create Gamification Profile
        gamification = GamificationProfile(
            student_id=student.id,
            total_points=random.randint(0, 500) if engagement_level != 'low' else random.randint(0, 100),
            academic_points=random.randint(0, 200) if engagement_level == 'high' else random.randint(0, 50),
            attendance_points=random.randint(0, 150) if engagement_level == 'high' else random.randint(0, 30),
            engagement_points=random.randint(0, 100) if engagement_level == 'high' else random.randint(0, 20),
            improvement_points=random.randint(0, 50),
            current_attendance_streak=random.randint(0, 15) if engagement_level == 'high' else random.randint(0, 3),
            longest_attendance_streak=random.randint(0, 30) if engagement_level == 'high' else random.randint(0, 5),
            current_submission_streak=random.randint(0, 10) if engagement_level == 'high' else random.randint(0, 2),
            longest_submission_streak=random.randint(0, 20) if engagement_level == 'high' else random.randint(0, 3)
        )
        
        db.session.add(gamification)
    
    try:
        db.session.commit()
        print(f"✅ Added LMS activity and behavioral data for {len(students)} students")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error adding enhanced data: {e}")


def generate_initial_alerts():
    """
    Generates initial alerts for all students based on their data.
    """
    students = Student.query.all()
    total_alerts = 0
    
    for student in students:
        try:
            alerts = AlertController.generate_alerts_for_student(student.id)
            if alerts:
                total_alerts += len(alerts)
        except Exception as e:
            print(f"⚠️ Error generating alerts for student {student.id}: {e}")
            continue
    
    print(f"✅ Generated {total_alerts} alerts for at-risk students")
    
    # Print summary
    stats = AlertController.get_alert_statistics()
    print(f"\n📊 Alert Summary:")
    print(f"   Total Active: {stats['total_active']}")
    print(f"   Critical: {stats['by_severity']['critical']}")
    print(f"   High: {stats['by_severity']['high']}")
    print(f"   Medium: {stats['by_severity']['medium']}")
    print(f"   Low: {stats['by_severity']['low']}")
    print(f"\n   Academic: {stats['by_type']['academic']}")
    print(f"   Financial: {stats['by_type']['financial']}")
    print(f"   Behavioral: {stats['by_type']['behavioral']}")
    print(f"   Psychological: {stats['by_type']['psychological']}")


def seed_demo_users():
    """
    Seeds demo users for testing authentication system:
    - teacher1 (password: password123)
    - student1 (password: password123)
    - admin (password: admin123)
    """
    print("🌱 Seeding demo users...")
    
    # Check if demo users already exist
    admin_exists = User.query.filter_by(username='admin').first()
    teacher_exists = User.query.filter_by(username='teacher1').first()
    student_exists = User.query.filter_by(username='student1').first()
    
    if admin_exists and teacher_exists and student_exists:
        print("⚠️  All demo users already exist.")
        print("\n📋 Demo Credentials:")
        print("   Admin:    username=admin, password=admin123")
        print("   Teacher:  username=teacher1, password=password123")
        print("   Student:  username=student1, password=password123")
        return
    
    # Create Admin User if not exists
    if not admin_exists:
        admin_user = User(
            username='admin',
            email='admin@educare.edu',
            full_name='System Administrator',
            role='admin',
            department='IT Administration',
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        try:
            db.session.commit()
            print("✅ Created admin user (username: admin, password: admin123)")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin user: {e}")
            return
    else:
        print("⚠️  Admin user already exists")
    
    # Create Teacher User if not exists
    if not teacher_exists:
        teacher_user = User(
            username='teacher1',
            email='teacher1@educare.edu',
            full_name='Dr. Sarah Johnson',
            role='teacher',
            department='Computer Science',
            phone='+1-555-0101',
            is_active=True
        )
        teacher_user.set_password('password123')
        db.session.add(teacher_user)
        
        # Commit to get user IDs
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating teacher user: {e}")
            return
        
        # Create Teacher Profile (after commit to get teacher_user.id)
        teacher_profile = Teacher(
            user_id=teacher_user.id,
            employee_id='T001',
            department='Computer Science',
            office_location='Building A, Room 301'
        )
        teacher_profile.set_subjects(['Data Science', 'Machine Learning', 'Programming'])
        teacher_profile.set_office_hours({
            'Monday': '10:00 AM - 12:00 PM',
            'Wednesday': '2:00 PM - 4:00 PM',
            'Friday': '10:00 AM - 12:00 PM'
        })
        db.session.add(teacher_profile)
        print("✅ Created teacher user (username: teacher1, password: password123)")
        
        # Commit to get teacher_id
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating teacher profile: {e}")
            return
    else:
        print("⚠️  Teacher user already exists")
        teacher_user = teacher_exists
    
    # Get teacher profile for assignment
    teacher_profile = Teacher.query.filter_by(user_id=teacher_user.id).first()
    
    # Create Student User if not exists
    if not student_exists:
        # Try to link to an existing student record first
        existing_student = Student.query.first()
        
        if existing_student and not existing_student.user_id:
            # Link existing student to new user
            student_user = User(
                username='student1',
                email=existing_student.email or 'student1@educare.edu',
                full_name=existing_student.name,
                role='student',
                is_active=True
            )
            student_user.set_password('password123')
            db.session.add(student_user)
            
            try:
                db.session.commit()
                # Link student to user
                existing_student.user_id = student_user.id
                db.session.commit()
                print(f"✅ Created student user linked to student #{existing_student.id} (username: student1, password: password123)")
                
                # Assign student to teacher
                if teacher_profile:
                    assignment = TeacherStudentAssignment(
                        teacher_id=teacher_profile.id,
                        student_id=existing_student.id,
                        course_name='Introduction to Machine Learning',
                        semester='Spring 2026',
                        academic_year='2025-2026',
                        is_active=True
                    )
                    db.session.add(assignment)
                    db.session.commit()
                    print(f"✅ Assigned student to teacher1")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error linking student: {e}")
        else:
            # Create new student if none exist  or all are already linked
            student_user = User(
                username='student1',
                email='student1@educare.edu',
                full_name='John Smith',
                role='student',
                is_active=True
            )
            student_user.set_password('password123')
            db.session.add(student_user)
            
            student_record = Student(
                name='John Smith',
                email='student1@educare.edu',
                age_at_enrollment=20,
                previous_qualification=3,
                scholarship_holder=True,
                debtor=False,
                tuition_fees_up_to_date=True,
                curricular_units_1st_sem_grade=15.5,
                curricular_units_2nd_sem_grade=14.8,
                gdp=2.1
            )
            db.session.add(student_record)
            
            try:
                db.session.commit()
                # Link them
                student_record.user_id = student_user.id
                db.session.commit()
                print(f"✅ Created new student user (username: student1, password: password123)")
                
                # Assign student to teacher
                if teacher_profile:
                    assignment = TeacherStudentAssignment(
                        teacher_id=teacher_profile.id,
                        student_id=student_record.id,
                        course_name='Introduction to Machine Learning',
                        semester='Spring 2026',
                        academic_year='2025-2026',
                        is_active=True
                    )
                    db.session.add(assignment)
                    db.session.commit()
                    print(f"✅ Assigned student to teacher1")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating student: {e}")
    else:
        print("⚠️  Student user already exists")
    
    print("\n✅ Demo users seeding complete!")
    print("\n📋 Demo Credentials:")
    print("   Admin:    username=admin, password=admin123")
    print("   Teacher:  username=teacher1, password=password123")
    print("   Student:  username=student1, password=password123")
