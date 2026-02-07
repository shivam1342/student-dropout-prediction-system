================================================================================
                    EDUCARE PROJECT - COMPLETE CONCEPTS GUIDE
                    Everything You Need to Know with Examples
================================================================================

TABLE OF CONTENTS
=================
1. FLASK FRAMEWORK CONCEPTS
2. DATABASE & ORM CONCEPTS (SQLAlchemy)
3. MACHINE LEARNING CONCEPTS
4. SOFTWARE ARCHITECTURE PATTERNS
5. WEB DEVELOPMENT CONCEPTS
6. PYTHON ADVANCED CONCEPTS
7. API & REST CONCEPTS
8. TESTING CONCEPTS
9. DEPLOYMENT & CONFIGURATION
10. DOMAIN-SPECIFIC CONCEPTS

================================================================================
                        1. FLASK FRAMEWORK CONCEPTS
================================================================================

1.1 APPLICATION FACTORY PATTERN
--------------------------------
WHAT: A design pattern where you create your Flask app inside a function
WHY: Allows creating multiple instances for testing, different configs

IMPLEMENTATION IN PROJECT:
```python
# app.py
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from routes.main_routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

# Usage:
app = create_app('development')  # For dev
app = create_app('testing')      # For tests
app = create_app('production')   # For prod
```

REAL-WORLD ANALOGY:
Like a car factory - same blueprint, different configurations (sedan, SUV, truck)


1.2 BLUEPRINTS
--------------
WHAT: Modular components that group related routes together
WHY: Organize large applications, reusable components

IMPLEMENTATION:
```python
# routes/student_routes.py
from flask import Blueprint

student_bp = Blueprint('student', __name__, url_prefix='/students')

@student_bp.route('/')
def list_students():
    return "All students"

@student_bp.route('/<int:id>')
def student_detail(id):
    return f"Student {id}"

# Registered in app.py:
app.register_blueprint(student_bp)

# URLs become:
# /students/          -> list_students()
# /students/123       -> student_detail(123)
```

PROJECT BLUEPRINTS:
- main_bp: Dashboard, home (/)
- student_bp: Student management (/students)
- alert_bp: Alert system (/alerts)
- prediction_bp: ML predictions (/predict)
- intervention_bp: Support actions (/interventions)
- gamification_bp: Points & badges (/gamification)
- chatbot_bp: AI chatbot (/chatbot)

REAL-WORLD ANALOGY:
Like departments in a company - HR, Finance, IT - each handles its own area


1.3 ROUTES & VIEW FUNCTIONS
----------------------------
WHAT: URL patterns mapped to Python functions
WHY: Connect URLs to code that handles requests

TYPES OF ROUTES:

A. Static Routes:
```python
@main_bp.route('/')
def home():
    return "Welcome"
# URL: http://localhost:5000/
```

B. Dynamic Routes:
```python
@student_bp.route('/<int:student_id>')
def profile(student_id):
    student = Student.query.get(student_id)
    return render_template('profile.html', student=student)
# URL: http://localhost:5000/students/42
```

C. HTTP Methods:
```python
@student_bp.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # Save data
        return redirect(url_for('student.list_students'))
    # Show form
    return render_template('add_student.html')
```

PROJECT EXAMPLE:
```python
# routes/student_routes.py line 15-30
@student_bp.route('/<int:student_id>')
def student_profile(student_id):
    # 1. Fetch student from database
    student = Student.query.get_or_404(student_id)
    
    # 2. Get related data
    alerts = Alert.query.filter_by(student_id=student_id).all()
    gamification = GamificationProfile.query.filter_by(student_id=student_id).first()
    
    # 3. Render template with data
    return render_template('student_profile.html',
                         student=student,
                         alerts=alerts,
                         gamification=gamification)
```


1.4 REQUEST & RESPONSE OBJECTS
-------------------------------
WHAT: Objects containing HTTP request/response data
WHY: Access form data, JSON, headers, cookies

REQUEST OBJECT:
```python
from flask import request

@app.route('/login', methods=['POST'])
def login():
    # Form data
    username = request.form.get('username')
    password = request.form.get('password')
    
    # JSON data
    data = request.get_json()
    username = data['username']
    
    # Query parameters (?key=value)
    page = request.args.get('page', 1, type=int)
    
    # Headers
    token = request.headers.get('Authorization')
    
    # Files
    file = request.files['resume']
```

RESPONSE TYPES:
```python
from flask import jsonify, render_template, redirect, url_for

# 1. HTML Response
return render_template('page.html', data=data)

# 2. JSON Response (APIs)
return jsonify({'status': 'success', 'data': data})

# 3. Redirect
return redirect(url_for('student.profile', student_id=123))

# 4. Custom Response
response = make_response(render_template('page.html'))
response.set_cookie('session_id', '123')
return response
```

PROJECT EXAMPLE (routes/main_routes.py):
```python
@main_bp.route('/dashboard')
def dashboard():
    # Query database
    total_students = Student.query.count()
    high_risk = RiskPrediction.query.filter_by(risk_category='High').count()
    
    # Pass to template
    return render_template('index.html',
                         total_students=total_students,
                         high_risk=high_risk)
```


1.5 TEMPLATE RENDERING (JINJA2)
--------------------------------
WHAT: Server-side HTML generation with Python data
WHY: Dynamic web pages without writing JavaScript for everything

JINJA2 SYNTAX:

A. Variables:
```html
<h1>Welcome {{ student.name }}</h1>
<p>Email: {{ student.email }}</p>
```

B. Control Flow:
```html
{% if student.risk_category == 'High' %}
    <span class="badge-danger">High Risk</span>
{% elif student.risk_category == 'Medium' %}
    <span class="badge-warning">Medium Risk</span>
{% else %}
    <span class="badge-success">Low Risk</span>
{% endif %}
```

C. Loops:
```html
<ul>
{% for alert in alerts %}
    <li class="alert-{{ alert.severity }}">{{ alert.title }}</li>
{% endfor %}
</ul>
```

D. Filters:
```html
<p>Created: {{ alert.created_at|datetime }}</p>
<p>Risk: {{ risk_score|round(2) }}%</p>
<p>Name: {{ student.name|upper }}</p>
```

PROJECT EXAMPLE (templates/student_profile.html):
```html
<div class="student-header">
    <h1>{{ student.name }}</h1>
    <span class="badge-{{ 'danger' if student.risk_score > 0.7 else 'success' }}">
        Risk: {{ (student.risk_score * 100)|round(1) }}%
    </span>
</div>

<div class="alerts">
    {% for alert in alerts %}
        <div class="alert alert-{{ alert.severity.lower() }}">
            <strong>{{ alert.alert_type }}</strong>: {{ alert.description }}
            <span class="date">{{ alert.created_at|datetime }}</span>
        </div>
    {% endfor %}
</div>
```

E. Template Inheritance:
```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}EduCare{% endblock %}</title>
</head>
<body>
    <nav>...</nav>
    {% block content %}{% endblock %}
    <footer>...</footer>
</body>
</html>

<!-- student_profile.html -->
{% extends "base.html" %}

{% block title %}{{ student.name }} - Profile{% endblock %}

{% block content %}
    <div class="profile">
        <!-- Student details here -->
    </div>
{% endblock %}
```


1.6 FLASK EXTENSIONS
--------------------
WHAT: Third-party packages that extend Flask functionality
WHY: Don't reinvent the wheel

PROJECT EXTENSIONS:

A. Flask-SQLAlchemy (Database ORM):
```python
# extensions.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# app.py
db.init_app(app)
```

B. Flask-Migrate (Database Migrations):
```python
from flask_migrate import Migrate
migrate = Migrate(app, db)

# Command line:
flask db init                # Initialize migrations
flask db migrate -m "Add alerts table"  # Create migration
flask db upgrade             # Apply migration
```

C. Flask-CORS (Cross-Origin Resource Sharing):
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```


1.7 FLASK CONTEXT
-----------------
WHAT: Special variables available during request processing
WHY: Access app/request data from anywhere

TYPES:

A. Application Context:
```python
from flask import current_app

# Access config
db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
```

B. Request Context:
```python
from flask import request, g

# g: request-global storage
@app.before_request
def before_request():
    g.user = get_current_user()

@app.route('/profile')
def profile():
    return f"Welcome {g.user.name}"
```

C. Context Processors:
```python
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Now 'now' available in all templates:
# <p>Current time: {{ now }}</p>
```


================================================================================
                    2. DATABASE & ORM CONCEPTS (SQLAlchemy)
================================================================================

2.1 ORM (Object-Relational Mapping)
------------------------------------
WHAT: Maps database tables to Python classes
WHY: Write Python instead of SQL, type safety, easier maintenance

TRADITIONAL SQL VS ORM:

SQL:
```sql
SELECT * FROM students WHERE id = 1;
INSERT INTO students (name, email) VALUES ('John', 'john@edu.com');
UPDATE students SET email = 'new@edu.com' WHERE id = 1;
DELETE FROM students WHERE id = 1;
```

ORM:
```python
student = Student.query.get(1)
student = Student(name='John', email='john@edu.com')
db.session.add(student)
db.session.commit()

student = Student.query.get(1)
student.email = 'new@edu.com'
db.session.commit()

student = Student.query.get(1)
db.session.delete(student)
db.session.commit()
```


2.2 MODEL DEFINITION
--------------------
WHAT: Python class representing a database table
WHY: Define structure once, use everywhere

BASIC MODEL:
```python
from extensions import db

class Student(db.Model):
    __tablename__ = 'students'  # Optional: defaults to lowercase class name
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Required fields
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    # Optional fields
    age = db.Column(db.Integer)
    
    # Default values
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Indexes for faster queries
    __table_args__ = (
        db.Index('idx_email', 'email'),
    )
```

PROJECT MODEL (models/student.py):
```python
class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    # Academic fields
    curricular_units_1st_sem_enrolled = db.Column(db.Integer)
    curricular_units_1st_sem_grade = db.Column(db.Float)
    
    # Financial fields
    tuition_fees_up_to_date = db.Column(db.Boolean)
    debtor = db.Column(db.Boolean)
    
    # Status
    target = db.Column(db.Integer)  # 0=Enrolled, 1=Dropout, 2=Graduate
    
    # Relationships (explained in section 2.3)
    alerts = db.relationship('Alert', backref='student', lazy='dynamic')
    predictions = db.relationship('RiskPrediction', backref='student', lazy=True)
```


2.3 RELATIONSHIPS
-----------------
WHAT: Connections between tables
WHY: Model real-world associations

TYPES:

A. ONE-TO-MANY (Most Common):
```python
# One student has many alerts
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alerts = db.relationship('Alert', backref='student', lazy='dynamic')

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    
# Usage:
student = Student.query.get(1)
alerts = student.alerts.all()  # Get all alerts for this student

