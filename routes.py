from flask import render_template, request, jsonify, flash, redirect, url_for
from app import app, db
from models import Employee, Resume, LearningProgress, WellnessCheck, PerformanceReview
from utils.nlp_processor import NLPProcessor
from utils.hr_analytics import HRAnalytics
from utils.document_parser import DocumentParser
from data.mock_data import MockDataGenerator
try:
    from data.real_data_loader import RealDataLoader
except ImportError as e:
    print(f"Warning: Could not import RealDataLoader: {e}")
    RealDataLoader = None
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime

nlp_processor = NLPProcessor()
hr_analytics = HRAnalytics()
document_parser = DocumentParser()
mock_data = MockDataGenerator()
real_data_loader = RealDataLoader() if RealDataLoader else None

@app.route('/')
def index():
    """HR Management Dashboard showing overview of all employee data"""
    # Get comprehensive HR stats for dashboard
    total_employees = Employee.query.count()
    total_resumes = Resume.query.count()
    active_learning = LearningProgress.query.filter_by(completed=False).count()
    recent_wellness = WellnessCheck.query.order_by(WellnessCheck.check_date.desc()).limit(5).all()

    # Department distribution
    dept_stats = db.session.query(Employee.department, db.func.count(Employee.id)).group_by(Employee.department).all()

    # Recent performance reviews
    recent_reviews = PerformanceReview.query.order_by(PerformanceReview.created_at.desc()).limit(5).all()

    # High performers
    top_performers = Employee.query.filter(Employee.performance_score >= 8.0).order_by(Employee.performance_score.desc()).limit(5).all()

    return render_template('index.html', 
                         total_employees=total_employees,
                         total_resumes=total_resumes,
                         active_learning=active_learning,
                         recent_wellness=recent_wellness,
                         dept_stats=dept_stats,
                         recent_reviews=recent_reviews,
                         top_performers=top_performers)

