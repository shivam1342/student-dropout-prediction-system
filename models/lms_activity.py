"""
LMS Activity Model
Tracks student engagement with Learning Management System
"""
from extensions import db
from datetime import datetime


class LMSActivity(db.Model):
    """Learning Management System activity tracking"""
    __tablename__ = 'lms_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    activity_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Activity metrics
    login_count = db.Column(db.Integer, default=0)
    assignment_submissions = db.Column(db.Integer, default=0)
    forum_posts = db.Column(db.Integer, default=0)
    video_watch_time = db.Column(db.Float, default=0.0)  # in hours
    quiz_attempts = db.Column(db.Integer, default=0)
    resource_downloads = db.Column(db.Integer, default=0)
    
    # Engagement score (0-100)
    engagement_score = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<LMSActivity {self.student_id}: {self.activity_date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'activity_date': self.activity_date.isoformat(),
            'login_count': self.login_count,
            'assignment_submissions': self.assignment_submissions,
            'forum_posts': self.forum_posts,
            'video_watch_time': self.video_watch_time,
            'quiz_attempts': self.quiz_attempts,
            'resource_downloads': self.resource_downloads,
            'engagement_score': self.engagement_score
        }