alert = Alert.query.get(1)
student = alert.student  # Get the student for this alert (via backref)
```

B. ONE-TO-ONE:
```python
# One student has one gamification profile
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gamification = db.relationship('GamificationProfile', 
                                  uselist=False,  # One-to-one
                                  backref='student')

class GamificationProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), unique=True)
    total_points = db.Column(db.Integer, default=0)

# Usage:
student = Student.query.get(1)
points = student.gamification.total_points
```

C. MANY-TO-MANY (Association Table):
```python
# Many students, many courses
student_courses = db.Table('student_courses',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courses = db.relationship('Course', secondary=student_courses, 
                            backref='students')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

# Usage:
student = Student.query.get(1)
student.courses.append(course)
db.session.commit()

course = Course.query.get(1)
enrolled_students = course.students  # All students in this course
```

RELATIONSHIP PARAMETERS:

- backref: Creates reverse relationship
- lazy='dynamic': Returns query object (for filtering)
- lazy='select': Loads data when accessed (default)
- lazy='joined': Loads with JOIN
- cascade='all,delete-orphan': Delete children when parent deleted


2.4 QUERYING
------------
WHAT: Retrieving data from database
WHY: Flexible, powerful data access

QUERY METHODS:

A. Basic Queries:
```python
# Get all
students = Student.query.all()

# Get one by primary key
student = Student.query.get(1)
student = Student.query.get_or_404(1)  # Raises 404 if not found

# Get first match
student = Student.query.first()
```

B. Filtering:
```python
# Simple filter
students = Student.query.filter_by(age=20).all()
students = Student.query.filter_by(is_active=True, age=20).all()

# Complex filter (using SQLAlchemy operators)
from sqlalchemy import and_, or_

students = Student.query.filter(Student.age > 18).all()
students = Student.query.filter(Student.age.between(18, 25)).all()
students = Student.query.filter(Student.name.like('%John%')).all()

# Multiple conditions
students = Student.query.filter(
    and_(
        Student.age > 18,
        Student.is_active == True
    )
).all()

students = Student.query.filter(
    or_(
        Student.risk_category == 'High',
        Student.risk_category == 'Medium'
    )
).all()
```

C. Ordering:
```python
from sqlalchemy import desc, asc

# Ascending (default)
students = Student.query.order_by(Student.name).all()
students = Student.query.order_by(asc(Student.name)).all()

# Descending
students = Student.query.order_by(desc(Student.created_at)).all()

# Multiple orders
students = Student.query.order_by(
    desc(Student.risk_score),
    asc(Student.name)
).all()
```

D. Limiting:
```python
# First 10 students
students = Student.query.limit(10).all()

# Skip first 10, get next 10 (pagination)
students = Student.query.offset(10).limit(10).all()
```

E. Aggregations:
```python
# Count
total = Student.query.count()
high_risk = Student.query.filter_by(risk_category='High').count()

# Sum
from sqlalchemy import func
total_points = db.session.query(func.sum(GamificationProfile.total_points)).scalar()

# Average
avg_grade = db.session.query(func.avg(Student.curricular_units_1st_sem_grade)).scalar()

# Max/Min
max_score = db.session.query(func.max(Student.risk_score)).scalar()
```

F. Joins:
```python
# Inner join
results = db.session.query(Student, Alert).join(Alert).all()

# Left outer join
results = db.session.query(Student).outerjoin(Alert).all()

# With filter
students = db.session.query(Student).join(Alert).filter(
    Alert.severity == 'High'
).all()
```

PROJECT EXAMPLES:

```python
# From routes/main_routes.py
def dashboard():
    # Count queries
    total_students = Student.query.count()
    high_risk = RiskPrediction.query.filter_by(risk_category='High').count()
    
    # Latest alerts
    recent_alerts = Alert.query.order_by(desc(Alert.created_at)).limit(10).all()
    
    # Top performers
    top_students = GamificationProfile.query.order_by(
        desc(GamificationProfile.total_points)
    ).limit(5).all()
    
    return render_template('index.html', 
                         total=total_students,
                         high_risk=high_risk,
                         alerts=recent_alerts,
                         leaderboard=top_students)
```

```python
# From controllers/alert_controller.py
class AlertController:
    @staticmethod
    def get_student_alerts(student_id, severity=None, status='Active'):
        query = Alert.query.filter_by(student_id=student_id, status=status)
        
        if severity:
            query = query.filter_by(severity=severity)
        
        return query.order_by(desc(Alert.created_at)).all()
```


2.5 CRUD OPERATIONS
-------------------
WHAT: Create, Read, Update, Delete - basic database operations
WHY: Essential for any data-driven application

A. CREATE:
```python
# Create new record
student = Student(
    name='John Doe',
    email='john@edu.com',
    age=20
)
db.session.add(student)
db.session.commit()

# Bulk create
students = [
    Student(name='Alice', email='alice@edu.com'),
    Student(name='Bob', email='bob@edu.com')
]
db.session.add_all(students)
db.session.commit()
```

B. READ:
```python
# Single read
student = Student.query.get(1)
student = Student.query.filter_by(email='john@edu.com').first()

# Multiple reads
all_students = Student.query.all()
active_students = Student.query.filter_by(is_active=True).all()
```

C. UPDATE:
```python
# Update single field
student = Student.query.get(1)
student.email = 'newemail@edu.com'
db.session.commit()

# Update multiple fields
student.name = 'New Name'
student.age = 21
db.session.commit()

# Bulk update
Student.query.filter(Student.age < 18).update({'is_minor': True})
db.session.commit()
```

D. DELETE:
```python
# Delete single
student = Student.query.get(1)
db.session.delete(student)
db.session.commit()

# Bulk delete
Student.query.filter(Student.is_active == False).delete()
db.session.commit()
```

PROJECT EXAMPLE (from routes/student_routes.py):
```python
@student_bp.route('/add', methods=['POST'])
def add_student():
    data = request.get_json()
    
    # CREATE
    student = Student(
        name=data['name'],
        email=data['email'],
        age=data.get('age'),
        curricular_units_1st_sem_grade=data.get('grade'),
        tuition_fees_up_to_date=data.get('fees_paid', False)
    )
    
    try:
        db.session.add(student)
        db.session.commit()
        return jsonify({'message': 'Student added', 'id': student.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@student_bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    # READ
    student = Student.query.get_or_404(student_id)
    data = request.get_json()
    
    # UPDATE
    student.name = data.get('name', student.name)
    student.email = data.get('email', student.email)
    
    db.session.commit()
    return jsonify({'message': 'Student updated'})

@student_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    # READ
    student = Student.query.get_or_404(student_id)
    
    # DELETE
    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Student deleted'})
```


2.6 DATABASE SESSIONS
---------------------
WHAT: Unit of work pattern for database transactions
WHY: Group operations, rollback on errors

SESSION LIFECYCLE:
```python
# 1. Begin (implicit)
student = Student(name='John')

# 2. Add to session
db.session.add(student)

# 3. Commit (saves to database)
db.session.commit()

# 4. Rollback (undo changes if error)
try:
    db.session.add(student)
    db.session.commit()
except Exception as e:
    db.session.rollback()
    print(f"Error: {e}")
```

TRANSACTION EXAMPLE:
```python
def transfer_points(from_student_id, to_student_id, points):
    try:
        # Both operations must succeed or both fail
        from_profile = GamificationProfile.query.get(from_student_id)
        to_profile = GamificationProfile.query.get(to_student_id)
        
        from_profile.total_points -= points
        to_profile.total_points += points
        
        db.session.commit()  # Save both
    except Exception as e:
        db.session.rollback()  # Undo both
        raise e
```


2.7 MIGRATIONS
--------------
WHAT: Version control for database schema
WHY: Track changes, deploy safely, rollback if needed

WORKFLOW:
```bash
# 1. Initialize migrations (once)
flask db init

# 2. Make changes to models (e.g., add column to Student)
class Student(db.Model):
    # ... existing columns
    phone = db.Column(db.String(20))  # NEW

# 3. Generate migration
flask db migrate -m "Add phone to students"
# Creates: migrations/versions/xxx_add_phone_to_students.py

# 4. Review migration file
# migrations/versions/xxx_add_phone_to_students.py
def upgrade():
    op.add_column('students', sa.Column('phone', sa.String(20)))

def downgrade():
    op.drop_column('students', 'phone')

# 5. Apply migration
flask db upgrade

# 6. Rollback if needed
flask db downgrade
```

MIGRATION FILE EXAMPLE:
```python
"""Add risk prediction table

Revision ID: abc123
Create Date: 2024-01-15 10:30:00
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('risk_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_category', sa.String(20), nullable=False),
        sa.Column('prediction_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('risk_predictions')
```


================================================================================
                    3. MACHINE LEARNING CONCEPTS
================================================================================

3.1 SUPERVISED LEARNING
-----------------------
WHAT: Learning from labeled data (input → output pairs)
WHY: Predict outcomes based on historical data

PROJECT USE CASE: Predict student dropout based on past student data

TYPES:
- Classification: Predict category (High/Medium/Low risk)
- Regression: Predict number (risk score 0-1)

WORKFLOW:
```
Historical Data → Training → Model → New Student Data → Prediction
```


3.2 FEATURE ENGINEERING
-----------------------
WHAT: Creating input variables (features) from raw data
WHY: Better features = better predictions

PROJECT FEATURES (104 total):

A. Demographic Features:
```python
features = [
    'age',                        # Continuous: 18-65
    'gender',                     # Binary: 0/1
    'marital_status',            # Categorical: 1=Single, 2=Married, etc.
    'nacionality',               # Categorical: Country code
]
```

B. Academic Features:
```python
features = [
    'curricular_units_1st_sem_enrolled',     # Count: 0-10
    'curricular_units_1st_sem_grade',        # Average: 0-20
    'curricular_units_1st_sem_approved',     # Count: 0-10
    'curricular_units_2nd_sem_enrolled',
    'curricular_units_2nd_sem_grade',
]
```

C. Financial Features:
```python
features = [
    'tuition_fees_up_to_date',   # Binary: 0=No, 1=Yes
    'debtor',                     # Binary: 0=No, 1=Yes
    'scholarship_holder',         # Binary: 0=No, 1=Yes
]
```

D. Behavioral Features (Custom):
```python
features = [
    'stress_level',              # Scale: 1-10
    'motivation_level',          # Scale: 1-10
    'social_integration',        # Scale: 1-10
]
```

E. LMS Features:
```python
features = [
    'login_frequency',           # Count per week
    'avg_time_on_platform',      # Minutes per session
    'assignment_submissions',    # Percentage: 0-100
]
```

FEATURE TRANSFORMATION:
```python
# ml/train_advanced_models.py line 50-80

# 1. Handle missing values
X = X.fillna(X.mean())  # Replace NaN with column mean

# 2. Encode categorical variables
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
X['marital_status'] = le.fit_transform(X['marital_status'])

# 3. Scale features (for neural networks)
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. Feature selection (remove low-importance features)
from sklearn.feature_selection import SelectKBest
selector = SelectKBest(k=50)
X_selected = selector.fit_transform(X, y)
```


3.3 TRAIN-TEST SPLIT
--------------------
WHAT: Divide data into training set (80%) and testing set (20%)
WHY: Evaluate model on unseen data to prevent overfitting

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,           # Features
    y,           # Labels (dropout or not)
    test_size=0.2,    # 20% for testing
    random_state=42,  # Reproducible split
    stratify=y        # Maintain class distribution
)

# Example:
# Total: 1000 students (700 enrolled, 300 dropout)
# Training: 800 students (560 enrolled, 240 dropout)
# Testing: 200 students (140 enrolled, 60 dropout)
```

PROJECT IMPLEMENTATION (ml/train_advanced_models.py line 90-95):
```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```


3.4 CLASSIFICATION ALGORITHMS
-----------------------------
WHAT: Algorithms that predict categories
WHY: Different algorithms for different data patterns

PROJECT USES 4 ALGORITHMS:

A. RANDOM FOREST:
```python
from sklearn.ensemble import RandomForestClassifier

# What it does: Creates many decision trees, combines their votes
# Analogy: Ask 100 experts, majority vote wins

rf_model = RandomForestClassifier(
    n_estimators=200,      # 200 trees
    max_depth=15,          # Max tree depth
    min_samples_split=5,   # Min samples to split node
    random_state=42
)

rf_model.fit(X_train, y_train)
predictions = rf_model.predict(X_test)

# Pros: Robust, handles non-linear data, feature importance
# Cons: Slow on large datasets, not interpretable
```

DECISION TREE EXAMPLE:
```
                    Grade < 12?
                   /            \
                Yes              No
               /                  \
        Fees Paid?            Age < 22?
         /      \              /      \
       Yes      No           Yes      No
        |        |            |        |
    Low Risk  High Risk  Medium Risk Low Risk
```

B. GRADIENT BOOSTING:
```python
from sklearn.ensemble import GradientBoostingClassifier

# What it does: Builds trees sequentially, each fixing errors of previous
# Analogy: Student learns from mistakes, improves gradually

gb_model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,    # How much to adjust per iteration
    max_depth=5,
    subsample=0.8,         # Use 80% of data per tree
    random_state=42
)

gb_model.fit(X_train, y_train)

# Pros: Very accurate, handles complex patterns
# Cons: Slow training, can overfit
```

SEQUENTIAL LEARNING:
```
Tree 1: Predicts, makes errors
Tree 2: Focuses on Tree 1's errors
Tree 3: Focuses on Tree 2's errors
...
Final Prediction = Sum(all trees with weights)
```

C. NEURAL NETWORK:
```python
from sklearn.neural_network import MLPClassifier

# What it does: Mimics brain neurons, learns complex patterns
# Analogy: Brain with neurons processing information

nn_model = MLPClassifier(
    hidden_layer_sizes=(128, 64, 32),  # 3 layers: 128→64→32 neurons
    activation='relu',                  # Activation function
    solver='adam',                      # Optimization algorithm
    alpha=0.001,                        # Regularization
    batch_size=32,                      # Samples per update
    learning_rate_init=0.001,
    max_iter=500,
    early_stopping=True,
    random_state=42
)

# Requires scaled data
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

nn_model.fit(X_train_scaled, y_train)

# Pros: Captures complex non-linear patterns
# Cons: Requires more data, slow training, "black box"
```

NEURAL NETWORK ARCHITECTURE:
```
Input Layer (104 features)
    ↓
Hidden Layer 1 (128 neurons) → ReLU activation
    ↓
Hidden Layer 2 (64 neurons) → ReLU activation
    ↓
Hidden Layer 3 (32 neurons) → ReLU activation
    ↓
Output Layer (2 neurons: Dropout/Enrolled) → Softmax
```

D. ENSEMBLE (VOTING):
```python
from sklearn.ensemble import VotingClassifier

# What it does: Combines predictions from multiple models
# Analogy: Committee of experts voting on decision

ensemble_model = VotingClassifier(
    estimators=[
        ('rf', rf_model),
        ('gb', gb_model),
        ('nn', nn_model)
    ],
    voting='soft',  # Use probability averages
    weights=[1, 1, 1]  # Equal weight
)

ensemble_model.fit(X_train, y_train)

# Example:
# RF predicts: 70% dropout
# GB predicts: 65% dropout
# NN predicts: 80% dropout
# Ensemble: (70 + 65 + 80) / 3 = 71.67% dropout

# Pros: Best accuracy, reduces individual model errors
# Cons: Slower, more memory
```


3.5 MODEL EVALUATION
--------------------
WHAT: Metrics to measure model performance
WHY: Choose best model, identify weaknesses

A. CONFUSION MATRIX:
```python
from sklearn.metrics import confusion_matrix

#                  Predicted
#              Enrolled  Dropout
# Actual 
# Enrolled        85       15      (True Neg, False Pos)
# Dropout         10       90      (False Neg, True Pos)

cm = confusion_matrix(y_test, predictions)
```

B. ACCURACY:
```python
from sklearn.metrics import accuracy_score

accuracy = accuracy_score(y_test, predictions)
# (85 + 90) / 200 = 0.875 = 87.5%

# Problem: Misleading if classes imbalanced
# E.g., 95% enrolled, 5% dropout
# Model predicting "always enrolled" = 95% accuracy!
```

C. PRECISION, RECALL, F1-SCORE:
```python
from sklearn.metrics import classification_report

print(classification_report(y_test, predictions))

#               precision  recall  f1-score  support
# Enrolled         0.89     0.85     0.87      100
# Dropout          0.86     0.90     0.88      100

# Precision: Of predictions, how many correct?
#   Dropout Precision = 90 / (90 + 15) = 85.7%
#   "When model says dropout, it's right 85.7% of time"

# Recall: Of actual cases, how many found?
#   Dropout Recall = 90 / (90 + 10) = 90%
#   "Model catches 90% of actual dropouts"

# F1-Score: Harmonic mean of precision & recall
#   F1 = 2 * (0.857 * 0.90) / (0.857 + 0.90) = 0.878
```

D. ROC-AUC:
```python
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib.pyplot as plt

# Get probability predictions
y_proba = model.predict_proba(X_test)[:, 1]  # Dropout probability

# Calculate AUC
auc = roc_auc_score(y_test, y_proba)
# 0.5 = Random guessing, 1.0 = Perfect

# Plot ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_proba)
plt.plot(fpr, tpr, label=f'AUC = {auc:.3f}')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
plt.show()
```

PROJECT EVALUATION (ml/train_advanced_models.py line 200-250):
```python
def evaluate_model(model, X_test, y_test, model_name):
    predictions = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, predictions)
    auc = roc_auc_score(y_test, y_proba)
    
    print(f"\n{model_name} Performance:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"AUC Score: {auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))
    
    return {
        'model_name': model_name,
        'accuracy': accuracy,
        'auc': auc
    }

# Compare all models
results = []
for name, model in models.items():
    result = evaluate_model(model, X_test, y_test, name)
    results.append(result)

# Select best
best_model = max(results, key=lambda x: x['auc'])
print(f"\nBest Model: {best_model['model_name']}")
```


3.6 MODEL PERSISTENCE
---------------------
WHAT: Save trained model to disk, load later
WHY: Don't retrain every time, deploy to production

```python
import pickle
import joblib

# Save model (pickle)
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Load model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Save model (joblib - better for sklearn)
joblib.dump(model, 'model.pkl')
model = joblib.load('model.pkl')

# Save multiple objects
save_dict = {
    'model': ensemble_model,
    'scaler': scaler,
    'feature_names': feature_names
}
joblib.dump(save_dict, 'model_bundle.pkl')
```

PROJECT IMPLEMENTATION (ml/train_advanced_models.py line 300-320):
```python
# Save best model
best_model_name = 'ensemble'
best_model = models[best_model_name]

save_data = {
    'model': best_model,
    'scaler': scaler,
    'feature_columns': X.columns.tolist(),
    'model_name': best_model_name,
    'accuracy': best_accuracy,
    'auc': best_auc
}

joblib.dump(save_data, 'ml/model.pkl')
print("✅ Model saved to ml/model.pkl")

# Later in controllers/prediction_controller_advanced.py
model_data = joblib.load('ml/model.pkl')
model = model_data['model']
scaler = model_data['scaler']
feature_columns = model_data['feature_columns']
```


3.7 EXPLAINABLE AI (SHAP)
-------------------------
WHAT: Explain why model made a prediction
WHY: Trust, debugging, regulatory compliance

SHAP (SHapley Additive exPlanations):
```python
import shap

# Create explainer
explainer = shap.TreeExplainer(model)

# Get SHAP values for a prediction
student_data = X_test.iloc[0].values.reshape(1, -1)
shap_values = explainer.shap_values(student_data)

# SHAP value = feature's contribution to prediction
# Positive SHAP = increases dropout risk
# Negative SHAP = decreases dropout risk

# Example output:
# curricular_units_1st_sem_grade: -0.23  (lower grade → higher risk)
# debtor: +0.18                           (being debtor → higher risk)
# tuition_fees_up_to_date: -0.15         (paid fees → lower risk)
```

PROJECT IMPLEMENTATION (controllers/prediction_controller_advanced.py):
```python
def get_feature_contributions(student_data, model, feature_names):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(student_data)
    
    # Get SHAP values for dropout class
    if isinstance(shap_values, list):
        shap_values = shap_values[1]  # Dropout class
    
    # Combine feature names with SHAP values
    contributions = list(zip(feature_names, shap_values[0]))
    
    # Sort by absolute contribution
    contributions.sort(key=lambda x: abs(x[1]), reverse=True)
    
    # Return top 5 factors
    top_factors = [
        {
            'feature': name,
            'contribution': float(value),
            'impact': 'Increases Risk' if value > 0 else 'Decreases Risk'
        }
        for name, value in contributions[:5]
    ]
    
    return top_factors

# Usage in prediction:
prediction = model.predict_proba(student_features)[0][1]
factors = get_feature_contributions(student_features, model, feature_names)

# Response:
{
    'risk_score': 0.78,
    'risk_category': 'High',
    'top_factors': [
        {
            'feature': 'curricular_units_1st_sem_grade',
            'contribution': -0.23,
            'impact': 'Decreases Risk',
            'description': 'Low grades increase dropout risk'
        },
        {
            'feature': 'debtor',
            'contribution': 0.18,
            'impact': 'Increases Risk',
            'description': 'Outstanding debts increase dropout risk'
        }
    ]
}
```


3.8 PREDICTION PIPELINE
-----------------------
WHAT: Complete flow from raw data to prediction
WHY: Standardize prediction process

PROJECT PIPELINE (controllers/prediction_controller_advanced.py):
```python
class MLModelManager:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.load_all_models()
    
    def load_all_models(self):
        """Load all trained models"""
        model_files = ['random_forest', 'gradient_boosting', 'neural_network', 'ensemble']
        
        for model_name in model_files:
            try:
                model_data = joblib.load(f'ml/{model_name}.pkl')
                self.models[model_name] = model_data['model']
                self.scalers[model_name] = model_data.get('scaler')
                self.feature_columns = model_data['feature_columns']
            except Exception as e:
                print(f"Warning: Could not load {model_name}: {e}")
    
    def predict_with_model(self, student_data, model_name='ensemble'):
        """
        Complete prediction pipeline
        
        Args:
            student_data: dict of student attributes
            model_name: which model to use
        
        Returns:
            dict with risk_score, category, and explanations
        """
        # Step 1: Extract features
        features = self._extract_features(student_data)
        
        # Step 2: Scale features (if neural network)
        if model_name == 'neural_network' and self.scalers.get(model_name):
            features = self.scalers[model_name].transform(features)
        
        # Step 3: Predict
        model = self.models[model_name]
        risk_proba = model.predict_proba(features)[0]
        risk_score = risk_proba[1]  # Probability of dropout
        
        # Step 4: Categorize risk
        if risk_score >= 0.7:
            category = 'High'
        elif risk_score >= 0.4:
            category = 'Medium'
        else:
            category = 'Low'
        
        # Step 5: Explain prediction
        top_factors = self._get_feature_contributions(features, model)
        
        # Step 6: Generate recommendations
        recommendations = self._generate_recommendations(category, top_factors)
        
        return {
            'risk_score': float(risk_score),
            'risk_category': category,
            'confidence': float(max(risk_proba)),
            'top_contributing_factors': top_factors,
            'recommendations': recommendations,
            'model_used': model_name
        }
    
    def _extract_features(self, student_data):
        """Convert student dict to feature vector"""
        feature_vector = []
        
        for col in self.feature_columns:
            value = student_data.get(col, 0)
            feature_vector.append(value)
        
        return np.array(feature_vector).reshape(1, -1)
    
    def _get_feature_contributions(self, features, model):
        """Use SHAP to explain prediction"""
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(features)
            
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            
            contributions = list(zip(self.feature_columns, shap_values[0]))
            contributions.sort(key=lambda x: abs(x[1]), reverse=True)
            
            return [
                {
                    'feature': self._humanize_feature_name(name),
                    'contribution': float(value),
                    'impact': 'Risk Increase' if value > 0 else 'Risk Decrease'
                }
                for name, value in contributions[:5]
            ]
        except Exception as e:
            return []
    
    def _humanize_feature_name(self, feature_name):
        """Convert technical name to readable"""
        mappings = {
            'curricular_units_1st_sem_grade': 'First Semester Grades',
            'debtor': 'Outstanding Fees',
            'tuition_fees_up_to_date': 'Fee Payment Status',
            'age_at_enrollment': 'Age at Enrollment',
            'curricular_units_1st_sem_approved': 'Courses Passed (Sem 1)'
        }
        return mappings.get(feature_name, feature_name.replace('_', ' ').title())
    
    def _generate_recommendations(self, category, factors):
        """Generate actionable recommendations"""
        recommendations = []
        
        if category == 'High':
            recommendations.append("Immediate academic counseling required")
            recommendations.append("Contact student for urgent intervention")
        
        for factor in factors:
            feature = factor['feature']
            
            if 'grade' in feature.lower():
                recommendations.append("Consider tutoring or study groups")
            elif 'fee' in feature.lower() or 'debtor' in feature.lower():
                recommendations.append("Refer to financial aid office")
            elif 'age' in feature.lower():
                recommendations.append("Provide age-appropriate support resources")
        
        return list(set(recommendations))  # Remove duplicates

# Global instance
ml_manager = MLModelManager()

# Usage in routes
@prediction_bp.route('/predict/<int:student_id>')
def predict_student_risk(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Convert student to dict
    student_data = {
        'age': student.age,
        'curricular_units_1st_sem_grade': student.curricular_units_1st_sem_grade,
        'debtor': 1 if student.debtor else 0,
        # ... all 104 features
    }
    
    # Get prediction
    result = ml_manager.predict_with_model(student_data, model_name='ensemble')
    
    # Save to database
    prediction = RiskPrediction(
        student_id=student_id,
        risk_score=result['risk_score'],
        risk_category=result['risk_category'],
        model_used=result['model_used'],
        contributing_factors=json.dumps(result['top_contributing_factors'])
    )
    db.session.add(prediction)
    db.session.commit()
    
    return jsonify(result)
```


3.9 CHATBOT ML (INTENT CLASSIFICATION)
--------------------------------------
WHAT: Use ML to understand user intent from text
WHY: Handle complex queries beyond simple keywords

PROJECT IMPLEMENTATION:

A. Training Data:
```python
# ml/train_chatbot_intent.py
training_data = [
    # Academic intent
    ("How can I improve my grades?", "academic_support"),
    ("I'm failing my classes", "academic_support"),
    ("Need help with studies", "academic_support"),
    
    # Financial intent
    ("Can't afford tuition", "financial_help"),
    ("Need scholarship information", "financial_help"),
    ("How to apply for financial aid?", "financial_help"),
    
    # Mental health intent
    ("I'm stressed about exams", "mental_health"),
    ("Feeling overwhelmed", "mental_health"),
    ("Having anxiety", "mental_health"),
    
    # General info
    ("What is my attendance?", "info_request"),
    ("Show my risk score", "info_request")
]
```

B. Model Training:
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Create pipeline
intent_model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=1000)),
    ('classifier', MultinomialNB())
])

# Train
texts = [text for text, _ in training_data]
labels = [label for _, label in training_data]
intent_model.fit(texts, labels)

# Save
joblib.dump(intent_model, 'ml/chatbot_intent_model.pkl')
```

C. Prediction:
```python
# controllers/chatbot_controller.py
class ChatbotController:
    def __init__(self):
        self.intent_model = joblib.load('ml/chatbot_intent_model.pkl')
        self.responses = self._load_response_templates()
    
    def get_response(self, user_message, student_id):
        # Step 1: Classify intent
        intent = self.intent_model.predict([user_message])[0]
        confidence = max(self.intent_model.predict_proba([user_message])[0])
        
        # Step 2: Get student context
        student = Student.query.get(student_id)
        
        # Step 3: Generate response based on intent
        if intent == 'academic_support':
            return self._academic_response(student)
        elif intent == 'financial_help':
            return self._financial_response(student)
        elif intent == 'mental_health':
            return self._mental_health_response(student)
        elif intent == 'info_request':
            return self._info_response(student, user_message)
        else:
            return "I'm not sure I understand. Can you rephrase?"
    
    def _academic_response(self, student):
        grade = student.curricular_units_1st_sem_grade
        
        if grade < 10:
            return ("Your grades are concerning. I recommend:\n"
                   "1. Schedule tutoring sessions\n"
                   "2. Join study groups\n"
                   "3. Meet with your academic advisor")
        else:
            return ("Your academic performance is good! "
                   "Keep up the great work.")
```


================================================================================
                    4. SOFTWARE ARCHITECTURE PATTERNS
================================================================================

4.1 MVC (MODEL-VIEW-CONTROLLER)
--------------------------------
WHAT: Separates application into 3 components
WHY: Organized code, easier maintenance, reusability

PROJECT STRUCTURE:
```
Model (Database Layer)
├── models/student.py           # Data structure
├── models/alert.py
└── models/*.py

Controller (Business Logic)
├── controllers/alert_controller.py     # Logic
├── controllers/prediction_controller_advanced.py
└── controllers/*.py

View (Presentation Layer)
├── templates/student_profile.html      # UI
├── templates/index.html
└── templates/*.html

Routes (Request Handlers)
├── routes/student_routes.py            # URL mapping
├── routes/alert_routes.py
└── routes/*.py
```

FLOW EXAMPLE:
```
1. User clicks "View Student Profile" (View)
   └→ GET /students/123

2. Route handler receives request (Route)
   └→ @student_bp.route('/<int:student_id>')
       def student_profile(student_id):

3. Controller fetches data (Controller)
   └→ student = Student.query.get(student_id)
   └→ alerts = AlertController.get_student_alerts(student_id)

4. Model queries database (Model)
   └→ SELECT * FROM students WHERE id = 123
   └→ SELECT * FROM alerts WHERE student_id = 123

5. Controller passes data to view (Controller)
   └→ return render_template('student_profile.html', 
                            student=student, alerts=alerts)

6. View renders HTML (View)
   └→ <h1>{{ student.name }}</h1>
   └→ <div>Risk: {{ student.risk_score }}</div>

7. HTML sent to browser (Response)
```


4.2 SEPARATION OF CONCERNS
---------------------------
WHAT: Each module has a single, well-defined responsibility
WHY: Easier to understand, test, and modify

PROJECT EXAMPLES:

A. Database Models (models/):
```python
# ONLY responsible for data structure
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    # NO business logic here!
```

B. Controllers (controllers/):
```python
# ONLY responsible for business logic
class AlertController:
    @staticmethod
    def generate_alerts_for_student(student_id):
        # Logic for alert generation
        # NO database structure definitions
        # NO HTML rendering
```

C. Routes (routes/):
```python
# ONLY responsible for HTTP handling
@alert_bp.route('/<int:alert_id>')
def alert_detail(alert_id):
    # Get data from controller
    alert = AlertController.get_alert(alert_id)
    # Render template
    return render_template('alert.html', alert=alert)
    # NO business logic
    # NO database queries
```

D. Templates (templates/):
```html
<!-- ONLY responsible for presentation -->
<div class="alert">
    <h3>{{ alert.title }}</h3>
    <p>{{ alert.description }}</p>
</div>
<!-- NO database queries -->
<!-- NO business logic -->
```


4.3 DEPENDENCY INJECTION
-------------------------
WHAT: Provide dependencies from outside rather than creating inside
WHY: Testable, flexible, loosely coupled

EXAMPLE WITHOUT DI (BAD):
```python
class AlertController:
    def send_notification(self, alert_id):
        # Hardcoded dependency
        email_service = GmailService()  # Tightly coupled!
        email_service.send(alert_id)
```

EXAMPLE WITH DI (GOOD):
```python
class AlertController:
    def __init__(self, email_service):
        self.email_service = email_service  # Injected!
    
    def send_notification(self, alert_id):
        self.email_service.send(alert_id)

# Usage:
gmail_service = GmailService()
controller = AlertController(email_service=gmail_service)

# Easy to test with mock:
mock_service = MockEmailService()
controller = AlertController(email_service=mock_service)
```

PROJECT IMPLEMENTATION:
```python
# extensions.py
db = SQLAlchemy()  # Initialized once

# app.py
def create_app():
    app = Flask(__name__)
    db.init_app(app)  # Injected into app
    return app

# Now any module can use 'db' without creating new instance
```


4.4 FACTORY PATTERN
-------------------
WHAT: Create objects without specifying exact class
WHY: Flexibility, encapsulation

PROJECT EXAMPLE (Application Factory):
```python
# app.py
def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Different configs for different environments
    if config_name == 'development':
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/educare_dev'
    elif config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/educare_test'
    elif config_name == 'production':
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from routes.main_routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

# Usage:
dev_app = create_app('development')
test_app = create_app('testing')
prod_app = create_app('production')
```


4.5 SINGLETON PATTERN
---------------------
WHAT: Ensure only one instance of a class exists
WHY: Shared resources (DB connection, config)

PROJECT EXAMPLE:
```python
# extensions.py
db = SQLAlchemy()  # One instance for entire app

# Why singleton?
# - Only one database connection pool needed
# - All models use same connection
# - Prevents multiple connection instances

# Usage in models:
from extensions import db

class Student(db.Model):
    # Uses the singleton 'db' instance
    pass

class Alert(db.Model):
    # Uses same 'db' instance
    pass
```


4.6 REPOSITORY PATTERN
----------------------
WHAT: Abstract data access layer
WHY: Decouple business logic from data access

PROJECT EXAMPLE (Implicit in SQLAlchemy):
```python
# Without Repository Pattern (Direct DB Access):
@student_bp.route('/<int:student_id>')
def profile(student_id):
    student = Student.query.get(student_id)  # Direct SQLAlchemy
    return render_template('profile.html', student=student)

# With Repository Pattern (Abstracted):
class StudentRepository:
    @staticmethod
    def get_by_id(student_id):
        return Student.query.get(student_id)
    
    @staticmethod
    def get_high_risk_students():
        return Student.query.join(RiskPrediction).filter(
            RiskPrediction.risk_category == 'High'
        ).all()
    
    @staticmethod
    def search(name=None, email=None):
        query = Student.query
        if name:
            query = query.filter(Student.name.like(f'%{name}%'))
        if email:
            query = query.filter(Student.email == email)
        return query.all()

# Usage:
@student_bp.route('/<int:student_id>')
def profile(student_id):
    student = StudentRepository.get_by_id(student_id)
    return render_template('profile.html', student=student)

# Benefits:
# - Change database? Only modify repository
# - Add caching? Implement in repository
# - Complex queries? Encapsulate in repository methods
```


4.7 SERVICE LAYER PATTERN
--------------------------
WHAT: Business logic layer between controllers and models
WHY: Reusable business operations

PROJECT EXAMPLE:
```python
# controllers/alert_controller.py
class AlertController:
    """Service layer for alert operations"""
    
    @staticmethod
    def generate_alerts_for_student(student_id):
        """Business logic: Create alerts based on student data"""
        
        student = Student.query.get(student_id)
        alerts = []
        
        # Academic alert logic
        if student.curricular_units_1st_sem_grade < 10:
            alert = Alert(
                student_id=student_id,
                alert_type='Academic',
                severity='High',
                title='Low Grades Alert',
                description=f'Grade {student.curricular_units_1st_sem_grade} below threshold'
            )
            alerts.append(alert)
        
        # Financial alert logic
        if student.debtor and not student.tuition_fees_up_to_date:
            alert = Alert(
                student_id=student_id,
                alert_type='Financial',
                severity='Medium',
                title='Outstanding Fees',
                description='Student has unpaid fees'
            )
            alerts.append(alert)
        
        # Save all alerts
        for// filepath: CONCEPTS_GUIDE.txt
================================================================================
                    EDUCARE PROJECT - COMPLETE CONCEPTS GUIDE
                    Everything You Need to Know with Examples
================================================================================

TABLE OF CONTENTS
=================
1. FLASK FRAMEWORK CONCEPTS
2. DATABASE & ORM CONCEPTS (SQLAlchemy)
3. MACHINE LEARNING CONCEPTS
4. SOFTWARE ARCHITECTURE PATTERNS
5. WEB DEVELOPMENT CONCEPTS
6. PYTHON ADVANCED CONCEPTS
7. API & REST CONCEPTS
8. TESTING CONCEPTS
9. DEPLOYMENT & CONFIGURATION
10. DOMAIN-SPECIFIC CONCEPTS

================================================================================
                        1. FLASK FRAMEWORK CONCEPTS
================================================================================

1.1 APPLICATION FACTORY PATTERN
--------------------------------
WHAT: A design pattern where you create your Flask app inside a function
WHY: Allows creating multiple instances for testing, different configs

IMPLEMENTATION IN PROJECT:
```python
# app.py
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from routes.main_routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

# Usage:
app = create_app('development')  # For dev
app = create_app('testing')      # For tests
app = create_app('production')   # For prod
```

REAL-WORLD ANALOGY:
Like a car factory - same blueprint, different configurations (sedan, SUV, truck)


1.2 BLUEPRINTS
--------------
WHAT: Modular components that group related routes together
WHY: Organize large applications, reusable components

IMPLEMENTATION:
```python
# routes/student_routes.py
from flask import Blueprint

student_bp = Blueprint('student', __name__, url_prefix='/students')

@student_bp.route('/')
def list_students():
    return "All students"

@student_bp.route('/<int:id>')
def student_detail(id):
    return f"Student {id}"

# Registered in app.py:
app.register_blueprint(student_bp)

# URLs become:
# /students/          -> list_students()
# /students/123       -> student_detail(123)
```

PROJECT BLUEPRINTS:
- main_bp: Dashboard, home (/)
- student_bp: Student management (/students)
- alert_bp: Alert system (/alerts)
- prediction_bp: ML predictions (/predict)
- intervention_bp: Support actions (/interventions)
- gamification_bp: Points & badges (/gamification)
- chatbot_bp: AI chatbot (/chatbot)

REAL-WORLD ANALOGY:
Like departments in a company - HR, Finance, IT - each handles its own area


1.3 ROUTES & VIEW FUNCTIONS
----------------------------
WHAT: URL patterns mapped to Python functions
WHY: Connect URLs to code that handles requests

TYPES OF ROUTES:

A. Static Routes:
```python
@main_bp.route('/')
def home():
    return "Welcome"
# URL: http://localhost:5000/
```

B. Dynamic Routes:
```python
@student_bp.route('/<int:student_id>')
def profile(student_id):
    student = Student.query.get(student_id)
    return render_template('profile.html', student=student)
# URL: http://localhost:5000/students/42
```

C. HTTP Methods:
```python
@student_bp.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # Save data
        return redirect(url_for('student.list_students'))
    # Show form
    return render_template('add_student.html')
```

PROJECT EXAMPLE:
```python
# routes/student_routes.py line 15-30
@student_bp.route('/<int:student_id>')
def student_profile(student_id):
    # 1. Fetch student from database
    student = Student.query.get_or_404(student_id)
    
    # 2. Get related data
    alerts = Alert.query.filter_by(student_id=student_id).all()
    gamification = GamificationProfile.query.filter_by(student_id=student_id).first()
    
    # 3. Render template with data
    return render_template('student_profile.html',
                         student=student,
                         alerts=alerts,
                         gamification=gamification)
```


1.4 REQUEST & RESPONSE OBJECTS
-------------------------------
WHAT: Objects containing HTTP request/response data
WHY: Access form data, JSON, headers, cookies

REQUEST OBJECT:
```python
from flask import request

@app.route('/login', methods=['POST'])
def login():
    # Form data
    username = request.form.get('username')
    password = request.form.get('password')
    
    # JSON data
    data = request.get_json()
    username = data['username']
    
    # Query parameters (?key=value)
    page = request.args.get('page', 1, type=int)
    
    # Headers
    token = request.headers.get('Authorization')
    
    # Files
    file = request.files['resume']
```

RESPONSE TYPES:
```python
from flask import jsonify, render_template, redirect, url_for

# 1. HTML Response
return render_template('page.html', data=data)

# 2. JSON Response (APIs)
return jsonify({'status': 'success', 'data': data})

# 3. Redirect
return redirect(url_for('student.profile', student_id=123))

# 4. Custom Response
response = make_response(render_template('page.html'))
response.set_cookie('session_id', '123')
return response
```

PROJECT EXAMPLE (routes/main_routes.py):
```python
@main_bp.route('/dashboard')
def dashboard():
    # Query database
    total_students = Student.query.count()
    high_risk = RiskPrediction.query.filter_by(risk_category='High').count()
    
    # Pass to template
    return render_template('index.html',
                         total_students=total_students,
                         high_risk=high_risk)
```


1.5 TEMPLATE RENDERING (JINJA2)
--------------------------------
WHAT: Server-side HTML generation with Python data
WHY: Dynamic web pages without writing JavaScript for everything

JINJA2 SYNTAX:

A. Variables:
```html
<h1>Welcome {{ student.name }}</h1>
<p>Email: {{ student.email }}</p>
```

B. Control Flow:
```html
{% if student.risk_category == 'High' %}
    <span class="badge-danger">High Risk</span>
{% elif student.risk_category == 'Medium' %}
    <span class="badge-warning">Medium Risk</span>
{% else %}
    <span class="badge-success">Low Risk</span>
{% endif %}
```

C. Loops:
```html
<ul>
{% for alert in alerts %}
    <li class="alert-{{ alert.severity }}">{{ alert.title }}</li>
{% endfor %}
</ul>
```

D. Filters:
```html
<p>Created: {{ alert.created_at|datetime }}</p>
<p>Risk: {{ risk_score|round(2) }}%</p>
<p>Name: {{ student.name|upper }}</p>
```

PROJECT EXAMPLE (templates/student_profile.html):
```html
<div class="student-header">
    <h1>{{ student.name }}</h1>
    <span class="badge-{{ 'danger' if student.risk_score > 0.7 else 'success' }}">
        Risk: {{ (student.risk_score * 100)|round(1) }}%
    </span>
</div>

<div class="alerts">
    {% for alert in alerts %}
        <div class="alert alert-{{ alert.severity.lower() }}">
            <strong>{{ alert.alert_type }}</strong>: {{ alert.description }}
            <span class="date">{{ alert.created_at|datetime }}</span>
        </div>
    {% endfor %}
</div>
```

E. Template Inheritance:
```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}EduCare{% endblock %}</title>
</head>
<body>
    <nav>...</nav>
    {% block content %}{% endblock %}
    <footer>...</footer>
</body>
</html>

<!-- student_profile.html -->
{% extends "base.html" %}

{% block title %}{{ student.name }} - Profile{% endblock %}

{% block content %}
    <div class="profile">
        <!-- Student details here -->
    </div>
{% endblock %}
```


1.6 FLASK EXTENSIONS
--------------------
WHAT: Third-party packages that extend Flask functionality
WHY: Don't reinvent the wheel

PROJECT EXTENSIONS:

A. Flask-SQLAlchemy (Database ORM):
```python
# extensions.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# app.py
db.init_app(app)
```

B. Flask-Migrate (Database Migrations):
```python
from flask_migrate import Migrate
migrate = Migrate(app, db)

# Command line:
flask db init                # Initialize migrations
flask db migrate -m "Add alerts table"  # Create migration
flask db upgrade             # Apply migration
```

C. Flask-CORS (Cross-Origin Resource Sharing):
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```


1.7 FLASK CONTEXT
-----------------
WHAT: Special variables available during request processing
WHY: Access app/request data from anywhere

TYPES:

A. Application Context:
```python
from flask import current_app

# Access config
db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
```

B. Request Context:
```python
from flask import request, g

# g: request-global storage
@app.before_request
def before_request():
    g.user = get_current_user()

@app.route('/profile')
def profile():
    return f"Welcome {g.user.name}"
```

C. Context Processors:
```python
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Now 'now' available in all templates:
# <p>Current time: {{ now }}</p>
```


================================================================================
                    2. DATABASE & ORM CONCEPTS (SQLAlchemy)
================================================================================

2.1 ORM (Object-Relational Mapping)
------------------------------------
WHAT: Maps database tables to Python classes
WHY: Write Python instead of SQL, type safety, easier maintenance

TRADITIONAL SQL VS ORM:

SQL:
```sql
SELECT * FROM students WHERE id = 1;
INSERT INTO students (name, email) VALUES ('John', 'john@edu.com');
UPDATE students SET email = 'new@edu.com' WHERE id = 1;
DELETE FROM students WHERE id = 1;
```

ORM:
```python
student = Student.query.get(1)
student = Student(name='John', email='john@edu.com')
db.session.add(student)
db.session.commit()

student = Student.query.get(1)
student.email = 'new@edu.com'
db.session.commit()

student = Student.query.get(1)
db.session.delete(student)
db.session.commit()
```


2.2 MODEL DEFINITION
--------------------
WHAT: Python class representing a database table
WHY: Define structure once, use everywhere

BASIC MODEL:
```python
from extensions import db

class Student(db.Model):
    __tablename__ = 'students'  # Optional: defaults to lowercase class name
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Required fields
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    # Optional fields
    age = db.Column(db.Integer)
    
    # Default values
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Indexes for faster queries
    __table_args__ = (
        db.Index('idx_email', 'email'),
    )
```

PROJECT MODEL (models/student.py):
```python
class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    # Academic fields
    curricular_units_1st_sem_enrolled = db.Column(db.Integer)
    curricular_units_1st_sem_grade = db.Column(db.Float)
    
    # Financial fields
    tuition_fees_up_to_date = db.Column(db.Boolean)
    debtor = db.Column(db.Boolean)
    
    # Status
    target = db.Column(db.Integer)  # 0=Enrolled, 1=Dropout, 2=Graduate
    
    # Relationships (explained in section 2.3)
    alerts = db.relationship('Alert', backref='student', lazy='dynamic')
    predictions = db.relationship('RiskPrediction', backref='student', lazy=True)
```


2.3 RELATIONSHIPS
-----------------
WHAT: Connections between tables
WHY: Model real-world associations

TYPES:

A. ONE-TO-MANY (Most Common):
```python
# One student has many alerts
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alerts = db.relationship('Alert', backref='student', lazy='dynamic')

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    
# Usage:
student = Student.query.get(1)
alerts = student.alerts.all()  # Get all alerts for this student

alert = Alert.query.get(1)
student = alert.student  # Get the student for this alert (via backref)
```

B. ONE-TO-ONE:
```python
# One student has one gamification profile
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gamification = db.relationship('GamificationProfile', 
                                  uselist=False,  # One-to-one
                                  backref='student')

class GamificationProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), unique=True)
    total_points = db.Column(db.Integer, default=0)

# Usage:
student = Student.query.get(1)
points = student.gamification.total_points
```

C. MANY-TO-MANY (Association Table):
```python
# Many students, many courses
student_courses = db.Table('student_courses',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courses = db.relationship('Course', secondary=student_courses, 
                            backref='students')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

# Usage:
student = Student.query.get(1)
student.courses.append(course)
db.session.commit()

course = Course.query.get(1)
enrolled_students = course.students  # All students in this course
```

RELATIONSHIP PARAMETERS:

- backref: Creates reverse relationship
- lazy='dynamic': Returns query object (for filtering)
- lazy='select': Loads data when accessed (default)
- lazy='joined': Loads with JOIN
- cascade='all,delete-orphan': Delete children when parent deleted


2.4 QUERYING
------------
WHAT: Retrieving data from database
WHY: Flexible, powerful data access

QUERY METHODS:

A. Basic Queries:
```python
# Get all
students = Student.query.all()

# Get one by primary key
student = Student.query.get(1)
student = Student.query.get_or_404(1)  # Raises 404 if not found

# Get first match
student = Student.query.first()
```

B. Filtering:
```python
# Simple filter
students = Student.query.filter_by(age=20).all()
students = Student.query.filter_by(is_active=True, age=20).all()

# Complex filter (using SQLAlchemy operators)
from sqlalchemy import and_, or_

students = Student.query.filter(Student.age > 18).all()
students = Student.query.filter(Student.age.between(18, 25)).all()
students = Student.query.filter(Student.name.like('%John%')).all()

# Multiple conditions
students = Student.query.filter(
    and_(
        Student.age > 18,
        Student.is_active == True
    )
).all()

students = Student.query.filter(
    or_(
        Student.risk_category == 'High',
        Student.risk_category == 'Medium'
    )
).all()
```

C. Ordering:
```python
from sqlalchemy import desc, asc

# Ascending (default)
students = Student.query.order_by(Student.name).all()
students = Student.query.order_by(asc(Student.name)).all()

# Descending
students = Student.query.order_by(desc(Student.created_at)).all()

# Multiple orders
students = Student.query.order_by(
    desc(Student.risk_score),
    asc(Student.name)
).all()
```

D. Limiting:
```python
# First 10 students
students = Student.query.limit(10).all()

# Skip first 10, get next 10 (pagination)
students = Student.query.offset(10).limit(10).all()
```

E. Aggregations:
```python
# Count
total = Student.query.count()
high_risk = Student.query.filter_by(risk_category='High').count()

# Sum
from sqlalchemy import func
total_points = db.session.query(func.sum(GamificationProfile.total_points)).scalar()

# Average
avg_grade = db.session.query(func.avg(Student.curricular_units_1st_sem_grade)).scalar()

# Max/Min
max_score = db.session.query(func.max(Student.risk_score)).scalar()
```

F. Joins:
```python
# Inner join
results = db.session.query(Student, Alert).join(Alert).all()

# Left outer join
results = db.session.query(Student).outerjoin(Alert).all()

# With filter
students = db.session.query(Student).join(Alert).filter(
    Alert.severity == 'High'
).all()
```

PROJECT EXAMPLES:

```python
# From routes/main_routes.py
def dashboard():
    # Count queries
    total_students = Student.query.count()
    high_risk = RiskPrediction.query.filter_by(risk_category='High').count()
    
    # Latest alerts
    recent_alerts = Alert.query.order_by(desc(Alert.created_at)).limit(10).all()
    
    # Top performers
    top_students = GamificationProfile.query.order_by(
        desc(GamificationProfile.total_points)
    ).limit(5).all()
    
    return render_template('index.html', 
                         total=total_students,
                         high_risk=high_risk,
                         alerts=recent_alerts,
                         leaderboard=top_students)
```

```python
# From controllers/alert_controller.py
class AlertController:
    @staticmethod
    def get_student_alerts(student_id, severity=None, status='Active'):
        query = Alert.query.filter_by(student_id=student_id, status=status)
        
        if severity:
            query = query.filter_by(severity=severity)
        
        return query.order_by(desc(Alert.created_at)).all()
```


2.5 CRUD OPERATIONS
-------------------
WHAT: Create, Read, Update, Delete - basic database operations
WHY: Essential for any data-driven application

A. CREATE:
```python
# Create new record
student = Student(
    name='John Doe',
    email='john@edu.com',
    age=20
)
db.session.add(student)
db.session.commit()

# Bulk create
students = [
    Student(name='Alice', email='alice@edu.com'),
    Student(name='Bob', email='bob@edu.com')
]
db.session.add_all(students)
db.session.commit()
```

B. READ:
```python
# Single read
student = Student.query.get(1)
student = Student.query.filter_by(email='john@edu.com').first()

# Multiple reads
all_students = Student.query.all()
active_students = Student.query.filter_by(is_active=True).all()
```

C. UPDATE:
```python
# Update single field
student = Student.query.get(1)
student.email = 'newemail@edu.com'
db.session.commit()

# Update multiple fields
student.name = 'New Name'
student.age = 21
db.session.commit()

# Bulk update
Student.query.filter(Student.age < 18).update({'is_minor': True})
db.session.commit()
```

D. DELETE:
```python
# Delete single
student = Student.query.get(1)
db.session.delete(student)
db.session.commit()

# Bulk delete
Student.query.filter(Student.is_active == False).delete()
db.session.commit()
```

PROJECT EXAMPLE (from routes/student_routes.py):
```python
@student_bp.route('/add', methods=['POST'])
def add_student():
    data = request.get_json()
    
    # CREATE
    student = Student(
        name=data['name'],
        email=data['email'],
        age=data.get('age'),
        curricular_units_1st_sem_grade=data.get('grade'),
        tuition_fees_up_to_date=data.get('fees_paid', False)
    )
    
    try:
        db.session.add(student)
        db.session.commit()
        return jsonify({'message': 'Student added', 'id': student.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@student_bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    # READ
    student = Student.query.get_or_404(student_id)
    data = request.get_json()
    
    # UPDATE
    student.name = data.get('name', student.name)
    student.email = data.get('email', student.email)
    
    db.session.commit()
    return jsonify({'message': 'Student updated'})

@student_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    # READ
    student = Student.query.get_or_404(student_id)
    
    # DELETE
    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Student deleted'})
```


2.6 DATABASE SESSIONS
---------------------
WHAT: Unit of work pattern for database transactions
WHY: Group operations, rollback on errors

SESSION LIFECYCLE:
```python
# 1. Begin (implicit)
student = Student(name='John')

# 2. Add to session
db.session.add(student)

# 3. Commit (saves to database)
db.session.commit()

# 4. Rollback (undo changes if error)
try:
    db.session.add(student)
    db.session.commit()
except Exception as e:
    db.session.rollback()
    print(f"Error: {e}")
```

TRANSACTION EXAMPLE:
```python
def transfer_points(from_student_id, to_student_id, points):
    try:
        # Both operations must succeed or both fail
        from_profile = GamificationProfile.query.get(from_student_id)
        to_profile = GamificationProfile.query.get(to_student_id)
        
        from_profile.total_points -= points
        to_profile.total_points += points
        
        db.session.commit()  # Save both
    except Exception as e:
        db.session.rollback()  # Undo both
        raise e
```


2.7 MIGRATIONS
--------------
WHAT: Version control for database schema
WHY: Track changes, deploy safely, rollback if needed

WORKFLOW:
```bash
# 1. Initialize migrations (once)
flask db init

# 2. Make changes to models (e.g., add column to Student)
class Student(db.Model):
    # ... existing columns
    phone = db.Column(db.String(20))  # NEW

# 3. Generate migration
flask db migrate -m "Add phone to students"
# Creates: migrations/versions/xxx_add_phone_to_students.py

# 4. Review migration file
# migrations/versions/xxx_add_phone_to_students.py
def upgrade():
    op.add_column('students', sa.Column('phone', sa.String(20)))

def downgrade():
    op.drop_column('students', 'phone')

# 5. Apply migration
flask db upgrade

# 6. Rollback if needed
flask db downgrade
```

MIGRATION FILE EXAMPLE:
```python
"""Add risk prediction table

Revision ID: abc123
Create Date: 2024-01-15 10:30:00
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('risk_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_category', sa.String(20), nullable=False),
        sa.Column('prediction_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('risk_predictions')
```


================================================================================
                    3. MACHINE LEARNING CONCEPTS
================================================================================

3.1 SUPERVISED LEARNING
-----------------------
WHAT: Learning from labeled data (input → output pairs)
WHY: Predict outcomes based on historical data

PROJECT USE CASE: Predict student dropout based on past student data

TYPES:
- Classification: Predict category (High/Medium/Low risk)
- Regression: Predict number (risk score 0-1)

WORKFLOW:
```
Historical Data → Training → Model → New Student Data → Prediction
```


3.2 FEATURE ENGINEERING
-----------------------
WHAT: Creating input variables (features) from raw data
WHY: Better features = better predictions

PROJECT FEATURES (104 total):

A. Demographic Features:
```python
features = [
    'age',                        # Continuous: 18-65
    'gender',                     # Binary: 0/1
    'marital_status',            # Categorical: 1=Single, 2=Married, etc.
    'nacionality',               # Categorical: Country code
]
```

B. Academic Features:
```python
features = [
    'curricular_units_1st_sem_enrolled',     # Count: 0-10
    'curricular_units_1st_sem_grade',        # Average: 0-20
    'curricular_units_1st_sem_approved',     # Count: 0-10
    'curricular_units_2nd_sem_enrolled',
    'curricular_units_2nd_sem_grade',
]
```

C. Financial Features:
```python
features = [
    'tuition_fees_up_to_date',   # Binary: 0=No, 1=Yes
    'debtor',                     # Binary: 0=No, 1=Yes
    'scholarship_holder',         # Binary: 0=No, 1=Yes
]
```

D. Behavioral Features (Custom):
```python
features = [
    'stress_level',              # Scale: 1-10
    'motivation_level',          # Scale: 1-10
    'social_integration',        # Scale: 1-10
]
```

E. LMS Features:
```python
features = [
    'login_frequency',           # Count per week
    'avg_time_on_platform',      # Minutes per session
    'assignment_submissions',    # Percentage: 0-100
]
```

FEATURE TRANSFORMATION:
```python
# ml/train_advanced_models.py line 50-80

# 1. Handle missing values
X = X.fillna(X.mean())  # Replace NaN with column mean

# 2. Encode categorical variables
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
X['marital_status'] = le.fit_transform(X['marital_status'])

# 3. Scale features (for neural networks)
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. Feature selection (remove low-importance features)
from sklearn.feature_selection import SelectKBest
selector = SelectKBest(k=50)
X_selected = selector.fit_transform(X, y)
```


3.3 TRAIN-TEST SPLIT
--------------------
WHAT: Divide data into training set (80%) and testing set (20%)
WHY: Evaluate model on unseen data to prevent overfitting

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,           # Features
    y,           # Labels (dropout or not)
    test_size=0.2,    # 20% for testing
    random_state=42,  # Reproducible split
    stratify=y        # Maintain class distribution
)

# Example:
# Total: 1000 students (700 enrolled, 300 dropout)
# Training: 800 students (560 enrolled, 240 dropout)
# Testing: 200 students (140 enrolled, 60 dropout)
```

PROJECT IMPLEMENTATION (ml/train_advanced_models.py line 90-95):
```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```


3.4 CLASSIFICATION ALGORITHMS
-----------------------------
WHAT: Algorithms that predict categories
WHY: Different algorithms for different data patterns

PROJECT USES 4 ALGORITHMS:

A. RANDOM FOREST:
```python
from sklearn.ensemble import RandomForestClassifier

# What it does: Creates many decision trees, combines their votes
# Analogy: Ask 100 experts, majority vote wins

rf_model = RandomForestClassifier(
    n_estimators=200,      # 200 trees
    max_depth=15,          # Max tree depth
    min_samples_split=5,   # Min samples to split node
    random_state=42
)

rf_model.fit(X_train, y_train)
predictions = rf_model.predict(X_test)

# Pros: Robust, handles non-linear data, feature importance
# Cons: Slow on large datasets, not interpretable
```

DECISION TREE EXAMPLE:
```
                    Grade < 12?
                   /            \
                Yes              No
               /                  \
        Fees Paid?            Age < 22?
         /      \              /      \
       Yes      No           Yes      No
        |        |            |        |
    Low Risk  High Risk  Medium Risk Low Risk
```

B. GRADIENT BOOSTING:
```python
from sklearn.ensemble import GradientBoostingClassifier

# What it does: Builds trees sequentially, each fixing errors of previous
# Analogy: Student learns from mistakes, improves gradually

gb_model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,    # How much to adjust per iteration
    max_depth=5,
    subsample=0.8,         # Use 80% of data per tree
    random_state=42
)

gb_model.fit(X_train, y_train)

# Pros: Very accurate, handles complex patterns
# Cons: Slow training, can overfit
```

SEQUENTIAL LEARNING:
```
Tree 1: Predicts, makes errors
Tree 2: Focuses on Tree 1's errors
Tree 3: Focuses on Tree 2's errors
...
Final Prediction = Sum(all trees with weights)
```

C. NEURAL NETWORK:
```python
from sklearn.neural_network import MLPClassifier

# What it does: Mimics brain neurons, learns complex patterns
# Analogy: Brain with neurons processing information

nn_model = MLPClassifier(
    hidden_layer_sizes=(128, 64, 32),  # 3 layers: 128→64→32 neurons
    activation='relu',                  # Activation function
    solver='adam',                      # Optimization algorithm
    alpha=0.001,                        # Regularization
    batch_size=32,                      # Samples per update
    learning_rate_init=0.001,
    max_iter=500,
    early_stopping=True,
    random_state=42
)

# Requires scaled data
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

nn_model.fit(X_train_scaled, y_train)

# Pros: Captures complex non-linear patterns
# Cons: Requires more data, slow training, "black box"
```

NEURAL NETWORK ARCHITECTURE:
```
Input Layer (104 features)
    ↓
Hidden Layer 1 (128 neurons) → ReLU activation
    ↓
Hidden Layer 2 (64 neurons) → ReLU activation
    ↓
Hidden Layer 3 (32 neurons) → ReLU activation
    ↓
Output Layer (2 neurons: Dropout/Enrolled) → Softmax
```

D. ENSEMBLE (VOTING):
```python
from sklearn.ensemble import VotingClassifier

# What it does: Combines predictions from multiple models
# Analogy: Committee of experts voting on decision

ensemble_model = VotingClassifier(
    estimators=[
        ('rf', rf_model),
        ('gb', gb_model),
        ('nn', nn_model)
    ],
    voting='soft',  # Use probability averages
    weights=[1, 1, 1]  # Equal weight
)

ensemble_model.fit(X_train, y_train)

# Example:
# RF predicts: 70% dropout
# GB predicts: 65% dropout
# NN predicts: 80% dropout
# Ensemble: (70 + 65 + 80) / 3 = 71.67% dropout

# Pros: Best accuracy, reduces individual model errors
# Cons: Slower, more memory
```


3.5 MODEL EVALUATION
--------------------
WHAT: Metrics to measure model performance
WHY: Choose best model, identify weaknesses

A. CONFUSION MATRIX:
```python
from sklearn.metrics import confusion_matrix

#                  Predicted
#              Enrolled  Dropout
# Actual 
# Enrolled        85       15      (True Neg, False Pos)
# Dropout         10       90      (False Neg, True Pos)

cm = confusion_matrix(y_test, predictions)
```

B. ACCURACY:
```python
from sklearn.metrics import accuracy_score

accuracy = accuracy_score(y_test, predictions)
# (85 + 90) / 200 = 0.875 = 87.5%

# Problem: Misleading if classes imbalanced
# E.g., 95% enrolled, 5% dropout
# Model predicting "always enrolled" = 95% accuracy!
```

C. PRECISION, RECALL, F1-SCORE:
```python
from sklearn.metrics import classification_report

print(classification_report(y_test, predictions))

#               precision  recall  f1-score  support
# Enrolled         0.89     0.85     0.87      100
# Dropout          0.86     0.90     0.88      100

# Precision: Of predictions, how many correct?
#   Dropout Precision = 90 / (90 + 15) = 85.7%
#   "When model says dropout, it's right 85.7% of time"

# Recall: Of actual cases, how many found?
#   Dropout Recall = 90 / (90 + 10) = 90%
#   "Model catches 90% of actual dropouts"

# F1-Score: Harmonic mean of precision & recall
#   F1 = 2 * (0.857 * 0.90) / (0.857 + 0.90) = 0.878
```

D. ROC-AUC:
```python
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib.pyplot as plt

# Get probability predictions
y_proba = model.predict_proba(X_test)[:, 1]  # Dropout probability

# Calculate AUC
auc = roc_auc_score(y_test, y_proba)
# 0.5 = Random guessing, 1.0 = Perfect

# Plot ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_proba)
plt.plot(fpr, tpr, label=f'AUC = {auc:.3f}')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
plt.show()
```

PROJECT EVALUATION (ml/train_advanced_models.py line 200-250):
```python
def evaluate_model(model, X_test, y_test, model_name):
    predictions = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, predictions)
    auc = roc_auc_score(y_test, y_proba)
    
    print(f"\n{model_name} Performance:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"AUC Score: {auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))
    
    return {
        'model_name': model_name,
        'accuracy': accuracy,
        'auc': auc
    }

# Compare all models
results = []
for name, model in models.items():
    result = evaluate_model(model, X_test, y_test, name)
    results.append(result)

# Select best
best_model = max(results, key=lambda x: x['auc'])
print(f"\nBest Model: {best_model['model_name']}")
```


3.6 MODEL PERSISTENCE
---------------------
WHAT: Save trained model to disk, load later
WHY: Don't retrain every time, deploy to production

```python
import pickle
import joblib

# Save model (pickle)
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Load model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Save model (joblib - better for sklearn)
joblib.dump(model, 'model.pkl')
model = joblib.load('model.pkl')

# Save multiple objects
save_dict = {
    'model': ensemble_model,
    'scaler': scaler,
    'feature_names': feature_names
}
joblib.dump(save_dict, 'model_bundle.pkl')
```

PROJECT IMPLEMENTATION (ml/train_advanced_models.py line 300-320):
```python
# Save best model
best_model_name = 'ensemble'
best_model = models[best_model_name]

save_data = {
    'model': best_model,
    'scaler': scaler,
    'feature_columns': X.columns.tolist(),
    'model_name': best_model_name,
    'accuracy': best_accuracy,
    'auc': best_auc
}

joblib.dump(save_data, 'ml/model.pkl')
print("✅ Model saved to ml/model.pkl")

# Later in controllers/prediction_controller_advanced.py
model_data = joblib.load('ml/model.pkl')
model = model_data['model']
scaler = model_data['scaler']
feature_columns = model_data['feature_columns']
```


3.7 EXPLAINABLE AI (SHAP)
-------------------------
WHAT: Explain why model made a prediction
WHY: Trust, debugging, regulatory compliance

SHAP (SHapley Additive exPlanations):
```python
import shap

# Create explainer
explainer = shap.TreeExplainer(model)

# Get SHAP values for a prediction
student_data = X_test.iloc[0].values.reshape(1, -1)
shap_values = explainer.shap_values(student_data)

# SHAP value = feature's contribution to prediction
# Positive SHAP = increases dropout risk
# Negative SHAP = decreases dropout risk

# Example output:
# curricular_units_1st_sem_grade: -0.23  (lower grade → higher risk)
# debtor: +0.18                           (being debtor → higher risk)
# tuition_fees_up_to_date: -0.15         (paid fees → lower risk)
```

PROJECT IMPLEMENTATION (controllers/prediction_controller_advanced.py):
```python
def get_feature_contributions(student_data, model, feature_names):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(student_data)
    
    # Get SHAP values for dropout class
    if isinstance(shap_values, list):
        shap_values = shap_values[1]  # Dropout class
    
    # Combine feature names with SHAP values
    contributions = list(zip(feature_names, shap_values[0]))
    
    # Sort by absolute contribution
    contributions.sort(key=lambda x: abs(x[1]), reverse=True)
    
    # Return top 5 factors
    top_factors = [
        {
            'feature': name,
            'contribution': float(value),
            'impact': 'Increases Risk' if value > 0 else 'Decreases Risk'
        }
        for name, value in contributions[:5]
    ]
    
    return top_factors

# Usage in prediction:
prediction = model.predict_proba(student_features)[0][1]
factors = get_feature_contributions(student_features, model, feature_names)

# Response:
{
    'risk_score': 0.78,
    'risk_category': 'High',
    'top_factors': [
        {
            'feature': 'curricular_units_1st_sem_grade',
            'contribution': -0.23,
            'impact': 'Decreases Risk',
            'description': 'Low grades increase dropout risk'
        },
        {
            'feature': 'debtor',
            'contribution': 0.18,
            'impact': 'Increases Risk',
            'description': 'Outstanding debts increase dropout risk'
        }
    ]
}
```


3.8 PREDICTION PIPELINE
-----------------------
WHAT: Complete flow from raw data to prediction
WHY: Standardize prediction process

PROJECT PIPELINE (controllers/prediction_controller_advanced.py):
```python
class MLModelManager:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.load_all_models()
    
    def load_all_models(self):
        """Load all trained models"""
        model_files = ['random_forest', 'gradient_boosting', 'neural_network', 'ensemble']
        
        for model_name in model_files:
            try:
                model_data = joblib.load(f'ml/{model_name}.pkl')
                self.models[model_name] = model_data['model']
                self.scalers[model_name] = model_data.get('scaler')
                self.feature_columns = model_data['feature_columns']
            except Exception as e:
                print(f"Warning: Could not load {model_name}: {e}")
    
    def predict_with_model(self, student_data, model_name='ensemble'):
        """
        Complete prediction pipeline
        
        Args:
            student_data: dict of student attributes
            model_name: which model to use
        
        Returns:
            dict with risk_score, category, and explanations
        """
        # Step 1: Extract features
        features = self._extract_features(student_data)
        
        # Step 2: Scale features (if neural network)
        if model_name == 'neural_network' and self.scalers.get(model_name):
            features = self.scalers[model_name].transform(features)
        
        # Step 3: Predict
        model = self.models[model_name]
        risk_proba = model.predict_proba(features)[0]
        risk_score = risk_proba[1]  # Probability of dropout
        
        # Step 4: Categorize risk
        if risk_score >= 0.7:
            category = 'High'
        elif risk_score >= 0.4:
            category = 'Medium'
        else:
            category = 'Low'
        
        # Step 5: Explain prediction
        top_factors = self._get_feature_contributions(features, model)
        
        # Step 6: Generate recommendations
        recommendations = self._generate_recommendations(category, top_factors)
        
        return {
            'risk_score': float(risk_score),
            'risk_category': category,
            'confidence': float(max(risk_proba)),
            'top_contributing_factors': top_factors,
            'recommendations': recommendations,
            'model_used': model_name
        }
    
    def _extract_features(self, student_data):
        """Convert student dict to feature vector"""
        feature_vector = []
        
        for col in self.feature_columns:
            value = student_data.get(col, 0)
            feature_vector.append(value)
        
        return np.array(feature_vector).reshape(1, -1)
    
    def _get_feature_contributions(self, features, model):
        """Use SHAP to explain prediction"""
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(features)
            
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            
            contributions = list(zip(self.feature_columns, shap_values[0]))
            contributions.sort(key=lambda x: abs(x[1]), reverse=True)
            
            return [
                {
                    'feature': self._humanize_feature_name(name),
                    'contribution': float(value),
                    'impact': 'Risk Increase' if value > 0 else 'Risk Decrease'
                }
                for name, value in contributions[:5]
            ]
        except Exception as e:
            return []
    
    def _humanize_feature_name(self, feature_name):
        """Convert technical name to readable"""
        mappings = {
            'curricular_units_1st_sem_grade': 'First Semester Grades',
            'debtor': 'Outstanding Fees',
            'tuition_fees_up_to_date': 'Fee Payment Status',
            'age_at_enrollment': 'Age at Enrollment',
            'curricular_units_1st_sem_approved': 'Courses Passed (Sem 1)'
        }
        return mappings.get(feature_name, feature_name.replace('_', ' ').title())
    
    def _generate_recommendations(self, category, factors):
        """Generate actionable recommendations"""
        recommendations = []
        
        if category == 'High':
            recommendations.append("Immediate academic counseling required")
            recommendations.append("Contact student for urgent intervention")
        
        for factor in factors:
            feature = factor['feature']
            
            if 'grade' in feature.lower():
                recommendations.append("Consider tutoring or study groups")
            elif 'fee' in feature.lower() or 'debtor' in feature.lower():
                recommendations.append("Refer to financial aid office")
            elif 'age' in feature.lower():
                recommendations.append("Provide age-appropriate support resources")
        
        return list(set(recommendations))  # Remove duplicates

# Global instance
ml_manager = MLModelManager()

# Usage in routes
@prediction_bp.route('/predict/<int:student_id>')
def predict_student_risk(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Convert student to dict
    student_data = {
        'age': student.age,
        'curricular_units_1st_sem_grade': student.curricular_units_1st_sem_grade,
        'debtor': 1 if student.debtor else 0,
        # ... all 104 features
    }
    
    # Get prediction
    result = ml_manager.predict_with_model(student_data, model_name='ensemble')
    
    # Save to database
    prediction = RiskPrediction(
        student_id=student_id,
        risk_score=result['risk_score'],
        risk_category=result['risk_category'],
        model_used=result['model_used'],
        contributing_factors=json.dumps(result['top_contributing_factors'])
    )
    db.session.add(prediction)
    db.session.commit()
    
    return jsonify(result)
```


3.9 CHATBOT ML (INTENT CLASSIFICATION)
--------------------------------------
WHAT: Use ML to understand user intent from text
WHY: Handle complex queries beyond simple keywords

PROJECT IMPLEMENTATION:

A. Training Data:
```python
# ml/train_chatbot_intent.py
training_data = [
    # Academic intent
    ("How can I improve my grades?", "academic_support"),
    ("I'm failing my classes", "academic_support"),
    ("Need help with studies", "academic_support"),
    
    # Financial intent
    ("Can't afford tuition", "financial_help"),
    ("Need scholarship information", "financial_help"),
    ("How to apply for financial aid?", "financial_help"),
    
    # Mental health intent
    ("I'm stressed about exams", "mental_health"),
    ("Feeling overwhelmed", "mental_health"),
    ("Having anxiety", "mental_health"),
    
    # General info
    ("What is my attendance?", "info_request"),
    ("Show my risk score", "info_request")
]
```

B. Model Training:
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Create pipeline
intent_model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=1000)),
    ('classifier', MultinomialNB())
])

