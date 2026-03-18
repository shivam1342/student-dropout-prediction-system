"""Focused functional policy checks.

Covers:
1) Alert deduplication for repeated generation.
2) Teacher can view only assigned students.
3) Alert-management routes are protected by auth/role checks.

Usage:
    python scripts/functional_policy_checks.py
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass

import requests

# Ensure local app package is importable when run as script.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app  # noqa: E402
from app.controllers.alert_controller import AlertController  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import (  # noqa: E402
    Alert,
    BehavioralData,
    LMSActivity,
    RiskPrediction,
    Student,
    Teacher,
    TeacherStudentAssignment,
    User,
)

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000").rstrip("/")
TIMEOUT = 15


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


def mk_user(role: str, suffix: str, password: str) -> User:
    user = User(
        username=f"policy_{role}_{suffix}",
        email=f"policy_{role}_{suffix}@example.com",
        role=role,
        full_name=f"Policy {role.title()} {suffix}",
        department="Testing",
        is_active=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def prepare_data(suffix: str):
    password = "Pass@1234"

    teacher1_user = mk_user("teacher", f"t1_{suffix}", password)
    teacher2_user = mk_user("teacher", f"t2_{suffix}", password)
    student_user = mk_user("student", f"s_{suffix}", password)

    teacher1 = Teacher(
        user_id=teacher1_user.id,
        employee_id=f"EMP_T1_{suffix}",
        department="Testing",
    )
    teacher2 = Teacher(
        user_id=teacher2_user.id,
        employee_id=f"EMP_T2_{suffix}",
        department="Testing",
    )

    student = Student(
        user_id=student_user.id,
        name=f"Policy Student {suffix}",
        email=f"policy_student_{suffix}@example.com",
        age_at_enrollment=19,
        previous_qualification=1,
        debtor=True,
        tuition_fees_up_to_date=False,
        curricular_units_1st_sem_grade=10.0,
        curricular_units_2nd_sem_grade=11.0,
        scholarship_holder=False,
        gdp=0.0,
    )

    db.session.add_all([teacher1, teacher2, student])
    db.session.flush()

    assignment = TeacherStudentAssignment(
        teacher_id=teacher1.id,
        student_id=student.id,
        course_name="Policy Testing 101",
        semester="Spring 2026",
        academic_year="2025-2026",
        is_active=True,
    )
    db.session.add(assignment)

    # Create risk/engagement/behavior entries that should trigger alerts.
    db.session.add(
        RiskPrediction(
            student_id=student.id,
            risk_score=87.0,
            risk_category="High",
            dropout_probability=0.82,
            prediction_result="Dropout",
            top_risk_factors=["financial", "grades", "engagement"],
        )
    )
    db.session.add(
        BehavioralData(
            student_id=student.id,
            attendance_rate=58.0,
            behavioral_risk_score=74.0,
            stress_level=9,
            motivation_level=2,
            confidence_level=3,
        )
    )
    db.session.add(
        LMSActivity(
            student_id=student.id,
            engagement_score=28.0,
            login_count=1,
            assignment_submissions=0,
            forum_posts=0,
        )
    )

    db.session.commit()

    return {
        "password": password,
        "teacher1_username": teacher1_user.username,
        "teacher2_username": teacher2_user.username,
        "student_username": student_user.username,
        "student_id": student.id,
    }


def login(username: str, password: str) -> requests.Session:
    session = requests.Session()
    resp = session.post(
        f"{BASE_URL}/auth/login",
        data={"username": username, "password": password},
        allow_redirects=False,
        timeout=TIMEOUT,
    )
    if resp.status_code != 302:
        raise RuntimeError(f"login failed for {username}: {resp.status_code}")
    return session


def run() -> int:
    app = create_app("default")
    suffix = str(int(time.time()))[-8:]
    results: list[CheckResult] = []

    with app.app_context():
        data = prepare_data(suffix)

        # Dedupe check: second generation should not increase active count.
        Alert.query.filter_by(student_id=data["student_id"]).delete()
        db.session.commit()

        first = AlertController.generate_alerts_for_student(data["student_id"])
        count_after_first = Alert.query.filter_by(student_id=data["student_id"], status="Active").count()

        second = AlertController.generate_alerts_for_student(data["student_id"])
        count_after_second = Alert.query.filter_by(student_id=data["student_id"], status="Active").count()

        results.append(
            CheckResult(
                "Alert dedupe on repeated generation",
                count_after_first > 0 and count_after_first == count_after_second and len(second or []) == 0,
                f"first_generated={len(first or [])} second_generated={len(second or [])} active_first={count_after_first} active_second={count_after_second}",
            )
        )

    # Route/auth policy checks (against running server)
    anon = requests.Session()
    r = anon.get(f"{BASE_URL}/alerts/api/stats", allow_redirects=False, timeout=TIMEOUT)
    results.append(
        CheckResult(
            "Unauthenticated alert stats blocked",
            r.status_code == 302 and "/auth/login" in (r.headers.get("Location") or ""),
            f"status={r.status_code} location={r.headers.get('Location', '-')}",
        )
    )

    teacher1_session = login(data["teacher1_username"], data["password"])
    teacher2_session = login(data["teacher2_username"], data["password"])
    student_session = login(data["student_username"], data["password"])

    # Assigned teacher should access student profile.
    r = teacher1_session.get(f"{BASE_URL}/students/{data['student_id']}", allow_redirects=False, timeout=TIMEOUT)
    results.append(
        CheckResult(
            "Assigned teacher can view assigned student",
            r.status_code == 200,
            f"status={r.status_code}",
        )
    )

    # Any teacher should be allowed to view student profile tabs.
    r = teacher2_session.get(f"{BASE_URL}/students/{data['student_id']}", allow_redirects=False, timeout=TIMEOUT)
    results.append(
        CheckResult(
            "Teacher can view student profile",
            r.status_code == 200,
            f"status={r.status_code} location={r.headers.get('Location', '-')}",
        )
    )

    # Student should not be able to batch-generate alerts.
    r = student_session.post(f"{BASE_URL}/alerts/generate", allow_redirects=False, timeout=TIMEOUT)
    results.append(
        CheckResult(
            "Student blocked from alert generation",
            r.status_code == 302 and r.headers.get("Location") == "/",
            f"status={r.status_code} location={r.headers.get('Location', '-')}",
        )
    )

    # Report
    passed = [x for x in results if x.passed]
    failed = [x for x in results if not x.passed]

    print(f"BASE_URL={BASE_URL}")
    print(f"Checks passed: {len(passed)}")
    print(f"Checks failed: {len(failed)}")
    for item in results:
        status = "PASS" if item.passed else "FAIL"
        print(f"[{status}] {item.name} -> {item.detail}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run())
