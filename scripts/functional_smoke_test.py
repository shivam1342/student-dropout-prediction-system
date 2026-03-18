"""Basic functional smoke tests against a running local Flask server.

Usage:
    python scripts/functional_smoke_test.py
Optional env vars:
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
TIMEOUT = 15


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


def _url(path: str) -> str:
    return f"{BASE_URL}{path}"


def post_form(session: requests.Session, path: str, data: dict, expected_status: int = 302) -> CheckResult:
    try:
        resp = session.post(_url(path), data=data, allow_redirects=False, timeout=TIMEOUT)
    except Exception as exc:
        return CheckResult(f"POST {path}", False, f"request failed: {exc}")

    ok = resp.status_code == expected_status
    return CheckResult(
        f"POST {path}",
        ok,
        f"status={resp.status_code} location={resp.headers.get('Location', '-')}",
    )


def get_page(
    session: requests.Session,
    path: str,
    expected_status: int = 200,
    allow_redirects: bool = True,
) -> CheckResult:
    try:
        resp = session.get(_url(path), allow_redirects=allow_redirects, timeout=TIMEOUT)
    except Exception as exc:
        return CheckResult(f"GET {path}", False, f"request failed: {exc}")

    ok = resp.status_code == expected_status
    detail = f"status={resp.status_code} final_url={resp.url}"
    if not allow_redirects:
        detail += f" location={resp.headers.get('Location', '-')}"
    return CheckResult(f"GET {path}", ok, detail)


def register_user(role: str, suffix: str) -> tuple[requests.Session, str, list[CheckResult]]:
    session = requests.Session()
    username = f"smoke_{role}_{suffix}"
    email = f"{username}@example.com"
    password = "Pass@1234"

    payload = {
        "username": username,
        "email": email,
        "password": password,
        "confirm_password": password,
        "full_name": f"Smoke {role.title()} {suffix}",
        "role": role,
    }

    if role == "teacher":
        payload["department"] = "Testing"
        payload["employee_id"] = f"EMP{suffix}"

    checks: list[CheckResult] = []
    checks.append(post_form(session, "/auth/register", payload, expected_status=302))

    checks.append(
        post_form(
            session,
            "/auth/login",
            {
                "username": username,
                "password": password,
            },
            expected_status=302,
        )
    )

    return session, username, checks


def extract_student_id(html: str) -> int | None:
    # Student dashboard contains a link to /students/<id>
    match = re.search(r"/students/(\d+)", html)
    return int(match.group(1)) if match else None


def run() -> int:
    suffix = str(int(time.time()))[-8:]
    results: list[CheckResult] = []

    # Server reachable
    anon = requests.Session()
    results.append(get_page(anon, "/auth/login", expected_status=200))

    # Teacher flow
    teacher_session, _, teacher_checks = register_user("teacher", suffix)
    results.extend(teacher_checks)
    results.append(get_page(teacher_session, "/auth/teacher/dashboard", expected_status=200))
    results.append(get_page(teacher_session, "/", expected_status=200))
    results.append(get_page(teacher_session, "/interventions/", expected_status=200))
    results.append(get_page(teacher_session, "/alerts/", expected_status=200))
    results.append(get_page(teacher_session, "/students/", expected_status=200))
    results.append(get_page(teacher_session, "/counselling/", expected_status=200))
    results.append(get_page(teacher_session, "/gamification/leaderboard", expected_status=200))
    results.append(get_page(teacher_session, "/chatbot", expected_status=302, allow_redirects=False))
    results.append(get_page(teacher_session, "/auth/student/dashboard", expected_status=302, allow_redirects=False))

    # Student flow
    student_session, _, student_checks = register_user("student", suffix)
    results.extend(student_checks)
    student_dash = student_session.get(_url("/auth/student/dashboard"), timeout=TIMEOUT)
    results.append(
        CheckResult(
            "GET /auth/student/dashboard",
            student_dash.status_code == 200,
            f"status={student_dash.status_code} final_url={student_dash.url}",
        )
    )
    results.append(get_page(student_session, "/chatbot", expected_status=200))
    results.append(get_page(student_session, "/auth/teacher/dashboard", expected_status=302, allow_redirects=False))
    results.append(get_page(student_session, "/students/", expected_status=200))

    student_id = extract_student_id(student_dash.text)
    if not student_id:
        # Fallback: dashboard may not expose direct /students/<id> links.
        students_page = student_session.get(_url("/students/"), timeout=TIMEOUT)
        if students_page.status_code == 200:
            student_ids = [int(x) for x in re.findall(r"/students/(\d+)", students_page.text)]
            if student_ids:
                student_id = max(student_ids)

    if student_id:
        # Student profile detail is staff-only now.
        results.append(get_page(student_session, f"/students/{student_id}", expected_status=302, allow_redirects=False))
        # Student must not access any other student profile
        results.append(get_page(student_session, f"/students/{student_id + 1}", expected_status=302, allow_redirects=False))
        # Student must not edit or delete another student
        results.append(get_page(student_session, f"/students/edit/{student_id + 1}", expected_status=302, allow_redirects=False))
        results.append(post_form(student_session, f"/students/delete/{student_id + 1}", {}, expected_status=302))
    else:
        results.append(CheckResult("Extract student_id", False, "could not parse /students/<id> from student dashboard HTML"))

    # Report
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]

    print(f"BASE_URL={BASE_URL}")
    print(f"Checks passed: {len(passed)}")
    print(f"Checks failed: {len(failed)}")

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name} -> {result.detail}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run())
