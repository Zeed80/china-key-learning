from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.learning import OverviewSeenIn
from app.schemas.radical import RadicalRead
from app.services.learning import get_radical, mark_overview_seen, next_overview_radical

router = APIRouter(prefix="/study", tags=["study"])


@router.get("/overview/next", response_model=RadicalRead | None)
def overview_next(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return next_overview_radical(db, user)


@router.post("/overview/seen", response_model=RadicalRead)
def overview_seen(payload: OverviewSeenIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    radical = get_radical(db, payload.radical_id)
    if radical is None:
        raise HTTPException(status_code=404, detail="Radical not found")
    mark_overview_seen(db, user, payload.radical_id)
    db.commit()
    return radical
