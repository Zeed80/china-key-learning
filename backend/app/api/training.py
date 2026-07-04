from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.learning import TrainingAnswerIn, TrainingAnswerOut, TrainingQuestion
from app.services.learning import apply_training_answer, make_training_question

router = APIRouter(prefix="/training", tags=["training"])


@router.post("/next", response_model=TrainingQuestion)
def next_question(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return make_training_question(db, user)


@router.post("/answer", response_model=TrainingAnswerOut)
def answer(payload: TrainingAnswerIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        is_correct, correct_id, mastery, explanation = apply_training_answer(
            db, user, payload.radical_id, payload.selected_radical_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return TrainingAnswerOut(
        is_correct=is_correct,
        correct_radical_id=correct_id,
        explanation=explanation,
        mastery=mastery,
        next_question=None,
    )
