from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import json

app = Flask(__name__)

# Add custom template filter for JSON parsing
@app.template_filter('from_json')
def from_json_filter(value):
    """Parse JSON string to Python object"""
    if not value:
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []

@app.template_filter('tojsonfilter')
def to_json_filter(value):
    """Convert Python object to JSON string"""
    try:
        return json.dumps(value)
    except (TypeError, ValueError):
        return 'null'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "hr_platform.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize extensions
db = SQLAlchemy(app)

# Import models after db initialization
from models import *

# Create tables
with app.app_context():
    db.create_all()

    # Auto-initialize data if database is empty
    from models import Employee, Resume, PerformanceReview
    if Employee.query.count() == 0:
        print("Database is empty. Initializing with real data...")
        try:
            from data.real_data_loader import RealDataLoader
            from datetime import datetime

            # Initialize real data loader
            real_data_loader = RealDataLoader()

            # Extract ZIP contents
            extracted_files = real_data_loader.extract_zip_contents()

            # Load employee metadata
            employees_data = real_data_loader.load_employee_metadata()

            # Add employees to database
            for emp_data in employees_data:
                employee = Employee(**emp_data)
                db.session.add(employee)

            db.session.commit()

            # Load resumes
            resumes_data = real_data_loader.load_resumes(extracted_files)
            for resume_data in resumes_data:
                resume = Resume(**resume_data)
                db.session.add(resume)

            # Generate performance reviews based on manager ratings
            employees = Employee.query.all()
            for employee in employees:
                review_data = {
                    'employee_id': employee.id,
                    'review_period': 'Q4 2023',
                    'feedback': f"Performance review for {employee.name}. Manager rating: {getattr(employee, 'manager_rating', 7.0)}/10. Areas for improvement: {getattr(employee, 'skill_gaps', 'General development')}",
                    'overall_rating': getattr(employee, 'manager_rating', 7.0),
                    'sentiment_score': 0.0,
                    'created_at': datetime.now()
                }
                review = PerformanceReview(**review_data)
                db.session.add(review)

            db.session.commit()

            # Cleanup temporary files
            real_data_loader.cleanup_temp_files()

            print(f"Successfully initialized {len(employees_data)} employees and {len(resumes_data)} resumes!")

        except Exception as e:
            print(f"Error auto-initializing data: {e}")
            db.session.rollback()
            # Import traceback for debugging
            import traceback
            traceback.print_exc()

# Create tables
with app.app_context():
    db.create_all()

    # Initialize sample gamification data
    from models import Challenge, Badge, Quiz

    # Check if sample data already exists
    if Challenge.query.count() == 0:
        # Create sample challenges
        sample_challenges = [
            Challenge(
                title="Ethics Champion",
                description="Complete the HR Ethics training module and pass the quiz with 80% or higher",
                xp_reward=100,
                challenge_type="quiz"
            ),
            Challenge(
                title="Policy Pro",
                description="Study company policies and complete the compliance assessment",
                xp_reward=75,
                challenge_type="training"
            ),
            Challenge(
                title="Fast Finisher",
                description="Complete any training challenge within 24 hours of starting",
                xp_reward=50,
                challenge_type="custom"
            ),
            Challenge(
                title="Team Contributor",
                description="Score 90% or higher on 3 different HR module quizzes",
                xp_reward=150,
                challenge_type="quiz"
            )
        ]

        for challenge in sample_challenges:
            db.session.add(challenge)

        # Create sample badges
        sample_badges = [
            Badge(
                name="First Steps",
                description="Earn your first 100 XP",
                icon="🌟",
                rarity="common",
                unlock_condition="Total XP >= 100"
            ),
            Badge(
                name="Rising Star",
                description="Reach 500 total XP",
                icon="⭐",
                rarity="rare",
                unlock_condition="Total XP >= 500"
            ),
            Badge(
                name="Champion",
                description="Achieve 1000 total XP",
                icon="🏆",
                rarity="epic",
                unlock_condition="Total XP >= 1000"
            ),
            Badge(
                name="Challenge Master",
                description="Complete 3 or more challenges",
                icon="🎯",
                rarity="rare",
                unlock_condition="Completed challenges >= 3"
            ),
            Badge(
                name="Ethics Expert",
                description="Master all ethics-related content",
                icon="⚖️",
                rarity="epic",
                unlock_condition="Complete Ethics modules"
            ),
            Badge(
                name="Speed Demon",
                description="Complete challenges quickly",
                icon="⚡",
                rarity="rare",
                unlock_condition="Fast completion times"
            )
        ]

        for badge in sample_badges:
            db.session.add(badge)

        db.session.commit()
        print("Sample gamification data created!")

    print("Database tables created successfully!")

# Import routes after everything is set up
import routes