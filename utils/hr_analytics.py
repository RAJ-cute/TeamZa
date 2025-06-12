import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
from models import Employee, LearningProgress, WellnessCheck, PerformanceReview

class HRAnalytics:
    """HR Analytics processor for various HR insights"""
    
    def __init__(self):
        self.leadership_weights = {
            'performance_score': 0.3,
            'experience_years': 0.2,
            'team_feedback': 0.2,
            'initiative_taking': 0.15,
            'communication_skills': 0.15
        }
    
    def calculate_leadership_potential(self, employee):
        """Calculate leadership potential score for an employee"""
        # Mock calculation based on various factors
        base_score = employee.performance_score or 5.0
        
        # Calculate years of experience
        experience_years = (datetime.now().date() - employee.hire_date).days / 365.25
        experience_score = min(experience_years / 5 * 10, 10)  # Max 10 for 5+ years
        
        # Mock additional scores (in real implementation, these would come from surveys/feedback)
        team_feedback_score = random.uniform(6, 10)
        initiative_score = random.uniform(5, 10)
        communication_score = random.uniform(6, 10)
        
        # Calculate weighted score
        potential_score = (
            base_score * self.leadership_weights['performance_score'] +
            experience_score * self.leadership_weights['experience_years'] +
            team_feedback_score * self.leadership_weights['team_feedback'] +
            initiative_score * self.leadership_weights['initiative_taking'] +
            communication_score * self.leadership_weights['communication_skills']
        )
        
        return round(potential_score, 2)
    
    def suggest_growth_actions(self, employee, potential_score):
        """Suggest growth actions based on leadership potential"""
        actions = []
        
        if potential_score >= 8.5:
            actions = [
                "Enroll in Executive Leadership Program",
                "Assign mentorship role for junior employees",
                "Include in strategic planning sessions",
                "Consider for cross-functional project leadership"
            ]
        elif potential_score >= 7.0:
            actions = [
                "Participate in Leadership Development Workshop",
                "Shadow senior management in meetings",
                "Lead a small team project",
                "Attend advanced communication training"
            ]
        else:
            actions = [
                "Focus on performance improvement",
                "Participate in team collaboration workshops",
                "Seek mentorship from senior colleagues",
                "Develop technical skills relevant to role"
            ]
        
        return actions
    
    def generate_appraisal_insights(self, reviews):
        """Generate insights from performance reviews"""
        if not reviews:
            return {
                'avg_rating': 0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'trends': [],
                'top_performers': [],
                'improvement_needed': []
            }
        
        # Calculate average rating
        avg_rating = sum(review.overall_rating for review in reviews) / len(reviews)
        
        # Sentiment distribution
        sentiment_dist = {'positive': 0, 'neutral': 0, 'negative': 0}
        for review in reviews:
            if review.sentiment_score >= 7:
                sentiment_dist['positive'] += 1
            elif review.sentiment_score >= 4:
                sentiment_dist['neutral'] += 1
            else:
                sentiment_dist['negative'] += 1
        
        # Top performers and improvement needed
        sorted_reviews = sorted(reviews, key=lambda x: x.overall_rating, reverse=True)
        top_performers = [
            {'name': review.employee.name, 'rating': review.overall_rating}
            for review in sorted_reviews[:5]
        ]
        
        improvement_needed = [
            {'name': review.employee.name, 'rating': review.overall_rating}
            for review in sorted_reviews[-5:] if review.overall_rating < 6
        ]
        
        return {
            'avg_rating': round(avg_rating, 2),
            'sentiment_distribution': sentiment_dist,
            'total_reviews': len(reviews),
            'top_performers': top_performers,
            'improvement_needed': improvement_needed
        }
    
    def calculate_quiz_score(self, user_answers, correct_answers):
        """Calculate quiz score"""
        if not correct_answers or not user_answers:
            return 0
        
        correct_count = sum(1 for i, answer in enumerate(user_answers) 
                          if i < len(correct_answers) and answer == correct_answers[i])
        
        return int((correct_count / len(correct_answers)) * 100)
    
    def get_learning_leaderboard(self):
        """Get learning leaderboard"""
        from app import db
        
        # Query learning progress and calculate total scores
        results = db.session.query(
            Employee.name,
            db.func.sum(LearningProgress.score).label('total_score'),
            db.func.count(LearningProgress.id).label('modules_completed')
        ).join(LearningProgress).group_by(Employee.id).order_by(
            db.func.sum(LearningProgress.score).desc()
        ).limit(10).all()
        
        leaderboard = []
        for i, (name, total_score, modules_completed) in enumerate(results):
            leaderboard.append({
                'rank': i + 1,
                'name': name,
                'total_score': total_score or 0,
                'modules_completed': modules_completed,
                'badge': self._get_badge(total_score or 0)
            })
        
        return leaderboard
    
    def _get_badge(self, score):
        """Get badge based on score"""
        if score >= 800:
            return 'Expert'
        elif score >= 600:
            return 'Advanced'
        elif score >= 400:
            return 'Intermediate'
        elif score >= 200:
            return 'Beginner'
        else:
            return 'Novice'
    
    def analyze_skill_gaps(self, current_skills, target_role):
        """Analyze skill gaps for a target role"""
        # Define role requirements (mock data)
        role_requirements = {
            'Software Engineer': ['python', 'java', 'sql', 'git', 'agile', 'problem solving'],
            'Data Scientist': ['python', 'r', 'sql', 'machine learning', 'statistics', 'pandas', 'numpy'],
            'Product Manager': ['agile', 'scrum', 'leadership', 'communication', 'project planning'],
            'DevOps Engineer': ['aws', 'docker', 'kubernetes', 'linux', 'ansible', 'terraform'],
            'UI/UX Designer': ['figma', 'sketch', 'photoshop', 'ui/ux', 'user research', 'prototyping']
        }
        
        required_skills = set(role_requirements.get(target_role, []))
        current_skills_set = set([skill.lower() for skill in current_skills])
        
        # Find gaps
        skill_gaps = required_skills - current_skills_set
        matching_skills = required_skills.intersection(current_skills_set)
        
        # Generate recommendations
        recommendations = []
        for skill in skill_gaps:
            urgency = 'High' if skill in ['python', 'java', 'sql', 'leadership'] else 'Medium'
            recommendations.append({
                'skill': skill,
                'urgency': urgency,
                'resources': self._get_learning_resources(skill)
            })
        
        return {
            'required_skills': list(required_skills),
            'current_skills': current_skills,
            'matching_skills': list(matching_skills),
            'skill_gaps': list(skill_gaps),
            'match_percentage': len(matching_skills) / len(required_skills) * 100 if required_skills else 0,
            'recommendations': recommendations
        }
    
    def _get_learning_resources(self, skill):
        """Get learning resources for a skill"""
        resources_db = {
            'python': ['Python Crash Course (Book)', 'Codecademy Python Track', 'Python.org Tutorial'],
            'java': ['Oracle Java Tutorials', 'Java: The Complete Reference', 'Spring Framework Course'],
            'sql': ['SQLBolt Interactive Tutorial', 'SQL Zoo', 'Database Systems Course'],
            'machine learning': ['Coursera ML Course', 'Hands-On ML Book', 'Kaggle Learn'],
            'aws': ['AWS Free Tier', 'AWS Certified Solutions Architect', 'A Cloud Guru'],
            'leadership': ['Leadership 101 Workshop', 'Harvard Leadership Course', 'Dale Carnegie Training']
        }
        
        return resources_db.get(skill.lower(), ['Online Courses', 'Books', 'Workshops'])
    
    def calculate_wellness_score(self, stress_level, sleep_quality, focus_level):
        """Calculate overall wellness score"""
        # Invert stress level (higher stress = lower wellness)
        stress_score = 11 - stress_level
        
        # Average the three components
        wellness_score = (stress_score + sleep_quality + focus_level) / 3
        
        return round(wellness_score, 2)
    
    def get_wellness_status(self, wellness_score):
        """Get wellness status based on score"""
        if wellness_score >= 7:
            return 'green'
        elif wellness_score >= 4:
            return 'yellow'
        else:
            return 'red'
    
    def get_wellness_recommendations(self, status, stress_level, sleep_quality, focus_level):
        """Get wellness recommendations"""
        recommendations = []
        
        if stress_level >= 7:
            recommendations.extend([
                "Take a 10-minute break every hour",
                "Practice deep breathing exercises",
                "Consider speaking with a counselor"
            ])
        
        if sleep_quality <= 4:
            recommendations.extend([
                "Establish a regular sleep schedule",
                "Avoid screens 1 hour before bedtime",
                "Create a relaxing bedtime routine"
            ])
        
        if focus_level <= 4:
            recommendations.extend([
                "Try the Pomodoro Technique",
                "Minimize distractions in your workspace",
                "Take short walks to clear your mind"
            ])
        
        if status == 'green':
            recommendations.append("Keep up the great work! You're doing well.")
        elif status == 'yellow':
            recommendations.append("Consider implementing some wellness practices.")
        else:
            recommendations.append("Please prioritize your well-being and consider reaching out for support.")
        
        return recommendations
    
    def generate_hr_insights(self):
        """Generate comprehensive HR insights"""
        from app import db
        
        # Basic statistics
        total_employees = Employee.query.count()
        departments = db.session.query(Employee.department, db.func.count(Employee.id)).group_by(Employee.department).all()
        
        # Performance distribution
        performance_data = db.session.query(Employee.performance_score).all()
        avg_performance = sum(score[0] for score in performance_data if score[0]) / len(performance_data) if performance_data else 0
        
        # Wellness trends
        wellness_checks = WellnessCheck.query.order_by(WellnessCheck.check_date.desc()).limit(30).all()
        wellness_distribution = {'green': 0, 'yellow': 0, 'red': 0}
        for check in wellness_checks:
            wellness_distribution[check.overall_wellness] += 1
        
        # Learning engagement
        learning_completion = db.session.query(
            db.func.count(LearningProgress.id).label('total'),
            db.func.sum(db.case((LearningProgress.completed == True, 1), else_=0)).label('completed')
        ).first()
        
        completion_rate = (learning_completion.completed / learning_completion.total * 100) if learning_completion.total else 0
        
        # Mock additional data for demonstration
        attrition_data = [
            {'month': 'Jan', 'rate': 2.1},
            {'month': 'Feb', 'rate': 1.8},
            {'month': 'Mar', 'rate': 2.3},
            {'month': 'Apr', 'rate': 1.9},
            {'month': 'May', 'rate': 2.0},
            {'month': 'Jun', 'rate': 1.7}
        ]
        
        return {
            'total_employees': total_employees,
            'departments': dict(departments),
            'avg_performance': round(avg_performance, 2),
            'wellness_distribution': wellness_distribution,
            'learning_completion_rate': round(completion_rate, 1),
            'attrition_data': attrition_data,
            'engagement_score': random.uniform(7.5, 9.0),  # Mock engagement score
            'diversity_stats': {
                'gender_distribution': {'Male': 52, 'Female': 45, 'Other': 3},
                'age_groups': {'20-30': 35, '30-40': 40, '40-50': 20, '50+': 5}
            }
        }
