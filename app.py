from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

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

# Import routes after everything is set up
import routes