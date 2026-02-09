"""
Gamification Routes Blueprint
Handles leaderboard, badges, and gamification features
"""
from flask import Blueprint, render_template, request, jsonify
from app.models import GamificationProfile, Student
from controllers.gamification_controller import GamificationController
from app.extensions import db
from sqlalchemy import desc

gamification_bp = Blueprint('gamification_bp', __name__)

@gamification_bp.route('/leaderboard')
def leaderboard():
    """Main leaderboard page"""
    # Get limit from query params (default 20)
    limit = request.args.get('limit', 20, type=int)
    category = request.args.get('category', 'all')
    
    # Get top students by total points
    if category == 'all':
        top_students = GamificationProfile.query.order_by(
            desc(GamificationProfile.total_points)
        ).limit(limit).all()
    else:
        # Sort by specific category points
        top_students = GamificationProfile.query.order_by(
            desc(getattr(GamificationProfile, f'{category}_points'))
        ).limit(limit).all()
    
    # Get leaderboard statistics
    stats = GamificationController.get_leaderboard_statistics()
    
    # Get available badges
    all_badges = GamificationController.get_all_available_badges()
    
    return render_template('leaderboard.html',
                         top_students=top_students,
                         limit=limit,
                         category=category,
                         stats=stats,
                         all_badges=all_badges)

@gamification_bp.route('/badges')
def badge_gallery():
    """Badge gallery page showing all available badges"""
    # Get all available badges
    badges = GamificationController.get_all_available_badges()
    
    # Get badge statistics - count students who have each badge
    badge_stats = {}
    all_profiles = GamificationProfile.query.all()
    
    for badge_name in badges:
        count = 0
        for profile in all_profiles:
            if profile.badges and isinstance(profile.badges, list):
                # Check if badge name is in the badges list
                badge_names = [b.get('name') if isinstance(b, dict) else b for b in profile.badges]
                if badge_name in badge_names:
                    count += 1
        badge_stats[badge_name] = count
    
    # Calculate total profiles for percentage
    total_profiles = len(all_profiles)
    
    return render_template('badge_gallery.html',
                         badges=badges,
                         badge_stats=badge_stats,
                         total_profiles=total_profiles)

@gamification_bp.route('/profile/<int:student_id>')
def gamification_profile(student_id):
    """Detailed gamification profile for a student"""
    student = Student.query.get_or_404(student_id)
    profile = GamificationProfile.query.filter_by(student_id=student_id).first()
    
    if not profile:
        # Create profile if it doesn't exist
        profile = GamificationController.initialize_profile(student_id)
    
    # Get student's rank
    rank = GamificationController.get_student_rank(student_id)
    
    # Get points breakdown
    points_breakdown = {
        'Academic': profile.academic_points,
        'Attendance': profile.attendance_points,
        'Participation': profile.participation_points,
        'Engagement': profile.engagement_points,
        'Social': profile.social_points
    }
    
    # Get achievement timeline
    timeline = GamificationController.get_achievement_timeline(student_id)
    
    # Calculate level progress
    level_progress = GamificationController.calculate_level_progress(profile.total_points)
    
    return render_template('gamification_profile.html',
                         student=student,
                         profile=profile,
                         rank=rank,
                         points_breakdown=points_breakdown,
                         timeline=timeline,
                         level_progress=level_progress)

@gamification_bp.route('/api/leaderboard')
def leaderboard_api():
    """API endpoint for leaderboard data (JSON)"""
    limit = request.args.get('limit', 10, type=int)
    category = request.args.get('category', 'all')
    
    if category == 'all':
        profiles = GamificationProfile.query.order_by(
            desc(GamificationProfile.total_points)
        ).limit(limit).all()
    else:
        profiles = GamificationProfile.query.order_by(
            desc(getattr(GamificationProfile, f'{category}_points'))
        ).limit(limit).all()
    
    leaderboard_data = []
    for i, profile in enumerate(profiles, 1):
        leaderboard_data.append({
            'rank': i,
            'student_id': profile.student_id,
            'student_name': profile.student.name if profile.student else 'Unknown',
            'total_points': profile.total_points,
            'level': profile.level,
            'badges_count': len(profile.badges_earned or []),
            'current_streak': profile.current_streak
        })
    
    return jsonify(leaderboard_data)

@gamification_bp.route('/api/badges/<int:student_id>')
def student_badges_api(student_id):
    """API endpoint for student badges (JSON)"""
    profile = GamificationProfile.query.filter_by(student_id=student_id).first()
    
    if not profile:
        return jsonify({'badges': [], 'count': 0})
    
    return jsonify({
        'badges': profile.badges_earned or [],
        'count': len(profile.badges_earned or []),
        'total_points': profile.total_points,
        'level': profile.level
    })

@gamification_bp.route('/api/stats')
def gamification_stats_api():
    """API endpoint for gamification statistics"""
    stats = GamificationController.get_leaderboard_statistics()
    return jsonify(stats)

@gamification_bp.route('/widget/ranking/<int:student_id>')
def ranking_widget(student_id):
    """Widget showing student ranking (for embedding in profile)"""
    profile = GamificationProfile.query.filter_by(student_id=student_id).first()
    
    if not profile:
        return render_template('widgets/ranking_widget.html',
                             profile=None,
                             rank=None,
                             total_students=0)
    
    rank = GamificationController.get_student_rank(student_id)
    total_students = GamificationProfile.query.count()
    
    # Get nearby students in ranking
    nearby_ranks = []
    if rank:
        # Get 2 above and 2 below
        profiles = GamificationProfile.query.order_by(
            desc(GamificationProfile.total_points)
        ).all()
        
        start_idx = max(0, rank - 3)
        end_idx = min(len(profiles), rank + 2)
        nearby_ranks = profiles[start_idx:end_idx]
    
    return render_template('widgets/ranking_widget.html',
                         profile=profile,
                         rank=rank,
                         total_students=total_students,
                         nearby_ranks=nearby_ranks)

@gamification_bp.route('/widget/badges/<int:student_id>')
def badges_widget(student_id):
    """Widget showing student badges (for embedding)"""
    profile = GamificationProfile.query.filter_by(student_id=student_id).first()
    
    if not profile:
        return render_template('widgets/badges_widget.html',
                             badges=[],
                             total_badges=0)
    
    badges = profile.badges_earned or []
    all_badges = GamificationController.get_all_available_badges()
    
    return render_template('widgets/badges_widget.html',
                         badges=badges,
                         total_badges=len(badges),
                         all_badges=all_badges)

@gamification_bp.route('/widget/progress/<int:student_id>')
def progress_widget(student_id):
    """Widget showing level progress (for embedding)"""
    profile = GamificationProfile.query.filter_by(student_id=student_id).first()
    
    if not profile:
        return render_template('widgets/progress_widget.html',
                             profile=None,
                             level_progress=None)
    
    level_progress = GamificationController.calculate_level_progress(profile.total_points)
    
    return render_template('widgets/progress_widget.html',
                         profile=profile,
                         level_progress=level_progress)
