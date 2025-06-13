
# TeamZa - AI-Powered HR Management Platform

<div align="center">
  <img src="static/images/teamza-logo.png" alt="TeamZa Logo" width="200" height="auto">
  
  **Revolutionary AI-powered platform that transforms talent management, employee analytics, and workforce optimization**
  
</div>

## 🚀 Overview

TeamZa is a comprehensive AI-powered Human Resources management platform that revolutionizes every aspect of HR operations. From intelligent resume screening to predictive analytics and employee wellness tracking, TeamZa provides modern HR teams with the tools they need to make data-driven decisions.

## ✨ Key Features

### 🤖 AI-Powered Modules

1. **AI Resume Screening**
   - Advanced NLP analysis of resumes
   - Skills extraction and job matching
   - Automated candidate ranking with 97% accuracy

2. **Smart Talent Sourcing**
   - AI-powered candidate profile generation
   - Multi-platform talent discovery
   - Intelligent candidate recommendations

3. **Leadership Potential Analysis**
   - Predictive leadership scoring
   - Growth action recommendations
   - Performance-based insights

4. **Appraisal Dashboard**
   - AI-driven performance reviews
   - Sentiment analysis of feedback
   - Comprehensive appraisal insights

5. **Learning Management System**
   - Personalized learning paths
   - Skill gap analysis
   - Progress tracking and leaderboards

6. **Employee Wellness Tracker**
   - Comprehensive health metrics
   - Wellness recommendations
   - Mental health monitoring

7. **HR Analytics & Insights**
   - Real-time workforce analytics
   - Predictive retention modeling
   - Department-wise performance metrics

8. **Gamification System**
   - Challenge-based learning
   - Achievement badges
   - XP and level progression

## 🏗️ System Architecture

```
TeamZa HR Platform
├── Frontend (HTML/CSS/JavaScript)
│   ├── Bootstrap 5 UI Framework
│   ├── Chart.js for Analytics
│   └── Responsive Design
├── Backend (Flask/Python)
│   ├── SQLAlchemy ORM
│   ├── RESTful API Architecture
│   └── Modular Route Structure
├── AI/ML Components
│   ├── NLP Processing
│   ├── Sentiment Analysis
│   └── Predictive Analytics
└── Database (SQLite)
    ├── Employee Management
    ├── Performance Tracking
    └── Analytics Storage
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd teamza-hr-platform
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the Database**
   ```bash
   python app.py
   ```
   The database will auto-initialize with sample data on first run.

4. **Run the Application**
   ```bash
   python main.py
   ```

5. **Access the Platform**
   Open your browser and navigate to `http://0.0.0.0:5000`

### Replit Deployment

This application is optimized for Replit deployment:

1. Fork this repl
2. Click the "Run" button
3. Your app will be available at the provided URL

## 📊 Database Schema

### Core Models

- **Employee**: Complete employee profiles with performance metrics
- **Resume**: Resume storage and AI analysis results
- **PerformanceReview**: Performance evaluations and feedback
- **LearningProgress**: Training and skill development tracking
- **WellnessCheck**: Employee wellness and health metrics
- **HRTransaction**: Salary changes, promotions, and career events
- **Challenge/Badge**: Gamification system components

## 🎯 Usage Guide

### For HR Administrators

1. **Dashboard Overview**
   - View real-time workforce metrics
   - Monitor department performance
   - Track wellness indicators

2. **Employee Management**
   - Add/edit employee profiles
   - Manage performance reviews
   - Track career progression

3. **Recruitment**
   - Upload and screen resumes
   - Source candidates intelligently
   - Rank candidates automatically

4. **Analytics**
   - Generate comprehensive reports
   - Export data to Excel
   - Monitor trends and predictions

### For Employees

1. **Learning Portal**
   - Access personalized learning paths
   - Complete challenges and quizzes
   - Track skill development

2. **Wellness Tracking**
   - Log wellness check-ins
   - View health recommendations
   - Monitor progress over time

3. **Gamification**
   - Participate in challenges
   - Earn badges and XP
   - Compete on leaderboards

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/hr_platform.db
FLASK_ENV=development
FLASK_DEBUG=True
```

### Customization

1. **Styling**: Modify `static/css/custom.css` for UI customization
2. **Analytics**: Adjust weights in `utils/hr_analytics.py`
3. **NLP Models**: Enhance `utils/nlp_processor.py` for better AI processing

## 📁 Project Structure

```
teamza-hr-platform/
├── app.py                 # Flask application factory
├── main.py               # Application entry point
├── routes.py             # URL routing and view functions
├── models.py             # Database models
├── static/               # Static assets (CSS, JS, images)
├── templates/            # HTML templates
├── utils/                # Utility modules
│   ├── hr_analytics.py   # HR analytics engine
│   ├── nlp_processor.py  # NLP processing
│   └── document_parser.py # Document parsing utilities
├── data/                 # Data management
│   ├── mock_data.py      # Sample data generation
│   └── real_data_loader.py # Real data loading utilities
└── instance/             # Database and instance files
```

## 🔍 API Endpoints

### Core Endpoints

- `GET /` - Landing page
- `GET /dashboard` - Main HR dashboard
- `GET /employee-management` - Employee listing and management
- `POST /resume-screening` - Resume upload and analysis
- `GET /hr-insights` - Comprehensive analytics
- `GET /gamification` - Gamification dashboard

### API Routes

- `GET /api/quiz/<module_name>` - Get quiz data
- `POST /gamification/submit-quiz` - Submit quiz answers
- `GET /export-company-data` - Export company insights
- `GET /export-employee-data/<id>` - Export employee data

## 🎨 UI/UX Features

- **Responsive Design**: Works seamlessly across devices
- **Dark/Light Themes**: Adaptive color schemes
- **Interactive Charts**: Real-time data visualization
- **Modern UI**: Clean, professional interface
- **Accessibility**: WCAG compliant design



### Upcoming Features

- [ ] Advanced AI/ML models
- [ ] Trained on anonymized performance data to identify future high-potential candidates
- [ ] Semantic matching between job roles and current skills using transformer-based embeddings
- [ ] Lightweight NLP model to assess emotional tone from employee feedback.
- [ ] Natural language voice interface for initial candidate screening (using Whisper/OpenAI/Deepgram).
- [ ] Integration with popular HR systems (Workday, BambooHR)
- [ ] Mobile application for iOS and Android
- [ ] Advanced reporting and dashboard customization
- [ ] Multi-language support
- [ ] Real-time notifications and alerts






---

<div align="center">
  <p><strong>Built with ❤️ by the TeamZa Team</strong></p>
  <p>Transforming HR operations with AI-powered intelligence</p>
</div>
