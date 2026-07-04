from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.radical import RadicalListItem, RadicalRead
from app.services.learning import ensure_states, get_radical, list_radicals

router = APIRouter(prefix="/radicals", tags=["radicals"])


@router.get("", response_model=list[RadicalListItem])
def radicals(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[RadicalListItem]:
    items = list_radicals(db)
    states = ensure_states(db, user, items)
    return [
        RadicalListItem(
            id=item.id,
            number=item.number,
            character=item.character,
            strokes=item.strokes,
            meaning_ru=item.meaning_ru,
            status=item.status,
            mastery=round(states[item.id].mastery, 3),
            asset_svg=item.assets[0].payload if item.assets else None,
        )
        for item in items
    ]


@router.get("/{radical_id}", response_model=RadicalRead)
def radical_detail(radical_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    radical = get_radical(db, radical_id)
    if radical is None:
        raise HTTPException(status_code=404, detail="Radical not found")
    return radical
