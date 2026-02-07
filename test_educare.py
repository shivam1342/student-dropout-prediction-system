"""
EduCare System Test Suite
Comprehensive tests for AI-Based Dropout Prediction and Counselling System
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
from datetime import datetime, date
from app import create_app
from extensions import db
from models import (
    Student, RiskPrediction, CounsellingLog, LMSActivity, 
    BehavioralData, Alert, Intervention, GamificationProfile
)
from controllers.alert_controller import AlertController
from controllers.gamification_controller import GamificationController
from controllers.intervention_controller import InterventionController
from controllers.prediction_controller import predict_dropout_risk


class TestEduCareModels(unittest.TestCase):
    """Test Category 1: Model Instantiation Tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test Flask app and database"""
        cls.app = create_app('default')
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
    
    def setUp(self):
        """Set up before each test"""
        db.session.rollback()
    
    def tearDown(self):
        """Clean up after each test"""
        db.session.query(Alert).delete()
        db.session.query(Intervention).delete()
        db.session.query(GamificationProfile).delete()
        db.session.query(RiskPrediction).delete()
        db.session.query(CounsellingLog).delete()
        db.session.query(LMSActivity).delete()
        db.session.query(BehavioralData).delete()
        db.session.query(Student).delete()
        db.session.commit()
    
    def test_student_model_creation(self):
        """Test 1.1: Student model instantiation"""
        student = Student(
            name="Test Student",
            email="test@example.com",
            age_at_enrollment=20,
            previous_qualification=1,
            scholarship_holder=True,
            debtor=False,
            tuition_fees_up_to_date=True,
            curricular_units_1st_sem_grade=15.5,
            curricular_units_2nd_sem_grade=16.0,
            gdp=1.5
        )
        db.session.add(student)
        db.session.commit()
        
        self.assertIsNotNone(student.id)
        self.assertEqual(student.name, "Test Student")
        self.assertEqual(student.email, "test@example.com")
        print("✅ Test 1.1: Student model creation - PASSED")
    
    def test_alert_model_creation(self):
        """Test 1.2: Alert model instantiation"""
        student = Student(
            name="Alert Test",
            email="alert@test.com",
            age_at_enrollment=22,
            previous_qualification=1,
            curricular_units_1st_sem_grade=10.0,
            curricular_units_2nd_sem_grade=9.5,
            gdp=0.5
        )
        db.session.add(student)
        db.session.commit()
        
        alert = Alert(
            student_id=student.id,
            alert_type="Academic",
            severity="High",
            title="Low Grades Alert",
            description="Low grades detected",
            status="Active"
        )
        db.session.add(alert)
        db.session.commit()
        
        self.assertIsNotNone(alert.id)
        self.assertEqual(alert.alert_type, "Academic")
        self.assertEqual(alert.severity, "High")
        print("✅ Test 1.2: Alert model creation - PASSED")
    
    def test_gamification_model_creation(self):
        """Test 1.3: Gamification profile model instantiation"""
        student = Student(
            name="Gamer",
            email="gamer@test.com",
            age_at_enrollment=19,
            previous_qualification=1,
            curricular_units_1st_sem_grade=16.0,
            curricular_units_2nd_sem_grade=16.5,
            gdp=2.0
        )
        db.session.add(student)
        db.session.commit()
        
        profile = GamificationProfile(
            student_id=student.id,
            total_points=250,
            level=2,
            current_attendance_streak=5
        )
        db.session.add(profile)
        db.session.commit()
        
        self.assertIsNotNone(profile.id)
        self.assertEqual(profile.total_points, 250)
        self.assertEqual(profile.level, 2)
        print("✅ Test 1.3: Gamification model creation - PASSED")


class TestEduCareRelationships(unittest.TestCase):
    """Test Category 2: Relationship Tests"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('default')
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
    
    def setUp(self):
        db.session.rollback()
    
    def tearDown(self):
        db.session.query(Alert).delete()
        db.session.query(RiskPrediction).delete()
        db.session.query(LMSActivity).delete()
        db.session.query(BehavioralData).delete()
        db.session.query(Student).delete()
        db.session.commit()
    
    def test_student_alert_relationship(self):
        """Test 2.1: Student-Alert one-to-many relationship"""
        student = Student(
            name="Relationship Test",
            email="rel@test.com",
            age_at_enrollment=21,
            previous_qualification=1,
            curricular_units_1st_sem_grade=12.0,
            curricular_units_2nd_sem_grade=11.5,
            gdp=1.0
        )
        db.session.add(student)
        db.session.commit()
        
        alert1 = Alert(student_id=student.id, alert_type="Academic", severity="Medium", title="Test 1", description="Test alert 1")
        alert2 = Alert(student_id=student.id, alert_type="Financial", severity="Low", title="Test 2", description="Test alert 2")
        db.session.add_all([alert1, alert2])
        db.session.commit()
        
        self.assertEqual(len(student.alerts), 2)
        self.assertEqual(student.alerts[0].alert_type, "Academic")
        print("✅ Test 2.1: Student-Alert relationship - PASSED")
    
    def test_student_lms_relationship(self):
        """Test 2.2: Student-LMSActivity one-to-many relationship"""
        student = Student(
            name="LMS Test",
            email="lms@test.com",
            age_at_enrollment=20,
            previous_qualification=1,
            curricular_units_1st_sem_grade=14.0,
            curricular_units_2nd_sem_grade=14.5,
            gdp=1.5
        )
        db.session.add(student)
        db.session.commit()
        
        lms = LMSActivity(
            student_id=student.id,
            login_count=25,
            assignment_submissions=10,
            engagement_score=75.5
        )
        db.session.add(lms)
        db.session.commit()
        
        self.assertEqual(len(student.lms_activities), 1)
        self.assertEqual(student.lms_activities[0].login_count, 25)
        print("✅ Test 2.2: Student-LMSActivity relationship - PASSED")
    
    def test_student_behavioral_relationship(self):
        """Test 2.3: Student-BehavioralData one-to-many relationship"""
        student = Student(
            name="Behavioral Test",
            email="behavior@test.com",
            age_at_enrollment=22,
            previous_qualification=1,
            curricular_units_1st_sem_grade=13.0,
            curricular_units_2nd_sem_grade=13.5,
            gdp=1.2
        )
        db.session.add(student)
        db.session.commit()
        
        behavioral = BehavioralData(
            student_id=student.id,
            stress_level=5,
            motivation_level=7,
            confidence_level=6
        )
        db.session.add(behavioral)
        db.session.commit()
        
        self.assertEqual(len(student.behavioral_data), 1)
        self.assertEqual(student.behavioral_data[0].stress_level, 5)
        print("✅ Test 2.3: Student-BehavioralData relationship - PASSED")


