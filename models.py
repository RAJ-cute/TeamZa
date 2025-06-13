from app import db
from datetime import datetime
from sqlalchemy import Text, JSON

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    current_salary = db.Column(db.Float, default=0.0)
    performance_score = db.Column(db.Float, default=0.0)
    skills = db.Column(Text)  # JSON string of skills
    gender = db.Column(db.String(20))
    region = db.Column(db.String(50))
    age = db.Column(db.Integer)
    experience_years = db.Column(db.Integer)
    manager_rating = db.Column(db.Float)
    last_hike_date = db.Column(db.Date)
    last_promotion_date = db.Column(db.Date)
    skill_gaps = db.Column(db.String(500))
    status = db.Column(db.String(20), default='active')  # active, inactive, terminated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Employee, self).__init__(**kwargs)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(Text, nullable=False)
    skills_extracted = db.Column(Text)  # JSON string
    score = db.Column(db.Float, default=0.0)
    job_description = db.Column(Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LearningProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    module_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime)
    employee = db.relationship('Employee', backref=db.backref('learning_progress', lazy=True))

class WellnessCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    stress_level = db.Column(db.Integer, nullable=False)  # 1-10 scale
    sleep_quality = db.Column(db.Integer, nullable=False)  # 1-10 scale
    focus_level = db.Column(db.Integer, nullable=False)  # 1-10 scale
    overall_wellness = db.Column(db.String(20), nullable=False)  # green/yellow/red
    recommendations = db.Column(Text)
    check_date = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship('Employee', backref=db.backref('wellness_checks', lazy=True))

class HealthMetrics(db.Model):
    """Comprehensive health metrics for employees"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    bmi = db.Column(db.Float)
    bmi_status = db.Column(db.String(20))  # Normal, Overweight, Obese, Underweight
    blood_pressure = db.Column(db.String(20))  # e.g., "120/80"
    bp_status = db.Column(db.String(20))  # Normal, Elevated
    avg_daily_steps = db.Column(db.Integer)
    avg_sleep_hours = db.Column(db.Float)
    stress_level = db.Column(db.Integer)  # 1-10
    stress_status = db.Column(db.String(20))  # Low, Moderate, High
    mood_score = db.Column(db.Integer)  # 1-10
    mood_status = db.Column(db.String(20))  # Positive, Neutral, Negative
    recommendations = db.Column(Text)  # JSON string of recommendations
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship('Employee', backref=db.backref('health_metrics', lazy=True))
    
    def __init__(self, **kwargs):
        super(HealthMetrics, self).__init__(**kwargs)

class PerformanceReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    review_period = db.Column(db.String(50), nullable=False)
    feedback = db.Column(Text, nullable=False)
    sentiment_score = db.Column(db.Float, default=0.0)
    overall_rating = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship('Employee', backref=db.backref('performance_reviews', lazy=True))

class HRTransaction(db.Model):
    """Track all HR transactions like increments, promotions, joinings, exits"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)  # Null for new joinings
    transaction_type = db.Column(db.String(50), nullable=False)  # increment, promotion, joining, exit, bonus
    amount = db.Column(db.Float)  # increment amount or bonus amount
    percentage = db.Column(db.Float)  # increment percentage
    previous_salary = db.Column(db.Float)
    new_salary = db.Column(db.Float)
    previous_position = db.Column(db.String(100))
    new_position = db.Column(db.String(100))
    department = db.Column(db.String(50))
    reason = db.Column(Text)  # reason for increment/promotion/exit
    effective_date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.String(100))  # HR person who made the entry
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship('Employee', backref=db.backref('hr_transactions', lazy=True))
    
    def __init__(self, **kwargs):
        super(HRTransaction, self).__init__(**kwargs)

class EmployeeHistory(db.Model):
    """Track employee historical data changes"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)  # salary, position, department, etc.
    old_value = db.Column(Text)
    new_value = db.Column(Text)
    change_date = db.Column(db.Date, nullable=False)
    changed_by = db.Column(db.String(100))
    notes = db.Column(Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship('Employee', backref=db.backref('history_records', lazy=True))
    
    def __init__(self, **kwargs):
        super(EmployeeHistory, self).__init__(**kwargs)

class CompanyMetrics(db.Model):
    """Store monthly/quarterly company-wide metrics"""
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50), nullable=False)  # headcount, attrition, satisfaction, etc.
    metric_value = db.Column(db.Float, nullable=False)
    period_type = db.Column(db.String(20), nullable=False)  # monthly, quarterly, yearly
    period_year = db.Column(db.Integer, nullable=False)
    period_month = db.Column(db.Integer)  # 1-12 for monthly metrics
    period_quarter = db.Column(db.Integer)  # 1-4 for quarterly metrics
    department = db.Column(db.String(50))  # null for company-wide metrics
    notes = db.Column(Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Challenge(db.Model):
    """HR Training Challenges for gamification"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(Text, nullable=False)
    xp_reward = db.Column(db.Integer, default=50)
    challenge_type = db.Column(db.String(50), default='training')  # training, quiz, module, custom
    requirements = db.Column(Text)  # JSON string of requirements
    deadline = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(100), default='HR Admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Challenge, self).__init__(**kwargs)

class Badge(db.Model):
    """Achievement badges for employees"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(Text)
    icon = db.Column(db.String(100), default='🏆')  # emoji or icon class
    badge_type = db.Column(db.String(50), default='achievement')  # achievement, milestone, special
    unlock_condition = db.Column(Text)  # JSON string describing unlock condition
    rarity = db.Column(db.String(20), default='common')  # common, rare, epic, legendary
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Badge, self).__init__(**kwargs)

class EmployeeXP(db.Model):
    """Track employee XP and level"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    total_xp = db.Column(db.Integer, default=0)
    current_level = db.Column(db.Integer, default=1)
    xp_to_next_level = db.Column(db.Integer, default=100)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship('Employee', backref=db.backref('xp_profile', uselist=False, lazy=True))
    
    def calculate_level(self):
        """Calculate level based on total XP"""
        level = 1
        xp_needed = 100
        remaining_xp = self.total_xp
        
        while remaining_xp >= xp_needed:
            remaining_xp -= xp_needed
            level += 1
            xp_needed = int(xp_needed * 1.2)  # Each level requires 20% more XP
        
        self.current_level = level
        self.xp_to_next_level = xp_needed - remaining_xp
        return level

class EmployeeBadge(db.Model):
    """Track badges earned by employees"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=False)
    earned_date = db.Column(db.DateTime, default=datetime.utcnow)
    earned_for = db.Column(db.String(200))  # What they earned it for
    employee = db.relationship('Employee', backref=db.backref('earned_badges', lazy=True))
    badge = db.relationship('Badge', backref=db.backref('earned_by', lazy=True))

class ChallengeParticipation(db.Model):
    """Track employee participation in challenges"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, failed
    progress = db.Column(db.Integer, default=0)  # Progress percentage
    started_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    xp_earned = db.Column(db.Integer, default=0)
    employee = db.relationship('Employee', backref=db.backref('challenge_participations', lazy=True))
    challenge = db.relationship('Challenge', backref=db.backref('participants', lazy=True))

class Quiz(db.Model):
    """Quiz questions for HR modules"""
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(100), nullable=False)
    question = db.Column(Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    explanation = db.Column(Text)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizAttempt(db.Model):
    """Track employee quiz attempts"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    selected_answer = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    attempt_date = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship('Employee', backref=db.backref('quiz_attempts', lazy=True))
    quiz = db.relationship('Quiz', backref=db.backref('attempts', lazy=True))
