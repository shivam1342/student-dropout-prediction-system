"""
Intervention Controller
Manages interventions, support services, and outcome tracking
"""
from datetime import datetime, timedelta
from app.models import Student, Intervention, Alert
from app.extensions import db


class InterventionController:
    """Controller for managing student interventions"""
    
    @staticmethod
    def create_intervention(student_id, intervention_type, priority, description, 
                          scheduled_date, assigned_to=None, alert_id=None):
        """Create a new intervention for a student"""
        intervention = Intervention(
            student_id=student_id,
            intervention_type=intervention_type,
            priority=priority,
            description=description,
            scheduled_date=scheduled_date,
            assigned_to=assigned_to,
            alert_id=alert_id,
            status='Scheduled',
            category=intervention_type,  # Default category to type
            title=f"{intervention_type} for student"
        )
        
        db.session.add(intervention)
        db.session.commit()
        
        return intervention
    
    @staticmethod
    def create_intervention_from_alert(alert_id, assigned_to, scheduled_date=None):
        """Create an intervention based on an alert"""
        alert = Alert.query.get(alert_id)
        if not alert:
            return None
        
        # Determine intervention type and category based on alert
        intervention_type = alert.alert_type
        category_mapping = {
            'Academic': 'Tutoring',
            'Behavioral': 'Counselling',
            'Financial': 'Financial Aid',
            'Psychological': 'Psychological Support'
        }
        
        category = category_mapping.get(alert.alert_type, 'General Support')
        
        intervention = Intervention(
            student_id=alert.student_id,
            intervention_type=intervention_type,
            category=category,
            title=f'Intervention for: {alert.title}',
            description=f'Alert-triggered intervention: {alert.description}',
            scheduled_date=scheduled_date or (datetime.utcnow() + timedelta(days=1)),
            assigned_to=assigned_to,
            status='Scheduled',
            follow_up_required=True,
            resources_provided=alert.recommended_actions or []
        )
        
        db.session.add(intervention)
        
        # Acknowledge the alert
        alert.status = 'Acknowledged'
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = assigned_to
        alert.notes = f'Intervention created: {intervention.title}'
        
        db.session.commit()
        
        return intervention
    
    @staticmethod
    def get_interventions(student_id=None, status=None, intervention_type=None):
        """Get interventions with optional filters"""
        query = Intervention.query
        
        if student_id:
            query = query.filter_by(student_id=student_id)
        if status:
            query = query.filter_by(status=status)
        if intervention_type:
            query = query.filter_by(intervention_type=intervention_type)
        
        return query.order_by(Intervention.scheduled_date.desc()).all()
    
    @staticmethod
    def get_upcoming_interventions(days_ahead=7):
        """Get upcoming interventions within specified days"""
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        interventions = Intervention.query.filter(
            Intervention.status == 'Scheduled',
            Intervention.scheduled_date <= end_date,
            Intervention.scheduled_date >= datetime.utcnow()
        ).order_by(Intervention.scheduled_date).all()
        
        return interventions
    
    @staticmethod
    def update_intervention_status(intervention_id, new_status):
        """Update intervention status"""
        intervention = Intervention.query.get(intervention_id)
        if not intervention:
            return None
        
        intervention.status = new_status
        
        if new_status == 'In Progress':
            # Intervention has started
            pass
        elif new_status == 'Completed':
            intervention.completed_date = datetime.utcnow()
        elif new_status == 'Cancelled':
            # Mark as cancelled
            pass
        
        db.session.commit()
        return intervention
    
    @staticmethod
    def complete_intervention(intervention_id, outcome, effectiveness_rating, notes=None,
                            follow_up_required=False, follow_up_date=None):
        """Mark intervention as completed with outcome"""
        intervention = Intervention.query.get(intervention_id)
        if not intervention:
            return None
        
        intervention.status = 'Completed'
        intervention.completed_date = datetime.utcnow()
        intervention.outcome = outcome
        intervention.effectiveness_rating = effectiveness_rating
        intervention.notes = notes
        intervention.follow_up_required = follow_up_required
        intervention.follow_up_date = follow_up_date
        
        db.session.commit()
        
        # Check if related alert should be resolved
        InterventionController._check_alert_resolution(intervention)
        
        return intervention
    
    @staticmethod
    def _check_alert_resolution(intervention):
        """Check if associated alert can be resolved based on intervention outcome"""
        # Find related active alerts for the student
        active_alerts = Alert.query.filter_by(
            student_id=intervention.student_id,
            alert_type=intervention.intervention_type,
            status='Acknowledged'
        ).all()
        
        # If intervention was effective (rating >= 4), resolve related alerts
        if intervention.effectiveness_rating and intervention.effectiveness_rating >= 4:
            for alert in active_alerts:
                alert.status = 'Resolved'
                alert.resolved_at = datetime.utcnow()
                alert.resolved_by = intervention.assigned_to
                alert.action_taken = f'Intervention completed: {intervention.title}'
            
            db.session.commit()
    
    @staticmethod
    def add_intervention_notes(intervention_id, notes):
        """Add notes to an intervention"""
        intervention = Intervention.query.get(intervention_id)
        if not intervention:
            return None
        
        intervention.follow_up_notes = notes
        db.session.commit()
        return intervention
    
    @staticmethod
    def get_intervention_statistics(student_id=None):
        """Get intervention statistics"""
        query = Intervention.query
        if student_id:
            query = query.filter_by(student_id=student_id)
        
        total = query.count()
        completed = query.filter_by(status='Completed').count()
        scheduled = query.filter_by(status='Scheduled').count()
        in_progress = query.filter_by(status='In Progress').count()
        cancelled = query.filter_by(status='Cancelled').count()
        
        # Calculate average effectiveness rating
        completed_interventions = query.filter(
            Intervention.status == 'Completed',
            Intervention.effectiveness_rating.isnot(None)
        ).all()
        
        avg_effectiveness = 0
        if completed_interventions:
            avg_effectiveness = sum(i.effectiveness_rating for i in completed_interventions) / len(completed_interventions)
        
        # Interventions by type
        by_type = {}
        for intervention_type in ['Academic Support', 'Counseling', 'Financial Aid', 'Mentoring', 'Peer Support']:
            count = query.filter_by(intervention_type=intervention_type).count()
            by_type[intervention_type] = count
        
        # Count follow-ups due
        follow_up_due = query.filter(
            Intervention.follow_up_required == True,
            Intervention.follow_up_date <= datetime.utcnow() + timedelta(days=7),
            Intervention.status == 'Completed'
        ).count()
        
        return {
            'total': total,
            'by_status': {
                'Scheduled': scheduled,
                'In Progress': in_progress,
                'Completed': completed,
                'Cancelled': cancelled
            },
            'avg_effectiveness': round(avg_effectiveness, 2) if avg_effectiveness else 0,
            'by_type': by_type,
            'completion_rate': round((completed / total * 100), 2) if total > 0 else 0,
            'follow_up_due': follow_up_due
        }
    
    @staticmethod
    def get_intervention_outcomes(intervention_type=None, min_rating=None):
        """Get intervention outcomes for analysis"""
        query = Intervention.query.filter_by(status='Completed')
        
        if intervention_type:
            query = query.filter_by(intervention_type=intervention_type)
        if min_rating:
            query = query.filter(Intervention.effectiveness_rating >= min_rating)
        
        interventions = query.all()
        
        outcomes = []
        for intervention in interventions:
            student = Student.query.get(intervention.student_id)
            outcomes.append({
                'student_name': student.name if student else 'Unknown',
                'intervention_type': intervention.intervention_type,
                'category': intervention.category,
                'title': intervention.title,
                'completed_date': intervention.completed_date.isoformat() if intervention.completed_date else None,
                'effectiveness_rating': intervention.effectiveness_rating,
                'outcome': intervention.outcome,
                'follow_up_required': intervention.follow_up_required
            })
        
        return outcomes
    
    @staticmethod
    def schedule_follow_up(intervention_id, follow_up_date, follow_up_notes):
        """Schedule a follow-up for an intervention"""
        intervention = Intervention.query.get(intervention_id)
        if not intervention:
            return None
        
        intervention.follow_up_required = True
        intervention.follow_up_date = follow_up_date
        intervention.follow_up_notes = follow_up_notes
        
        db.session.commit()
        return intervention
    
    @staticmethod
    def get_follow_ups_due(days_ahead=7):
        """Get interventions with follow-ups due"""
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        interventions = Intervention.query.filter(
            Intervention.follow_up_required == True,
            Intervention.follow_up_date <= end_date,
            Intervention.follow_up_date >= datetime.utcnow()
        ).order_by(Intervention.follow_up_date).all()
        
        return interventions
    
    @staticmethod
    def get_student_intervention_history(student_id):
        """Get comprehensive intervention history for a student"""
        interventions = Intervention.query.filter_by(student_id=student_id).order_by(Intervention.created_at.desc()).all()
        
        student = Student.query.get(student_id)
        
        return {
            'student_name': student.name if student else 'Unknown',
            'total_interventions': len(interventions),
            'interventions': [i.to_dict() for i in interventions],
            'statistics': InterventionController.get_intervention_statistics(student_id)
        }
    
    @staticmethod
    def recommend_interventions(student_id):
        """Recommend interventions based on student's active alerts"""
        active_alerts = Alert.query.filter_by(student_id=student_id, status='Active').all()
        
        recommendations = []
        
        for alert in active_alerts:
            recommendation = {
                'alert_id': alert.id,
                'alert_title': alert.title,
                'severity': alert.severity,
                'recommended_intervention_type': alert.alert_type,
                'suggested_category': InterventionController._suggest_category(alert.alert_type),
                'suggested_actions': alert.recommended_actions,
                'urgency': InterventionController._calculate_urgency(alert)
            }
            recommendations.append(recommendation)
        
        # Sort by urgency
        recommendations.sort(key=lambda x: x['urgency'], reverse=True)
        
        return recommendations
    
    @staticmethod
    def _suggest_category(alert_type):
        """Suggest intervention category based on alert type"""
        mapping = {
            'Academic': 'Tutoring',
            'Behavioral': 'Counselling',
            'Financial': 'Financial Aid',
            'Psychological': 'Psychological Support'
        }
        return mapping.get(alert_type, 'General Support')
    
    @staticmethod
    def _calculate_urgency(alert):
        """Calculate urgency score (0-100) for an alert"""
        severity_scores = {'Critical': 100, 'High': 75, 'Medium': 50, 'Low': 25}
        base_score = severity_scores.get(alert.severity, 0)
        
        # Increase urgency based on how long alert has been active
        days_active = (datetime.utcnow() - alert.created_at).days
        urgency_boost = min(days_active * 5, 25)  # Max 25 points boost
        
        return min(base_score + urgency_boost, 100)
    
    @staticmethod
    def get_active_alerts():
        """Get all active alerts for generating interventions"""
        return Alert.query.filter_by(status='Active').all()
    
    @staticmethod
    def batch_generate_alerts():
        """Batch generate alerts for all students (placeholder)"""
        # This would typically check all students and create alerts
        # For now, return count of existing active alerts
        return Alert.query.filter_by(status='Active').count()

