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
    
    def analyze_employee_skill_gaps(self, employee):
        """Analyze skill gaps for a specific employee and provide course recommendations"""
        
        # Get skill gaps from employee record
        skill_gaps = employee.skill_gaps or ""
        skill_gap_list = [s.strip() for s in skill_gaps.split(',') if s.strip()] if skill_gaps else []
        
        # Get course recommendations based on job role and skill gaps
        course_recommendations = self._get_course_recommendations_for_employee(employee.position, skill_gap_list)
        
        return {
            'employee': employee,
            'skill_gaps': skill_gaps if skill_gaps else None,
            'skill_gap_list': skill_gap_list,
            'course_recommendations': course_recommendations
        }
    
    def _get_course_recommendations_for_employee(self, job_role, skill_gaps):
        """Get course recommendations based on job role and specific skill gaps"""
        
        # Course recommendations database
        course_db = {
            "Product Manager": {
                "User Research": [
                    {"title": "User Research and Design", "platform": "Coursera", "url": "https://www.coursera.org/learn/user-research"},
                    {"title": "UX Research at Scale: Surveys, Analytics, Online Testing", "platform": "Udemy", "url": "https://www.udemy.com/course/ux-research-at-scale"},
                    {"title": "User Experience Research and Design Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/user-experience-research-and-design"},
                    {"title": "User Research for Product Managers", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/user-research-for-product-managers"}
                ],
                "Agile": [
                    {"title": "Agile Development Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/agile-development"},
                    {"title": "Agile Crash Course: Agile Project Management", "platform": "Udemy", "url": "https://www.udemy.com/course/agile-crash-course"},
                    {"title": "Agile Meets Design Thinking", "platform": "Coursera", "url": "https://www.coursera.org/learn/agile-meets-design-thinking"},
                    {"title": "Agile Product Management", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/agile-product-management"}
                ],
                "Tech Understanding": [
                    {"title": "Technology for Product Managers", "platform": "Udemy", "url": "https://www.udemy.com/course/technology-for-product-managers"},
                    {"title": "Software Product Management Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/product-management"},
                    {"title": "Technical Product Management", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/technical-product-management"},
                    {"title": "Product Management for Technical Professionals", "platform": "Udemy", "url": "https://www.udemy.com/course/product-management-for-technical-professionals"}
                ]
            },
            "Sales Executive": {
                "CRM": [
                    {"title": "CRM Fundamentals", "platform": "Udemy", "url": "https://www.udemy.com/course/crm-fundamentals"},
                    {"title": "Salesforce Administrator Certification Training", "platform": "Coursera", "url": "https://www.coursera.org/learn/salesforce-administrator"},
                    {"title": "HubSpot CRM Implementation", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/hubspot-crm-implementation"},
                    {"title": "CRM: Customer Relationship Management", "platform": "Udemy", "url": "https://www.udemy.com/course/crm-customer-relationship-management"}
                ],
                "Presentation Skills": [
                    {"title": "Presentation Skills: Speechwriting and Storytelling", "platform": "Udemy", "url": "https://www.udemy.com/course/presentation-skills-speechwriting-and-storytelling"},
                    {"title": "Successful Presentation", "platform": "Coursera", "url": "https://www.coursera.org/learn/successful-presentation"},
                    {"title": "Presentation Skills: Designing Presentation Slides", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/presentation-skills-designing-presentation-slides"},
                    {"title": "The Complete Presentation and Public Speaking Course", "platform": "Udemy", "url": "https://www.udemy.com/course/publicspeaking"}
                ],
                "Negotiation": [
                    {"title": "Successful Negotiation: Essential Strategies and Skills", "platform": "Coursera", "url": "https://www.coursera.org/learn/negotiation-skills"},
                    {"title": "The Complete Negotiation Skills Masterclass", "platform": "Udemy", "url": "https://www.udemy.com/course/negotiation-skills-masterclass"},
                    {"title": "Negotiation Skills", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/negotiation-skills"},
                    {"title": "Sales Negotiation Strategies", "platform": "Udemy", "url": "https://www.udemy.com/course/sales-negotiation-strategies"}
                ]
            },
            "HR Manager": {
                "Employee Engagement": [
                    {"title": "Employee Engagement and Retention", "platform": "Udemy", "url": "https://www.udemy.com/course/employee-engagement-and-retention"},
                    {"title": "HR Analytics: Employee Engagement", "platform": "Coursera", "url": "https://www.coursera.org/learn/hr-analytics-employee-engagement"},
                    {"title": "Employee Engagement", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/employee-engagement"},
                    {"title": "The Complete Employee Engagement Course", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-employee-engagement-course"}
                ],
                "HR Analytics": [
                    {"title": "HR Analytics Using MS Excel for Human Resource Management", "platform": "Udemy", "url": "https://www.udemy.com/course/hr-analytics-using-ms-excel-for-human-resource-management"},
                    {"title": "People Analytics", "platform": "Coursera", "url": "https://www.coursera.org/learn/people-analytics"},
                    {"title": "HR Analytics: Building a Data-Driven HR Department", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/hr-analytics-building-a-data-driven-hr-department"},
                    {"title": "The Complete HR Analytics Course in Excel & R", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-hr-analytics-course-in-excel-r"}
                ],
                "Conflict Resolution": [
                    {"title": "Conflict Resolution Skills", "platform": "Udemy", "url": "https://www.udemy.com/course/conflict-resolution-skills"},
                    {"title": "Conflict Management Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/conflict-management"},
                    {"title": "Conflict Resolution Foundations", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/conflict-resolution-foundations"},
                    {"title": "Workplace Conflict Resolution: A Practical Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/workplace-conflict-resolution"}
                ],
                "Talent Management": [
                    {"title": "Talent Management", "platform": "Coursera", "url": "https://www.coursera.org/learn/talent-management"},
                    {"title": "Strategic Talent Management", "platform": "Udemy", "url": "https://www.udemy.com/course/strategic-talent-management"},
                    {"title": "Talent Management", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/talent-management"},
                    {"title": "The Complete Talent Management Course", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-talent-management-course"}
                ]
            },
            "Cybersecurity Specialist": {
                "Ethical Hacking": [
                    {"title": "Ethical Hacking for Beginners", "platform": "Udemy", "url": "https://www.udemy.com/course/ethical-hacking-for-beginners"},
                    {"title": "Introduction to Cyber Security Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/intro-cyber-security"},
                    {"title": "Ethical Hacking: Penetration Testing", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/ethical-hacking-penetration-testing"},
                    {"title": "The Complete Ethical Hacking Course", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-ethical-hacking-course"}
                ],
                "SIEM": [
                    {"title": "SIEM for Beginners", "platform": "Udemy", "url": "https://www.udemy.com/course/siem-for-beginners"},
                    {"title": "Splunk Beginner to Architect", "platform": "Udemy", "url": "https://www.udemy.com/course/splunk-beginner-to-architect"},
                    {"title": "Security Information and Event Management (SIEM) Foundations", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/security-information-and-event-management-siem-foundations"},
                    {"title": "The Complete Splunk Beginner Course", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-splunk-beginner-course"}
                ],
                "Network Security": [
                    {"title": "Network Security Fundamentals", "platform": "Udemy", "url": "https://www.udemy.com/course/network-security-fundamentals"},
                    {"title": "Introduction to Cybersecurity Tools & Cyber Attacks", "platform": "Coursera", "url": "https://www.coursera.org/learn/introduction-cybersecurity-cyber-attacks"},
                    {"title": "Network Security", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/network-security"},
                    {"title": "The Complete Cyber Security Course: Network Security", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-internet-security-privacy-course-volume-1"}
                ]
            },
            "Data Analyst": {
                "SQL": [
                    {"title": "SQL for Data Science", "platform": "Coursera", "url": "https://www.coursera.org/learn/sql-for-data-science"},
                    {"title": "The Complete SQL Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp"},
                    {"title": "SQL Essential Training", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/sql-essential-training"},
                    {"title": "Advanced SQL: MySQL Data Analysis & Business Intelligence", "platform": "Udemy", "url": "https://www.udemy.com/course/advanced-sql-mysql-data-analysis-business-intelligence"}
                ],
                "Excel": [
                    {"title": "Excel Skills for Business Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/excel"},
                    {"title": "Microsoft Excel - Excel from Beginner to Advanced", "platform": "Udemy", "url": "https://www.udemy.com/course/microsoft-excel-2013-from-beginner-to-advanced-and-beyond"},
                    {"title": "Excel Essential Training (Office 365/Microsoft 365)", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/excel-essential-training-office-365-microsoft-365"},
                    {"title": "Microsoft Excel - Data Visualization, Excel Charts & Graphs", "platform": "Udemy", "url": "https://www.udemy.com/course/microsoft-excel-data-visualization-excel-charts-and-graphs"}
                ],
                "Data Visualization": [
                    {"title": "Data Visualization with Tableau Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/data-visualization"},
                    {"title": "Data Visualization in Python Masterclass", "platform": "Udemy", "url": "https://www.udemy.com/course/data-visualization-in-python"},
                    {"title": "Learning Data Visualization", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/learning-data-visualization"},
                    {"title": "The Complete Data Visualization Course with Python, R, Tableau", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-data-visualization-course"}
                ],
                "Python": [
                    {"title": "Python for Data Science and AI", "platform": "Coursera", "url": "https://www.coursera.org/learn/python-for-applied-data-science-ai"},
                    {"title": "Python for Data Science and Machine Learning Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp"},
                    {"title": "Python for Data Analysis", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/python-for-data-analysis"},
                    {"title": "The Complete Python Course for Data Science and ML", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-python-course-for-data-science-and-ml"}
                ]
            }
        }
        
        recommendations = {}
        
        # Get recommendations for each skill gap
        if skill_gaps:
            for skill in skill_gaps:
                skill_clean = skill.strip()
                
                # Look for exact matches first
                found_courses = None
                if job_role in course_db:
                    for course_skill, courses in course_db[job_role].items():
                        if skill_clean.lower() in course_skill.lower() or course_skill.lower() in skill_clean.lower():
                            found_courses = courses
                            break
                
                # If exact match not found, provide general courses for the role
                if not found_courses and job_role in course_db:
                    # Get first available skill's courses as general recommendations
                    first_skill = next(iter(course_db[job_role]))
                    found_courses = course_db[job_role][first_skill]
                
                if found_courses:
                    recommendations[skill_clean] = found_courses
        
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
            db.func.sum(db.case([(LearningProgress.completed == True, 1)], else_=0)).label('completed')
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
