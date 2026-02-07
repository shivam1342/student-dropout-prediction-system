@echo off
REM This script performs the one-time setup for the Flask application with PostgreSQL.
REM 
REM PREREQUISITES:
REM 1. PostgreSQL must be installed and running
REM 2. Create a database named 'student_counselling_db' 
REM 3. Ensure the postgres user has access (or modify credentials in app.py)
REM
REM To create the database, run in psql:
REM   CREATE DATABASE student_counselling_db;
REM   GRANT ALL PRIVILEGES ON DATABASE student_counselling_db TO postgres;

echo [1/5] Setting up environment variables...
set FLASK_APP=app.py

@REM echo [2/5] Installing Python dependencies from requirements.txt...
@REM pip install -r requirements.txt

echo [3/5] Training the machine learning model...
python ml/train_model.py
python ml/train_advanced_models.py

@REM echo [4/5] Creating database tables...
@REM flask db-create

@REM echo [5/5] Seeding the database with initial data...
@REM flask seed-db


echo.
echo ====================================================
echo  SETUP COMPLETE!
echo  
echo  DATABASE: PostgreSQL (student_counselling_db)
echo  To run the application, use the following command:
echo  python app.py
echo  
echo  Make sure PostgreSQL is running and the database
echo  'student_counselling_db' exists before running.
echo ====================================================

pause
