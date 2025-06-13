"""
Real HR Analytics - Process actual HR data for insights dashboard
"""
import json
from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_, or_
from collections import defaultdict
import pandas as pd
from io import BytesIO

class RealHRAnalytics:
    """Process real HR data for comprehensive insights"""
    
    def __init__(self):
        pass
    
    def get_company_insights(self):
        """Generate comprehensive company-wide insights from real data"""
        from app import db
        from models import Employee, HRTransaction, EmployeeHistory, CompanyMetrics, PerformanceReview
        
        current_year = datetime.now().year
        
        # Basic employee metrics
        total_employees = Employee.query.filter_by(status='active').count()
        
        # Department distribution
        dept_distribution = db.session.query(
            Employee.department,
            func.count(Employee.id).label('count')
        ).filter_by(status='active').group_by(Employee.department).all()
        
        dept_data = {dept: count for dept, count in dept_distribution}
        
        # Increment analysis
        increment_data = self._analyze_increments(current_year)
        
        # Joining/Leaving analysis
        joining_leaving_data = self._analyze_workforce_changes(current_year)
        
        # Performance distribution
        performance_data = self._analyze_performance()
        
        # Employee leaderboard
        leaderboard = self._get_employee_leaderboard()
        
        # Monthly trends
        monthly_trends = self._get_monthly_trends(current_year)
        
        # Wellness summary
        wellness_summary = self._get_wellness_summary()
        
        return {
            'total_employees': total_employees,
            'department_distribution': dept_data,
            'increment_data': increment_data,
            'joining_leaving_data': joining_leaving_data,
            'performance_data': performance_data,
            'employee_leaderboard': leaderboard,
            'monthly_trends': monthly_trends,
            'wellness_summary': wellness_summary
        }
    
    def _analyze_increments(self, year):
        """Analyze increment data for the year"""
        from app import db
        from models import HRTransaction
        
        # Get all increment transactions for the year
        increments = HRTransaction.query.filter(
            and_(
                HRTransaction.transaction_type == 'increment',
                extract('year', HRTransaction.effective_date) == year
            )
        ).all()
        
        if not increments:
            return {
                'total_increments': 0,
                'total_amount': 0,
                'average_percentage': 0,
                'by_department': {},
                'by_month': {}
            }
        
        total_increments = len(increments)
        total_amount = sum(inc.amount or 0 for inc in increments)
        avg_percentage = sum(inc.percentage or 0 for inc in increments) / total_increments
        
        # By department
        dept_increments = defaultdict(lambda: {'count': 0, 'total_amount': 0})
        for inc in increments:
            if inc.department:
                dept_increments[inc.department]['count'] += 1
                dept_increments[inc.department]['total_amount'] += inc.amount or 0
        
        # By month
        monthly_increments = defaultdict(lambda: {'count': 0, 'total_amount': 0})
        for inc in increments:
            month = inc.effective_date.month
            monthly_increments[month]['count'] += 1
            monthly_increments[month]['total_amount'] += inc.amount or 0
        
        return {
            'total_increments': total_increments,
            'total_amount': total_amount,
            'average_percentage': round(avg_percentage, 2),
            'by_department': dict(dept_increments),
            'by_month': dict(monthly_increments)
        }
    
    def _analyze_workforce_changes(self, year):
        """Analyze workforce joining and leaving patterns"""
        from app import db
        from models import HRTransaction, Employee
        
        # Joinings
        joinings = HRTransaction.query.filter(
            and_(
                HRTransaction.transaction_type == 'joining',
                extract('year', HRTransaction.effective_date) == year
            )
        ).count()
        
        # Exits
        exits = HRTransaction.query.filter(
            and_(
                HRTransaction.transaction_type == 'exit',
                extract('year', HRTransaction.effective_date) == year
            )
        ).count()
        
        # Net growth
        net_growth = joinings - exits
        
        # Attrition rate (exits / average headcount)
        avg_headcount = Employee.query.count()
        attrition_rate = (exits / avg_headcount * 100) if avg_headcount > 0 else 0
        
        return {
            'joined_this_year': joinings,
            'left_this_year': exits,
            'net_growth': net_growth,
            'attrition_rate': round(attrition_rate, 2)
        }
    
    def _analyze_performance(self):
        """Analyze performance distribution"""
        from app import db
        from models import Employee, PerformanceReview
        
        # Get recent performance reviews
        recent_reviews = PerformanceReview.query.filter(
            PerformanceReview.created_at >= datetime.now() - timedelta(days=365)
        ).all()
        
        if not recent_reviews:
            # Fallback to employee performance scores
            employees = Employee.query.filter_by(status='active').all()
            if not employees:
                return {'distribution': {}, 'average_rating': 0}
            
            scores = [emp.performance_score or 7.0 for emp in employees]
            avg_score = sum(scores) / len(scores)
            
            distribution = {
                'excellent': len([s for s in scores if s >= 9.0]),
                'good': len([s for s in scores if 7.0 <= s < 9.0]),
                'average': len([s for s in scores if 5.0 <= s < 7.0]),
                'needs_improvement': len([s for s in scores if s < 5.0])
            }
            
            return {
                'distribution': distribution,
                'average_rating': round(avg_score, 2)
            }
        
        ratings = [review.overall_rating for review in recent_reviews]
        avg_rating = sum(ratings) / len(ratings)
        
        distribution = {
            'excellent': len([r for r in ratings if r >= 4.5]),
            'good': len([r for r in ratings if 3.5 <= r < 4.5]),
            'average': len([r for r in ratings if 2.5 <= r < 3.5]),
            'needs_improvement': len([r for r in ratings if r < 2.5])
        }
        
        return {
            'distribution': distribution,
            'average_rating': round(avg_rating, 2)
        }
    
    def _get_employee_leaderboard(self):
        """Get top performing employees"""
        from app import db
        from models import Employee, PerformanceReview, HRTransaction
        
        # Get employees with recent performance data
        employees = Employee.query.filter_by(status='active').all()
        
        leaderboard_data = []
        for emp in employees:
            # Get latest performance review
            latest_review = PerformanceReview.query.filter_by(
                employee_id=emp.id
            ).order_by(PerformanceReview.created_at.desc()).first()
            
            rating = latest_review.overall_rating if latest_review else emp.performance_score or 7.0
            
            # Get recent increments
            recent_increments = HRTransaction.query.filter(
                and_(
                    HRTransaction.employee_id == emp.id,
                    HRTransaction.transaction_type == 'increment',
                    HRTransaction.effective_date >= datetime.now().date() - timedelta(days=365)
                )
            ).count()
            
            leaderboard_data.append({
                'id': emp.id,
                'name': emp.name,
                'department': emp.department,
                'position': emp.position,
                'rating': rating,
                'increments_this_year': recent_increments
            })
        
        # Sort by rating and recent increments
        leaderboard_data.sort(key=lambda x: (x['rating'], x['increments_this_year']), reverse=True)
        
        return leaderboard_data[:10]  # Top 10
    
    def _get_monthly_trends(self, year):
        """Get monthly trends for various HR metrics"""
        from app import db
        from models import HRTransaction, Employee
        
        trends = {}
        
        # Monthly increments
        monthly_increments = db.session.query(
            extract('month', HRTransaction.effective_date).label('month'),
            func.count(HRTransaction.id).label('count')
        ).filter(
            and_(
                HRTransaction.transaction_type == 'increment',
                extract('year', HRTransaction.effective_date) == year
            )
        ).group_by(extract('month', HRTransaction.effective_date)).all()
        
        trends['increments'] = {int(month): count for month, count in monthly_increments}
        
        # Monthly joinings
        monthly_joinings = db.session.query(
            extract('month', HRTransaction.effective_date).label('month'),
            func.count(HRTransaction.id).label('count')
        ).filter(
            and_(
                HRTransaction.transaction_type == 'joining',
                extract('year', HRTransaction.effective_date) == year
            )
        ).group_by(extract('month', HRTransaction.effective_date)).all()
        
        trends['joinings'] = {int(month): count for month, count in monthly_joinings}
        
        # Monthly exits
        monthly_exits = db.session.query(
            extract('month', HRTransaction.effective_date).label('month'),
            func.count(HRTransaction.id).label('count')
        ).filter(
            and_(
                HRTransaction.transaction_type == 'exit',
                extract('year', HRTransaction.effective_date) == year
            )
        ).group_by(extract('month', HRTransaction.effective_date)).all()
        
        trends['exits'] = {int(month): count for month, count in monthly_exits}
        
        return trends
    
    def _get_wellness_summary(self):
        """Get wellness metrics summary"""
        from app import db
        from models import WellnessCheck
        
        # Get recent wellness checks (last 30 days)
        recent_checks = WellnessCheck.query.filter(
            WellnessCheck.check_date >= datetime.now() - timedelta(days=30)
        ).all()
        
        if not recent_checks:
            return {'total_checks': 0, 'distribution': {}}
        
        distribution = {
            'green': len([c for c in recent_checks if c.overall_wellness == 'green']),
            'yellow': len([c for c in recent_checks if c.overall_wellness == 'yellow']),
            'red': len([c for c in recent_checks if c.overall_wellness == 'red'])
        }
        
        return {
            'total_checks': len(recent_checks),
            'distribution': distribution
        }
    
    def get_employee_detailed_insights(self, employee_id):
        """Get detailed insights for a specific employee"""
        from app import db
        from models import Employee, HRTransaction, EmployeeHistory, PerformanceReview, WellnessCheck
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return None
        
        # HR Transactions history
        transactions = HRTransaction.query.filter_by(
            employee_id=employee_id
        ).order_by(HRTransaction.effective_date.desc()).all()
        
        # Performance reviews
        reviews = PerformanceReview.query.filter_by(
            employee_id=employee_id
        ).order_by(PerformanceReview.created_at.desc()).all()
        
        # Employee history
        history = EmployeeHistory.query.filter_by(
            employee_id=employee_id
        ).order_by(EmployeeHistory.change_date.desc()).all()
        
        # Wellness checks
        wellness = WellnessCheck.query.filter_by(
            employee_id=employee_id
        ).order_by(WellnessCheck.check_date.desc()).limit(10).all()
        
        # Calculate insights
        insights = self._calculate_employee_insights(employee, transactions, reviews)
        
        return {
            'employee': employee,
            'transactions': transactions,
            'reviews': reviews,
            'history': history,
            'wellness': wellness,
            'insights': insights
        }
    
    def _calculate_employee_insights(self, employee, transactions, reviews):
        """Calculate specific insights for an employee"""
        insights = {}
        
        # Last increment details
        last_increment = None
        for transaction in transactions:
            if transaction.transaction_type == 'increment':
                last_increment = transaction
                break
        
        insights['last_increment'] = {
            'date': last_increment.effective_date if last_increment else None,
            'amount': last_increment.amount if last_increment else 0,
            'percentage': last_increment.percentage if last_increment else 0
        }
        
        # Total increments received
        total_increments = len([t for t in transactions if t.transaction_type == 'increment'])
        insights['total_increments'] = total_increments
        
        # Performance trend
        if reviews:
            recent_ratings = [r.overall_rating for r in reviews[:5]]  # Last 5 reviews
            if len(recent_ratings) > 1:
                trend = 'improving' if recent_ratings[0] > recent_ratings[-1] else 'declining'
                if recent_ratings[0] == recent_ratings[-1]:
                    trend = 'stable'
            else:
                trend = 'stable'
            insights['performance_trend'] = trend
            insights['current_rating'] = recent_ratings[0] if recent_ratings else 0
        else:
            insights['performance_trend'] = 'no_data'
            insights['current_rating'] = employee.performance_score or 0
        
        # Time since last increment
        if last_increment:
            days_since = (datetime.now().date() - last_increment.effective_date).days
            insights['days_since_last_increment'] = days_since
        else:
            insights['days_since_last_increment'] = None
        
        # Career progression
        promotions = [t for t in transactions if t.transaction_type == 'promotion']
        insights['total_promotions'] = len(promotions)
        
        return insights
    
    def export_company_data_to_excel(self):
        """Export company insights data to Excel format"""
        insights = self.get_company_insights()
        
        # Create a temporary file path for Excel export
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_path = temp_file.name
        
        # Create Excel file
        with pd.ExcelWriter(temp_path, engine='xlsxwriter') as writer:
            # Company overview
            overview_data = {
                'Metric': ['Total Employees', 'Total Increments', 'Average Increment %', 
                          'Joinings This Year', 'Exits This Year', 'Net Growth', 'Attrition Rate %'],
                'Value': [
                    insights['total_employees'],
                    insights['increment_data']['total_increments'],
                    insights['increment_data']['average_percentage'],
                    insights['joining_leaving_data']['joined_this_year'],
                    insights['joining_leaving_data']['left_this_year'],
                    insights['joining_leaving_data']['net_growth'],
                    insights['joining_leaving_data']['attrition_rate']
                ]
            }
            pd.DataFrame(overview_data).to_excel(writer, sheet_name='Company Overview', index=False)
            
            # Department distribution
            dept_data = {
                'Department': list(insights['department_distribution'].keys()),
                'Employee Count': list(insights['department_distribution'].values())
            }
            pd.DataFrame(dept_data).to_excel(writer, sheet_name='Department Distribution', index=False)
            
            # Employee leaderboard
            leaderboard_df = pd.DataFrame(insights['employee_leaderboard'])
            leaderboard_df.to_excel(writer, sheet_name='Employee Leaderboard', index=False)
            
            # Monthly trends
            trends = insights['monthly_trends']
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            trend_data = {
                'Month': months,
                'Increments': [trends['increments'].get(i+1, 0) for i in range(12)],
                'Joinings': [trends['joinings'].get(i+1, 0) for i in range(12)],
                'Exits': [trends['exits'].get(i+1, 0) for i in range(12)]
            }
            pd.DataFrame(trend_data).to_excel(writer, sheet_name='Monthly Trends', index=False)
        
        # Read the file and return binary data
        with open(temp_path, 'rb') as f:
            excel_data = f.read()
        
        # Clean up temp file
        os.unlink(temp_path)
        return excel_data
    
    def export_employee_data_to_excel(self, employee_id):
        """Export individual employee data to Excel"""
        data = self.get_employee_detailed_insights(employee_id)
        if not data:
            return None
        
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_path = temp_file.name
        
        with pd.ExcelWriter(temp_path, engine='xlsxwriter') as writer:
            # Employee details
            emp = data['employee']
            emp_data = {
                'Field': ['Name', 'Email', 'Department', 'Position', 'Hire Date', 
                         'Current Salary', 'Performance Score', 'Status'],
                'Value': [emp.name, emp.email, emp.department, emp.position,
                         emp.hire_date, emp.current_salary, emp.performance_score, emp.status]
            }
            pd.DataFrame(emp_data).to_excel(writer, sheet_name='Employee Details', index=False)
            
            # HR Transactions
            if data['transactions']:
                trans_data = []
                for trans in data['transactions']:
                    trans_data.append({
                        'Date': trans.effective_date,
                        'Type': trans.transaction_type,
                        'Amount': trans.amount,
                        'Percentage': trans.percentage,
                        'Previous Salary': trans.previous_salary,
                        'New Salary': trans.new_salary,
                        'Reason': trans.reason
                    })
                pd.DataFrame(trans_data).to_excel(writer, sheet_name='HR Transactions', index=False)
            
            # Performance Reviews
            if data['reviews']:
                review_data = []
                for review in data['reviews']:
                    review_data.append({
                        'Date': review.created_at.date(),
                        'Period': review.review_period,
                        'Rating': review.overall_rating,
                        'Feedback': review.feedback[:200] + '...' if len(review.feedback) > 200 else review.feedback
                    })
                pd.DataFrame(review_data).to_excel(writer, sheet_name='Performance Reviews', index=False)
        
        output.seek(0)
        return output.getvalue()