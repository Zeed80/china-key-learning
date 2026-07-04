from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.radical import RadicalConfusable, RadicalExample, RadicalVariant
from app.models.user import User
from app.schemas.radical import ConfusableInput, ExampleInput, RadicalRead, RadicalUpdate, VariantInput
from app.services.learning import get_radical, list_radicals

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/radicals", response_model=list[RadicalRead])
def admin_radicals(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return list_radicals(db)


@router.get("/radicals/{radical_id}", response_model=RadicalRead)
def admin_radical(radical_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    radical = get_radical(db, radical_id)
    if radical is None:
        raise HTTPException(status_code=404, detail="Radical not found")
    return radical


@router.patch("/radicals/{radical_id}", response_model=RadicalRead)
def update_radical(
    radical_id: int,
    payload: RadicalUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    radical = get_radical(db, radical_id)
    if radical is None:
        raise HTTPException(status_code=404, detail="Radical not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(radical, field, value)
    db.commit()
    db.refresh(radical)
    return get_radical(db, radical_id)


@router.put("/radicals/{radical_id}/variants", response_model=RadicalRead)
def replace_variants(
    radical_id: int,
    payload: list[VariantInput],
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    radical = get_radical(db, radical_id)
    if radical is None:
        raise HTTPException(status_code=404, detail="Radical not found")
    for item in list(radical.variants):
        db.delete(item)
    db.flush()
    for item in payload:
        db.add(RadicalVariant(radical_id=radical.id, **item.model_dump()))
    db.commit()
    return get_radical(db, radical_id)


@router.put("/radicals/{radical_id}/examples", response_model=RadicalRead)
def replace_examples(
    radical_id: int,
    payload: list[ExampleInput],
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    radical = get_radical(db, radical_id)
    if radical is None:
        raise HTTPException(status_code=404, detail="Radical not found")
    for item in list(radical.examples):
        db.delete(item)
    db.flush()
    for item in payload:
        db.add(RadicalExample(radical_id=radical.id, **item.model_dump()))
    db.commit()
    return get_radical(db, radical_id)


@router.put("/radicals/{radical_id}/confusables", response_model=RadicalRead)
def replace_confusables(
    radical_id: int,
    payload: list[ConfusableInput],
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    radical = get_radical(db, radical_id)
    if radical is None:
        raise HTTPException(status_code=404, detail="Radical not found")
    for item in list(radical.confusables):
        db.delete(item)
    db.flush()
    for item in payload:
        db.add(RadicalConfusable(radical_id=radical.id, **item.model_dump()))
    db.commit()
    return get_radical(db, radical_id)
