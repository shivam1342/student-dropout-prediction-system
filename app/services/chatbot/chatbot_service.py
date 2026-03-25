"""Chatbot service entrypoints and user-context assembly."""
from __future__ import annotations

from typing import List, Tuple, Dict, Any, Optional
import re
from datetime import datetime, timedelta

from app.models import Student, RiskPrediction, Alert, Intervention, CounsellingLog, User, TeacherStudentAssignment
from app.extensions import db


def _safe_float(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}"
    except Exception:
        return "N/A"


def _humanize_factor_name(value: str) -> str:
    """Convert model feature-like labels into user-friendly text."""
    if not value:
        return value
    cleaned = value.replace("_", " ").strip()
    aliases = {
        "curricular units 1st sem grade": "Semester 1 performance",
        "curricular units 2nd sem grade": "Semester 2 performance",
        "tuition fees up to date": "Fee payment consistency",
        "previous qualification": "Foundation preparedness",
        "age at enrollment": "Adjustment support need",
        "scholarship holder": "Scholarship stability",
        "debtor": "Financial stress risk",
    }
    key = cleaned.lower()
    return aliases.get(key, cleaned.title())


def _build_student_chunks(user: User) -> Tuple[List[str], List[Dict[str, Any]]]:
    texts: List[str] = []
    metas: List[Dict[str, Any]] = []

    if not user or not user.student_profile:
        return texts, metas

    student = user.student_profile
    base_meta = {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
    }

    profile_chunk = (
        f"Student Profile: name={student.name}, email={student.email}, age_at_enrollment={student.age_at_enrollment}, "
        f"previous_qualification={student.previous_qualification}, scholarship_holder={student.scholarship_holder}, "
        f"debtor={student.debtor}, tuition_fees_up_to_date={student.tuition_fees_up_to_date}, "
        f"sem1_grade={_safe_float(student.curricular_units_1st_sem_grade)}, "
        f"sem2_grade={_safe_float(student.curricular_units_2nd_sem_grade)}, gdp={_safe_float(student.gdp)}"
    )
    texts.append(profile_chunk)
    metas.append({**base_meta, "source_type": "profile"})

    prediction = (
        RiskPrediction.query.filter_by(student_id=student.id)
        .order_by(RiskPrediction.prediction_date.desc())
        .first()
    )
    if prediction:
        pred_chunk = (
            f"Latest Prediction: risk_score={_safe_float(prediction.risk_score)}%, risk_category={prediction.risk_category}, "
            f"dropout_probability={_safe_float(prediction.dropout_probability)}, top_feature_1={prediction.top_feature_1}, "
            f"top_feature_2={prediction.top_feature_2}, top_feature_3={prediction.top_feature_3}"
        )
        texts.append(pred_chunk)
        metas.append({**base_meta, "source_type": "prediction"})

    alerts = (
        Alert.query.filter_by(student_id=student.id)
        .order_by(Alert.created_at.desc())
        .limit(10)
        .all()
    )
    for alert in alerts:
        texts.append(
            f"Alert: status={alert.status}, type={alert.alert_type}, severity={alert.severity}, title={alert.title}, description={alert.description}"
        )
        metas.append({**base_meta, "source_type": "alert"})

    interventions = (
        Intervention.query.filter_by(student_id=student.id)
        .order_by(Intervention.created_at.desc())
        .limit(10)
        .all()
    )
    for item in interventions:
        texts.append(
            f"Intervention: status={item.status}, type={item.intervention_type}, priority={item.priority}, title={item.title}, description={item.description}"
        )
        metas.append({**base_meta, "source_type": "intervention"})

    counselling_logs = (
        CounsellingLog.query.filter_by(student_id=student.id)
        .order_by(CounsellingLog.log_date.desc())
        .limit(10)
        .all()
    )
    for log in counselling_logs:
        texts.append(
            f"Counselling Log: type={log.intervention_type}, status={log.status}, recommendation={log.recommendation}, notes={log.counsellor_notes or 'N/A'}"
        )
        metas.append({**base_meta, "source_type": "counselling"})

    return texts, metas


