from flask import render_template, request, jsonify, flash, redirect, url_for
from app import app, db
from models import Employee, Resume, LearningProgress, WellnessCheck, PerformanceReview
from utils.nlp_processor import NLPProcessor
from utils.hr_analytics import HRAnalytics
from data.mock_data import MockDataGenerator
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime

nlp_processor = NLPProcessor()
hr_analytics = HRAnalytics()
mock_data = MockDataGenerator()

@app.route('/')
def index():
    """Main dashboard showing overview of all HR modules"""
    # Get basic stats for dashboard
    total_employees = Employee.query.count()
    total_resumes = Resume.query.count()
    active_learning = LearningProgress.query.filter_by(completed=False).count()
    recent_wellness = WellnessCheck.query.order_by(WellnessCheck.check_date.desc()).limit(5).all()
    
    return render_template('index.html', 
                         total_employees=total_employees,
                         total_resumes=total_resumes,
                         active_learning=active_learning,
                         recent_wellness=recent_wellness)

@app.route('/resume-screening', methods=['GET', 'POST'])
def resume_screening():
    """Resume screening bot module"""
    if request.method == 'POST':
        job_description = request.form.get('job_description', '')
        
        # Handle file uploads
        uploaded_files = request.files.getlist('resumes')
        results = []
        
        for file in uploaded_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                content = file.read().decode('utf-8', errors='ignore')
                
                # Process resume with NLP
                skills = nlp_processor.extract_skills(content)
                score = nlp_processor.calculate_match_score(content, job_description)
                
                # Save to database
                resume = Resume(
                    filename=filename,
                    content=content,
                    skills_extracted=json.dumps(skills),
                    score=score,
                    job_description=job_description
                )
                db.session.add(resume)
                
                results.append({
                    'filename': filename,
                    'skills': skills,
                    'score': score,
                    'reasoning': nlp_processor.generate_reasoning(content, skills, score)
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
    
    # Analyze leadership potential
    leadership_candidates = []
    for employee in employees:
        potential_score = hr_analytics.calculate_leadership_potential(employee)
        if potential_score > 7.0:  # High potential threshold
            growth_actions = hr_analytics.suggest_growth_actions(employee, potential_score)
            leadership_candidates.append({
                'employee': employee,
                'potential_score': potential_score,
                'growth_actions': growth_actions
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

@app.route('/learning-module', methods=['GET', 'POST'])
def learning_module():
    """Gamified learning module"""
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        module_name = request.form.get('module_name')
        answers = request.form.getlist('answers')
        
        # Calculate score (mock quiz data)
        quiz_data = mock_data.get_quiz_data(module_name)
        score = hr_analytics.calculate_quiz_score(answers, quiz_data['correct_answers'])
        
        # Save progress
        progress = LearningProgress(
            employee_id=employee_id,
            module_name=module_name,
            score=score,
            completed=True,
            completion_date=datetime.now()
        )
        db.session.add(progress)
        db.session.commit()
        
        flash(f'Quiz completed! Your score: {score}/100', 'success')
        return redirect(url_for('learning_module'))
    
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
    """Skill gap analysis module"""
    if request.method == 'POST':
        current_skills = request.form.getlist('current_skills')
        target_role = request.form.get('target_role')
        
        # Analyze skill gaps
        gap_analysis = hr_analytics.analyze_skill_gaps(current_skills, target_role)
        
        return render_template('skill_gap_analysis.html', 
                             gap_analysis=gap_analysis,
                             current_skills=current_skills,
                             target_role=target_role)
    
    # Get available skills and roles
    available_skills = mock_data.get_available_skills()
    target_roles = mock_data.get_target_roles()
    
    return render_template('skill_gap_analysis.html', 
                         available_skills=available_skills,
                         target_roles=target_roles)

@app.route('/wellness-tracker', methods=['GET', 'POST'])
def wellness_tracker():
    """Employee wellness tracker with chatbot"""
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
        wellness_check = WellnessCheck(
            employee_id=employee_id,
            stress_level=stress_level,
            sleep_quality=sleep_quality,
            focus_level=focus_level,
            overall_wellness=wellness_status,
            recommendations=json.dumps(recommendations)
        )
        db.session.add(wellness_check)
        db.session.commit()
        
        return render_template('wellness_tracker.html', 
                             wellness_result={
                                 'status': wellness_status,
                                 'score': wellness_score,
                                 'recommendations': recommendations
                             },
                             employees=Employee.query.all())
    
    employees = Employee.query.all()
    recent_checks = WellnessCheck.query.order_by(WellnessCheck.check_date.desc()).limit(10).all()
    
    return render_template('wellness_tracker.html', 
                         employees=employees,
                         recent_checks=recent_checks)

@app.route('/hr-insights')
def hr_insights():
    """Unified HR insights dashboard"""
    # Generate comprehensive HR analytics
    insights = hr_analytics.generate_hr_insights()
    
    return render_template('hr_insights.html', insights=insights)

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
