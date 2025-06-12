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

        # Add word boundary checking for better accuracy
        import re

        for skill in self.all_skills:
            # Create pattern with word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)

        # Also look for common skill variations and abbreviations
        skill_variations = {
            'javascript': ['js', 'node.js', 'nodejs'],
            'python': ['py'],
            'artificial intelligence': ['ai', 'machine learning', 'ml'],
            'user interface': ['ui'],
            'user experience': ['ux'],
            'application programming interface': ['api'],
            'database': ['db'],
            'software development': ['dev', 'development']
        }

        for main_skill, variations in skill_variations.items():
            for variation in variations:
                pattern = r'\b' + re.escape(variation) + r'\b'
                if re.search(pattern, text_lower) and main_skill not in [s.lower() for s in found_skills]:
                    found_skills.append(main_skill)

        # Remove duplicates and return
        return list(set(found_skills))

    def calculate_match_score(self, resume_text, job_description):
        """Calculate match score between resume and job description"""
        resume_skills = set(self.extract_skills(resume_text))
        job_skills = set(self.extract_skills(job_description))

        if not job_skills:
            return 0.0

        # Calculate skill match score with weights
        intersection = resume_skills.intersection(job_skills)
        skill_match_score = len(intersection) / len(job_skills) if job_skills else 0

        # Calculate keyword frequency score
        resume_words = self._preprocess_text(resume_text)
        job_words = self._preprocess_text(job_description)
        keyword_score = self._calculate_keyword_similarity(resume_words, job_words)

        # Experience bonus
        experience_bonus = 0
        resume_lower = resume_text.lower()
        import re
        years_match = re.findall(r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)', resume_lower)
        if years_match:
            max_years = max([int(y) for y in years_match])
            if max_years >= 5:
                experience_bonus = 0.1
            elif max_years >= 2:
                experience_bonus = 0.05

        # Education bonus
        education_bonus = 0
        if any(word in resume_lower for word in ['bachelor', 'master', 'phd', 'degree', 'university', 'college']):
            education_bonus = 0.05

        # Combine scores with weights
        base_score = (skill_match_score * 0.5 + keyword_score * 0.4) * 100
        final_score = base_score + (experience_bonus * 100) + (education_bonus * 100)

        # Add some randomization to avoid identical scores
        import random
        random.seed(hash(resume_text) % (2**32))  # Deterministic but varies per resume
        variation = random.uniform(-2, 2)
        final_score += variation

        return round(max(0, min(final_score, 100)), 2)

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

    def generate_reasoning(self, content, skills, score):
        """Generate reasoning for the match score"""
        # Analyze content for key indicators
        content_lower = content.lower()

        strengths = []
        concerns = []

        # Experience indicators - check for specific years/experience
        experience_years = self._extract_experience_years(content_lower)
        if experience_years >= 5:
            strengths.append(f"{experience_years}+ years of relevant experience")
        elif experience_years >= 2:
            strengths.append(f"{experience_years} years of experience")
        else:
            concerns.append("Limited professional experience")

        # Leadership indicators
        leadership_terms = ['senior', 'lead', 'manager', 'director', 'head', 'principal', 'architect']
        leadership_count = sum(1 for term in leadership_terms if term in content_lower)
        if leadership_count >= 2:
            strengths.append("Strong leadership experience")
        elif leadership_count == 1:
            strengths.append("Some leadership experience")

        # Education indicators
        education_terms = ['degree', 'university', 'college', 'masters', 'phd', 'bachelor', 'mba']
        education_count = sum(1 for term in education_terms if term in content_lower)
        if education_count >= 2:
            strengths.append("Strong educational background")
        elif education_count == 1:
            strengths.append("Relevant education")

        # Skills assessment
        if len(skills) >= 7:
            strengths.append(f"Excellent skills match ({len(skills)} relevant skills identified)")
        elif len(skills) >= 4:
            strengths.append(f"Good skills match ({len(skills)} relevant skills)")
        elif len(skills) >= 2:
            concerns.append(f"Moderate skills match ({len(skills)} skills)")
        else:
            concerns.append("Limited relevant skills identified")

        # Technical certifications
        cert_terms = ['certified', 'certification', 'aws', 'azure', 'google cloud', 'oracle', 'cisco']
        cert_count = sum(1 for term in cert_terms if term in content_lower)
        if cert_count >= 2:
            strengths.append("Multiple professional certifications")
        elif cert_count == 1:
            strengths.append("Professional certification")

        # Project experience
        project_terms = ['project', 'developed', 'built', 'implemented', 'designed', 'created']
        project_count = sum(1 for term in project_terms if term in content_lower)
        if project_count >= 5:
            strengths.append("Extensive project experience")
        elif project_count >= 3:
            strengths.append("Good project experience")

        # Generate dynamic reasoning based on analysis
        reasoning_parts = []

        if score >= 8.5:
            reasoning_parts.append("⭐ Exceptional candidate with outstanding qualifications.")
        elif score >= 7.5:
            reasoning_parts.append("✅ Strong candidate with solid qualifications.")
        elif score >= 6.0:
            reasoning_parts.append("👍 Good candidate with potential.")
        elif score >= 4.0:
            reasoning_parts.append("⚠️ Moderate fit requiring careful consideration.")
        else:
            reasoning_parts.append("❌ Limited fit for this position.")

        if strengths:
            reasoning_parts.append(f"Key strengths: {', '.join(strengths[:3])}")

        if concerns:
            reasoning_parts.append(f"Areas of concern: {', '.join(concerns[:2])}")

        # Add recommendation
        if score >= 7.5:
            reasoning_parts.append("Highly recommended for immediate interview.")
        elif score >= 6.0:
            reasoning_parts.append("Recommended for further screening.")
        elif score >= 4.0:
            reasoning_parts.append("Consider for junior roles or with additional training.")
        else:
            reasoning_parts.append("Not recommended for this position.")

        return " ".join(reasoning_parts)

    def _extract_experience_years(self, content):
        """Extract years of experience from resume content"""
        import re

        # Look for patterns like "5 years", "3+ years", "2-4 years"
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\s*(?:-|to)\s*\d+\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?'
        ]

        max_years = 0
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    years = int(match)
                    max_years = max(max_years, years)
                except ValueError:
                    continue

        # If no explicit years found, estimate from job history
        if max_years == 0:
            job_indicators = content.count('experience') + content.count('worked') + content.count('position')
            if job_indicators >= 3:
                max_years = 3
            elif job_indicators >= 2:
                max_years = 2
            else:
                max_years = 1

        return min(max_years, 20)  # Cap at 20 years to be reasonable

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