from flask import render_template, request, jsonify, flash, redirect, url_for
from app import app, db
from models import Employee, Resume, LearningProgress, WellnessCheck, PerformanceReview, HRTransaction, EmployeeHistory, CompanyMetrics, HealthMetrics, Challenge, Badge, EmployeeXP, EmployeeBadge, ChallengeParticipation, Quiz, QuizAttempt
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
import data.mock_data as mock_data

nlp_processor = NLPProcessor()
hr_analytics = HRAnalytics()
document_parser = DocumentParser()
mock_data_gen = MockDataGenerator()
real_data_loader = RealDataLoader() if RealDataLoader else None

@app.route('/')
def index():
    """Professional landing page with company info and features"""
    return render_template('landing.html')

@app.route('/login')
def login():
    """Login page for accessing the HR platform"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
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
        candidates = mock_data_gen.generate_candidate_profiles(job_title, job_description)

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
                employee.name, manager_rating
            )

            leadership_candidates.append({
                'employee': employee,
                'potential_score': potential_score,
                'growth_actions': growth_actions,
                'review': review_data['feedback'],
                'reviewer': review_data['reviewer'],
                'star_rating': int(review_data['overall_rating'])
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
    modules = mock_data_gen.get_learning_modules()
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
    from utils.health_generator import HealthDataGenerator
    health_gen = HealthDataGenerator()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'generate_health_data':
            # Generate comprehensive health data for all employees
            generated_count = health_gen.generate_for_all_employees()
            flash(f'Generated health data for {generated_count} employees', 'success')
            return redirect(url_for('wellness_tracker'))
            
        elif action == 'add_wellness_check':
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

    # Get comprehensive health overview
    health_overview = health_gen.get_health_overview()
    
    # Get all employees with their health metrics
    employees_with_health = db.session.query(Employee, HealthMetrics).outerjoin(HealthMetrics).all()
    
    # Get recent wellness checks
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
                         employees_with_health=employees_with_health,
                         recent_checks=recent_checks,
                         total_checks=total_checks,
                         green_status=green_status,
                         yellow_status=yellow_status,
                         red_status=red_status,
                         concern_employees=concern_employees,
                         health_overview=health_overview)

@app.route('/hr-insights')
def hr_insights():
    """Comprehensive HR Insights Dashboard with Company and Individual Analytics"""
    # Get comprehensive company insights using existing analytics
    insights_data = hr_analytics.generate_hr_insights()

    # Get all employees for individual insights tab
    employees = Employee.query.filter_by(status='active').all()
    
    # Department distribution
    dept_stats_raw = db.session.query(Employee.department, db.func.count(Employee.id)).group_by(Employee.department).all()
    dept_stats = [{'department': dept, 'count': count} for dept, count in dept_stats_raw]
    
    # Performance data
    avg_performance = db.session.query(db.func.avg(Employee.performance_score)).scalar() or 0
    top_performers = Employee.query.filter(Employee.performance_score >= 8.5).all()
    
    # Monthly trends (simplified)
    total_employees = Employee.query.count()
    monthly_trends = {
        'headcount': [total_employees] * 12,
        'performance': [avg_performance] * 12,
        'satisfaction': [7.5] * 12
    }
    
    # Wellness summary
    wellness_summary = {
        'total_checks': WellnessCheck.query.count(),
        'green_status': WellnessCheck.query.filter_by(overall_wellness='green').count(),
        'yellow_status': WellnessCheck.query.filter_by(overall_wellness='yellow').count(),
        'red_status': WellnessCheck.query.filter_by(overall_wellness='red').count(),
        'distribution': {
            'green': WellnessCheck.query.filter_by(overall_wellness='green').count(),
            'yellow': WellnessCheck.query.filter_by(overall_wellness='yellow').count(),
            'red': WellnessCheck.query.filter_by(overall_wellness='red').count()
        }
    }

    # Add missing increment data
    increment_data = {
        'total_increments': HRTransaction.query.filter_by(transaction_type='increment').count(),
        'avg_increment': db.session.query(db.func.avg(HRTransaction.percentage)).filter_by(transaction_type='increment').scalar() or 0
    }
    
    # Add missing joining/leaving data
    joining_leaving_data = {
        'joined_this_year': HRTransaction.query.filter_by(transaction_type='joining').count(),
        'left_this_year': HRTransaction.query.filter_by(transaction_type='exit').count()
    }
    
    # Generate performance data for charts
    performance_data = {
        'average': round(avg_performance, 2),
        'distribution': {
            'excellent': Employee.query.filter(Employee.performance_score >= 9).count(),
            'good': Employee.query.filter(Employee.performance_score >= 7, Employee.performance_score < 9).count(),
            'average': Employee.query.filter(Employee.performance_score >= 5, Employee.performance_score < 7).count(),
            'needs_improvement': Employee.query.filter(Employee.performance_score < 5).count()
        }
    }
    
    return render_template('hr_insights.html',
                         total_employees=total_employees,
                         dept_stats=dept_stats,
                         performance_data=performance_data,
                         avg_performance=avg_performance,
                         top_performers=top_performers,
                         monthly_trends=monthly_trends,
                         wellness_summary=wellness_summary,
                         insights_data=insights_data,
                         increment_data=increment_data,
                         joining_leaving_data=joining_leaving_data,
                         employees=employees)

@app.route('/hr-data-management', methods=['GET', 'POST'])
def hr_data_management():
    """HR Data Management - Add/Update employee data, increments, promotions"""
    from datetime import datetime
    from models import HRTransaction, EmployeeHistory

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_increment':
            employee_id_str = request.form.get('employee_id')
            increment_amount_str = request.form.get('increment_amount', '0')
            increment_percentage_str = request.form.get('increment_percentage', '0')
            increment_date_str = request.form.get('increment_date')
            
            if not employee_id_str or not increment_date_str:
                flash('Employee ID and increment date are required', 'error')
                return redirect(url_for('hr_data_management'))
                
            employee_id = int(employee_id_str)
            increment_amount = float(increment_amount_str)
            increment_percentage = float(increment_percentage_str)
            increment_date = datetime.strptime(increment_date_str, '%Y-%m-%d').date()
            reason = request.form.get('reason', '')
            created_by = request.form.get('created_by', 'HR Admin')

            employee = Employee.query.get(employee_id)
            if employee:
                # Record HR transaction
                previous_salary = employee.current_salary or 0
                new_salary = previous_salary + increment_amount

                transaction = HRTransaction(
                    employee_id=employee_id,
                    transaction_type='increment',
                    amount=increment_amount,
                    percentage=increment_percentage,
                    previous_salary=previous_salary,
                    new_salary=new_salary,
                    department=employee.department,
                    reason=reason,
                    effective_date=increment_date,
                    created_by=created_by
                )
                db.session.add(transaction)

                # Update employee record
                employee.current_salary = new_salary
                employee.last_hike_date = increment_date

                # Record history
                history = EmployeeHistory(
                    employee_id=employee_id,
                    field_name='salary',
                    old_value=str(previous_salary),
                    new_value=str(new_salary),
                    change_date=increment_date,
                    changed_by=created_by,
                    notes=f'Increment: {increment_percentage}% - {reason}'
                )
                db.session.add(history)

                db.session.commit()
                flash(f'Increment of {increment_percentage}% recorded for {employee.name}', 'success')
            else:
                flash('Employee not found', 'error')

        elif action == 'add_promotion':
            employee_id_str = request.form.get('employee_id')
            new_position = request.form.get('new_position')
            promotion_date_str = request.form.get('promotion_date')
            
            if not employee_id_str or not new_position or not promotion_date_str:
                flash('Employee ID, new position, and promotion date are required', 'error')
                return redirect(url_for('hr_data_management'))
                
            employee_id = int(employee_id_str)
            promotion_date = datetime.strptime(promotion_date_str, '%Y-%m-%d').date()
            created_by = request.form.get('created_by', 'HR Admin')
            reason = request.form.get('reason', '')

            employee = Employee.query.get(employee_id)
            if employee:
                previous_position = employee.position

                # Record HR transaction
                transaction = HRTransaction(
                    employee_id=employee_id,
                    transaction_type='promotion',
                    previous_position=previous_position,
                    new_position=new_position,
                    department=employee.department,
                    reason=reason,
                    effective_date=promotion_date,
                    created_by=created_by
                )
                db.session.add(transaction)

                # Update employee record
                employee.position = new_position
                employee.last_promotion_date = promotion_date

                # Record history
                history = EmployeeHistory(
                    employee_id=employee_id,
                    field_name='position',
                    old_value=previous_position,
                    new_value=new_position,
                    change_date=promotion_date,
                    changed_by=created_by,
                    notes=f'Promotion - {reason}'
                )
                db.session.add(history)

                db.session.commit()
                flash(f'Promotion to {new_position} recorded for {employee.name}', 'success')
            else:
                flash('Employee not found', 'error')

        elif action == 'add_exit':
            employee_id_str = request.form.get('employee_id')
            exit_date_str = request.form.get('exit_date')
            
            if not employee_id_str or not exit_date_str:
                flash('Employee ID and exit date are required', 'error')
                return redirect(url_for('hr_data_management'))
                
            employee_id = int(employee_id_str)
            exit_date = datetime.strptime(exit_date_str, '%Y-%m-%d').date()
            reason = request.form.get('reason', '')
            created_by = request.form.get('created_by', 'HR Admin')

            employee = Employee.query.get(employee_id)
            if employee:
                # Record HR transaction
                transaction = HRTransaction(
                    employee_id=employee_id,
                    transaction_type='exit',
                    department=employee.department,
                    reason=reason,
                    effective_date=exit_date,
                    created_by=created_by
                )
                db.session.add(transaction)

                # Update employee status
                employee.status = 'terminated'

                # Record history
                history = EmployeeHistory(
                    employee_id=employee_id,
                    field_name='status',
                    old_value='active',
                    new_value='terminated',
                    change_date=exit_date,
                    changed_by=created_by,
                    notes=f'Exit - {reason}'
                )
                db.session.add(history)

                db.session.commit()
                flash(f'Exit recorded for {employee.name}', 'success')
            else:
                flash('Employee not found', 'error')

        elif action == 'add_joining':
            name = request.form.get('name')
            email = request.form.get('email')
            department = request.form.get('department')
            position = request.form.get('position')
            hire_date_str = request.form.get('hire_date')
            
            if not name or not email or not department or not position or not hire_date_str:
                flash('All fields are required for new joining', 'error')
                return redirect(url_for('hr_data_management'))
                
            hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
            salary = float(request.form.get('salary', 0))
            created_by = request.form.get('created_by', 'HR Admin')

            # Create new employee
            employee = Employee(
                name=name,
                email=email,
                department=department,
                position=position,
                hire_date=hire_date,
                current_salary=salary,
                performance_score=0.0,
                status='active'
            )
            db.session.add(employee)
            db.session.flush()  # Get the employee ID

            # Record HR transaction
            transaction = HRTransaction(
                employee_id=employee.id,
                transaction_type='joining',
                new_salary=salary,
                new_position=position,
                department=department,
                reason=f'New hire - {position}',
                effective_date=hire_date,
                created_by=created_by
            )
            db.session.add(transaction)

            db.session.commit()
            flash(f'Employee {name} added successfully', 'success')

        return redirect(url_for('hr_data_management'))

    # Get all employees and recent transactions
    employees = Employee.query.order_by(Employee.name).all()
    recent_transactions = HRTransaction.query.order_by(HRTransaction.created_at.desc()).limit(20).all()
    departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'Product']

    return render_template('hr_data_management.html',
                         employees=employees,
                         recent_transactions=recent_transactions,
                         departments=departments)

@app.route('/export-company-data')
def export_company_data():
    """Export company insights data to Excel"""
    from utils.real_hr_analytics import RealHRAnalytics
    from flask import send_file
    import io

    analytics = RealHRAnalytics()
    excel_data = analytics.export_company_data_to_excel()

    # Create file-like object
    output = io.BytesIO(excel_data)

    return send_file(
        output,
        as_attachment=True,
        download_name=f'company_hr_insights_{datetime.now().strftime("%Y%m%d")}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/export-employee-data/<int:employee_id>')
def export_employee_data(employee_id):
    """Export individual employee data to Excel"""
    from utils.real_hr_analytics import RealHRAnalytics
    from flask import send_file
    import io

    analytics = RealHRAnalytics()
    excel_data = analytics.export_employee_data_to_excel(employee_id)

    if not excel_data:
        flash('Employee not found', 'error')
        return redirect(url_for('hr_insights'))

    employee = Employee.query.get(employee_id)
    employee_name = employee.name.replace(' ', '_') if employee else 'employee'

    # Create file-like object
    output = io.BytesIO(excel_data)

    return send_file(
        output,
        as_attachment=True,
        download_name=f'{employee_name}_details_{datetime.now().strftime("%Y%m%d")}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/gamification', methods=['GET', 'POST'])
def gamification():
    """Gamified HR Portal - Main dashboard for challenges, badges, and leaderboards"""
    from models import Challenge, Badge, EmployeeXP, EmployeeBadge, ChallengeParticipation, Quiz, QuizAttempt
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create_challenge':
            title = request.form.get('title')
            description = request.form.get('description')
            xp_reward = int(request.form.get('xp_reward', 50))
            challenge_type = request.form.get('challenge_type', 'training')
            deadline_str = request.form.get('deadline')
            
            deadline = None
            if deadline_str:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            
            challenge = Challenge(
                title=title,
                description=description,
                xp_reward=xp_reward,
                challenge_type=challenge_type,
                deadline=deadline,
                created_by=request.form.get('created_by', 'HR Admin')
            )
            db.session.add(challenge)
            db.session.commit()
            
            flash(f'Challenge "{title}" created successfully!', 'success')
            return redirect(url_for('gamification'))
            
        elif action == 'create_badge':
            name = request.form.get('name')
            description = request.form.get('description')
            icon = request.form.get('icon', '🏆')
            badge_type = request.form.get('badge_type', 'achievement')
            rarity = request.form.get('rarity', 'common')
            unlock_condition = request.form.get('unlock_condition')
            
            badge = Badge(
                name=name,
                description=description,
                icon=icon,
                badge_type=badge_type,
                rarity=rarity,
                unlock_condition=unlock_condition
            )
            db.session.add(badge)
            db.session.commit()
            
            flash(f'Badge "{name}" created successfully!', 'success')
            return redirect(url_for('gamification'))
            
        elif action == 'join_challenge':
            employee_id = int(request.form.get('employee_id'))
            challenge_id = int(request.form.get('challenge_id'))
            
            # Check if already participating
            existing = ChallengeParticipation.query.filter_by(
                employee_id=employee_id, 
                challenge_id=challenge_id
            ).first()
            
            if not existing:
                participation = ChallengeParticipation(
                    employee_id=employee_id,
                    challenge_id=challenge_id
                )
                db.session.add(participation)
                db.session.commit()
                flash('Successfully joined the challenge!', 'success')
            else:
                flash('Already participating in this challenge!', 'info')
                
            return redirect(url_for('gamification'))
    
    # Get all data for the dashboard
    challenges = Challenge.query.filter_by(is_active=True).order_by(Challenge.created_at.desc()).all()
    badges = Badge.query.filter_by(is_active=True).order_by(Badge.created_at.desc()).all()
    employees = Employee.query.filter_by(status='active').all()
    
    # Initialize XP profiles for employees who don't have them
    for employee in employees:
        if not employee.xp_profile:
            xp_profile = EmployeeXP(employee_id=employee.id)
            db.session.add(xp_profile)
    db.session.commit()
    
    # Get leaderboard (top 10)
    leaderboard = db.session.query(Employee, EmployeeXP).join(EmployeeXP).order_by(EmployeeXP.total_xp.desc()).limit(10).all()
    
    # Get recent achievements
    recent_badges = db.session.query(EmployeeBadge, Employee, Badge).join(Employee).join(Badge).order_by(EmployeeBadge.earned_date.desc()).limit(5).all()
    
    # Challenge statistics
    total_challenges = Challenge.query.count()
    active_challenges = Challenge.query.filter_by(is_active=True).count()
    total_participations = ChallengeParticipation.query.count()
    completed_challenges = ChallengeParticipation.query.filter_by(status='completed').count()
    
    return render_template('gamification.html',
                         challenges=challenges,
                         badges=badges,
                         employees=employees,
                         leaderboard=leaderboard,
                         recent_badges=recent_badges,
                         total_challenges=total_challenges,
                         active_challenges=active_challenges,
                         total_participations=total_participations,
                         completed_challenges=completed_challenges)

@app.route('/gamification/quiz/<int:challenge_id>')
def take_quiz(challenge_id):
    """Take a quiz for a specific challenge"""
    from models import Challenge, Quiz
    
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Get quiz questions for this challenge/module
    quiz_questions = Quiz.query.filter_by(module_name='Ethics').limit(5).all()  # Sample quiz
    
    if not quiz_questions:
        # Create sample quiz questions if none exist
        sample_questions = [
            {
                'question': 'What is the most important aspect of workplace ethics?',
                'option_a': 'Following company policies',
                'option_b': 'Respecting colleagues and maintaining integrity',
                'option_c': 'Completing tasks on time',
                'option_d': 'Attending all meetings',
                'correct_answer': 'B',
                'explanation': 'Workplace ethics is fundamentally about respect and integrity in all professional interactions.'
            },
            {
                'question': 'How should confidential information be handled?',
                'option_a': 'Share only with trusted colleagues',
                'option_b': 'Keep it completely private unless authorized to share',
                'option_c': 'Use it for decision making only',
                'option_d': 'Store it in personal files',
                'correct_answer': 'B',
                'explanation': 'Confidential information should only be shared when properly authorized.'
            },
            {
                'question': 'What constitutes a conflict of interest?',
                'option_a': 'Working overtime',
                'option_b': 'Having personal relationships with colleagues',
                'option_c': 'Personal interests interfering with professional judgment',
                'option_d': 'Disagreeing with management',
                'correct_answer': 'C',
                'explanation': 'A conflict of interest occurs when personal interests could compromise professional judgment.'
            }
        ]
        
        for q_data in sample_questions:
            quiz = Quiz(
                module_name='Ethics',
                question=q_data['question'],
                option_a=q_data['option_a'],
                option_b=q_data['option_b'],
                option_c=q_data['option_c'],
                option_d=q_data['option_d'],
                correct_answer=q_data['correct_answer'],
                explanation=q_data['explanation']
            )
            db.session.add(quiz)
        
        db.session.commit()
        quiz_questions = Quiz.query.filter_by(module_name='Ethics').limit(5).all()
    
    return render_template('quiz.html', challenge=challenge, questions=quiz_questions)

@app.route('/gamification/submit-quiz', methods=['POST'])
def submit_quiz():
    """Submit quiz answers and calculate score"""
    from models import QuizAttempt, EmployeeXP, ChallengeParticipation, EmployeeBadge, Badge
    
    employee_id = int(request.form.get('employee_id'))
    challenge_id = int(request.form.get('challenge_id'))
    
    # Get submitted answers
    submitted_answers = {}
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            submitted_answers[question_id] = value
    
    # Calculate score
    correct_answers = 0
    total_questions = len(submitted_answers)
    
    for question_id, answer in submitted_answers.items():
        quiz = Quiz.query.get(question_id)
        is_correct = (answer.upper() == quiz.correct_answer.upper())
        
        if is_correct:
            correct_answers += 1
        
        # Record attempt
        attempt = QuizAttempt(
            employee_id=employee_id,
            quiz_id=question_id,
            selected_answer=answer.upper(),
            is_correct=is_correct
        )
        db.session.add(attempt)
    
    # Calculate percentage
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Award XP if score is good (80% or higher)
    if score_percentage >= 80:
        challenge = Challenge.query.get(challenge_id)
        xp_to_award = challenge.xp_reward
        
        # Update employee XP
        employee_xp = EmployeeXP.query.filter_by(employee_id=employee_id).first()
        if employee_xp:
            employee_xp.total_xp += xp_to_award
            employee_xp.calculate_level()
            employee_xp.last_activity = datetime.utcnow()
        
        # Mark challenge as completed
        participation = ChallengeParticipation.query.filter_by(
            employee_id=employee_id, 
            challenge_id=challenge_id
        ).first()
        
        if participation:
            participation.status = 'completed'
            participation.completed_date = datetime.utcnow()
            participation.xp_earned = xp_to_award
            participation.progress = 100
        
        # Check for badge awards
        _check_and_award_badges(employee_id)
        
        db.session.commit()
        
        flash(f'Congratulations! You scored {score_percentage:.1f}% and earned {xp_to_award} XP!', 'success')
    else:
        flash(f'You scored {score_percentage:.1f}%. You need 80% or higher to complete the challenge.', 'warning')
    
    return redirect(url_for('gamification'))

def _check_and_award_badges(employee_id):
    """Check if employee qualifies for any new badges"""
    from models import Badge, EmployeeBadge, EmployeeXP, ChallengeParticipation
    
    employee_xp = EmployeeXP.query.filter_by(employee_id=employee_id).first()
    completed_challenges = ChallengeParticipation.query.filter_by(
        employee_id=employee_id, 
        status='completed'
    ).count()
    
    # Check for XP-based badges
    if employee_xp and employee_xp.total_xp >= 100:
        _award_badge_if_not_earned(employee_id, 'First Steps', '🌟')
    
    if employee_xp and employee_xp.total_xp >= 500:
        _award_badge_if_not_earned(employee_id, 'Rising Star', '⭐')
    
    if employee_xp and employee_xp.total_xp >= 1000:
        _award_badge_if_not_earned(employee_id, 'Champion', '🏆')
    
    # Check for challenge completion badges
    if completed_challenges >= 3:
        _award_badge_if_not_earned(employee_id, 'Challenge Master', '🎯')

def _award_badge_if_not_earned(employee_id, badge_name, icon):
    """Award a badge if not already earned"""
    from models import Badge, EmployeeBadge
    
    # Check if badge exists
    badge = Badge.query.filter_by(name=badge_name).first()
    if not badge:
        badge = Badge(name=badge_name, icon=icon, description=f'Earned for {badge_name.lower()}')
        db.session.add(badge)
        db.session.flush()
    
    # Check if already earned
    existing = EmployeeBadge.query.filter_by(employee_id=employee_id, badge_id=badge.id).first()
    if not existing:
        earned_badge = EmployeeBadge(
            employee_id=employee_id,
            badge_id=badge.id,
            earned_for=f'Awarded for {badge_name.lower()}'
        )
        db.session.add(earned_badge)

@app.route('/employee-insights/<int:employee_id>')
def employee_insights(employee_id):
    """Individual employee detailed insights"""
    employee = Employee.query.get_or_404(employee_id)
    
    # Get all related data for this employee
    performance_reviews = PerformanceReview.query.filter_by(employee_id=employee_id).order_by(PerformanceReview.created_at.desc()).all()
    learning_progress = LearningProgress.query.filter_by(employee_id=employee_id).all()
    wellness_checks = WellnessCheck.query.filter_by(employee_id=employee_id).order_by(WellnessCheck.check_date.desc()).all()
    hr_transactions = HRTransaction.query.filter_by(employee_id=employee_id).order_by(HRTransaction.created_at.desc()).all()
    
    # Calculate additional metrics
    leadership_score = hr_analytics.calculate_leadership_potential(employee)
    recent_wellness = wellness_checks[0] if wellness_checks else None
    
    return render_template('employee_insights.html', 
                         employee=employee,
                         performance_reviews=performance_reviews,
                         learning_progress=learning_progress,
                         wellness_checks=wellness_checks,
                         hr_transactions=hr_transactions,
                         leadership_score=leadership_score,
                         recent_wellness=recent_wellness)

@app.route('/api/quiz/<module_name>')
def get_quiz(module_name):
    """API endpoint to get quiz data"""
    quiz_data = mock_data_gen.get_quiz_data(module_name)
    return jsonify(quiz_data)

@app.route('/reset-data')
def reset_data():
    """Reset and reload data (for testing purposes)"""
    try:
        # Clear existing data
        Resume.query.delete()
        PerformanceReview.query.delete()
        LearningProgress.query.delete()
        WellnessCheck.query.delete()
        Employee.query.delete()
        HRTransaction.query.delete()
        EmployeeHistory.query.delete()
        db.session.commit()

        flash('Data reset successfully! The system will reload real data automatically.', 'success')

    except Exception as e:
        flash(f'Error resetting data: {str(e)}', 'error')
        db.session.rollback()

    return redirect(url_for('index'))