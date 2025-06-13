import random
import json
from datetime import datetime, timedelta
from models import Employee, HealthMetrics
from app import db

class HealthDataGenerator:
    """Generate comprehensive health data for employees based on their profiles"""
    
    def __init__(self):
        pass
    
    def generate_health_data(self, employee):
        """Generate health data for a specific employee"""
        age = employee.age or 30
        job_role = employee.position
        
        # Physical health metrics
        bmi = round(random.uniform(18.5, 32.5), 1)
        if bmi > 30:
            bmi_status = "Obese"
        elif bmi > 25:
            bmi_status = "Overweight"
        elif bmi > 18.5:
            bmi_status = "Normal"
        else:
            bmi_status = "Underweight"
        
        blood_pressure = f"{random.randint(100, 140)}/{random.randint(60, 90)}"
        if int(blood_pressure.split('/')[0]) > 130 or int(blood_pressure.split('/')[1]) > 85:
            bp_status = "Elevated"
        else:
            bp_status = "Normal"
        
        steps_avg = random.randint(3000, 12000)
        sleep_avg = round(random.uniform(5.5, 8.5), 1)
        
        # Mental health metrics
        stress_level = random.randint(1, 10)
        if stress_level > 7:
            stress_status = "High"
        elif stress_level > 4:
            stress_status = "Moderate"
        else:
            stress_status = "Low"
        
        mood_score = random.randint(3, 10)
        if mood_score > 7:
            mood_status = "Positive"
        elif mood_score > 5:
            mood_status = "Neutral"
        else:
            mood_status = "Negative"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(job_role, age, bmi_status, stress_status)
        
        return {
            "employee_id": employee.id,
            "bmi": bmi,
            "bmi_status": bmi_status,
            "blood_pressure": blood_pressure,
            "bp_status": bp_status,
            "avg_daily_steps": steps_avg,
            "avg_sleep_hours": sleep_avg,
            "stress_level": stress_level,
            "stress_status": stress_status,
            "mood_score": mood_score,
            "mood_status": mood_status,
            "recommendations": json.dumps(recommendations)
        }
    
    def _generate_recommendations(self, job_role, age, bmi_status, stress_status):
        """Generate personalized recommendations based on employee profile"""
        recommendations = []
        
        # Job-specific recommendations
        if "Product Manager" in job_role:
            recommendations.append("Practice mindfulness techniques to manage cross-functional team stress")
            recommendations.append("Schedule regular breaks from screen time to reduce eye strain")
        elif "Sales Executive" in job_role:
            recommendations.append("Consider voice care exercises to maintain vocal health with frequent client calls")
            recommendations.append("Stretch regularly to counteract long hours of travel/standing")
        elif "HR Manager" in job_role:
            recommendations.append("Engage in stress-relief activities to manage employee relations workload")
            recommendations.append("Practice active listening techniques to reduce emotional fatigue")
        elif "Cybersecurity Specialist" in job_role:
            recommendations.append("Follow the 20-20-20 rule (every 20 minutes, look at something 20 feet away for 20 seconds)")
            recommendations.append("Consider blue light filtering glasses for prolonged screen exposure")
        elif "Data Analyst" in job_role:
            recommendations.append("Take micro-breaks every hour to prevent repetitive strain injuries")
            recommendations.append("Try desk exercises to improve circulation during long analysis sessions")
        else:
            recommendations.append("Maintain good posture and take regular breaks during work hours")
            recommendations.append("Stay hydrated and maintain regular meal times")
        
        # Age-specific recommendations
        if age > 40:
            recommendations.append("Consider annual comprehensive health checkups")
            recommendations.append("Focus on joint mobility exercises")
        elif age > 30:
            recommendations.append("Schedule preventive health screenings")
            recommendations.append("Maintain work-life balance to prevent burnout")
        else:
            recommendations.append("Establish healthy habits early for long-term wellness")
        
        # BMI-specific recommendations
        if bmi_status in ["Overweight", "Obese"]:
            recommendations.append("Consult with a nutritionist for personalized diet advice")
            recommendations.append("Incorporate 30 minutes of moderate exercise daily")
        elif bmi_status == "Underweight":
            recommendations.append("Consult with a nutritionist to ensure adequate calorie intake")
        
        # Stress-specific recommendations
        if stress_status == "High":
            recommendations.append("Practice deep breathing exercises for 5 minutes daily")
            recommendations.append("Consider speaking with a counselor about stress management")
        
        return recommendations
    
    def generate_for_all_employees(self):
        """Generate health data for all employees who don't have it"""
        employees = Employee.query.all()
        generated_count = 0
        
        for employee in employees:
            # Check if employee already has health metrics
            existing_metrics = HealthMetrics.query.filter_by(employee_id=employee.id).first()
            if not existing_metrics:
                health_data = self.generate_health_data(employee)
                health_metrics = HealthMetrics(**health_data)
                db.session.add(health_metrics)
                generated_count += 1
        
        db.session.commit()
        return generated_count
    
    def get_health_overview(self):
        """Get overall health statistics for all employees"""
        all_metrics = HealthMetrics.query.all()
        if not all_metrics:
            return {}
        
        normal_bmi = len([m for m in all_metrics if m.bmi_status == 'Normal'])
        normal_bp = len([m for m in all_metrics if m.bp_status == 'Normal'])
        low_stress = len([m for m in all_metrics if m.stress_status == 'Low'])
        positive_mood = len([m for m in all_metrics if m.mood_status == 'Positive'])
        
        return {
            'total_employees': len(all_metrics),
            'normal_bmi_count': normal_bmi,
            'normal_bp_count': normal_bp,
            'low_stress_count': low_stress,
            'positive_mood_count': positive_mood,
            'normal_bmi_percent': round((normal_bmi / len(all_metrics)) * 100, 1),
            'normal_bp_percent': round((normal_bp / len(all_metrics)) * 100, 1),
            'low_stress_percent': round((low_stress / len(all_metrics)) * 100, 1),
            'positive_mood_percent': round((positive_mood / len(all_metrics)) * 100, 1)
        }