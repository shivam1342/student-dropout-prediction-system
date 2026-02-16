"""
Counselling Controller
Generates recommendations based on student risk factors.
"""

def generate_recommendations(top_features):
    """
    Generates counselling recommendations based on a rule-based system.

    Args:
        top_features (list): List of dictionaries of top contributing features.

    Returns:
        list: A list of dictionaries, each containing an intervention type and recommendation.
    """
    recommendations = []
    
    # Rule-based logic
    for feature in top_features:
        feature_name = feature['name'].lower().replace(' ', '_')
        feature_value = feature['value']
        
        rec = {'intervention_type': 'General', 'recommendation': 'Monitor student closely.'}
        
        if feature_name == 'attendance_rate' and feature_value < 80:
            rec['intervention_type'] = 'Academic'
            rec['recommendation'] = f"Low attendance ({feature_value}%). Schedule a meeting to discuss potential issues."
        elif feature_name == 'gpa' and feature_value < 2.5:
            rec['intervention_type'] = 'Academic'
            rec['recommendation'] = f"Low GPA ({feature_value}). Recommend academic support or tutoring."
        elif feature_name == 'fees_paid' and feature_value == 0:
            rec['intervention_type'] = 'Financial'
            rec['recommendation'] = "No fees paid. Connect student with the financial aid office."
        elif feature_name == 'mentor_meetings' and feature_value == 0:
            rec['intervention_type'] = 'Engagement'
            rec['recommendation'] = "No mentor meetings recorded. Assign a mentor and schedule an introductory session."
        
        if rec not in recommendations:
            recommendations.append(rec)
            
    if not recommendations:
        recommendations.append({
            'intervention_type': 'Proactive',
            'recommendation': 'Student profile appears stable, but proactive check-in is advised.'
        })
        
    return recommendations
