from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.learning import QuizAttempt
from app.models.user import User
from app.schemas.learning import ProgressRadical, ProgressSummary
from app.services.learning import progress_rows

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/radicals", response_model=list[ProgressRadical])
def radicals_progress(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return progress_rows(db, user)


@router.get("/summary", response_model=ProgressSummary)
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = progress_rows(db, user)
    attempts = list(
        db.scalars(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user.id, QuizAttempt.status == "finished")
            .order_by(QuizAttempt.finished_at.desc())
        ).all()
    )
    average = sum(row.mastery for row in rows) / max(1, len(rows))
    remembered_count = sum(1 for row in rows if row.mastery >= 0.75)
    remembered_ratio = remembered_count / max(1, len(rows))
    exam_accuracy = (
        sum((attempt.correct_count / max(1, attempt.total_questions)) for attempt in attempts) / len(attempts)
        if attempts
        else None
    )
    exam_component = exam_accuracy if exam_accuracy is not None else average
    learning_score = round(((average * 0.55) + (remembered_ratio * 0.25) + (exam_component * 0.20)) * 10, 1)
    return ProgressSummary(
        total_radicals=len(rows),
        overview_seen=sum(1 for row in rows if row.overview_seen_count > 0),
        average_mastery=round(average, 3),
        remembered_count=remembered_count,
        strong_count=remembered_count,
        weak_count=sum(1 for row in rows if row.mastery < 0.35),
        exams_taken=len(attempts),
        exam_accuracy=round(exam_accuracy, 3) if exam_accuracy is not None else None,
        learning_score_10=learning_score,
        last_score_10=attempts[0].score_10 if attempts else None,
    )