def _fallback_reply(query: str) -> str:
    q = query.lower()
    if "stress" in q or "anxious" in q:
        return "I hear you. Try a short breathing break, list one immediate task, and reach out to your mentor or counsellor if stress continues."
    if "study" in q or "exam" in q:
        return "Try a 45-minute study block with 10-minute breaks, prioritize weak topics first, and review with active recall."
    return "I can help with weak-topic analysis, monthly study planning, risk explanation, and support guidance. Tell me your goal in one line."


def _format_user_profile(user: User) -> str:
    if not user or not user.student_profile:
        return "I could not find your student profile data yet."

    student = user.student_profile
    prediction = (
        RiskPrediction.query.filter_by(student_id=student.id)
        .order_by(RiskPrediction.prediction_date.desc())
        .first()
    )

    lines = [
        f"Here is your current information, {student.name}:",
        f"- Email: {student.email}",
        f"- Age at enrollment: {student.age_at_enrollment}",
        f"- Semester 1 grade: {_safe_float(student.curricular_units_1st_sem_grade)}",
        f"- Semester 2 grade: {_safe_float(student.curricular_units_2nd_sem_grade)}",
        f"- Scholarship holder: {'Yes' if student.scholarship_holder else 'No'}",
        f"- Tuition fees up to date: {'Yes' if student.tuition_fees_up_to_date else 'No'}",
    ]

    if prediction:
        lines.append(
            f"- Latest risk: {prediction.risk_category} ({_safe_float(prediction.risk_score)}%)"
        )
    else:
        lines.append("- Latest risk: Not predicted yet")

    return "\n".join(lines)


def _infer_weak_topics(user: User) -> List[str]:
    weak_topics: List[str] = []
    if not user or not user.student_profile:
        return weak_topics

    student = user.student_profile
    sem1 = float(student.curricular_units_1st_sem_grade or 0)
    sem2 = float(student.curricular_units_2nd_sem_grade or 0)

    if sem1 < 12:
        weak_topics.append("Semester 1 core subjects (foundation topics)")
    if sem2 < 12:
        weak_topics.append("Semester 2 advanced subjects")
    if sem2 < sem1:
        weak_topics.append("Consistency and revision retention between semesters")
    if not student.tuition_fees_up_to_date:
        weak_topics.append("Financial pressure management impacting study focus")

    prediction = (
        RiskPrediction.query.filter_by(student_id=student.id)
        .order_by(RiskPrediction.prediction_date.desc())
        .first()
    )
    for feat in [
        prediction.top_feature_1 if prediction else None,
        prediction.top_feature_2 if prediction else None,
        prediction.top_feature_3 if prediction else None,
    ]:
        nice = _humanize_factor_name(str(feat)) if feat else None
        if nice and nice not in weak_topics:
            weak_topics.append(nice)

    return weak_topics[:5]


def _topic_actions(topic: str) -> List[str]:
    t = (topic or "").lower()
    if "semester 1" in t or "foundation" in t:
        return [
            "Rebuild key concepts using class notes + 10 practice questions daily.",
            "Keep a mistake log and revise it every weekend.",
        ]
    if "semester 2" in t or "advanced" in t:
        return [
            "Practice mixed-difficulty problems 4 days per week.",
            "Do one timed mini-test every 3 days.",
        ]
    if "financial" in t or "fee" in t:
        return [
            "Stabilize weekly study slots to reduce stress-driven inconsistency.",
            "Reach out to advisor/counsellor for support options early.",
        ]
    return [
        "Plan 45-minute focused blocks for this area at least 5 times/week.",
        "Track progress with a simple score sheet after each session.",
    ]


def _monthly_study_plan(user: User) -> str:
    weak_topics = _infer_weak_topics(user)
    focus = weak_topics[0] if weak_topics else "your lowest-performing academic area"

    lines = [
        "Here is a 4-week study plan tailored to your profile:",
        "- Week 1: Diagnose and organize",
        f"  - Review past quizzes/assignments and list errors in {focus}.",
        "  - Set a fixed daily 90-minute study slot (2 x 45 minutes).",
        "- Week 2: Core rebuilding",
        "  - Cover fundamentals first, then solve 20-30 focused practice questions.",
        "  - Use active recall + short notes after each session.",
        "- Week 3: Application and testing",
        "  - Attempt mixed-topic timed practice 3 days this week.",
        "  - Review mistakes the same day and track weak patterns.",
        "- Week 4: Consolidation",
        "  - Do 2 full revision cycles and one mock test.",
        "  - Final 2 days: only error-log revision + formula/concept summary.",
        "- Daily rule: 45 min study + 10 min break + 45 min study.",
    ]
    if weak_topics:
        lines.append(f"- Priority weak areas: {', '.join(weak_topics)}")
    return "\n".join(lines)