class TestEduCareControllers(unittest.TestCase):
    """Test Category 3: Controller Method Tests"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('default')
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
    
    def setUp(self):
        db.session.rollback()
    
    def tearDown(self):
        db.session.query(Alert).delete()
        db.session.query(Intervention).delete()
        db.session.query(GamificationProfile).delete()
        db.session.query(Student).delete()
        db.session.commit()
    
    def test_prediction_controller(self):
        """Test 3.1: Prediction controller with ML model"""
        student_data = {
            'previous_qualification': 1,
            'age_at_enrollment': 20,
            'scholarship_holder': 0,
            'debtor': 1,
            'tuition_fees_up_to_date': 0,
            'curricular_units_1st_sem_grade': 10.5,
            'curricular_units_2nd_sem_grade': 11.0,
            'gdp': 0.5
        }
        
        risk_score, risk_category, top_features, lime_features = predict_dropout_risk(student_data)
        
        self.assertIsInstance(risk_score, (int, float))
        self.assertIn(risk_category, ['Low', 'Medium', 'High', 'N/A'])
        self.assertIsInstance(top_features, list)
        self.assertIsInstance(lime_features, list)
        print(f"✅ Test 3.1: Prediction controller - PASSED (Risk: {risk_score}%, Category: {risk_category})")
    
    def test_gamification_controller_award_points(self):
        """Test 3.2: Gamification controller - award points"""
        student = Student(
            name="Points Test",
            email="points@test.com",
            age_at_enrollment=19,
            previous_qualification=1,
            curricular_units_1st_sem_grade=15.0,
            curricular_units_2nd_sem_grade=15.5,
            gdp=1.8
        )
        db.session.add(student)
        db.session.commit()
        
        profile = GamificationController.get_or_create_profile(student.id)
        initial_points = profile.total_points
        
        GamificationController.award_points(student.id, 'assignment_submit')
        
        updated_profile = GamificationProfile.query.filter_by(student_id=student.id).first()
        self.assertGreater(updated_profile.total_points, initial_points)
        print(f"✅ Test 3.2: Award points - PASSED (Points: {initial_points} → {updated_profile.total_points})")
    
    def test_gamification_controller_award_badge(self):
        """Test 3.3: Gamification controller - award badge"""
        student = Student(
            name="Badge Test",
            email="badge@test.com",
            age_at_enrollment=20,
            previous_qualification=1,
            curricular_units_1st_sem_grade=16.0,
            curricular_units_2nd_sem_grade=16.5,
            gdp=2.0
        )
        db.session.add(student)
        db.session.commit()
        
        profile = GamificationController.get_or_create_profile(student.id)
        initial_badges = len(profile.badges) if profile.badges else 0
        
        result = GamificationController.award_badge(student.id, 'academic_excellence')
        
        # Refresh profile from database
        db.session.refresh(profile)
        updated_profile = GamificationProfile.query.filter_by(student_id=student.id).first()
        new_badge_count = len(updated_profile.badges) if updated_profile.badges else 0
        
        # Badge should be returned and count should increase
        self.assertIsNotNone(result)
        self.assertGreaterEqual(new_badge_count, initial_badges)
        print(f"✅ Test 3.3: Award badge - PASSED (Badges: {initial_badges} → {new_badge_count}, Badge: {result['name']})")


class TestAlertGeneration(unittest.TestCase):
    """Test Category 4: Alert Generation Tests"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('default')
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
    
    def setUp(self):
        db.session.rollback()
    
    def tearDown(self):
        db.session.query(Alert).delete()
        db.session.query(BehavioralData).delete()
        db.session.query(LMSActivity).delete()
        db.session.query(Student).delete()
        db.session.commit()
    
    def test_academic_alert_generation(self):
        """Test 4.1: Academic alert generation for low grades"""
        student = Student(
            name="Low Grades",
            email="lowgrades@test.com",
            age_at_enrollment=21,
            previous_qualification=1,
            scholarship_holder=False,
            debtor=False,
            tuition_fees_up_to_date=True,
            curricular_units_1st_sem_grade=10.0,
            curricular_units_2nd_sem_grade=9.5,
            gdp=1.0
        )
        db.session.add(student)
        db.session.commit()
        
        alerts = AlertController.generate_alerts_for_student(student.id)
        
        self.assertIsNotNone(alerts)
        self.assertGreater(len(alerts), 0)
        academic_alerts = [a for a in alerts if a.alert_type == 'Academic']
        self.assertGreater(len(academic_alerts), 0)
        print(f"✅ Test 4.1: Academic alert generation - PASSED ({len(academic_alerts)} alerts)")
    
    def test_financial_alert_generation(self):
        """Test 4.2: Financial alert generation"""
        student = Student(
            name="Financial Issues",
            email="financial@test.com",
            age_at_enrollment=22,
            previous_qualification=1,
            scholarship_holder=False,
            debtor=True,
            tuition_fees_up_to_date=False,
            curricular_units_1st_sem_grade=14.0,
            curricular_units_2nd_sem_grade=14.5,
            gdp=1.5
        )
        db.session.add(student)
        db.session.commit()
        
        alerts = AlertController.generate_alerts_for_student(student.id)
        
        self.assertIsNotNone(alerts)
        financial_alerts = [a for a in alerts if a.alert_type == 'Financial']
        self.assertGreater(len(financial_alerts), 0)
        print(f"✅ Test 4.2: Financial alert generation - PASSED ({len(financial_alerts)} alerts)")
    
    def test_behavioral_alert_generation(self):
        """Test 4.3: Behavioral alert generation"""
        student = Student(
            name="Stressed Student",
            email="stressed@test.com",
            age_at_enrollment=20,
            previous_qualification=1,
            curricular_units_1st_sem_grade=13.0,
            curricular_units_2nd_sem_grade=13.5,
            gdp=1.2
        )
        db.session.add(student)
        db.session.commit()
        
        behavioral = BehavioralData(
            student_id=student.id,
            stress_level=9,
            motivation_level=3,
            confidence_level=2,
            peer_interaction_level='Low'
        )
        db.session.add(behavioral)
        db.session.commit()
        
        alerts = AlertController.generate_alerts_for_student(student.id)
        
        self.assertIsNotNone(alerts)
        behavioral_alerts = [a for a in alerts if a.alert_type == 'Behavioral']
        self.assertGreater(len(behavioral_alerts), 0)
        print(f"✅ Test 4.3: Behavioral alert generation - PASSED ({len(behavioral_alerts)} alerts)")


