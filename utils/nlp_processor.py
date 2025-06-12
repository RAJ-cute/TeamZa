import re
import json
from collections import Counter
import math

class NLPProcessor:
    """Basic NLP processor for HR platform"""
    
    def __init__(self):
        # Common skills database
        self.skills_db = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'kotlin'],
            'web_development': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'cassandra'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible'],
            'data_science': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'jupyter', 'r', 'tableau'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'creativity', 'adaptability'],
            'project_management': ['agile', 'scrum', 'kanban', 'jira', 'confluence', 'project planning'],
            'design': ['photoshop', 'illustrator', 'figma', 'sketch', 'ui/ux', 'graphic design']
        }
        
        # Flatten skills for easy searching
        self.all_skills = []
        for category in self.skills_db.values():
            self.all_skills.extend(category)
    
    def extract_skills(self, text):
        """Extract skills from text using keyword matching"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.all_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    def calculate_match_score(self, resume_text, job_description):
        """Calculate match score between resume and job description"""
        resume_skills = set(self.extract_skills(resume_text))
        job_skills = set(self.extract_skills(job_description))
        
        if not job_skills:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(resume_skills.intersection(job_skills))
        union = len(resume_skills.union(job_skills))
        
        if union == 0:
            return 0.0
        
        jaccard_score = intersection / union
        
        # Calculate keyword frequency score
        resume_words = self._preprocess_text(resume_text)
        job_words = self._preprocess_text(job_description)
        
        keyword_score = self._calculate_keyword_similarity(resume_words, job_words)
        
        # Combine scores (weighted average)
        final_score = (jaccard_score * 0.6 + keyword_score * 0.4) * 100
        
        return round(min(final_score, 100), 2)
    
    def _preprocess_text(self, text):
        """Preprocess text for analysis"""
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        words = text.split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return words
    
    def _calculate_keyword_similarity(self, words1, words2):
        """Calculate cosine similarity between two word lists"""
        # Count word frequencies
        freq1 = Counter(words1)
        freq2 = Counter(words2)
        
        # Get all unique words
        all_words = set(freq1.keys()) | set(freq2.keys())
        
        if not all_words:
            return 0.0
        
        # Create vectors
        vec1 = [freq1.get(word, 0) for word in all_words]
        vec2 = [freq2.get(word, 0) for word in all_words]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def generate_reasoning(self, resume_text, skills, score):
        """Generate reasoning for the match score"""
        if score >= 80:
            return f"Excellent match! Found {len(skills)} relevant skills including {', '.join(skills[:3])}. Strong alignment with job requirements."
        elif score >= 60:
            return f"Good match. Identified {len(skills)} relevant skills. Some additional training may be beneficial."
        elif score >= 40:
            return f"Moderate match. Found {len(skills)} relevant skills but may lack some key requirements."
        else:
            return f"Limited match. Only {len(skills)} relevant skills identified. Significant skill gaps present."
    
    def analyze_sentiment(self, text):
        """Basic sentiment analysis using keyword matching"""
        positive_words = [
            'excellent', 'outstanding', 'exceptional', 'great', 'good', 'positive', 'strong',
            'impressed', 'exceeded', 'successful', 'effective', 'innovative', 'creative',
            'dedicated', 'motivated', 'reliable', 'professional', 'skilled', 'talented'
        ]
        
        negative_words = [
            'poor', 'bad', 'weak', 'inadequate', 'disappointing', 'failed', 'struggling',
            'needs improvement', 'below average', 'unsatisfactory', 'problematic',
            'concerning', 'difficult', 'challenging', 'issues', 'problems'
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        # Calculate sentiment score (-1 to 1)
        sentiment_score = (positive_count - negative_count) / max(total_words / 10, 1)
        
        # Normalize to 0-10 scale
        normalized_score = (sentiment_score + 1) * 5
        
        return round(max(0, min(10, normalized_score)), 2)
