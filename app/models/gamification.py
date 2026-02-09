"""
Gamification Model
Tracks student engagement through points, badges, streaks, and achievements
"""
from app.extensions import db
from datetime import datetime


class GamificationProfile(db.Model):
    """Student gamification profile with points, badges, and achievements"""
    __tablename__ = 'gamification_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Points system
    total_points = db.Column(db.Integer, default=0)
    academic_points = db.Column(db.Integer, default=0)
    attendance_points = db.Column(db.Integer, default=0)
    engagement_points = db.Column(db.Integer, default=0)
    improvement_points = db.Column(db.Integer, default=0)
    
    # Level system
    level = db.Column(db.Integer, default=1)
    experience_to_next_level = db.Column(db.Integer, default=100)
    
    # Streaks
    current_attendance_streak = db.Column(db.Integer, default=0)
    longest_attendance_streak = db.Column(db.Integer, default=0)
    current_submission_streak = db.Column(db.Integer, default=0)
    longest_submission_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    
    # Badges earned (JSON array of badge objects)
    badges = db.Column(db.JSON, default=list)
    
    # Achievements (JSON array of achievement objects)
    achievements = db.Column(db.JSON, default=list)
    
    # Challenges completed
    challenges_completed = db.Column(db.Integer, default=0)
    current_challenges = db.Column(db.JSON, default=list)
    
    # Leaderboard rank
    rank_in_class = db.Column(db.Integer)
    rank_in_school = db.Column(db.Integer)
    
    @property
    def current_streak(self):
        """Get the highest current streak"""
        return max(self.current_attendance_streak or 0, self.current_submission_streak or 0)
    
    @property
    def longest_streak(self):
        """Get the longest streak ever"""
        return max(self.longest_attendance_streak or 0, self.longest_submission_streak or 0)
    
    @property
    def badges_earned(self):
        """Get list of badge names"""
        if not self.badges:
            return []
        return [badge.get('name') for badge in self.badges if isinstance(badge, dict)]
    
    @property
    def participation_points(self):
        """Alias for engagement points for compatibility"""
        return self.engagement_points
    
    @property
    def social_points(self):
        """Social points (part of engagement)"""
        return 0  # Can be calculated from engagement if needed
    
    def __repr__(self):
        return f'<GamificationProfile {self.student_id}: Level {self.level}, {self.total_points} points>'
    
    def add_points(self, points, category='general'):
        """Add points to student profile"""
        self.total_points += points
        
        if category == 'academic':
            self.academic_points += points
        elif category == 'attendance':
            self.attendance_points += points
        elif category == 'engagement':
            self.engagement_points += points
        elif category == 'improvement':
            self.improvement_points += points
        
        # Check for level up
        while self.total_points >= self.experience_to_next_level:
            self.level += 1
            self.experience_to_next_level = self.level * 100
    
    def award_badge(self, badge_name, badge_description, badge_icon=None):
        """Award a badge to the student"""
        badge = {
            'name': badge_name,
            'description': badge_description,
            'icon': badge_icon,
            'earned_at': datetime.utcnow().isoformat()
        }
        if self.badges is None:
            self.badges = []
        self.badges.append(badge)
    
    def unlock_achievement(self, achievement_name, achievement_description):
        """Unlock an achievement"""
        achievement = {
            'name': achievement_name,
            'description': achievement_description,
            'unlocked_at': datetime.utcnow().isoformat()
        }
        if self.achievements is None:
            self.achievements = []
        self.achievements.append(achievement)
    
    def update_streak(self, streak_type='attendance'):
        """Update activity streaks"""
        today = datetime.utcnow().date()
        
        if self.last_activity_date:
            days_diff = (today - self.last_activity_date).days
            
            if days_diff == 1:  # Consecutive day
                if streak_type == 'attendance':
                    self.current_attendance_streak += 1
                    if self.current_attendance_streak > self.longest_attendance_streak:
                        self.longest_attendance_streak = self.current_attendance_streak
                elif streak_type == 'submission':
                    self.current_submission_streak += 1
                    if self.current_submission_streak > self.longest_submission_streak:
                        self.longest_submission_streak = self.current_submission_streak
            elif days_diff > 1:  # Streak broken
                if streak_type == 'attendance':
                    self.current_attendance_streak = 1
                elif streak_type == 'submission':
                    self.current_submission_streak = 1
        else:
            # First activity
            if streak_type == 'attendance':
                self.current_attendance_streak = 1
            elif streak_type == 'submission':
                self.current_submission_streak = 1
        
        self.last_activity_date = today
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'total_points': self.total_points,
            'academic_points': self.academic_points,
            'attendance_points': self.attendance_points,
            'engagement_points': self.engagement_points,
            'improvement_points': self.improvement_points,
            'level': self.level,
            'experience_to_next_level': self.experience_to_next_level,
            'current_attendance_streak': self.current_attendance_streak,
            'longest_attendance_streak': self.longest_attendance_streak,
            'current_submission_streak': self.current_submission_streak,
            'longest_submission_streak': self.longest_submission_streak,
            'badges': self.badges or [],
            'achievements': self.achievements or [],
            'challenges_completed': self.challenges_completed,
            'current_challenges': self.current_challenges or [],
            'rank_in_class': self.rank_in_class,
            'rank_in_school': self.rank_in_school,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None
        }
