from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.learning import QuizAttempt
from app.models.user import User
from app.schemas.learning import ExamAnswerIn, ExamAnswerOut, ExamFinishOut, ExamStartOut
from app.services.learning import exam_review, finish_exam, make_exam_question, progress_rows, record_exam_answer

router = APIRouter(prefix="/exams", tags=["exams"])


def get_attempt(db: Session, user: User, attempt_id: int) -> QuizAttempt:
    attempt = db.scalar(
        select(QuizAttempt)
        .options(selectinload(QuizAttempt.answers))
        .where(QuizAttempt.id == attempt_id, QuizAttempt.user_id == user.id)
    )
    if attempt is None:
        raise HTTPException(status_code=404, detail="Exam attempt not found")
    return attempt


@router.post("/start", response_model=ExamStartOut)
def start_exam(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    attempt = QuizAttempt(user_id=user.id, total_questions=20)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    question = make_exam_question(db, attempt)
    return ExamStartOut(attempt_id=attempt.id, total=attempt.total_questions, question=question)


@router.post("/{attempt_id}/answer", response_model=ExamAnswerOut)
def answer_exam(
    attempt_id: int,
    payload: ExamAnswerIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    attempt = get_attempt(db, user, attempt_id)
    try:
        record_exam_answer(db, attempt, payload.radical_id, payload.selected_radical_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    next_question = make_exam_question(db, attempt)
    if next_question is None and attempt.answered_count >= attempt.total_questions:
        finish_exam(db, attempt)
    db.commit()
    return ExamAnswerOut(
        answered_count=attempt.answered_count,
        total=attempt.total_questions,
        next_question=next_question,
    )


@router.post("/{attempt_id}/finish", response_model=ExamFinishOut)
def finish(
    attempt_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    attempt = get_attempt(db, user, attempt_id)
    finish_exam(db, attempt)
    db.commit()
    rows = progress_rows(db, user)
    weak = sorted(rows, key=lambda row: row.mastery)[:10]
    return ExamFinishOut(
        attempt_id=attempt.id,
        score_10=attempt.score_10 or 0.0,
        correct_count=attempt.correct_count,
        total=attempt.total_questions,
        weak_radicals=weak,
        review=exam_review(db, attempt),
    )