def _assigned_teacher_names(student_id: int) -> List[str]:
    names: List[str] = []
    assignments = TeacherStudentAssignment.query.filter_by(
        student_id=student_id,
        is_active=True,
    ).all()
    for assignment in assignments:
        teacher = assignment.teacher
        teacher_user = teacher.user_account if teacher else None
        if teacher_user and teacher_user.full_name:
            names.append(teacher_user.full_name)

    # Preserve order while removing duplicates.
    unique_names: List[str] = []
    seen = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        unique_names.append(name)
    return unique_names


def _mentor_summary(user: User) -> str:
    if not user or not user.student_profile:
        return "I could not find your student profile yet."

    mentor_names = _assigned_teacher_names(user.student_profile.id)
    if mentor_names:
        return "Your assigned mentor/teacher(s): " + ", ".join(mentor_names) + "."
    return "You do not have an active assigned mentor yet. Please contact admin/teacher management for assignment."


def _escalate_crisis_alert(user: User, query: str) -> bool:
    """Create an urgent safety alert and attach teacher context for staff follow-up."""
    if not user or not user.student_profile:
        return False

    student = user.student_profile
    now = datetime.utcnow()
    dedupe_window_start = now - timedelta(minutes=30)

    recent_same = (
        Alert.query.filter_by(
            student_id=student.id,
            alert_type='Psychological',
            severity='Critical',
            title='Urgent Safety Escalation from Chatbot',
            status='Active',
        )
        .filter(Alert.created_at >= dedupe_window_start)
        .first()
    )
    if recent_same:
        return False

    teachers = _assigned_teacher_names(student.id)
    teacher_note = (
        f"Assigned teacher(s): {', '.join(teachers)}"
        if teachers else
        "Assigned teacher(s): none active"
    )

    try:
        alert = Alert(
            student_id=student.id,
            alert_type='Psychological',
            severity='Critical',
            title='Urgent Safety Escalation from Chatbot',
            description='Student message indicates potential self-harm or violence risk and needs immediate follow-up.',
            trigger_factors={
                'source': 'chatbot',
                'message_excerpt': (query or '')[:500],
            },
            recommended_actions=[
                'Contact assigned teacher/counselor immediately.',
                'Perform urgent welfare check for student safety.',
                'Escalate to emergency services if there is immediate danger.',
            ],
            status='Active',
            action_taken='Auto-escalated by chatbot safety policy.',
            notes=teacher_note,
        )
        db.session.add(alert)
        db.session.commit()
        return True
    except Exception as exc:
        db.session.rollback()
        print(f"WARNING: Chatbot crisis escalation failed: {exc}")
        return False


