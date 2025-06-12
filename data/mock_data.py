import random
import json
from datetime import datetime, timedelta
from faker import Faker

class MockDataGenerator:
    """Generate mock data for HR platform demonstration"""
    
    def __init__(self):
        self.fake = Faker()
        self.departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations']
        self.positions = {
            'Engineering': ['Software Engineer', 'Senior Developer', 'DevOps Engineer', 'QA Engineer', 'Tech Lead'],
            'Marketing': ['Marketing Manager', 'Content Writer', 'SEO Specialist', 'Social Media Manager', 'Brand Manager'],
            'Sales': ['Sales Representative', 'Account Manager', 'Sales Director', 'Business Development', 'Sales Coordinator'],
            'HR': ['HR Manager', 'Recruiter', 'HR Coordinator', 'Talent Acquisition', 'HR Business Partner'],
            'Finance': ['Financial Analyst', 'Accountant', 'Finance Manager', 'Controller', 'Financial Planner'],
            'Operations': ['Operations Manager', 'Project Manager', 'Operations Coordinator', 'Process Analyst', 'Logistics Manager']
        }
        
        self.skills_database = {
            'programming': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Rust', 'Kotlin'],
            'web_development': ['HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django', 'Flask'],
            'database': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'Cassandra'],
            'cloud': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Ansible'],
            'data_science': ['Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'Jupyter', 'R', 'Tableau'],
            'soft_skills': ['Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Creativity', 'Adaptability'],
            'project_management': ['Agile', 'Scrum', 'Kanban', 'Jira', 'Confluence', 'Project Planning'],
            'design': ['Photoshop', 'Illustrator', 'Figma', 'Sketch', 'UI/UX', 'Graphic Design'],
            'marketing': ['SEO', 'SEM', 'Content Marketing', 'Social Media', 'Email Marketing', 'Analytics'],
            'finance': ['Financial Analysis', 'Accounting', 'Budgeting', 'Excel', 'QuickBooks', 'SAP']
        }
        
        self.learning_modules = [
            {
                'id': 'leadership-101',
                'title': 'Leadership Fundamentals',
                'description': 'Master the basics of effective leadership and team management',
                'duration': 45,
                'difficulty': 'Beginner',
                'icon': 'fas fa-crown',
                'questions': 10
            },
            {
                'id': 'communication-skills',
                'title': 'Communication Excellence',
                'description': 'Enhance your verbal and written communication skills',
                'duration': 30,
                'difficulty': 'Intermediate',
                'icon': 'fas fa-comments',
                'questions': 8
            },
            {
                'id': 'project-management',
                'title': 'Project Management Basics',
                'description': 'Learn essential project management methodologies and tools',
                'duration': 60,
                'difficulty': 'Intermediate',
                'icon': 'fas fa-tasks',
                'questions': 12
            },
            {
                'id': 'data-analysis',
                'title': 'Data Analysis Fundamentals',
                'description': 'Introduction to data analysis and visualization techniques',
                'duration': 50,
                'difficulty': 'Advanced',
                'icon': 'fas fa-chart-bar',
                'questions': 15
            },
            {
                'id': 'customer-service',
                'title': 'Customer Service Excellence',
                'description': 'Deliver outstanding customer service and build relationships',
                'duration': 35,
                'difficulty': 'Beginner',
                'icon': 'fas fa-handshake',
                'questions': 8
            }
        ]
    
    def generate_employees(self, count=25):
        """Generate mock employee data"""
        employees = []
        
        for _ in range(count):
            department = random.choice(self.departments)
            position = random.choice(self.positions[department])
            
            # Generate skills based on department
            dept_skills = self._get_department_skills(department)
            skills_json = json.dumps(random.sample(dept_skills, k=random.randint(3, 7)))
            
            employee = {
                'name': self.fake.name(),
                'email': self.fake.email(),
                'department': department,
                'position': position,
                'hire_date': self.fake.date_between(start_date='-5y', end_date='today'),
                'performance_score': round(random.uniform(6.0, 9.5), 1),
                'skills': skills_json
            }
            
            employees.append(employee)
        
        return employees
    
    def _get_department_skills(self, department):
        """Get relevant skills for a department"""
        skill_mapping = {
            'Engineering': self.skills_database['programming'] + self.skills_database['web_development'] + self.skills_database['cloud'],
            'Marketing': self.skills_database['marketing'] + self.skills_database['design'] + self.skills_database['soft_skills'],
            'Sales': self.skills_database['soft_skills'] + ['CRM', 'Negotiation', 'Lead Generation'],
            'HR': self.skills_database['soft_skills'] + ['Recruitment', 'Employee Relations', 'HRIS'],
            'Finance': self.skills_database['finance'] + ['Risk Management', 'Compliance', 'Taxation'],
            'Operations': self.skills_database['project_management'] + ['Process Improvement', 'Supply Chain', 'Quality Management']
        }
        
        return skill_mapping.get(department, self.skills_database['soft_skills'])
    
    def generate_performance_review(self, employee_id):
        """Generate a mock performance review"""
        review_periods = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2023']
        
        # Generate realistic feedback based on rating
        rating = round(random.uniform(5.0, 9.5), 1)
        
        if rating >= 8.0:
            feedback = random.choice([
                "Exceptional performance throughout the review period. Consistently exceeds expectations and demonstrates strong leadership qualities. Takes initiative on challenging projects and mentors junior team members effectively.",
                "Outstanding contributor who goes above and beyond in all assignments. Shows excellent problem-solving skills and maintains high quality standards. Positive attitude and great team collaboration.",
                "Excellent work quality and productivity. Demonstrates strong technical skills and business acumen. Proactive in identifying improvements and implementing solutions."
            ])
        elif rating >= 6.5:
            feedback = random.choice([
                "Good performance with consistent delivery of quality work. Shows improvement in areas identified in previous review. Collaborates well with team members and meets most deadlines.",
                "Solid contributor who handles responsibilities well. Shows good technical competency and willingness to learn. Some areas for improvement in time management and communication.",
                "Meets expectations in most areas with room for growth. Demonstrates good potential and shows effort in professional development. Needs to work on taking more initiative."
            ])
        else:
            feedback = random.choice([
                "Performance below expectations in several key areas. Needs improvement in meeting deadlines and quality standards. Requires additional support and training to reach expected performance levels.",
                "Struggling to meet basic job requirements. Issues with attendance and work quality need immediate attention. Development plan required to address performance gaps.",
                "Inconsistent performance with missed deadlines and quality issues. Needs to improve communication and collaboration with team members. Additional supervision recommended."
            ])
        
        return {
            'employee_id': employee_id,
            'review_period': random.choice(review_periods),
            'feedback': feedback,
            'overall_rating': rating,
            'sentiment_score': 0.0,  # Will be calculated by NLP processor
            'created_at': datetime.now() - timedelta(days=random.randint(1, 90))
        }
    
    def generate_candidate_profiles(self, job_title, job_description, count=5):
        """Generate mock candidate profiles for talent sourcing"""
        candidates = []
        
        # Extract skills from job description (simplified)
        job_skills = self._extract_skills_from_text(job_description)
        
        for _ in range(count):
            # Generate candidate skills with some overlap with job requirements
            candidate_skills = list(set(
                random.sample(job_skills, k=min(len(job_skills), random.randint(2, 4))) +
                random.sample([skill for skills in self.skills_database.values() for skill in skills], k=random.randint(3, 6))
            ))
            
            # Calculate relevance score based on skill overlap
            skill_overlap = len(set(candidate_skills) & set(job_skills))
            relevance_score = min(10, max(5, skill_overlap + random.uniform(-1, 2)))
            
            candidate = {
                'name': self.fake.name(),
                'location': f"{self.fake.city()}, {self.fake.state_abbr()}",
                'current_role': self._generate_similar_role(job_title),
                'company': self.fake.company(),
                'years_experience': random.randint(2, 12),
                'education': random.choice(['Bachelor\'s Degree', 'Master\'s Degree', 'PhD', 'Certificate']),
                'skills': candidate_skills,
                'relevance_score': round(relevance_score, 1),
                'availability': random.choice(['Available', 'Open to offers', 'Not actively looking']),
                'platforms': self._generate_platform_profiles(),
                'assessment': self._generate_candidate_assessment(relevance_score, skill_overlap)
            }
            
            candidates.append(candidate)
        
        # Sort by relevance score
        return sorted(candidates, key=lambda x: x['relevance_score'], reverse=True)
    
    def _extract_skills_from_text(self, text):
        """Extract skills from job description text"""
        text_lower = text.lower()
        found_skills = []
        
        for category_skills in self.skills_database.values():
            for skill in category_skills:
                if skill.lower() in text_lower:
                    found_skills.append(skill)
        
        return list(set(found_skills)) if found_skills else ['Communication', 'Teamwork', 'Problem Solving']
    
    def _generate_similar_role(self, job_title):
        """Generate a similar role title"""
        title_variations = {
            'engineer': ['Developer', 'Engineer', 'Architect', 'Specialist'],
            'manager': ['Manager', 'Director', 'Lead', 'Coordinator'],
            'analyst': ['Analyst', 'Specialist', 'Consultant', 'Associate'],
            'designer': ['Designer', 'Artist', 'Creative', 'Specialist']
        }
        
        for key, variations in title_variations.items():
            if key in job_title.lower():
                return f"{random.choice(['Senior', 'Junior', ''])} {random.choice(variations)}".strip()
        
        return job_title
    
    def _generate_platform_profiles(self):
        """Generate mock social/professional platform profiles"""
        platforms = ['github', 'linkedin', 'twitter', 'stackoverflow']
        selected_platforms = random.sample(platforms, k=random.randint(2, 4))
        
        profiles = {}
        for platform in selected_platforms:
            profiles[platform] = {
                'username': f"@{self.fake.user_name()}",
                'url': f"https://{platform}.com/{self.fake.user_name()}"
            }
        
        return profiles
    
    def _generate_candidate_assessment(self, relevance_score, skill_overlap):
        """Generate AI assessment text"""
        if relevance_score >= 8:
            return f"Excellent match with {skill_overlap} overlapping skills. Strong background and experience align well with requirements. Highly recommended for interview."
        elif relevance_score >= 6:
            return f"Good candidate with {skill_overlap} relevant skills. Some experience gaps but shows potential. Worth considering for next round."
        else:
            return f"Moderate fit with {skill_overlap} matching skills. May require additional training but has foundational knowledge."
    
    def get_learning_modules(self):
        """Get available learning modules"""
        return self.learning_modules
    
    def get_quiz_data(self, module_id):
        """Generate quiz data for a learning module"""
        quiz_questions = {
            'leadership-101': {
                'questions': [
                    {
                        'question': 'What is the most important quality of a good leader?',
                        'options': ['Authority', 'Empathy', 'Intelligence', 'Experience'],
                        'correct': 1
                    },
                    {
                        'question': 'Which leadership style involves sharing decision-making with team members?',
                        'options': ['Autocratic', 'Democratic', 'Laissez-faire', 'Transactional'],
                        'correct': 1
                    },
                    {
                        'question': 'What is emotional intelligence in leadership?',
                        'options': ['IQ level', 'Technical skills', 'Understanding emotions', 'Communication speed'],
                        'correct': 2
                    },
                    {
                        'question': 'How should a leader handle team conflicts?',
                        'options': ['Ignore them', 'Address immediately', 'Let team resolve', 'Fire someone'],
                        'correct': 1
                    },
                    {
                        'question': 'What motivates employees most according to research?',
                        'options': ['Money only', 'Recognition', 'Job security', 'All of the above'],
                        'correct': 3
                    }
                ],
                'correct_answers': [1, 1, 2, 1, 3]
            },
            'communication-skills': {
                'questions': [
                    {
                        'question': 'What percentage of communication is non-verbal?',
                        'options': ['25%', '50%', '75%', '90%'],
                        'correct': 2
                    },
                    {
                        'question': 'Active listening involves:',
                        'options': ['Waiting to speak', 'Interrupting', 'Asking questions', 'Looking away'],
                        'correct': 2
                    },
                    {
                        'question': 'In written communication, what is most important?',
                        'options': ['Length', 'Clarity', 'Vocabulary', 'Font'],
                        'correct': 1
                    },
                    {
                        'question': 'How should you give constructive feedback?',
                        'options': ['Publicly', 'Privately', 'Via email', 'Through others'],
                        'correct': 1
                    }
                ],
                'correct_answers': [2, 2, 1, 1]
            },
            'project-management': {
                'questions': [
                    {
                        'question': 'What does SCRUM stand for?',
                        'options': ['Nothing', 'System Control', 'Software Cycle', 'Sprint Concept'],
                        'correct': 0
                    },
                    {
                        'question': 'What is a project milestone?',
                        'options': ['End date', 'Key achievement', 'Team meeting', 'Budget limit'],
                        'correct': 1
                    },
                    {
                        'question': 'Which is NOT a project constraint?',
                        'options': ['Time', 'Budget', 'Quality', 'Location'],
                        'correct': 3
                    },
                    {
                        'question': 'What is risk management in projects?',
                        'options': ['Avoiding all risks', 'Identifying threats', 'Insurance only', 'Blame assignment'],
                        'correct': 1
                    }
                ],
                'correct_answers': [0, 1, 3, 1]
            }
        }
        
        # Return quiz data or generate generic one
        if module_id in quiz_questions:
            return quiz_questions[module_id]
        else:
            # Generate generic quiz
            return {
                'questions': [
                    {
                        'question': f'What is the key concept in {module_id.replace("-", " ").title()}?',
                        'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                        'correct': random.randint(0, 3)
                    } for _ in range(5)
                ],
                'correct_answers': [random.randint(0, 3) for _ in range(5)]
            }
    
    def get_available_skills(self):
        """Get all available skills categorized"""
        return self.skills_database
    
    def get_target_roles(self):
        """Get available target roles for skill gap analysis"""
        roles = []
        for positions in self.positions.values():
            roles.extend(positions)
        
        # Add some generic roles
        roles.extend(['Software Engineer', 'Data Scientist', 'Product Manager', 'DevOps Engineer', 'UI/UX Designer'])
        
        return sorted(list(set(roles)))
