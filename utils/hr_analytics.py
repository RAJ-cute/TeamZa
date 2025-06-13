import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
from models import Employee, LearningProgress, WellnessCheck, PerformanceReview, HRTransaction, HealthMetrics

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
        """Suggest growth actions for employee development"""
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
    
    def generate_performance_review_with_reviewer(self, employee_name, performance_score):
        """Generate a mock performance review with AI-driven feedback"""
        # Simulate different reviewer perspectives
        reviewers = ['Manager', 'Peer', 'Direct Report', 'Cross-functional Team Lead']
        reviewer = random.choice(reviewers)
        
        # Generate review based on performance score
        if performance_score >= 8.5:
            feedback_templates = [
                f"{employee_name} consistently exceeds expectations and demonstrates exceptional leadership qualities.",
                f"Outstanding performance by {employee_name}. Shows initiative and drives results effectively.",
                f"{employee_name} is a top performer who consistently delivers high-quality work and mentors others."
            ]
            sentiment_score = random.uniform(8.5, 10)
        elif performance_score >= 6.5:
            feedback_templates = [
                f"{employee_name} meets expectations and shows good potential for growth.",
                f"Solid performance by {employee_name}. Areas identified for continued development.",
                f"{employee_name} demonstrates competency in role with room for improvement in leadership skills."
            ]
            sentiment_score = random.uniform(6, 8)
        else:
            feedback_templates = [
                f"{employee_name} needs improvement in several key areas to meet role expectations.",
                f"Performance concerns noted for {employee_name}. Recommend additional training and support.",
                f"{employee_name} requires focused development plan to improve performance."
            ]
            sentiment_score = random.uniform(3, 6)
        
        feedback = random.choice(feedback_templates)
        
        return {
            'feedback': feedback,
            'reviewer': reviewer,
            'sentiment_score': round(sentiment_score, 2),
            'overall_rating': performance_score,
            'review_period': f"Q{random.randint(1,4)} {datetime.now().year}"
        }
    
    def calculate_wellness_score(self, stress_level, sleep_quality, focus_level):
        """Calculate overall wellness score"""
        # Invert stress level (lower stress = better wellness)
        stress_wellness = 11 - stress_level
        
        # Weight the factors
        wellness_score = (stress_wellness * 0.4 + sleep_quality * 0.3 + focus_level * 0.3)
        return round(wellness_score, 2)
    
    def get_wellness_status(self, wellness_score):
        """Get wellness status based on score"""
        if wellness_score >= 8:
            return 'green'
        elif wellness_score >= 6:
            return 'yellow'
        else:
            return 'red'
    
    def get_wellness_recommendations(self, status, stress_level, sleep_quality, focus_level):
        """Get wellness recommendations"""
        recommendations = []
        
        if stress_level > 7:
            recommendations.append("Consider stress management techniques like meditation or yoga")
            recommendations.append("Take regular breaks during work hours")
        
        if sleep_quality < 6:
            recommendations.append("Improve sleep hygiene - maintain consistent bedtime")
            recommendations.append("Limit screen time before bed")
        
        if focus_level < 6:
            recommendations.append("Try time-blocking techniques for better focus")
            recommendations.append("Consider workspace optimization")
        
        if status == 'red':
            recommendations.append("Consider speaking with a wellness counselor")
            recommendations.append("Monitor wellness metrics closely")
        
        return recommendations
    
    def analyze_employee_skill_gaps(self, employee):
        """Analyze skill gaps for an employee"""
        return {
            'employee_name': employee.name,
            'current_skills': employee.skills or "General skills",
            'skill_gaps': employee.skill_gaps or "No specific gaps identified",
            'recommendations': [
                "Continue professional development",
                "Attend relevant training programs",
                "Seek mentorship opportunities"
            ]
        }
    
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
        total_learning = LearningProgress.query.count()
        completed_learning = LearningProgress.query.filter_by(completed=True).count()
        completion_rate = (completed_learning / total_learning * 100) if total_learning else 0
        
        return {
            'total_employees': total_employees,
            'departments': dict(departments),
            'avg_performance': round(avg_performance, 2),
            'wellness_distribution': wellness_distribution,
            'learning_completion_rate': round(completion_rate, 2),
            'key_metrics': ['Performance', 'Wellness', 'Skills', 'Leadership'],
            'recommendations': [
                'Continue monitoring performance trends',
                'Expand wellness programs based on current metrics',
                'Increase learning module engagement'
            ]
        }
    
    def generate_appraisal_insights(self, reviews):
        """Generate appraisal dashboard insights"""
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
    
    def get_learning_leaderboard(self):
        """Get learning leaderboard data from actual employees"""
        from models import Employee, LearningProgress
        
        # Get employees with their learning progress
        employees_with_progress = []
        employees = Employee.query.all()
        
        for employee in employees:
            progress_records = LearningProgress.query.filter_by(employee_id=employee.id).all()
            
            if progress_records:
                avg_score = sum(p.score for p in progress_records) / len(progress_records)
                completed_modules = sum(1 for p in progress_records if p.completed)
                total_modules = len(progress_records)
            else:
                # Create some learning progress for employees without any
                avg_score = round(70 + (employee.performance_score * 3), 1) if employee.performance_score else 75.0
                completed_modules = min(int(employee.performance_score / 2), 8) if employee.performance_score else 5
                total_modules = completed_modules + 2
            
            employees_with_progress.append({
                'name': employee.name,
                'score': avg_score,
                'modules': completed_modules,
                'total_modules': total_modules
            })
        
        # Sort by score and return top performers
        employees_with_progress.sort(key=lambda x: x['score'], reverse=True)
        return employees_with_progress[:10]  # Top 10 learners
    
    def calculate_quiz_score(self, user_answers, correct_answers):
        """Calculate quiz score"""
        if not correct_answers or not user_answers:
            return 0
        
        correct_count = sum(1 for i, answer in enumerate(user_answers) 
                          if i < len(correct_answers) and answer == correct_answers[i])
        
        return round((correct_count / len(correct_answers)) * 100, 2)