def _quick_intent_reply(query: str, user: User) -> Optional[str]:
    q = (query or "").strip().lower()
    if not q:
        return "Please provide a message."

    # Safety-critical intent: self-harm / suicide mentions.
    crisis_patterns = [
        r"\bsuicide\b",
        r"\bsuicidal\b",
        r"\bsuicidal thoughts\b",
        r"\bkill myself\b",
        r"\bkill me\b",
        r"\bend my life\b",
        r"\bself harm\b",
        r"\bself-harm\b",
        r"\bi want to die\b",
        r"\bmurder\b",
        r"\bhomicide\b",
        r"\bkill someone\b",
        r"\bhurt others\b",
        r"\bharm others\b",
    ]
    if any(re.search(p, q) for p in crisis_patterns):
        escalated = _escalate_crisis_alert(user, query)
        escalation_line = " I have also alerted your assigned support staff for urgent follow-up." if escalated else ""
        return (
            "I am really glad you shared this. Your safety matters right now. "
            "Please contact local emergency services immediately if you are in danger, and reach out to a trusted person near you now. "
            "If you can, call a suicide crisis helpline in your country right away. "
            "I can also help you write a short message to ask someone for urgent support."
            + escalation_line
        )

    if any(x in q for x in ["hello", "hi", "hey", "how are you"]):
        return "Hi, I am here for you. I can help with your profile summary, risk details, study planning, and support guidance."

    if any(x in q for x in [
        "my information", "my info", "about my information", "my profile", "about me",
        "my details", "what are my details", "show my details", "my data"
    ]):
        return _format_user_profile(user)

    if any(x in q for x in [
        "my mentor", "about my mentor", "who is my mentor", "my teacher", "assigned teacher"
    ]):
        return _mentor_summary(user)

    if any(x in q for x in ["weak topic", "weak topics", "where am i weak", "where i am weak", "my weak areas"]):
        topics = _infer_weak_topics(user)
        if not topics:
            return "From your current records, no strong weak-topic signal is available yet. I can still suggest a structured monthly plan if you want."
        top = topics[0]
        actions = _topic_actions(top)
        return (
            "Based on your data, your likely weak areas are: " + ", ".join(topics) + ".\n"
            f"Start with {top}:\n"
            f"- {actions[0]}\n"
            f"- {actions[1]}"
        )

    if any(x in q for x in ["study plan for a month", "monthly study plan", "plan for a month", "month study plan"]):
        return _monthly_study_plan(user)

    if any(x in q for x in ["in points", "bullet points", "point wise", "point-wise"]):
        # Handle conversational follow-ups like "give me that in points".
        if any(x in q for x in ["month", "study", "exam", "plan", "that", "same", "again", "it"]):
            return _monthly_study_plan(user)
        topics = _infer_weak_topics(user)
        if topics:
            return "Your likely weak areas (point-wise):\n- " + "\n- ".join(topics)
        return "I can provide point-wise guidance. Tell me if you want a monthly study plan or weak-area analysis."

    if any(x in q for x in ["improve my grades", "how to improve", "improve performance", "improve my score"]):
        topics = _infer_weak_topics(user)
        focus = topics[0] if topics else "your weakest topic"
        actions = _topic_actions(focus)
        return (
            "You can improve steadily with this focused routine:\n"
            f"- Primary focus: {focus}\n"
            f"- {actions[0]}\n"
            f"- {actions[1]}\n"
            "- Weekly check: compare your mistake count and timed-test score against last week."
        )

    if any(x in q for x in ["risk", "risk factor", "prediction", "dropout"]):
        if not user or not user.student_profile:
            return "I could not find your profile to check risk details."
        prediction = (
            RiskPrediction.query.filter_by(student_id=user.student_profile.id)
            .order_by(RiskPrediction.prediction_date.desc())
            .first()
        )
        if not prediction:
            return "You do not have a prediction yet. Please run prediction first and I can explain it."
        return (
            f"Your latest dropout risk is {prediction.risk_category} ({_safe_float(prediction.risk_score)}%). "
            f"Top factors: {prediction.top_feature_1 or 'N/A'}, {prediction.top_feature_2 or 'N/A'}, {prediction.top_feature_3 or 'N/A'}."
        )

    return None


def chatbot_reply_from_user(query: str, user: User) -> str:
    if not query or not query.strip():
        return "Please provide a message."

    quick_reply = _quick_intent_reply(query, user)
    if quick_reply:
        return quick_reply

    try:
        texts, metas = _build_student_chunks(user)
        if not texts:
            return _fallback_reply(query)

        from app.services.chatbot.retriever import get_retriever
        from app.services.chatbot.chain import build_chain

        retriever = get_retriever(texts, metas, user_id=user.id)
        chain = build_chain(retriever)

        # RetrievalQA accepts dict input in invoke for modern LangChain versions.
        result = chain.invoke({"query": query})
        if isinstance(result, dict):
            response = result.get("result") or result.get("output_text")
            return response.strip() if isinstance(response, str) and response.strip() else _fallback_reply(query)
        text = str(result).strip()
        return text if text else _fallback_reply(query)
    except Exception as exc:
        print(f"WARNING: Chatbot RAG path failed, using fallback. Error: {exc}")
        return _fallback_reply(query)


def chatbot_reply(query: str, username_or_email: str) -> str:
    """Compatibility helper that resolves user by unique username/email."""
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()
    if not user:
        return "I could not find your account context."
    return chatbot_reply_from_user(query, user)
