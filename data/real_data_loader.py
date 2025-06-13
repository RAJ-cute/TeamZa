
import pandas as pd
import json
import os
import zipfile
from datetime import datetime
from werkzeug.utils import secure_filename

class RealDataLoader:
    """Load real employee data from uploaded files"""
    
    def __init__(self, zip_file_path=None, excel_file_path=None):
        self.zip_file_path = zip_file_path or "attached_assets/Employee_Resumes_and_Metadata_1749732886082.zip"
        self.excel_file_path = excel_file_path
        self.employee_data = []
        self.resume_data = []
        
    def extract_zip_contents(self):
        """Extract and process ZIP file contents"""
        extracted_files = {}
        
        try:
            with zipfile.ZipFile(self.zip_file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                for file_name in file_list:
                    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                        # Extract Excel file
                        zip_ref.extract(file_name, 'temp_extracted/')
                        self.excel_file_path = f'temp_extracted/{file_name}'
                        extracted_files['excel'] = self.excel_file_path
                    elif file_name.endswith('.pdf') or file_name.endswith('.docx') or file_name.endswith('.txt'):
                        # Extract resume files
                        zip_ref.extract(file_name, 'temp_extracted/')
                        extracted_files[file_name] = f'temp_extracted/{file_name}'
                        
        except Exception as e:
            print(f"Error extracting ZIP: {e}")
            return {}
            
        return extracted_files
    
    def load_employee_metadata(self):
        """Load employee metadata from Excel file"""
        if not self.excel_file_path or not os.path.exists(self.excel_file_path):
            print("Excel file not found, using fallback data")
            return self._get_fallback_employee_data()
            
        try:
            df = pd.read_excel(self.excel_file_path)
            
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            employees = []
            for _, row in df.iterrows():
                employee = {
                    'name': str(row.get('employee_name', row.get('name', f'Employee_{len(employees)+1}'))),
                    'email': f"{str(row.get('employee_name', f'employee{len(employees)+1}')).lower().replace(' ', '.')}@company.com",
                    'department': self._map_job_role_to_department(str(row.get('job_role', 'Unknown'))),
                    'position': str(row.get('job_role', 'Unknown')),
                    'hire_date': self._calculate_hire_date(row.get('experience', 2)),
                    'performance_score': self._calculate_performance_score(row.get('manager_rating', 7)),
                    'gender': str(row.get('gender', 'Not Specified')),
                    'region': str(row.get('region', 'Unknown')),
                    'age': int(row.get('age', 30)) if pd.notna(row.get('age')) else 30,
                    'experience_years': int(row.get('experience', 2)) if pd.notna(row.get('experience')) else 2,
                    'manager_rating': float(row.get('manager_rating', 7.0)) if pd.notna(row.get('manager_rating')) else 7.0,
                    'last_hike_date': self._parse_date_string(row.get('last_hike_date', '2023-01-01')),
                    'last_promotion_date': self._parse_date_string(row.get('last_promotion_date', '2022-01-01')),
                    'skill_gaps': str(row.get('skill_gaps', 'Communication, Leadership')),
                    'skills': self._generate_skills_from_role(str(row.get('job_role', 'Unknown')))
                }
                employees.append(employee)
                
            return employees
            
        except Exception as e:
            print(f"Error loading Excel data: {e}")
            return self._get_fallback_employee_data()
    
    def _map_job_role_to_department(self, job_role):
        """Map job role to department"""
        role_lower = job_role.lower()
        
        if any(term in role_lower for term in ['engineer', 'developer', 'tech', 'software', 'programmer']):
            return 'Engineering'
        elif any(term in role_lower for term in ['market', 'brand', 'content', 'seo']):
            return 'Marketing'
        elif any(term in role_lower for term in ['sales', 'account', 'business']):
            return 'Sales'
        elif any(term in role_lower for term in ['hr', 'human', 'recruit', 'talent']):
            return 'HR'
        elif any(term in role_lower for term in ['finance', 'account', 'financial']):
            return 'Finance'
        elif any(term in role_lower for term in ['operations', 'project', 'manager']):
            return 'Operations'
        else:
            return 'General'
    
    def _calculate_hire_date(self, experience_years):
        """Calculate hire date based on experience"""
        try:
            years_ago = int(experience_years) if experience_years else 2
            hire_date = datetime.now().date().replace(year=datetime.now().year - years_ago)
            return hire_date
        except:
            return datetime.now().date().replace(year=datetime.now().year - 2)
    
    def _calculate_performance_score(self, manager_rating):
        """Convert manager rating to performance score"""
        try:
            rating = float(manager_rating) if manager_rating else 7.0
            # Convert to 10-point scale if needed
            if rating <= 5:
                return rating * 2  # Scale 1-5 to 2-10
            return min(rating, 10.0)
        except:
            return 7.0
    
    def _parse_date_string(self, date_str):
        """Parse date string to date object"""
        try:
            if isinstance(date_str, str):
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            return date_str
        except:
            return datetime.now().date()
    
    def _generate_skills_from_role(self, job_role):
        """Generate relevant skills based on job role"""
        role_lower = job_role.lower()
        
        skill_sets = {
            'engineer': ['Python', 'Java', 'JavaScript', 'SQL', 'Git', 'Agile', 'Problem Solving'],
            'manager': ['Leadership', 'Project Management', 'Communication', 'Strategic Planning', 'Team Building'],
            'analyst': ['Excel', 'SQL', 'Data Analysis', 'Reporting', 'Critical Thinking'],
            'sales': ['Negotiation', 'CRM', 'Communication', 'Lead Generation', 'Customer Relations'],
            'marketing': ['Digital Marketing', 'Content Creation', 'SEO', 'Social Media', 'Analytics'],
            'hr': ['Recruitment', 'Employee Relations', 'HRIS', 'Communication', 'Conflict Resolution'],
            'finance': ['Financial Analysis', 'Excel', 'Accounting', 'Budgeting', 'Risk Management']
        }
        
        for role_type, skills in skill_sets.items():
            if role_type in role_lower:
                return json.dumps(skills)
        
        # Default skills
        return json.dumps(['Communication', 'Teamwork', 'Problem Solving', 'Time Management'])
    
    def _get_fallback_employee_data(self):
        """Fallback employee data if Excel file can't be loaded"""
        return [
            {
                'name': 'John Smith',
                'email': 'john.smith@company.com',
                'department': 'Engineering',
                'position': 'Software Engineer',
                'hire_date': datetime(2022, 1, 15).date(),
                'performance_score': 8.5,
                'gender': 'Male',
                'region': 'North',
                'age': 28,
                'experience_years': 5,
                'manager_rating': 8.5,
                'last_hike_date': datetime(2023, 6, 1).date(),
                'last_promotion_date': datetime(2022, 12, 1).date(),
                'skill_gaps': 'Leadership, Public Speaking',
                'skills': json.dumps(['Python', 'JavaScript', 'SQL', 'React', 'Git'])
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.johnson@company.com',
                'department': 'Marketing',
                'position': 'Marketing Manager',
                'hire_date': datetime(2021, 3, 10).date(),
                'performance_score': 9.0,
                'gender': 'Female',
                'region': 'South',
                'age': 32,
                'experience_years': 7,
                'manager_rating': 9.0,
                'last_hike_date': datetime(2023, 7, 15).date(),
                'last_promotion_date': datetime(2023, 1, 1).date(),
                'skill_gaps': 'Data Analysis, Technical Skills',
                'skills': json.dumps(['Digital Marketing', 'SEO', 'Content Strategy', 'Social Media', 'Analytics'])
            },
            # Add more fallback employees as needed
        ]
    
    def load_resumes(self, extracted_files):
        """Load and process resume files"""
        resumes = []
        
        for file_name, file_path in extracted_files.items():
            if file_name != 'excel' and os.path.exists(file_path):
                try:
                    # Extract text content based on file type
                    content = self._extract_text_content(file_path, file_name)
                    
                    if content:
                        resume = {
                            'filename': file_name,
                            'content': content,
                            'skills_extracted': json.dumps(self._extract_skills_from_resume(content)),
                            'score': 0.0,  # Will be calculated during screening
                            'job_description': ''
                        }
                        resumes.append(resume)
                        
                except Exception as e:
                    print(f"Error processing resume {file_name}: {e}")
        
        return resumes
    
    def _extract_text_content(self, file_path, file_name):
        """Extract text content from different file types"""
        try:
            if file_name.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            elif file_name.endswith('.pdf'):
                # For PDF files - would need PyPDF2 or similar
                return f"Resume content from {file_name} - PDF processing would require additional libraries"
            elif file_name.endswith('.docx'):
                # For DOCX files - would need python-docx
                return f"Resume content from {file_name} - DOCX processing would require additional libraries"
            else:
                return f"Resume content from {file_name}"
        except Exception as e:
            print(f"Error extracting text from {file_name}: {e}")
            return f"Error reading {file_name}"
    
    def _extract_skills_from_resume(self, content):
        """Extract skills from resume content"""
        # Common skills to look for
        all_skills = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Go',
            'HTML', 'CSS', 'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
            'AWS', 'Azure', 'Docker', 'Kubernetes',
            'Leadership', 'Communication', 'Project Management', 'Agile', 'Scrum',
            'Excel', 'Tableau', 'Power BI', 'Analytics'
        ]
        
        content_lower = content.lower()
        found_skills = []
        
        for skill in all_skills:
            if skill.lower() in content_lower:
                found_skills.append(skill)
        
        return found_skills[:10]  # Limit to top 10 skills
    
    def cleanup_temp_files(self):
        """Clean up temporary extracted files"""
        import shutil
        if os.path.exists('temp_extracted'):
            shutil.rmtree('temp_extracted')
