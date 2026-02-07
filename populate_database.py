"""
Populate database with realistic student profiles for testing
Creates diverse student profiles across different risk categories
"""
from app import app
from extensions import db
from models.student import Student
from models.behavioral_data import BehavioralData
from models.lms_activity import LMSActivity
from models.alert import Alert
from models.intervention import Intervention
from models.gamification import GamificationProfile
from models.risk_prediction import RiskPrediction
from controllers.prediction_controller import predict_dropout_risk
from datetime import datetime, timedelta
import random

def create_student_profiles():
    """Create realistic student profiles"""
    with app.app_context():
        print("🗑️ Clearing existing data...")
        # Clear existing data
        GamificationProfile.query.delete()
        RiskPrediction.query.delete()
        Alert.query.delete()
        Intervention.query.delete()
        LMSActivity.query.delete()
        BehavioralData.query.delete()
        Student.query.delete()
        db.session.commit()
        
        print("👥 Creating student profiles...\n")
        
        # HIGH RISK STUDENTS (15 students)
        high_risk_students = [
            {
                'name': 'Alex Johnson', 'email': 'alex.johnson@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 9.5, 'curricular_units_2nd_sem_grade': 8.2,
                'previous_qualification': 1, 'gdp': 2.5
            },
            {
                'name': 'Sarah Mitchell', 'email': 'sarah.mitchell@university.edu', 'age_at_enrollment': 23,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 8.8, 'curricular_units_2nd_sem_grade': 7.5,
                'previous_qualification': 1, 'gdp': 2.8
            },
            {
                'name': 'Marcus Brown', 'email': 'marcus.brown@university.edu', 'age_at_enrollment': 21,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 9.0, 'curricular_units_2nd_sem_grade': 8.0,
                'previous_qualification': 1, 'gdp': 2.6
            },
            {
                'name': 'Emily Davis', 'email': 'emily.davis@university.edu', 'age_at_enrollment': 20,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 8.5, 'curricular_units_2nd_sem_grade': 7.8,
                'previous_qualification': 1, 'gdp': 2.7
            },
            {
                'name': 'Jordan Lee', 'email': 'jordan.lee@university.edu', 'age_at_enrollment': 22,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 9.2, 'curricular_units_2nd_sem_grade': 8.5,
                'previous_qualification': 1, 'gdp': 2.5
            },
            {
                'name': 'Aisha Rahman', 'email': 'aisha.rahman@university.edu', 'age_at_enrollment': 24,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 8.3, 'curricular_units_2nd_sem_grade': 7.9,
                'previous_qualification': 1, 'gdp': 2.4
            },
            {
                'name': 'Carlos Rodriguez', 'email': 'carlos.rodriguez@university.edu', 'age_at_enrollment': 20,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 8.7, 'curricular_units_2nd_sem_grade': 8.1,
                'previous_qualification': 1, 'gdp': 2.6
            },
            {
                'name': 'Maya Thompson', 'email': 'maya.thompson@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 9.1, 'curricular_units_2nd_sem_grade': 7.6,
                'previous_qualification': 1, 'gdp': 2.5
            },
            {
                'name': 'Dmitri Volkov', 'email': 'dmitri.volkov@university.edu', 'age_at_enrollment': 23,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 8.9, 'curricular_units_2nd_sem_grade': 8.3,
                'previous_qualification': 1, 'gdp': 2.7
            },
            {
                'name': 'Priya Sharma', 'email': 'priya.sharma@university.edu', 'age_at_enrollment': 21,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 8.6, 'curricular_units_2nd_sem_grade': 7.7,
                'previous_qualification': 1, 'gdp': 2.8
            },
            {
                'name': 'Hassan Ali', 'email': 'hassan.ali@university.edu', 'age_at_enrollment': 22,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 9.3, 'curricular_units_2nd_sem_grade': 8.4,
                'previous_qualification': 1, 'gdp': 2.5
            },
            {
                'name': 'Isabella Santos', 'email': 'isabella.santos@university.edu', 'age_at_enrollment': 20,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 8.4, 'curricular_units_2nd_sem_grade': 7.9,
                'previous_qualification': 1, 'gdp': 2.6
            },
            {
                'name': 'Kevin O\'Connor', 'email': 'kevin.oconnor@university.edu', 'age_at_enrollment': 24,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 9.0, 'curricular_units_2nd_sem_grade': 8.2,
                'previous_qualification': 1, 'gdp': 2.7
            },
            {
                'name': 'Yuki Tanaka', 'email': 'yuki.tanaka@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 8.8, 'curricular_units_2nd_sem_grade': 8.0,
                'previous_qualification': 1, 'gdp': 2.4
            },
            {
                'name': 'Fatima Nkosi', 'email': 'fatima.nkosi@university.edu', 'age_at_enrollment': 21,
                'scholarship_holder': False, 'debtor': True, 'tuition_fees_up_to_date': False,
                'curricular_units_1st_sem_grade': 9.1, 'curricular_units_2nd_sem_grade': 7.8,
                'previous_qualification': 1, 'gdp': 2.5
            }
        ]
        
        # MEDIUM RISK STUDENTS (20 students)
        medium_risk_students = [
            {
                'name': 'Chris Anderson', 'email': 'chris.anderson@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 12.5, 'curricular_units_2nd_sem_grade': 11.8,
                'previous_qualification': 1, 'gdp': 3.2
            },
            {
                'name': 'Taylor Wilson', 'email': 'taylor.wilson@university.edu', 'age_at_enrollment': 20,
                'scholarship_holder': False, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 11.8, 'curricular_units_2nd_sem_grade': 12.2,
                'previous_qualification': 1, 'gdp': 3.1
            },
            {
                'name': 'Jamie Martinez', 'email': 'jamie.martinez@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 12.0, 'curricular_units_2nd_sem_grade': 11.5,
                'previous_qualification': 1, 'gdp': 3.0
            },
            {
                'name': 'Morgan Garcia', 'email': 'morgan.garcia@university.edu', 'age_at_enrollment': 21,
                'scholarship_holder': False, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 11.5, 'curricular_units_2nd_sem_grade': 12.0,
                'previous_qualification': 1, 'gdp': 3.3
            },
            {
                'name': 'Casey Thompson', 'email': 'casey.thompson@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 12.2, 'curricular_units_2nd_sem_grade': 11.7,
                'previous_qualification': 1, 'gdp': 3.1
            },
            {
                'name': 'Riley Rodriguez', 'email': 'riley.rodriguez@university.edu', 'age_at_enrollment': 20,
                'scholarship_holder': False, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 11.9, 'curricular_units_2nd_sem_grade': 12.1,
                'previous_qualification': 1, 'gdp': 3.2
            },
            {
                'name': 'Dakota White', 'email': 'dakota.white@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 12.3, 'curricular_units_2nd_sem_grade': 11.6,
                'previous_qualification': 1, 'gdp': 3.0
            },
            {
                'name': 'Amara Okafor', 'email': 'amara.okafor@university.edu', 'age_at_enrollment': 22,
                'scholarship_holder': False, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 11.7, 'curricular_units_2nd_sem_grade': 12.3,
                'previous_qualification': 1, 'gdp': 3.2
            },
            {
                'name': 'Lucas Silva', 'email': 'lucas.silva@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 12.1, 'curricular_units_2nd_sem_grade': 11.4,
                'previous_qualification': 1, 'gdp': 3.1
            },
            {
                'name': 'Mei Lin', 'email': 'mei.lin@university.edu', 'age_at_enrollment': 21,
                'scholarship_holder': False, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 11.6, 'curricular_units_2nd_sem_grade': 12.0,
                'previous_qualification': 1, 'gdp': 3.3
            },
            {
                'name': 'Omar Hassan', 'email': 'omar.hassan@university.edu', 'age_at_enrollment': 20,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 12.4, 'curricular_units_2nd_sem_grade': 11.9,
                'previous_qualification': 1, 'gdp': 3.0
            },
            {
                'name': 'Nina Kowalski', 'email': 'nina.kowalski@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': False, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 11.8, 'curricular_units_2nd_sem_grade': 12.2,
                'previous_qualification': 1, 'gdp': 3.2
            },
            {
                'name': 'Raj Patel', 'email': 'raj.patel@university.edu', 'age_at_enrollment': 22,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 12.0, 'curricular_units_2nd_sem_grade': 11.7,
                'previous_qualification': 1, 'gdp': 3.1
            },
            {
                'name': 'Elena Popescu', 'email': 'elena.popescu@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': False, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 11.9, 'curricular_units_2nd_sem_grade': 12.4,
                'previous_qualification': 1, 'gdp': 3.3
            },
            {
                'name': 'Kwame Mensah', 'email': 'kwame.mensah@university.edu', 'age_at_enrollment': 21,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 12.2, 'curricular_units_2nd_sem_grade': 11.5,
                'previous_qualification': 1, 'gdp': 3.0
            },
            {
                'name': 'Aria Martinez', 'email': 'aria.martinez@university.edu', 'age_at_enrollment': 20,
                'scholarship_holder': False, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 11.7, 'curricular_units_2nd_sem_grade': 12.1,
                'previous_qualification': 1, 'gdp': 3.2
            },
            {
                'name': 'Hiroshi Nakamura', 'email': 'hiroshi.nakamura@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 12.3, 'curricular_units_2nd_sem_grade': 11.8,
                'previous_qualification': 1, 'gdp': 3.1
            },
            {
                'name': 'Zara Khan', 'email': 'zara.khan@university.edu', 'age_at_enrollment': 22,
                'scholarship_holder': False, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 11.6, 'curricular_units_2nd_sem_grade': 12.3,
                'previous_qualification': 1, 'gdp': 3.3
            },
            {
                'name': 'Miguel Fernandez', 'email': 'miguel.fernandez@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 12.1, 'curricular_units_2nd_sem_grade': 11.6,
                'previous_qualification': 1, 'gdp': 3.0
            },
            {
                'name': 'Lily Chen', 'email': 'lily.chen@university.edu', 'age_at_enrollment': 21,
                'scholarship_holder': False, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 11.8, 'curricular_units_2nd_sem_grade': 12.0,
                'previous_qualification': 1, 'gdp': 3.2
            }
        ]
        
        # LOW RISK STUDENTS (15 students)
        low_risk_students = [
            {
                'name': 'Sophia Chen', 'email': 'sophia.chen@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 15.5, 'curricular_units_2nd_sem_grade': 16.2,
                'previous_qualification': 1, 'gdp': 3.8
            },
            {
                'name': 'Liam O\'Brien', 'email': 'liam.obrien@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 16.8, 'curricular_units_2nd_sem_grade': 15.9,
                'previous_qualification': 1, 'gdp': 3.9
            },
            {
                'name': 'Emma Patel', 'email': 'emma.patel@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 17.2, 'curricular_units_2nd_sem_grade': 16.5,
                'previous_qualification': 1, 'gdp': 4.0
            },
            {
                'name': 'Noah Kim', 'email': 'noah.kim@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 15.8, 'curricular_units_2nd_sem_grade': 16.0,
                'previous_qualification': 1, 'gdp': 3.7
            },
            {
                'name': 'Olivia Nguyen', 'email': 'olivia.nguyen@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 16.5, 'curricular_units_2nd_sem_grade': 17.0,
                'previous_qualification': 1, 'gdp': 3.9
            },
            {
                'name': 'Ethan Singh', 'email': 'ethan.singh@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 16.0, 'curricular_units_2nd_sem_grade': 16.8,
                'previous_qualification': 1, 'gdp': 3.8
            },
            {
                'name': 'Ava Johnson', 'email': 'ava.johnson@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 17.5, 'curricular_units_2nd_sem_grade': 16.3,
                'previous_qualification': 1, 'gdp': 4.0
            },
            {
                'name': 'William Zhang', 'email': 'william.zhang@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 15.7, 'curricular_units_2nd_sem_grade': 16.4,
                'previous_qualification': 1, 'gdp': 3.7
            },
            {
                'name': 'Amelia Brown', 'email': 'amelia.brown@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 16.9, 'curricular_units_2nd_sem_grade': 17.2,
                'previous_qualification': 1, 'gdp': 3.9
            },
            {
                'name': 'James Anderson', 'email': 'james.anderson@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 15.6, 'curricular_units_2nd_sem_grade': 16.1,
                'previous_qualification': 1, 'gdp': 3.8
            },
            {
                'name': 'Mia Garcia', 'email': 'mia.garcia@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 17.1, 'curricular_units_2nd_sem_grade': 16.7,
                'previous_qualification': 1, 'gdp': 4.0
            },
            {
                'name': 'Benjamin Lee', 'email': 'benjamin.lee@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 16.3, 'curricular_units_2nd_sem_grade': 15.8,
                'previous_qualification': 1, 'gdp': 3.7
            },
            {
                'name': 'Charlotte Wilson', 'email': 'charlotte.wilson@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 16.6, 'curricular_units_2nd_sem_grade': 17.4,
                'previous_qualification': 1, 'gdp': 3.9
            },
            {
                'name': 'Alexander Martinez', 'email': 'alexander.martinez@university.edu', 'age_at_enrollment': 19,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 15.9, 'curricular_units_2nd_sem_grade': 16.6,
                'previous_qualification': 1, 'gdp': 3.8
            },
            {
                'name': 'Isabella Thomas', 'email': 'isabella.thomas@university.edu', 'age_at_enrollment': 18,
                'scholarship_holder': True, 'debtor': False, 'tuition_fees_up_to_date': True,
                'curricular_units_1st_sem_grade': 17.3, 'curricular_units_2nd_sem_grade': 16.9,
                'previous_qualification': 1, 'gdp': 4.0
            }
        ]
        
        # Combine all students
        all_students_data = high_risk_students + medium_risk_students + low_risk_students
        
        for idx, student_data in enumerate(all_students_data, 1):
            student = Student(**student_data)
            db.session.add(student)
            db.session.flush()  # Get student ID
            
            # Use ML model to predict risk
            student_features = {
                'previous_qualification': student.previous_qualification,
                'age_at_enrollment': student.age_at_enrollment,
                'scholarship_holder': int(student.scholarship_holder),
                'debtor': int(student.debtor),
                'tuition_fees_up_to_date': int(student.tuition_fees_up_to_date),
                'curricular_units_1st_sem_grade': student.curricular_units_1st_sem_grade,
                'curricular_units_2nd_sem_grade': student.curricular_units_2nd_sem_grade,
                'gdp': student.gdp
            }
            
            # Get ML prediction (now returns SHAP features and LIME features)
            risk_score, risk_category, top_features, lime_features = predict_dropout_risk(student_features)
            
            print(f"✅ Created: {student.name} (Predicted: {risk_category} Risk - {risk_score}%)")
            
            # Create Risk Prediction with ML results
            prediction = RiskPrediction(
                student_id=student.id,
                risk_score=risk_score,
                risk_category=risk_category,
                top_feature_1=top_features[0]['name'] if len(top_features) > 0 else 'N/A',
                top_feature_1_value=float(top_features[0]['value']) if len(top_features) > 0 else 0.0,
                top_feature_2=top_features[1]['name'] if len(top_features) > 1 else 'N/A',
                top_feature_2_value=float(top_features[1]['value']) if len(top_features) > 1 else 0.0,
                top_feature_3=top_features[2]['name'] if len(top_features) > 2 else 'N/A',
                top_feature_3_value=float(top_features[2]['value']) if len(top_features) > 2 else 0.0
            )
            db.session.add(prediction)
            
            # Create Behavioral Data (last 10 days)
            for day in range(10):
                date = datetime.now() - timedelta(days=day)
                
                if risk_category == 'High':
                    attendance = random.randint(40, 70)
                    stress = random.randint(6, 10)
                    motivation = random.randint(2, 5)
                elif risk_category == 'Medium':
                    attendance = random.randint(70, 85)
                    stress = random.randint(4, 7)
                    motivation = random.randint(5, 7)
                else:
                    attendance = random.randint(85, 100)
                    stress = random.randint(2, 5)
                    motivation = random.randint(7, 10)
                
                behavioral = BehavioralData(
                    student_id=student.id,
                    attendance_rate=attendance,
                    stress_level=stress,
                    motivation_level=motivation,
                    record_date=date
                )
                db.session.add(behavioral)
            
            # Create LMS Activities (last 15 days)
            for day in range(15):
                date = datetime.now() - timedelta(days=day)
                
                if risk_category == 'Low':
                    login_cnt = random.randint(3, 5)
                    assignments = random.randint(2, 4)
                    forum = random.randint(1, 3)
                    video_time = random.uniform(1.5, 3.0)
                    engagement = random.randint(80, 100)
                elif risk_category == 'Medium':
                    login_cnt = random.randint(1, 3)
                    assignments = random.randint(1, 2)
                    forum = random.randint(0, 2)
                    video_time = random.uniform(0.5, 1.5)
                    engagement = random.randint(50, 79)
                else:
                    login_cnt = random.randint(0, 1)
                    assignments = random.randint(0, 1)
                    forum = random.randint(0, 1)
                    video_time = random.uniform(0.0, 0.5)
                    engagement = random.randint(10, 49)
                
                lms = LMSActivity(
                    student_id=student.id,
                    activity_date=date,
                    login_count=login_cnt,
                    assignment_submissions=assignments,
                    forum_posts=forum,
                    video_watch_time=video_time,
                    quiz_attempts=random.randint(0, 2),
                    resource_downloads=random.randint(0, 3),
                    engagement_score=engagement
                )
                db.session.add(lms)
            
            # Create Alerts for at-risk students (based on ML prediction)
            if risk_category == 'High':
                alert1 = Alert(
                    student_id=student.id,
                    alert_type='Academic Performance',
                    severity='Critical',
                    title='Multiple Course Failures',
                    description=f'{student.name} has failed multiple courses this semester.',
                    status='Active'
                )
                db.session.add(alert1)
                
                alert2 = Alert(
                    student_id=student.id,
                    alert_type='Financial',
                    severity='High',
                    title='Outstanding Tuition Fees',
                    description=f'{student.name} has outstanding tuition fees.',
                    status='Active'
                )
                db.session.add(alert2)
                
                alert3 = Alert(
                    student_id=student.id,
                    alert_type='Attendance',
                    severity='High',
                    title='Low Attendance Rate',
                    description=f'{student.name} attendance rate is below 70%.',
                    status='Active'
                )
                db.session.add(alert3)
                
            elif risk_category == 'Medium':
                alert = Alert(
                    student_id=student.id,
                    alert_type='Behavioral',
                    severity='Medium',
                    title='Decreased Engagement',
                    description=f'{student.name} showing signs of decreased engagement.',
                    status='Active'
                )
                db.session.add(alert)
            
            # Create Interventions for at-risk students (based on ML prediction)
            if risk_category == 'High':
                intervention1 = Intervention(
                    student_id=student.id,
                    intervention_type='Academic',
                    priority='High',
                    category='Tutoring',
                    title='One-on-One Tutoring Sessions',
                    description=f'One-on-one tutoring sessions arranged for {student.name} to improve grades.',
                    scheduled_date=datetime.now() - timedelta(days=10),
                    status='In Progress',
                    outcome='Student attending sessions regularly.'
                )
                db.session.add(intervention1)
                
                intervention2 = Intervention(
                    student_id=student.id,
                    intervention_type='Financial',
                    priority='Critical',
                    category='Financial Aid',
                    title='Payment Plan Discussion',
                    description=f'Meeting with financial aid office to discuss payment plan for {student.name}.',
                    scheduled_date=datetime.now() - timedelta(days=7),
                    completed_date=datetime.now() - timedelta(days=5),
                    status='Completed',
                    outcome='Payment plan established.'
                )
                db.session.add(intervention2)
                
            elif risk_category == 'Medium':
                intervention = Intervention(
                    student_id=student.id,
                    intervention_type='Social',
                    priority='Medium',
                    category='Mentoring',
                    title='Peer Mentoring Program',
                    description=f'Peer mentoring program assigned to support {student.name}.',
                    scheduled_date=datetime.now() - timedelta(days=5),
                    status='In Progress',
                    outcome='Positive feedback from mentor.'
                )
                db.session.add(intervention)
            
            # Create Gamification Profile
            if risk_category == 'Low':
                total_points = random.randint(2500, 5000)
                academic_pts = random.randint(800, 1500)
                attendance_pts = random.randint(500, 1000)
                engagement_pts = random.randint(700, 1200)
                badges = [
                    {'name': 'High Achiever', 'icon': 'fa-trophy', 'earned_date': '2025-10-01'},
                    {'name': 'Perfect Attendance', 'icon': 'fa-calendar-check', 'earned_date': '2025-09-15'},
                    {'name': 'Engagement Master', 'icon': 'fa-comments', 'earned_date': '2025-10-10'}
                ]
                streak = random.randint(15, 30)
            elif risk_category == 'Medium':
                total_points = random.randint(1000, 2499)
                academic_pts = random.randint(400, 799)
                attendance_pts = random.randint(250, 499)
                engagement_pts = random.randint(350, 699)
                badges = [
                    {'name': 'Improvement Champion', 'icon': 'fa-chart-line', 'earned_date': '2025-09-20'}
                ]
                streak = random.randint(5, 14)
            else:  # High risk
                total_points = random.randint(100, 999)
                academic_pts = random.randint(50, 399)
                attendance_pts = random.randint(20, 249)
                engagement_pts = random.randint(30, 349)
                badges = []
                streak = random.randint(0, 4)
            
            gamification = GamificationProfile(
                student_id=student.id,
                total_points=total_points,
                academic_points=academic_pts,
                attendance_points=attendance_pts,
                engagement_points=engagement_pts,
                level=total_points // 1000 + 1,
                badges=badges,
                current_attendance_streak=streak,
                longest_attendance_streak=streak + random.randint(0, 5),
                current_submission_streak=streak - random.randint(0, 3),
                longest_submission_streak=streak + random.randint(0, 3)
            )
            db.session.add(gamification)
        
        db.session.commit()
        
        # Count actual ML predictions
        high_risk_count = RiskPrediction.query.filter_by(risk_category='High').count()
        medium_risk_count = RiskPrediction.query.filter_by(risk_category='Medium').count()
        low_risk_count = RiskPrediction.query.filter_by(risk_category='Low').count()
        
        print(f"\n{'='*70}")
        print(f"✅ DATABASE POPULATED SUCCESSFULLY!")
        print(f"{'='*70}")
        print(f"📊 Total Students Created: {len(all_students_data)}")
        print(f"   🔴 High Risk (ML Predicted): {high_risk_count}")
        print(f"   🟡 Medium Risk (ML Predicted): {medium_risk_count}")
        print(f"   🟢 Low Risk (ML Predicted): {low_risk_count}")
        print(f"{'='*70}")
        print(f"\n🎯 ML model classified students based on trained patterns!")
        print(f"🌐 Visit: http://127.0.0.1:5000/students")

if __name__ == '__main__':
    create_student_profiles()
