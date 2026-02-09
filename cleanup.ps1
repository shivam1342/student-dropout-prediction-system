# SAFE CLEANUP SCRIPT
# Run this to delete old duplicate files after restructuring
# Review carefully before executing!

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EDUCARE PROJECT CLEANUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[WARNING] This will delete old duplicate files!" -ForegroundColor Yellow
Write-Host "Review FILES_TO_KEEP_DELETE.md first!" -ForegroundColor Yellow
Write-Host ""
$confirmation = Read-Host "Type 'DELETE' to proceed"

if ($confirmation -ne "DELETE") {
    Write-Host "[CANCELLED] No files deleted." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Starting cleanup..." -ForegroundColor Green
$deletedCount = 0

# Function to safely delete
function Safe-Delete {
    param($Path, $Description)
    if (Test-Path $Path) {
        Remove-Item $Path -Recurse -Force -ErrorAction SilentlyContinue
        if ($?) {
            Write-Host "[OK] Deleted: $Description" -ForegroundColor Green
            return 1
        } else {
            Write-Host "[SKIP] Could not delete: $Description" -ForegroundColor Yellow
            return 0
        }
    } else {
        Write-Host "[SKIP] Not found: $Description" -ForegroundColor Gray
        return 0
    }
}

# 1. Delete old root files
Write-Host ""
Write-Host "=== Deleting Old Root Files ===" -ForegroundColor Cyan
$deletedCount += Safe-Delete "app.py" "app.py (old entry point)"
$deletedCount += Safe-Delete "app_config.py" "app_config.py (old config)"
$deletedCount += Safe-Delete "populate_database.py" "populate_database.py"
$deletedCount += Safe-Delete "recreate_db.py" "recreate_db.py"
$deletedCount += Safe-Delete "test_educare.py" "test_educare.py"
$deletedCount += Safe-Delete "models.py" "models.py (old single file)"
$deletedCount += Safe-Delete "tempCodeRunnerFile.bat" "tempCodeRunnerFile.bat"

# 2. Delete duplicate model files (keep models/__init__.py)
Write-Host ""
Write-Host "=== Deleting Duplicate Model Files ===" -ForegroundColor Cyan
$deletedCount += Safe-Delete "models\user.py" "models/user.py"
$deletedCount += Safe-Delete "models\student.py" "models/student.py"
$deletedCount += Safe-Delete "models\risk_prediction.py" "models/risk_prediction.py"
$deletedCount += Safe-Delete "models\alert.py" "models/alert.py"
$deletedCount += Safe-Delete "models\intervention.py" "models/intervention.py"
$deletedCount += Safe-Delete "models\counselling_log.py" "models/counselling_log.py"
$deletedCount += Safe-Delete "models\lms_activity.py" "models/lms_activity.py"
$deletedCount += Safe-Delete "models\behavioral_data.py" "models/behavioral_data.py"
$deletedCount += Safe-Delete "models\gamification.py" "models/gamification.py"

# 3. Delete old directories (copies exist in app/)
Write-Host ""
Write-Host "=== Deleting Old Directories ===" -ForegroundColor Cyan
$deletedCount += Safe-Delete "routes" "routes/ directory"
$deletedCount += Safe-Delete "utils" "utils/ directory"
$deletedCount += Safe-Delete "ml" "ml/ directory"
$deletedCount += Safe-Delete "static" "static/ directory (root)"
$deletedCount += Safe-Delete "templates" "templates/ directory (root)"
$deletedCount += Safe-Delete "backups" "backups/ directory"

# 4. Delete cache directories
Write-Host ""
Write-Host "=== Deleting Cache Directories ===" -ForegroundColor Cyan
Get-ChildItem -Path . -Recurse -Directory -Filter __pycache__ -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    if ($?) {
        Write-Host "[OK] Deleted: $($_.FullName)" -ForegroundColor Green
        $deletedCount++
    }
}

# 5. Delete doc file
Write-Host ""
Write-Host "=== Deleting Miscellaneous Files ===" -ForegroundColor Cyan
$deletedCount += Safe-Delete "AI-Based_Dropout_Prediction_and_Counselling_System.docx" "Word document"

# Final summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CLEANUP COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deleted: $deletedCount files/directories" -ForegroundColor Green
Write-Host ""
Write-Host "✅ KEPT:" -ForegroundColor Green
Write-Host "  - run.py (entry point)" -ForegroundColor White
Write-Host "  - app/ directory (new structure)" -ForegroundColor White
Write-Host "  - controllers/ (still in use)" -ForegroundColor White
Write-Host "  - models/__init__.py (compatibility)" -ForegroundColor White
Write-Host "  - extensions.py (compatibility)" -ForegroundColor White
Write-Host "  - dataset.csv, requirements.txt" -ForegroundColor White
Write-Host "  - All documentation (.md, .txt)" -ForegroundColor White
Write-Host "  - instance/ (database)" -ForegroundColor White
Write-Host "  - venv/ (virtual environment)" -ForegroundColor White
Write-Host ""
Write-Host "Test the app: python run.py" -ForegroundColor Cyan
Write-Host ""
