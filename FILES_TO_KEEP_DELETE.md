# 🗂️ ACTIVE FILES - DO NOT DELETE

## ✅ ROOT LEVEL (KEEP)
run.py                          # Main entry point (NEW)
dataset.csv                     # ML training data
requirements.txt                # Python dependencies
.env                           # Environment variables (if exists)
.gitignore                     # Git ignore rules
setup.bat                      # Setup script

# COMPATIBILITY SHIMS (needed until Day 2 complete)
extensions.py                  # Imports from app.extensions
models/__init__.py             # Imports from app.models

---

## ✅ app/ DIRECTORY (NEW STRUCTURE - ALL ACTIVE)

### Core Application
app/__init__.py                # App factory
app/config.py                  # Configuration
app/extensions.py              # Flask extensions

### Models (9 files)
app/models/__init__.py
app/models/user.py
app/models/student.py
app/models/risk_prediction.py
app/models/alert.py
app/models/intervention.py
app/models/counselling_log.py
app/models/lms_activity.py
app/models/behavioral_data.py
app/models/gamification.py

### Routes (8 files)
app/routes/__init__.py
app/routes/main_routes.py
app/routes/student_routes.py
app/routes/api_routes.py
app/routes/alert_routes.py
app/routes/intervention_routes.py
app/routes/counselling_routes.py
app/routes/gamification_routes.py
app/routes/favicon_routes.py

### ML Pipeline
app/ml/__init__.py
app/ml/train_model.py          # Active training script
app/ml/train_advanced_models.py
app/ml/train_intent_model.py
app/ml/pipeline/__init__.py
app/ml/predictors/__init__.py
app/ml/models/                 # All .pkl model files
app/ml/models/model.pkl        # Current active model
app/ml/models/model_comparison.json

### Utilities
app/utils/__init__.py
app/utils/helpers.py
app/utils/explainability.py
app/utils/preprocessing.py
app/utils/migrate_to_multiuser.py
app/utils/simple_test.py
app/utils/test_migration.py

### Future Structure (empty but keep)
app/services/__init__.py
app/repositories/__init__.py
app/cli/__init__.py

### Frontend
app/static/                    # Entire directory (CSS, JS, images)
app/templates/                 # Entire directory (all HTML files)

---

## ✅ controllers/ (OLD BUT STILL IN USE)

**⚠️ KEEP UNTIL DAY 2 SERVICE LAYER COMPLETE**

controllers/alert_controller.py
controllers/chatbot_controller.py
controllers/counselling_controller.py
controllers/data_controller.py
controllers/db_utils.py
controllers/gamification_controller.py
controllers/intervention_controller.py
controllers/prediction_controller.py
controllers/prediction_controller_advanced.py

---

## ✅ DOCUMENTATION (KEEP)

README.md
RESTRUCTURE_PLAN.md
DAY1_CHECKLIST.md
DAY2_CHECKLIST.md
BEFORE_AFTER_COMPARISON.md
todo.txt
learnn.md
structure.txt
docs/database_migration_plan.md
docs/database_schema_user_model.md
docs/foreign_key_relationships.md

---

## ✅ INSTANCE & DATA (KEEP)

instance/                      # Database files
.git/                         # Git repository

---

## ❌ SAFE TO DELETE

### Old Root Files (Replaced)
app.py                        # OLD - replaced by run.py + app/__init__.py
app_config.py                 # OLD - copied to app/config.py
populate_database.py          # OLD - can recreate if needed
recreate_db.py                # OLD - use Flask CLI commands
test_educare.py               # OLD test file
models.py                     # OLD single file (if exists)
tempCodeRunnerFile.bat        # Temp file

### Old Directories (Duplicates)
models/user.py                # Duplicate - keep only models/__init__.py
models/student.py             # Duplicate
models/risk_prediction.py     # Duplicate
models/alert.py               # Duplicate
models/intervention.py        # Duplicate
models/counselling_log.py     # Duplicate
models/lms_activity.py        # Duplicate
models/behavioral_data.py     # Duplicate
models/gamification.py        # Duplicate

routes/                       # All .py files (copied to app/routes/)
utils/                        # All .py files (copied to app/utils/)
ml/                          # All files except: (copied to app/ml/)
static/                      # Entire directory (copied to app/static/)
templates/                   # Entire directory (copied to app/templates/)

### Backups & Cache
backups/                     # Old backups
__pycache__/                # All __pycache__ directories (everywhere)

### Etc
AI-Based_Dropout_Prediction_and_Counselling_System.docx

---

## ⚠️ DO NOT DELETE (but exclude from git)

venv/                        # Virtual environment - DON'T DELETE!
instance/*.db                # Database files - DON'T DELETE!

---

## 📝 DELETE COMMANDS (Run these carefully)

```powershell
# Delete old root files
Remove-Item app.py, app_config.py, populate_database.py, recreate_db.py, test_educare.py, models.py, tempCodeRunnerFile.bat -Force -ErrorAction SilentlyContinue

# Delete duplicate model files (keep models/__init__.py)
Remove-Item models\user.py, models\student.py, models\risk_prediction.py, models\alert.py, models\intervention.py, models\counselling_log.py, models\lms_activity.py, models\behavioral_data.py, models\gamification.py -Force -ErrorAction SilentlyContinue

# Delete old directories
Remove-Item routes -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item utils -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item ml -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item static -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item templates -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item backups -Recurse -Force -ErrorAction SilentlyContinue

# Delete cache
Get-ChildItem -Path . -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force

# Delete doc file
Remove-Item "AI-Based_Dropout_Prediction_and_Counselling_System.docx" -Force -ErrorAction SilentlyContinue
```

---

## 🎯 SUMMARY

**ACTIVE STRUCTURE:**
```
capstone/
├── run.py                      # Entry point
├── dataset.csv                 # Data
├── requirements.txt            # Dependencies
├── extensions.py               # Compatibility shim
├── models/__init__.py          # Compatibility shim
├── controllers/                # OLD but still used (9 files)
├── instance/                   # Database
├── docs/                       # Documentation
├── app/                        # NEW STRUCTURE
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models/                 (9 models)
│   ├── routes/                 (8 routes)
│   ├── controllers/            (future - for Day 2)
│   ├── services/               (future - for Day 2)
│   ├── repositories/           (future - for Day 2)
│   ├── ml/                     (models + training)
│   ├── utils/                  (6 utilities)
│   ├── static/                 (CSS, JS, images)
│   └── templates/              (HTML files)
└── *.md, *.txt                # Documentation files
```

**FILES TO DELETE:** 70+ old duplicate files
**FILES TO KEEP:** ~60 active files + all static/templates
