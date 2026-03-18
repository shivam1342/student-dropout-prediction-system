"""Prediction/chat API edge-case checks against running local server.

Usage:
    python scripts/functional_prediction_checks.py
Optional env var:
    BASE_URL=http://127.0.0.1:5000
"""

from __future__ import annotations

import os
import re
import sys
import time
from dataclasses import dataclass

import requests

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000").rstrip("/")
TIMEOUT = 20


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


def register_and_login(role: str, suffix: str) -> tuple[requests.Session, str, str, list[CheckResult]]:
    session = requests.Session()
    username = f"pred_{role}_{suffix}"
    password = "Pass@1234"

    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": password,
        "confirm_password": password,
        "full_name": f"Pred {role.title()} {suffix}",
        "role": role,
    }
    if role == "teacher":
        payload["department"] = "Testing"
        payload["employee_id"] = f"EMP{suffix}"

    checks: list[CheckResult] = []

    r = session.post(f"{BASE_URL}/auth/register", data=payload, allow_redirects=False, timeout=TIMEOUT)
    checks.append(CheckResult(f"register {role}", r.status_code == 302, f"status={r.status_code} location={r.headers.get('Location', '-')}"))

    r = session.post(
        f"{BASE_URL}/auth/login",
        data={"username": username, "password": password},
        allow_redirects=False,
        timeout=TIMEOUT,
    )
    checks.append(CheckResult(f"login {role}", r.status_code == 302, f"status={r.status_code} location={r.headers.get('Location', '-')}"))

    return session, username, password, checks


def extract_student_id(html: str) -> int | None:
    match = re.search(r"/students/(\d+)", html)
    return int(match.group(1)) if match else None


def run() -> int:
    suffix = str(int(time.time()))[-8:]
    results: list[CheckResult] = []

    student_session, _, _, student_checks = register_and_login("student", suffix)
    results.extend(student_checks)

    dash = student_session.get(f"{BASE_URL}/auth/student/dashboard", timeout=TIMEOUT)
    results.append(CheckResult("student dashboard", dash.status_code == 200, f"status={dash.status_code}"))

    student_id = extract_student_id(dash.text)
    if not student_id:
        # Fallback: dashboard may not include direct profile links in current UI.
        students_page = student_session.get(f"{BASE_URL}/students/", timeout=TIMEOUT)
        if students_page.status_code == 200:
            student_ids = [int(x) for x in re.findall(r"/students/(\d+)", students_page.text)]
            if student_ids:
                student_id = max(student_ids)

    if not student_id:
        results.append(CheckResult("extract student id", False, "could not parse /students/<id> from dashboard html"))
    else:
        # Own prediction should succeed.
        r = student_session.post(f"{BASE_URL}/api/predict/{student_id}", allow_redirects=False, timeout=120)
        results.append(CheckResult("student own prediction", r.status_code == 200, f"status={r.status_code}"))

        # Different student should be forbidden.
        r = student_session.post(f"{BASE_URL}/api/predict/{student_id + 1}", allow_redirects=False, timeout=TIMEOUT)
        results.append(
            CheckResult(
                "student blocked from other student prediction",
                r.status_code == 403,
                f"status={r.status_code} body={r.text[:80]}",
            )
        )

        # Unauthenticated prediction should redirect to login.
        anon = requests.Session()
        r = anon.post(f"{BASE_URL}/api/predict/{student_id}", allow_redirects=False, timeout=TIMEOUT)
        results.append(
            CheckResult(
                "unauthenticated prediction blocked",
                r.status_code == 302 and "/auth/login" in (r.headers.get("Location") or ""),
                f"status={r.status_code} location={r.headers.get('Location', '-')}",
            )
        )

    # Teacher tests
    teacher_session, _, _, teacher_checks = register_and_login("teacher", suffix)
    results.extend(teacher_checks)

    if student_id:
        r = teacher_session.post(f"{BASE_URL}/api/predict/{student_id}", allow_redirects=False, timeout=TIMEOUT)
        results.append(
            CheckResult(
                "unassigned teacher blocked from prediction",
                r.status_code == 403,
                f"status={r.status_code} body={r.text[:80]}",
            )
        )

    # Chatbot malformed / role checks
    r = student_session.post(f"{BASE_URL}/api/chatbot", data="", allow_redirects=False, timeout=TIMEOUT)
    results.append(
        CheckResult(
            "student chatbot empty payload returns 400",
            r.status_code == 400,
            f"status={r.status_code} body={r.text[:80]}",
        )
    )

    r = teacher_session.post(
        f"{BASE_URL}/api/chatbot",
        json={"message": "hello"},
        allow_redirects=False,
        timeout=TIMEOUT,
    )
    results.append(
        CheckResult(
            "teacher blocked from chatbot api",
            r.status_code == 403,
            f"status={r.status_code} body={r.text[:80]}",
        )
    )

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
    sys.exit(run())
