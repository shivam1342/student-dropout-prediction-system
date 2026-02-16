"""
Data Controller
Handles CRUD operations for student data.
"""
from app.extensions import db
from app.models import Student, RiskPrediction, CounsellingLog

def get_all_students():
    """Fetch all students with their latest risk prediction."""
    students = Student.query.all()
    for student in students:
        student.latest_prediction = RiskPrediction.query.filter_by(student_id=student.id).order_by(RiskPrediction.prediction_date.desc()).first()
    return students

def get_student_by_id(student_id):
    """Fetch a single student by ID with all related data."""
    student = Student.query.get_or_404(student_id)
    student.predictions = RiskPrediction.query.filter_by(student_id=student.id).order_by(RiskPrediction.prediction_date.desc()).all()
    student.counselling_logs = CounsellingLog.query.filter_by(student_id=student.id).order_by(CounsellingLog.log_date.desc()).all()
    student.latest_prediction = student.predictions[0] if student.predictions else None
    return student

def add_student(data):
    """Add a new student to the database."""
    new_student = Student(
        name=data['name'],
        email=data['email'],
        age_at_enrollment=int(data['age_at_enrollment']),
        previous_qualification=int(data['previous_qualification']),
        scholarship_holder='scholarship_holder' in data,
        debtor='debtor' in data,
        tuition_fees_up_to_date='tuition_fees_up_to_date' in data,
        curricular_units_1st_sem_grade=float(data['curricular_units_1st_sem_grade']),
        curricular_units_2nd_sem_grade=float(data['curricular_units_2nd_sem_grade']),
        gdp=float(data['gdp'])
    )
    db.session.add(new_student)
    db.session.commit()
    return new_student

def update_student(student_id, data):
    """Update an existing student's details."""
    student = Student.query.get_or_404(student_id)
    student.name = data['name']
    student.email = data['email']
    student.age_at_enrollment = int(data['age_at_enrollment'])
    student.previous_qualification = int(data['previous_qualification'])
    student.scholarship_holder = 'scholarship_holder' in data
    student.debtor = 'debtor' in data
    student.tuition_fees_up_to_date = 'tuition_fees_up_to_date' in data
    student.curricular_units_1st_sem_grade = float(data['curricular_units_1st_sem_grade'])
    student.curricular_units_2nd_sem_grade = float(data['curricular_units_2nd_sem_grade'])
    student.gdp = float(data['gdp'])
    db.session.commit()
    return student

def delete_student(student_id):
    """Delete a student from the database."""
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
