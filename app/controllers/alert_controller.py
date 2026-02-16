"""
Alert Controller
Handles alert generation, management, and real-time monitoring
"""
from datetime import datetime, timedelta
from app.models import Student, Alert, RiskPrediction, BehavioralData, LMSActivity
from app.extensions import db


class AlertController:
    """Controller for managing student alerts"""
    
    # Alert thresholds
    THRESHOLDS = {
        'academic': {
            'critical': 12.0,  # Grade below 12
            'high': 13.5,
            'medium': 14.5
        },
        'attendance': {
            'critical': 60.0,  # Below 60%
            'high': 70.0,
            'medium': 80.0
        },
        'engagement': {
            'critical': 30.0,  # Engagement score below 30
            'high': 50.0,
            'medium': 70.0
        },
        'behavioral_risk': {
            'critical': 70.0,  # Behavioral risk above 70
            'high': 50.0,
            'medium': 30.0
        },
        'dropout_risk': {
            'critical': 0.7,  # 70% dropout probability
            'high': 0.5,
            'medium': 0.3
        }
    }
    
    @staticmethod
    def generate_alerts_for_student(student_id):
        """Generate alerts for a specific student based on current data"""
        student = Student.query.get(student_id)
        if not student:
            return None
        
        alerts_generated = []
        
        # Check academic performance
        avg_grade = (student.curricular_units_1st_sem_grade + student.curricular_units_2nd_sem_grade) / 2
        academic_alert = AlertController._check_academic_performance(student, avg_grade)
        if academic_alert:
            alerts_generated.append(academic_alert)
        
        # Check financial status
        financial_alert = AlertController._check_financial_status(student)
        if financial_alert:
            alerts_generated.append(financial_alert)
        
        # Check behavioral data if available
        behavioral_data = BehavioralData.query.filter_by(student_id=student_id).order_by(BehavioralData.record_date.desc()).first()
        if behavioral_data:
            behavioral_alert = AlertController._check_behavioral_indicators(student, behavioral_data)
            if behavioral_alert:
                alerts_generated.append(behavioral_alert)
        
        # Check LMS engagement if available
        lms_activity = LMSActivity.query.filter_by(student_id=student_id).order_by(LMSActivity.activity_date.desc()).first()
        if lms_activity:
            engagement_alert = AlertController._check_lms_engagement(student, lms_activity)
            if engagement_alert:
                alerts_generated.append(engagement_alert)
        
        # Check dropout risk prediction
        latest_prediction = RiskPrediction.query.filter_by(student_id=student_id).order_by(RiskPrediction.prediction_date.desc()).first()
        if latest_prediction:
            dropout_alert = AlertController._check_dropout_risk(student, latest_prediction)
            if dropout_alert:
                alerts_generated.append(dropout_alert)
        
        # Save all generated alerts
        for alert in alerts_generated:
            db.session.add(alert)
        
        db.session.commit()
        
        return alerts_generated
    
    @staticmethod
    def _check_academic_performance(student, avg_grade):
        """Check academic performance and generate alert if needed"""
        severity = None
        
        if avg_grade < AlertController.THRESHOLDS['academic']['critical']:
            severity = 'Critical'
        elif avg_grade < AlertController.THRESHOLDS['academic']['high']:
            severity = 'High'
        elif avg_grade < AlertController.THRESHOLDS['academic']['medium']:
            severity = 'Medium'
        
        if severity:
            return Alert(
                student_id=student.id,
                alert_type='Academic',
                severity=severity,
                title=f'Low Academic Performance - Average Grade: {avg_grade:.2f}',
                description=f'{student.name} has an average grade of {avg_grade:.2f}, which is below the acceptable threshold.',
                trigger_factors={
                    'average_grade': avg_grade,
                    'semester_1_grade': student.curricular_units_1st_sem_grade,
                    'semester_2_grade': student.curricular_units_2nd_sem_grade
                },
                recommended_actions=['Schedule academic counselling', 'Arrange tutoring sessions', 'Review study plan']
            )
        return None
    
    @staticmethod
    def _check_financial_status(student):
        """Check financial status and generate alert if needed"""
        if student.debtor or not student.tuition_fees_up_to_date:
            severity = 'High' if student.debtor else 'Medium'
            
            return Alert(
                student_id=student.id,
                alert_type='Financial',
                severity=severity,
                title='Financial Issues Detected',
                description=f'{student.name} has financial difficulties that may impact academic performance.',
                trigger_factors={
                    'debtor': student.debtor,
                    'tuition_fees_up_to_date': student.tuition_fees_up_to_date,
                    'scholarship_holder': student.scholarship_holder
                },
                recommended_actions=['Contact financial aid office', 'Discuss payment plans', 'Explore scholarship opportunities']
            )
        return None
    
    @staticmethod
    def _check_behavioral_indicators(student, behavioral_data):
        """Check behavioral indicators and generate alert if needed"""
        severity = None
        issues = []
        
        # Check attendance
        if behavioral_data.attendance_rate < AlertController.THRESHOLDS['attendance']['critical']:
            severity = 'Critical'
            issues.append(f'Very low attendance rate ({behavioral_data.attendance_rate:.1f}%)')
        elif behavioral_data.attendance_rate < AlertController.THRESHOLDS['attendance']['high']:
            severity = 'High'
            issues.append(f'Low attendance rate ({behavioral_data.attendance_rate:.1f}%)')
        
        # Check behavioral risk score
        if behavioral_data.behavioral_risk_score > AlertController.THRESHOLDS['behavioral_risk']['critical']:
            severity = 'Critical'
            issues.append(f'Critical behavioral risk score ({behavioral_data.behavioral_risk_score:.1f})')
        elif behavioral_data.behavioral_risk_score > AlertController.THRESHOLDS['behavioral_risk']['high']:
            if not severity:
                severity = 'High'
            issues.append(f'High behavioral risk score ({behavioral_data.behavioral_risk_score:.1f})')
        
        # Check psychological indicators
        if behavioral_data.stress_level and behavioral_data.stress_level > 7:
            if not severity:
                severity = 'High'
            issues.append(f'High stress level ({behavioral_data.stress_level}/10)')
        
        if behavioral_data.motivation_level and behavioral_data.motivation_level < 3:
            if not severity:
                severity = 'Medium'
            issues.append(f'Low motivation level ({behavioral_data.motivation_level}/10)')
        
        if issues:
            return Alert(
                student_id=student.id,
                alert_type='Behavioral',
                severity=severity or 'Medium',
                title='Behavioral Concerns Detected',
                description=f'{student.name} is showing concerning behavioral patterns: {", ".join(issues)}',
                trigger_factors={
                    'attendance_rate': behavioral_data.attendance_rate,
                    'behavioral_risk_score': behavioral_data.behavioral_risk_score,
                    'stress_level': behavioral_data.stress_level,
                    'motivation_level': behavioral_data.motivation_level,
                    'confidence_level': behavioral_data.confidence_level
                },
                recommended_actions=['Schedule counselling session', 'Reach out to student', 'Monitor attendance closely']
            )
        return None
    
    @staticmethod
    def _check_lms_engagement(student, lms_activity):
        """Check LMS engagement and generate alert if needed"""
        if lms_activity.engagement_score < AlertController.THRESHOLDS['engagement']['critical']:
            severity = 'Critical'
        elif lms_activity.engagement_score < AlertController.THRESHOLDS['engagement']['high']:
            severity = 'High'
        elif lms_activity.engagement_score < AlertController.THRESHOLDS['engagement']['medium']:
            severity = 'Medium'
        else:
            return None
        
        return Alert(
            student_id=student.id,
            alert_type='Academic',
            severity=severity,
            title=f'Low LMS Engagement - Score: {lms_activity.engagement_score:.1f}',
            description=f'{student.name} has very low engagement with the learning management system.',
            trigger_factors={
                'engagement_score': lms_activity.engagement_score,
                'login_count': lms_activity.login_count,
                'assignment_submissions': lms_activity.assignment_submissions,
                'forum_posts': lms_activity.forum_posts
            },
            recommended_actions=['Send engagement reminder', 'Check for technical issues', 'Offer LMS training']
        )
    
    @staticmethod
    def _check_dropout_risk(student, prediction):
        """Check dropout risk prediction and generate alert if needed"""
        dropout_prob = prediction.dropout_probability
        
        # Handle None dropout probability
        if dropout_prob is None:
            dropout_prob = 0.0
        
        if dropout_prob > AlertController.THRESHOLDS['dropout_risk']['critical']:
            severity = 'Critical'
        elif dropout_prob > AlertController.THRESHOLDS['dropout_risk']['high']:
            severity = 'High'
        elif dropout_prob > AlertController.THRESHOLDS['dropout_risk']['medium']:
            severity = 'Medium'
        else:
            return None
        
        return Alert(
            student_id=student.id,
            alert_type='Psychological',
            severity=severity,
            title=f'High Dropout Risk - Probability: {dropout_prob*100:.1f}%',
            description=f'{student.name} has a {dropout_prob*100:.1f}% predicted probability of dropping out.',
            trigger_factors={
                'dropout_probability': dropout_prob,
                'prediction_result': prediction.prediction_result,
                'top_risk_factors': prediction.top_risk_factors
            },
            recommended_actions=['Immediate intervention required', 'Schedule urgent meeting', 'Develop retention plan']
        )
    
    @staticmethod
    def get_active_alerts(student_id=None, severity=None, alert_type=None):
        """Get active alerts with optional filters"""
        query = Alert.query.filter_by(status='Active')
        
        if student_id:
            query = query.filter_by(student_id=student_id)
        if severity:
            query = query.filter_by(severity=severity)
        if alert_type:
            query = query.filter_by(alert_type=alert_type)
        
        return query.order_by(Alert.created_at.desc()).all()
    
    @staticmethod
    def acknowledge_alert(alert_id, acknowledged_by, notes=None):
        """Acknowledge an alert"""
        alert = Alert.query.get(alert_id)
        if alert:
            alert.status = 'Acknowledged'
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = acknowledged_by
            if notes:
                alert.notes = notes
            db.session.commit()
            return alert
        return None
    
    @staticmethod
    def resolve_alert(alert_id, resolved_by, action_taken, notes=None):
        """Resolve an alert"""
        alert = Alert.query.get(alert_id)
        if alert:
            alert.status = 'Resolved'
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = resolved_by
            alert.action_taken = action_taken
            if notes:
                alert.notes = notes
            db.session.commit()
            return alert
        return None
    
    @staticmethod
    def batch_generate_alerts():
        """Generate alerts for all students (can be run as scheduled task)"""
        students = Student.query.all()
        total_alerts = 0
        
        for student in students:
            alerts = AlertController.generate_alerts_for_student(student.id)
            if alerts:
                total_alerts += len(alerts)
        
        return {
            'total_students_checked': len(students),
            'total_alerts_generated': total_alerts
        }
    
    @staticmethod
    def get_alert_statistics():
        """Get overall alert statistics"""
        return {
            'total_active': Alert.query.filter_by(status='Active').count(),
            'total_acknowledged': Alert.query.filter_by(status='Acknowledged').count(),
            'total_resolved': Alert.query.filter_by(status='Resolved').count(),
            'by_severity': {
                'critical': Alert.query.filter_by(status='Active', severity='Critical').count(),
                'high': Alert.query.filter_by(status='Active', severity='High').count(),
                'medium': Alert.query.filter_by(status='Active', severity='Medium').count(),
                'low': Alert.query.filter_by(status='Active', severity='Low').count()
            },
            'by_type': {
                'academic': Alert.query.filter_by(status='Active', alert_type='Academic').count(),
                'behavioral': Alert.query.filter_by(status='Active', alert_type='Behavioral').count(),
                'financial': Alert.query.filter_by(status='Active', alert_type='Financial').count(),
                'psychological': Alert.query.filter_by(status='Active', alert_type='Psychological').count()
            }
        }
