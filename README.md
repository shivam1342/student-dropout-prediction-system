# EduCare - Intelligent Dropout Prediction and Counselling System

## Project Overview
A comprehensive AI-powered Flask web application that predicts student dropout risk using machine learning, provides automated counselling recommendations, real-time alerts, gamification features, and intervention tracking to improve student retention rates and engagement.

## ✨ Key Features

### Core Features (Original)
- 🎯 **Dropout Risk Prediction**: ML-powered prediction with 84%+ accuracy
- 👨‍🎓 **Student Management**: Complete CRUD operations for student records
- 📊 **Interactive Dashboard**: Real-time analytics and visualizations
- 🤖 **AI Chatbot**: Automated student support and guidance
- 💡 **Counselling System**: Intelligent recommendation engine
- 🔍 **Explainable AI**: SHAP-based feature importance analysis

### ✨ Advanced Features (EduCare Enhancement - Phase 1)
- 🚨 **Real-Time Alert System**: Automated early warning system with multi-dimensional checks
  - Academic performance monitoring
  - Financial status tracking
  - Behavioral indicators
  - LMS engagement analysis
  - Dropout risk alerts
  
- 🎮 **Gamification System**: Boost student motivation and engagement
  - Points system (4 categories)
  - Level progression
  - 8 predefined badges
  - Attendance & submission streaks
  - Leaderboards
  - Custom challenges
  
- 🩺 **Intervention Management**: Track support services and measure effectiveness
  - Create interventions from alerts
  - Schedule and assign to counsellors
  - Record outcomes with ratings
  - Follow-up tracking
  - Statistics dashboard
  
- 📈 **Multi-Modal Data Tracking**: Comprehensive student monitoring
  - LMS activity (logins, submissions, forum posts, video watch time)
  - Behavioral data (attendance, participation, timeliness)
  - Social indicators (peer interaction, mentor meetings)
  - Psychological indicators (stress, motivation, confidence)

## Technology Stack
- **Backend**: Flask 3.0.0, SQLAlchemy 2.0.23
- **Database**: PostgreSQL 17.6
- **ML/AI**: scikit-learn 1.3.2, SHAP 0.41.0
- **Frontend**: HTML5, CSS3, Bootstrap 5, Chart.js
- **Data Processing**: pandas 2.1.3, numpy 1.26.2

## Project Structure
```
capstone/
│
├── app.py                      # Main application entry point
├── config.py                   # Configuration management
├── extensions.py               # Flask extensions
├── requirements.txt            # Python dependencies
├── dataset.csv                # Training dataset
│
├── controllers/                # Business logic layer
│   ├── chatbot_controller.py
│   ├── counselling_controller.py
│   ├── data_controller.py
│   ├── prediction_controller.py
│   ├── db_utils.py
│   ├── alert_controller.py         # ✨ Alert generation & management
│   ├── gamification_controller.py  # ✨ Points, badges, streaks
│   └── intervention_controller.py  # ✨ Intervention management
│
├── models/                     # Database models (ORM)
│   ├── __init__.py
│   ├── student.py              # Student model
│   ├── risk_prediction.py      # Risk prediction model
│   ├── counselling_log.py      # Counselling log model
│   ├── lms_activity.py         # ✨ LMS engagement tracking
│   ├── behavioral_data.py      # ✨ Behavioral/psychological indicators
│   ├── alert.py                # ✨ Real-time alert system
│   ├── intervention.py         # ✨ Intervention tracking
│   └── gamification.py         # ✨ Gamification profiles
│
├── routes/                     # API endpoints & views
│   ├── main_routes.py
│   ├── student_routes.py
│   ├── api_routes.py
│   ├── counselling_routes.py
│   └── favicon_routes.py
│
├── ml/                         # Machine learning components
│   ├── model.pkl
│   └── train_model.py
│
├── static/                     # Static assets
│   ├── css/
│   ├── js/
│   └── images/
│
└── templates/                  # HTML templates
    ├── layout.html
    ├── index.html
    ├── students.html
    ├── student_form.html
    ├── student_profile.html
    ├── counselling.html
    ├── chatbot.html
    └── about.html
```

## Installation

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
   ```bash
   cd capstone
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   Create `.env` file in the root directory:
   ```env
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=student_counselling_db
   SECRET_KEY=your-secret-key-here
   ```

5. **Setup database**
   ```bash
   # Create PostgreSQL database
   createdb student_counselling_db
   
   # Initialize tables
   set FLASK_APP=app.py
   flask db-create
   
   # Seed sample data
   flask seed-db
   ```

6. **Train ML model**
   ```bash
   python ml/train_model.py
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

Visit `http://localhost:5000` in your browser.

## Usage

### Dashboard
- View overall student statistics
- Monitor risk trends and patterns
- Identify high-risk students requiring intervention

### Student Management
- Add new student records
- Update existing information
- View detailed student profiles
- Delete student records

### Risk Prediction
- Generate dropout risk predictions
- View feature importance analysis
- Access personalized recommendations

### Counselling Interface
- Review high-risk students
- Access automated intervention recommendations
- Track counselling activities

### AI Chatbot
- Interactive student support
- Academic guidance
- Resource information

## Machine Learning Model

- **Algorithm**: Random Forest Classifier
- **Accuracy**: ~84.6%
- **Features**: 8 key predictors
  - Age at enrollment
  - Previous qualification
  - Scholarship holder status
  - Debtor status
  - Tuition fees status
  - 1st semester grades
  - 2nd semester grades
  - GDP indicator

- **Risk Categories**:
  - Low: < 40%
  - Medium: 40% - 70%
  - High: > 70%

## API Endpoints

### Student Routes
- `GET /students/` - List all students
- `GET /students/<id>` - View student profile
- `POST /students/add` - Add new student
- `POST /students/edit/<id>` - Update student
- `POST /students/delete/<id>` - Delete student

### API Routes
- `POST /api/predict/<student_id>` - Generate risk prediction
- `POST /api/chatbot` - Chatbot interaction

### Counselling Routes
- `GET /counselling/` - View counselling dashboard

## Development

### Running in Development Mode
```bash
set FLASK_ENV=development
python app.py
```

### Running in Production Mode
```bash
set FLASK_ENV=production
python app.py
```

## Database Schema

### Students Table
- Personal information
- Academic records
- Financial status
- Enrollment details

### Risk Predictions Table
- Prediction scores
- Risk categories
- Top contributing features
- Prediction timestamps

### Counselling Logs Table
- Intervention types
- Recommendations
- Status tracking
- Counsellor notes

## Security Considerations
- Environment-based configuration
- SQL injection protection via ORM
- Session management
- Input validation

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is for educational purposes.

## Contact & Support
For questions and support, please contact the development team.

---
**Developed as part of AI-Based Student Support Systems Initiative**
