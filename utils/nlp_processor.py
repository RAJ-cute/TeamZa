import re
import json
from collections import Counter
import math

class NLPProcessor:
    """Basic NLP processor for HR platform"""

    def __init__(self):
        # Comprehensive skills database with synonyms and variations
        self.skills_db = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'kotlin', 'swift', 'scala', 'perl', 'matlab', 'typescript'],
            'web_development': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'laravel', 'spring boot', 'asp.net', 'ruby on rails'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'cassandra', 'dynamodb', 'elasticsearch', 'neo4j'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'ci/cd', 'devops', 'microservices'],
            'data_science': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'jupyter', 'r', 'tableau', 'power bi', 'matplotlib', 'seaborn', 'spark'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'creativity', 'adaptability', 'analytical thinking', 'project management'],
            'project_management': ['agile', 'scrum', 'kanban', 'jira', 'confluence', 'project planning', 'waterfall', 'lean', 'six sigma', 'pmp'],
            'design': ['photoshop', 'illustrator', 'figma', 'sketch', 'ui/ux', 'graphic design', 'adobe creative suite', 'wireframing', 'prototyping'],
            'business': ['product management', 'business analysis', 'market research', 'strategic planning', 'stakeholder management', 'roadmap planning'],
            'mobile': ['ios', 'android', 'react native', 'flutter', 'xamarin', 'mobile development', 'app store', 'google play'],
            'security': ['cybersecurity', 'penetration testing', 'vulnerability assessment', 'security auditing', 'compliance', 'risk management'],
            'testing': ['selenium', 'test automation', 'unit testing', 'integration testing', 'performance testing', 'qa', 'quality assurance']
        }

        # Enhanced skill variations and synonyms
        self.skill_variations = {
            'javascript': ['js', 'node.js', 'nodejs', 'ecmascript'],
            'python': ['py', 'python3', 'python2'],
            'artificial intelligence': ['ai', 'machine learning', 'ml', 'deep learning', 'neural networks'],
            'user interface': ['ui', 'user experience', 'ux', 'frontend'],
            'application programming interface': ['api', 'rest api', 'restful', 'graphql'],
            'database': ['db', 'databases', 'data management'],
            'software development': ['dev', 'development', 'programming', 'coding'],
            'amazon web services': ['aws', 'amazon cloud'],
            'microsoft azure': ['azure', 'azure cloud'],
            'google cloud platform': ['gcp', 'google cloud'],
            'continuous integration': ['ci', 'ci/cd', 'continuous deployment'],
            'object oriented programming': ['oop', 'object oriented'],
            'version control': ['git', 'github', 'gitlab', 'bitbucket', 'svn'],
            'product management': ['product manager', 'product owner', 'roadmap planning'],
            'business intelligence': ['bi', 'power bi', 'tableau', 'qlik']
        }

        # Flatten skills for searching
        self.all_skills = []
        for category in self.skills_db.values():
            self.all_skills.extend(category)

        # Add variations to all skills
        for main_skill, variations in self.skill_variations.items():
            if main_skill not in self.all_skills:
                self.all_skills.append(main_skill)
            self.all_skills.extend(variations)

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
        """Calculate intelligent match score between resume and job description"""
        resume_skills = set(self.extract_skills(resume_text))
        job_skills = set(self.extract_skills(job_description))

        if not job_skills:
            return 0.0

        # 1. Skills matching (40% weight)
        intersection = resume_skills.intersection(job_skills)
        skill_match_score = len(intersection) / len(job_skills) if job_skills else 0

        # Bonus for having more skills than required
        skill_abundance_bonus = min(0.1, (len(resume_skills) - len(job_skills)) / len(job_skills)) if len(job_skills) > 0 else 0
        skill_match_score = min(1.0, skill_match_score + max(0, skill_abundance_bonus))

        # 2. Contextual keyword matching (25% weight)
        resume_words = self._preprocess_text(resume_text)
        job_words = self._preprocess_text(job_description)
        keyword_score = self._calculate_keyword_similarity(resume_words, job_words)

        # 3. Experience analysis (20% weight)
        experience_score = self._calculate_experience_score(resume_text, job_description)

        # 4. Education relevance (10% weight)
        education_score = self._calculate_education_score(resume_text, job_description)

        # 5. Role-specific indicators (5% weight)
        role_score = self._calculate_role_specific_score(resume_text, job_description)

        # Combine all scores with weights
        final_score = (
            skill_match_score * 0.40 +
            keyword_score * 0.25 +
            experience_score * 0.20 +
            education_score * 0.10 +
            role_score * 0.05
        ) * 100

        # Ensure score is between 0 and 100
        return round(max(0, min(final_score, 100)), 1)

    def _calculate_experience_score(self, resume_text, job_description):
        """Calculate experience relevance score"""
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()

        # Extract years from resume
        resume_years = self._extract_experience_years(resume_lower)

        # Try to find required experience in job description
        import re
        job_years_match = re.findall(r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)', job_lower)
        required_years = max([int(y) for y in job_years_match]) if job_years_match else 2

        # Score based on experience match
        if resume_years >= required_years * 1.5:  # Significantly more experience
            return 1.0
        elif resume_years >= required_years:  # Meets requirement
            return 0.8
        elif resume_years >= required_years * 0.7:  # Close to requirement
            return 0.6
        elif resume_years >= required_years * 0.5:  # Some experience
            return 0.4
        else:  # Limited experience
            return 0.2

    def _calculate_education_score(self, resume_text, job_description):
        """Calculate education relevance score"""
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()

        # Education levels
        education_levels = {
            'phd': 4, 'doctorate': 4, 'doctoral': 4,
            'master': 3, 'mba': 3, 'ms': 3, 'ma': 3,
            'bachelor': 2, 'bs': 2, 'ba': 2, 'degree': 2,
            'diploma': 1, 'certificate': 1
        }

        # Find highest education in resume
        resume_edu_level = 0
        for edu, level in education_levels.items():
            if edu in resume_lower:
                resume_edu_level = max(resume_edu_level, level)

        # Find required education in job description
        required_edu_level = 0
        for edu, level in education_levels.items():
            if edu in job_lower:
                required_edu_level = max(required_edu_level, level)

        # Default to bachelor's if no specific requirement found but mentions "degree"
        if required_edu_level == 0 and 'degree' in job_lower:
            required_edu_level = 2

        # Score based on education match
        if resume_edu_level >= required_edu_level:
            return 1.0
        elif resume_edu_level >= required_edu_level - 1:
            return 0.7
        elif resume_edu_level > 0:
            return 0.4
        else:
            return 0.1

    def _calculate_role_specific_score(self, resume_text, job_description):
        """Calculate role-specific indicators score"""
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()

        # Industry-specific terms
        industry_terms = [
            'healthcare', 'finance', 'fintech', 'banking', 'insurance',
            'retail', 'e-commerce', 'manufacturing', 'automotive',
            'technology', 'software', 'startup', 'enterprise',
            'government', 'non-profit', 'education', 'media'
        ]

        # Company size indicators
        size_terms = [
            'startup', 'small business', 'mid-size', 'enterprise',
            'fortune 500', 'multinational', 'global company'
        ]

        # Work style indicators
        work_terms = [
            'remote', 'hybrid', 'agile', 'waterfall', 'collaborative',
            'cross-functional', 'fast-paced', 'deadline-driven'
        ]

        all_terms = industry_terms + size_terms + work_terms

        # Count matching terms
        matching_terms = 0
        total_terms = 0

        for term in all_terms:
            if term in job_lower:
                total_terms += 1
                if term in resume_lower:
                    matching_terms += 1

        return matching_terms / total_terms if total_terms > 0 else 0.5

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

    def generate_reasoning(self, content, skills, score, job_description=""):
        """Generate intelligent, personalized reasoning for the match score"""
        content_lower = content.lower()
        job_lower = job_description.lower() if job_description else ""

        # Analyze different aspects
        analysis = self._analyze_candidate_profile(content_lower, job_lower)

        strengths = analysis['strengths']
        concerns = analysis['concerns']
        unique_factors = analysis['unique_factors']

        # Generate dynamic reasoning based on score and analysis
        reasoning_parts = []

        # Opening assessment based on score
        if score >= 85:
            reasoning_parts.append("🌟 **Exceptional Match** - This candidate demonstrates outstanding alignment with the role requirements.")
        elif score >= 75:
            reasoning_parts.append("✅ **Strong Candidate** - Well-qualified with solid experience and relevant skills.")
        elif score >= 65:
            reasoning_parts.append("👍 **Good Potential** - Promising candidate with transferable skills and growth potential.")
        elif score >= 50:
            reasoning_parts.append("⚠️ **Moderate Fit** - Some relevant experience but may need additional development.")
        else:
            reasoning_parts.append("❌ **Limited Match** - Significant gaps in required qualifications.")

        # Detailed strengths analysis
        if strengths:
            if len(strengths) >= 4:
                reasoning_parts.append(f"**Key Strengths:** {', '.join(strengths[:4])}.")
            else:
                reasoning_parts.append(f"**Strengths:** {', '.join(strengths)}.")

        # Skills-specific analysis
        skills_analysis = self._analyze_skills_match(skills, job_description)
        if skills_analysis:
            reasoning_parts.append(skills_analysis)

        # Unique differentiators
        if unique_factors:
            reasoning_parts.append(f"**Differentiators:** {', '.join(unique_factors[:2])}.")

        # Areas for improvement
        if concerns:
            reasoning_parts.append(f"**Development Areas:** {', '.join(concerns[:2])}.")

        # Final recommendation with specific action
        recommendation = self._generate_recommendation(score, analysis)
        reasoning_parts.append(f"**Recommendation:** {recommendation}")

        return " ".join(reasoning_parts)

    def _analyze_candidate_profile(self, content_lower, job_lower):
        """Comprehensive analysis of candidate profile"""
        strengths = []
        concerns = []
        unique_factors = []

        # Experience analysis
        experience_years = self._extract_experience_years(content_lower)
        if experience_years >= 10:
            strengths.append(f"Highly experienced ({experience_years}+ years)")
        elif experience_years >= 5:
            strengths.append(f"Solid experience ({experience_years} years)")
        elif experience_years >= 2:
            strengths.append(f"Relevant experience ({experience_years} years)")
        else:
            concerns.append("Limited professional experience")

        # Leadership and seniority
        leadership_terms = ['senior', 'lead', 'manager', 'director', 'head', 'principal', 'architect', 'chief', 'vp']
        leadership_count = sum(1 for term in leadership_terms if term in content_lower)
        if leadership_count >= 3:
            strengths.append("Strong leadership background")
            unique_factors.append("Executive-level experience")
        elif leadership_count >= 1:
            strengths.append("Leadership experience")

        # Technical depth
        tech_indicators = ['architecture', 'design patterns', 'scalability', 'performance optimization', 'system design']
        tech_count = sum(1 for term in tech_indicators if term in content_lower)
        if tech_count >= 2:
            unique_factors.append("Deep technical expertise")

        # Education and certifications
        advanced_edu = ['phd', 'doctorate', 'master', 'mba']
        if any(edu in content_lower for edu in advanced_edu):
            strengths.append("Advanced education")

        cert_terms = ['certified', 'certification', 'aws certified', 'microsoft certified', 'google certified']
        if any(cert in content_lower for cert in cert_terms):
            strengths.append("Professional certifications")

        # Industry experience
        if job_lower:
            industry_match = self._check_industry_alignment(content_lower, job_lower)
            if industry_match:
                strengths.append(f"Relevant {industry_match} experience")

        # Collaboration and soft skills
        collab_terms = ['collaborative', 'cross-functional', 'stakeholder', 'communication', 'presentation']
        if sum(1 for term in collab_terms if term in content_lower) >= 2:
            strengths.append("Strong collaboration skills")

        # Innovation and impact
        impact_terms = ['innovative', 'optimization', 'improvement', 'award', 'recognition', 'patent']
        if sum(1 for term in impact_terms if term in content_lower) >= 2:
            unique_factors.append("Proven track record of innovation")

        return {
            'strengths': strengths,
            'concerns': concerns,
            'unique_factors': unique_factors
        }

    def _analyze_skills_match(self, skills, job_description):
        """Analyze specific skills alignment"""
        if not skills or len(skills) < 2:
            return "Limited relevant technical skills identified."

        job_skills = self.extract_skills(job_description) if job_description else []

        if len(skills) >= 8:
            if job_skills:
                overlap = len(set(skills).intersection(set(job_skills)))
                if overlap >= len(job_skills) * 0.7:
                    return f"Excellent skills alignment with {overlap}/{len(job_skills)} key requirements met."
                else:
                    return f"Broad skill set ({len(skills)} skills) with {overlap} direct matches to requirements."
            else:
                return f"Comprehensive technical skill set ({len(skills)} skills identified)."
        elif len(skills) >= 4:
            return f"Good technical foundation with {len(skills)} relevant skills."
        else:
            return f"Basic skill coverage ({len(skills)} skills) - may need additional training."

    def _check_industry_alignment(self, content_lower, job_lower):
        """Check for industry-specific alignment"""
        industries = {
            'fintech': ['fintech', 'financial technology', 'payments', 'banking', 'trading'],
            'healthcare': ['healthcare', 'medical', 'clinical', 'hospital', 'pharmaceutical'],
            'e-commerce': ['e-commerce', 'retail', 'marketplace', 'shopping', 'consumer'],
            'enterprise': ['enterprise', 'b2b', 'saas', 'corporate', 'business software'],
            'startup': ['startup', 'early stage', 'seed', 'series a', 'venture']
        }

        for industry, terms in industries.items():
            job_has_industry = any(term in job_lower for term in terms)
            candidate_has_industry = any(term in content_lower for term in terms)

            if job_has_industry and candidate_has_industry:
                return industry

        return None

    def _generate_recommendation(self, score, analysis):
        """Generate specific recommendation based on analysis"""
        if score >= 85:
            return "Fast-track to final interview. Exceptional fit for immediate hire consideration."
        elif score >= 75:
            return "Schedule technical interview. Strong candidate likely to succeed in role."
        elif score >= 65:
            return "Proceed with phone screening. Good potential with some skill gaps to assess."
        elif score >= 50:
            if len(analysis['strengths']) >= 3:
                return "Consider for junior version of role or with mentorship program."
            else:
                return "Marginal fit - consider only if candidate pool is limited."
        else:
            return "Not recommended for this position. Significant training would be required."

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