"""
Utility Functions
Includes database seeding logic.
"""
import random
from models import Student
from extensions import db
from faker import Faker

fake = Faker()

def seed_db(num_students=50):
    """
    Seeds the database with dummy student data.
    This function is called by the 'flask seed-db' command.
    """
    # Check if data already exists
    if Student.query.count() > 0:
        print("Database already seeded.")
        return

    print(f"🌱 Seeding database with {num_students} students...")
    
    students_to_add = []
    for i in range(num_students):
        student = Student(
            name=fake.name(),
            email=fake.unique.email(),
            age_at_enrollment=random.randint(18, 25),
            previous_qualification=random.randint(1, 5),
            scholarship_holder=random.choice([True, False]),
            debtor=random.choice([True, False]),
            tuition_fees_up_to_date=random.choice([True, False]),
            curricular_units_1st_sem_grade=round(random.uniform(10, 18), 2),
            curricular_units_2nd_sem_grade=round(random.uniform(10, 18), 2),
            gdp=round(random.uniform(-2, 3), 2)
        )
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
    
    print("✅ Database seeding complete.")