@app.route('/employee-management')
def employee_management():
    """Employee Management - View, search, and manage all employees"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    department = request.args.get('department', '')

    query = Employee.query

    if search:
        query = query.filter(
            db.or_(
                Employee.name.contains(search),
                Employee.email.contains(search),
                Employee.position.contains(search)
            )
        )

    if department:
        query = query.filter(Employee.department == department)

    employees = query.order_by(Employee.name).paginate(
        page=page, per_page=20, error_out=False
    )

    departments = db.session.query(Employee.department).distinct().all()
    departments = [dept[0] for dept in departments]

    return render_template('employee_management.html',
                         employees=employees,
                         departments=departments,
                         search=search,
                         selected_department=department)

@app.route('/employee/<int:employee_id>')
def employee_profile(employee_id):
    """Individual employee profile with complete HR data"""
    employee = Employee.query.get_or_404(employee_id)

    # Get all related data for this employee
    performance_reviews = PerformanceReview.query.filter_by(employee_id=employee_id).order_by(PerformanceReview.created_at.desc()).all()
    learning_progress = LearningProgress.query.filter_by(employee_id=employee_id).all()
    wellness_checks = WellnessCheck.query.filter_by(employee_id=employee_id).order_by(WellnessCheck.check_date.desc()).all()

    # Calculate additional metrics
    leadership_score = hr_analytics.calculate_leadership_potential(employee)
    recent_wellness = wellness_checks[0] if wellness_checks else None

    return render_template('employee_profile.html',
                         employee=employee,
                         performance_reviews=performance_reviews,
                         learning_progress=learning_progress,
                         wellness_checks=wellness_checks,
                         leadership_score=leadership_score,
                         recent_wellness=recent_wellness)

@app.route('/resume-screening', methods=['GET', 'POST'])
def resume_screening():
    """HR Resume Screening Management - AI-powered candidate evaluation"""
    if request.method == 'POST':
        job_description = request.form.get('job_description', '')

        # Handle file uploads
        uploaded_files = request.files.getlist('resumes')
        results = []

        for file in uploaded_files:
            if file and file.filename:
                filename = secure_filename(file.filename)

                # Check if file format is supported
                if not document_parser.is_supported_format(filename):
                    flash(f'Unsupported file format for {filename}. Please upload PDF, DOCX, DOC, or TXT files.', 'warning')
                    continue

                # Extract text content using proper document parser
                content = document_parser.extract_text_from_file(file, filename)

                # Skip if content extraction failed
                if not content or (isinstance(content, str) and content.startswith('Error:')):
                    flash(f'Could not parse {filename}. Please ensure the file is not corrupted.', 'error')
                    continue

                # Process resume with NLP
                skills = nlp_processor.extract_skills(content)
                score = nlp_processor.calculate_match_score(content, job_description)

                # Save to database
                resume = Resume()
                resume.filename = filename
                resume.content = content
                resume.skills_extracted = json.dumps(skills)
                resume.score = score
                resume.job_description = job_description
                db.session.add(resume)

                results.append({
                    'filename': filename,
                    'skills': skills,
                    'score': score,
                    'reasoning': nlp_processor.generate_reasoning(content, skills, score, job_description)
                })

        db.session.commit()

        # Sort by score and get top 3
        results.sort(key=lambda x: x['score'], reverse=True)
        top_candidates = results[:3]

        return render_template('resume_screening.html', 
                             results=top_candidates, 
                             job_description=job_description)

    return render_template('resume_screening.html')

@app.route('/talent-sourcing', methods=['GET', 'POST'])
def talent_sourcing():
    """Smart talent sourcing module"""
    if request.method == 'POST':
        job_title = request.form.get('job_title', '')
        job_description = request.form.get('job_description', '')

        # Generate mock candidate profiles
        candidates = mock_data.generate_candidate_profiles(job_title, job_description)

        return render_template('talent_sourcing.html', 
                             candidates=candidates, 
                             job_title=job_title)

    return render_template('talent_sourcing.html')

@app.route('/leadership-potential')
def leadership_potential():
    """Leadership potential identifier module"""
    # Get all employees with performance data
    employees = Employee.query.all()

    # Review givers
    reviewers = [
        "Mr. Prabhu Narayan (Team Lead)",
        "Ms. Dhruti Chand (Managing Director)", 
        "Ms. Pratibha Sharma (Recruitment Officer)"
    ]

    # Analyze leadership potential
    leadership_candidates = []
    reviewer_usage = {reviewer: 0 for reviewer in reviewers}

    for employee in employees:
        potential_score = hr_analytics.calculate_leadership_potential(employee)
        if potential_score > 7.0:  # High potential threshold
            growth_actions = hr_analytics.suggest_growth_actions(employee, potential_score)

            # Generate review based on manager rating
            manager_rating = employee.manager_rating or 7.0
            review_data = hr_analytics.generate_performance_review_with_reviewer(
                employee, manager_rating, reviewers, reviewer_usage
            )

            # Serialize employee data
            employee_data = {
                'id': employee.id,
                'name': employee.name,
                'email': employee.email,
                'department': employee.department,
                'position': employee.position,
                'hire_date': employee.hire_date,  # Keep as datetime object
                'performance_score': employee.performance_score,
                'manager_rating': employee.manager_rating,
                'experience_years': employee.experience_years,
                'skills': employee.skills
            }

            leadership_candidates.append({
                'employee': employee_data,
                'potential_score': potential_score,
                'growth_actions': growth_actions,
                'review': review_data['review'],
                'reviewer': review_data['reviewer'],
                'star_rating': review_data['star_rating']
            })

    # Sort by potential score
    leadership_candidates.sort(key=lambda x: x['potential_score'], reverse=True)

    return render_template('leadership_potential.html', 
                         candidates=leadership_candidates)

@app.route('/appraisal-dashboard')
def appraisal_dashboard():
    """AI-driven appraisal dashboard"""
    # Get performance reviews with sentiment analysis
    reviews = PerformanceReview.query.order_by(PerformanceReview.created_at.desc()).all()

    # Analyze sentiment for each review
    for review in reviews:
        if review.sentiment_score == 0.0:  # Not analyzed yet
            review.sentiment_score = nlp_processor.analyze_sentiment(review.feedback)
            db.session.commit()

    # Generate dashboard data
    dashboard_data = hr_analytics.generate_appraisal_insights(reviews)

    return render_template('appraisal_dashboard.html', 
                         reviews=reviews, 
                         dashboard_data=dashboard_data)

@app.route('/learning-module')
def learning_module():
    """HR Employee Learning Management - Track and manage employee learning progress"""

    # Get learning modules and leaderboard
    modules = mock_data.get_learning_modules()
    leaderboard = hr_analytics.get_learning_leaderboard()
    employees = Employee.query.all()

    return render_template('learning_module.html', 
                         modules=modules, 
                         leaderboard=leaderboard,
                         employees=employees)

@app.route('/skill-gap-analysis', methods=['GET', 'POST'])
def skill_gap_analysis():
    """Employee-based skill gap analysis module"""
    employees = Employee.query.order_by(Employee.name).all()

    if request.method == 'POST':
        employee_name = request.form.get('employee_name')

        if employee_name:
            # Find the employee
            employee = Employee.query.filter_by(name=employee_name).first()

            if employee:
                # Analyze skill gaps using the new approach
                employee_analysis = hr_analytics.analyze_employee_skill_gaps(employee)

                return render_template('skill_gap_analysis.html', 
                                     employees=employees,
                                     employee_analysis=employee_analysis,
                                     selected_employee=employee_name)
            else:
                flash('Employee not found', 'error')

    return render_template('skill_gap_analysis.html', employees=employees)

@app.route('/wellness-tracker', methods=['GET', 'POST'])
def wellness_tracker():
    """HR Employee Wellness Management - View and manage all employee wellness data"""
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        stress_level = int(request.form.get('stress_level', 5))
        sleep_quality = int(request.form.get('sleep_quality', 5))
        focus_level = int(request.form.get('focus_level', 5))

        # Calculate overall wellness
        wellness_score = hr_analytics.calculate_wellness_score(stress_level, sleep_quality, focus_level)
        wellness_status = hr_analytics.get_wellness_status(wellness_score)
        recommendations = hr_analytics.get_wellness_recommendations(wellness_status, stress_level, sleep_quality, focus_level)

        # Save wellness check
        wellness_check = WellnessCheck()
        wellness_check.employee_id = employee_id
        wellness_check.stress_level = stress_level
        wellness_check.sleep_quality = sleep_quality
        wellness_check.focus_level = focus_level
        wellness_check.overall_wellness = wellness_status
        wellness_check.recommendations = json.dumps(recommendations)
        db.session.add(wellness_check)
        db.session.commit()

        flash('Wellness check recorded successfully', 'success')
        return redirect(url_for('wellness_tracker'))

    # Get all employees with their latest wellness data
    employees = Employee.query.all()
    recent_checks = WellnessCheck.query.order_by(WellnessCheck.check_date.desc()).limit(20).all()

    # Wellness statistics
    total_checks = WellnessCheck.query.count()
    green_status = WellnessCheck.query.filter_by(overall_wellness='green').count()
    yellow_status = WellnessCheck.query.filter_by(overall_wellness='yellow').count()
    red_status = WellnessCheck.query.filter_by(overall_wellness='red').count()

    # Get employees with wellness concerns (red status in last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    concern_employees = db.session.query(Employee).join(WellnessCheck).filter(
        WellnessCheck.overall_wellness == 'red',
        WellnessCheck.check_date >= thirty_days_ago
    ).distinct().all()

    return render_template('wellness_tracker.html', 
                         employees=employees,
                         recent_checks=recent_checks,
                         total_checks=total_checks,
                         green_status=green_status,
                         yellow_status=yellow_status,
                         red_status=red_status,
                         concern_employees=concern_employees)

@app.route('/hr-insights')
def hr_insights():
    """Comprehensive HR Insights Dashboard with Company and Individual Analytics"""
    from datetime import datetime, timedelta
    import random

    # Get all employees
    employees = Employee.query.all()

    # Company-wide insights
    total_employees = len(employees)

    # Department distribution
    dept_stats = {}
    for emp in employees:
        dept_stats[emp.department] = dept_stats.get(emp.department, 0) + 1

    # Performance metrics
    if employees:
        avg_performance = sum(emp.performance_score or 7.0 for emp in employees) / len(employees)
        top_performers = [emp for emp in employees if (emp.performance_score or 7.0) >= 8.5]
    else:
        avg_performance = 0
        top_performers = []

    # Mock increment data (in real scenario, this would come from HR records)
    increment_data = {
        'total_increments': random.randint(15, 25),
        'avg_increment_percent': random.uniform(8, 15),
        'increment_by_dept': {dept: random.randint(2, 5) for dept in dept_stats.keys()}
    }

    # Mock joining/leaving data
    joining_leaving_data = {
        'joined_this_year': random.randint(8, 15),
        'left_this_year': random.randint(2, 8),
        'net_growth': 0
    }
    joining_leaving_data['net_growth'] = joining_leaving_data['joined_this_year'] - joining_leaving_data['left_this_year']

    # Employee leaderboard based on performance
    employee_leaderboard = sorted(
        [(emp.name, emp.performance_score or 7.0, emp.department) for emp in employees],
        key=lambda x: x[1], reverse=True
    )[:10]

    # Monthly trends (mock data)
    monthly_trends = {
        'performance': [
            {'month': 'Jan', 'avg_score': 7.8},
            {'month': 'Feb', 'avg_score': 8.1},
            {'month': 'Mar', 'avg_score': 8.3},
            {'month': 'Apr', 'avg_score': 8.0},
            {'month': 'May', 'avg_score': 8.4},
            {'month': 'Jun', 'avg_score': 8.6}
        ],
        'headcount': [
            {'month': 'Jan', 'count': total_employees - 5},
            {'month': 'Feb', 'count': total_employees - 3},
            {'month': 'Mar', 'count': total_employees - 2},
            {'month': 'Apr', 'count': total_employees - 1},
            {'month': 'May', 'count': total_employees},
            {'month': 'Jun', 'count': total_employees + 2}
        ]
    }

    # Wellness overview
    wellness_summary = {
        'green': random.randint(60, 80),
        'yellow': random.randint(15, 25),
        'red': random.randint(5, 15)
    }

    # Prepare data for Excel export
    export_data = {
        'company_summary': {
            'total_employees': total_employees,
            'departments': dept_stats,
            'avg_performance': round(avg_performance, 2),
            'increments': increment_data,
            'joining_leaving': joining_leaving_data
        },
        'employee_details': [
            {
                'name': emp.name,
                'department': emp.department,
                'position': emp.position,
                'performance_score': emp.performance_score or 7.0,
                'hire_date': emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else 'N/A',
                'last_increment': emp.last_hike_date or 'N/A',
                'manager_rating': emp.manager_rating or 7.0,
                'skill_gaps': emp.skill_gaps or 'None identified'
            }
            for emp in employees
        ]
    }

    return render_template('hr_insights.html',
                         total_employees=total_employees,
                         dept_stats=dept_stats,
                         avg_performance=round(avg_performance, 2),
                         top_performers=top_performers,
                         increment_data=increment_data,
                         joining_leaving_data=joining_leaving_data,
                         employee_leaderboard=employee_leaderboard,
                         monthly_trends=monthly_trends,
                         wellness_summary=wellness_summary,
                         employees=employees,
                         export_data=export_data)

@app.route('/hr-data-management', methods=['GET', 'POST'])
def hr_data_management():
    """HR Data Management - Add/Update employee data, increments, promotions"""
    from datetime import datetime
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_increment':
            employee_id = request.form.get('employee_id')
            increment_amount = float(request.form.get('increment_amount'))
            increment_date = request.form.get('increment_date')
            
            employee = Employee.query.get(employee_id)
            if employee:
                employee.last_hike_date = increment_date
                db.session.commit()
                flash(f'Increment of {increment_amount}% recorded for {employee.name}', 'success')
            else:
                flash('Employee not found', 'error')
                
        elif action == 'add_promotion':
            employee_id = request.form.get('employee_id')
            new_position = request.form.get('new_position')
            promotion_date = request.form.get('promotion_date')
            
            employee = Employee.query.get(employee_id)
            if employee:
                employee.position = new_position
                employee.last_promotion_date = promotion_date
                db.session.commit()
                flash(f'Promotion to {new_position} recorded for {employee.name}', 'success')
            else:
                flash('Employee not found', 'error')
                
        elif action == 'update_performance':
            employee_id = request.form.get('employee_id')
            performance_score = float(request.form.get('performance_score'))
            manager_rating = float(request.form.get('manager_rating'))
            
            employee = Employee.query.get(employee_id)
            if employee:
                employee.performance_score = performance_score
                employee.manager_rating = manager_rating
                db.session.commit()
                flash(f'Performance updated for {employee.name}', 'success')
            else:
                flash('Employee not found', 'error')
                
        elif action == 'add_employee':
            name = request.form.get('name')
            email = request.form.get('email')
            department = request.form.get('department')
            position = request.form.get('position')
            hire_date = datetime.strptime(request.form.get('hire_date'), '%Y-%m-%d')
            
            employee = Employee(
                name=name,
                email=email,
                department=department,
                position=position,
                hire_date=hire_date,
                performance_score=7.0,
                manager_rating=7.0
            )
            db.session.add(employee)
            db.session.commit()
            flash(f'Employee {name} added successfully', 'success')
        
        return redirect(url_for('hr_data_management'))
    
    # Get all employees and departments for forms
    employees = Employee.query.order_by(Employee.name).all()
    departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'Product']
    
    return render_template('hr_data_management.html',
                         employees=employees,
                         departments=departments)

@app.route('/api/quiz/<module_name>')
def get_quiz(module_name):
    """API endpoint to get quiz data"""
    quiz_data = mock_data.get_quiz_data(module_name)
    return jsonify(quiz_data)

@app.route('/initialize-data')
def initialize_data():
    """Initialize database with mock data"""
    try:
        # Generate mock employees
        employees_data = mock_data.generate_employees()
        for emp_data in employees_data:
            employee = Employee(**emp_data)
            db.session.add(employee)

        # Generate mock performance reviews
        db.session.commit()  # Commit employees first

        employees = Employee.query.all()
        for employee in employees:
            review_data = mock_data.generate_performance_review(employee.id)
            review = PerformanceReview(**review_data)
            db.session.add(review)

        db.session.commit()
        flash('Mock data initialized successfully!', 'success')
    except Exception as e:
        flash(f'Error initializing data: {str(e)}', 'error')
        db.session.rollback()

    return redirect(url_for('index'))

@app.route('/initialize-real-data')
def initialize_real_data():
    """Initialize database with real employee data from uploaded files"""
    if not real_data_loader:
        flash('Real data loader not available. Please install required dependencies.', 'error')
        return redirect(url_for('index'))

    try:
        # Clear existing data
        Resume.query.delete()
        PerformanceReview.query.delete()
        LearningProgress.query.delete()
        WellnessCheck.query.delete()
        Employee.query.delete()
        db.session.commit()

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

        flash(f'Real employee data initialized successfully! Loaded {len(employees_data)} employees and {len(resumes_data)} resumes.', 'success')

    except Exception as e:
        flash(f'Error initializing real data: {str(e)}', 'error')
        db.session.rollback()
        import traceback
        traceback.print_exc()

    return redirect(url_for('index'))