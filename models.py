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