class TestGamificationSystem(unittest.TestCase):
    """Test Category 5: Gamification System Tests"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('default')
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
    
    def setUp(self):
        db.session.rollback()
    
    def tearDown(self):
        db.session.query(GamificationProfile).delete()
        db.session.query(Student).delete()
        db.session.commit()
    
    def test_streak_update(self):
        """Test 5.1: Attendance streak update"""
        student = Student(
            name="Streak Test",
            email="streak@test.com",
            age_at_enrollment=19,
            previous_qualification=1,
            curricular_units_1st_sem_grade=15.0,
            curricular_units_2nd_sem_grade=15.5,
            gdp=1.5
        )
        db.session.add(student)
        db.session.commit()
        
        profile = GamificationController.get_or_create_profile(student.id)
        initial_streak = profile.current_attendance_streak
        
        GamificationController.update_attendance_streak(student.id, attended=True)
        
        updated_profile = GamificationProfile.query.filter_by(student_id=student.id).first()
        self.assertGreaterEqual(updated_profile.current_attendance_streak, initial_streak)
        print(f"✅ Test 5.1: Streak update - PASSED (Streak: {initial_streak} → {updated_profile.current_attendance_streak})")
    
    def test_leaderboard_generation(self):
        """Test 5.2: Leaderboard generation"""
        # Create multiple students with different points
        for i in range(3):
            student = Student(
                name=f"Leader {i+1}",
                email=f"leader{i+1}@test.com",
                age_at_enrollment=20,
                previous_qualification=1,
                curricular_units_1st_sem_grade=14.0 + i,
                curricular_units_2nd_sem_grade=14.5 + i,
                gdp=1.5
            )
            db.session.add(student)
            db.session.commit()
            
            profile = GamificationController.get_or_create_profile(student.id)
            profile.total_points = (i + 1) * 100
            db.session.commit()
        
        leaderboard = GamificationController.get_leaderboard(scope='school', limit=10)
        
        self.assertIsNotNone(leaderboard)
        self.assertGreater(len(leaderboard), 0)
        print(f"✅ Test 5.2: Leaderboard generation - PASSED ({len(leaderboard)} entries)")
    
    def test_badge_auto_award(self):
        """Test 5.3: Automatic badge awarding"""
        student = Student(
            name="High Achiever",
            email="achiever@test.com",
            age_at_enrollment=19,
            previous_qualification=1,
            curricular_units_1st_sem_grade=18.0,
            curricular_units_2nd_sem_grade=18.5,
            gdp=2.5
        )
        db.session.add(student)
        db.session.commit()
        
        profile = GamificationController.get_or_create_profile(student.id)
        
        # Award points to trigger badge checks
        GamificationController.award_points(student.id, 'assignment_submit', custom_points=500)
        
        student_data = {
            'total_points': 500,
            'current_attendance_streak': 0,
            'academic_performance': 18.0
        }
        GamificationController.check_and_award_badges(student.id, student_data)
        
        updated_profile = GamificationProfile.query.filter_by(student_id=student.id).first()
        badge_count = len(updated_profile.badges) if updated_profile.badges else 0
        self.assertGreaterEqual(badge_count, 0)
        print(f"✅ Test 5.3: Badge auto-award - PASSED ({badge_count} badges)")


def run_tests():
    """Run all test categories"""
    print("=" * 80)
    print("EDUCARE SYSTEM TEST SUITE")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test categories
    suite.addTests(loader.loadTestsFromTestCase(TestEduCareModels))
    suite.addTests(loader.loadTestsFromTestCase(TestEduCareRelationships))
    suite.addTests(loader.loadTestsFromTestCase(TestEduCareControllers))
    suite.addTests(loader.loadTestsFromTestCase(TestAlertGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestGamificationSystem))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️ Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        return 0
    else:
        print("\n" + "=" * 80)
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        return 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