# Train
texts = [text for text, _ in training_data]
labels = [label for _, label in training_data]
intent_model.fit(texts, labels)

# Save
joblib.dump(intent_model, 'ml/chatbot_intent_model.pkl')
```

C. Prediction:
```python
# controllers/chatbot_controller.py
class ChatbotController:
    def __init__(self):
        self.intent_model = joblib.load('ml/chatbot_intent_model.pkl')
        self.responses = self._load_response_templates()
    
    def get_response(self, user_message, student_id):
        # Step 1: Classify intent
        intent = self.intent_model.predict([user_message])[0]
        confidence = max(self.intent_model.predict_proba([user_message])[0])
        
        # Step 2: Get student context
        student = Student.query.get(student_id)
        
        # Step 3: Generate response based on intent
        if intent == 'academic_support':
            return self._academic_response(student)
        elif intent == 'financial_help':
            return self._financial_response(student)
        elif intent == 'mental_health':
            return self._mental_health_response(student)
        elif intent == 'info_request':
            return self._info_response(student, user_message)
        else:
            return "I'm not sure I understand. Can you rephrase?"
    
    def _academic_response(self, student):
        grade = student.curricular_units_1st_sem_grade
        
        if grade < 10:
            return ("Your grades are concerning. I recommend:\n"
                   "1. Schedule tutoring sessions\n"
                   "2. Join study groups\n"
                   "3. Meet with your academic advisor")
        else:
            return ("Your academic performance is good! "
                   "Keep up the great work.")
```


================================================================================
                    4. SOFTWARE ARCHITECTURE PATTERNS
================================================================================

4.1 MVC (MODEL-VIEW-CONTROLLER)
------…