from __future__ import annotations

import json
import random
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.learning import LearningState, QuizAnswer, QuizAttempt
from app.models.radical import Radical
from app.models.user import User
from app.schemas.learning import AnswerOption, ExamQuestion, ExamReviewItem, ProgressRadical, TrainingQuestion


RADICAL_LOAD = (
    selectinload(Radical.variants),
    selectinload(Radical.assets),
    selectinload(Radical.examples),
    selectinload(Radical.confusables),
)


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def list_radicals(db: Session) -> list[Radical]:
    return list(db.scalars(select(Radical).options(*RADICAL_LOAD).order_by(Radical.number)).all())


def get_radical(db: Session, radical_id: int) -> Radical | None:
    return db.scalar(select(Radical).options(*RADICAL_LOAD).where(Radical.id == radical_id))


def get_state(db: Session, user_id: int, radical_id: int) -> LearningState:
    state = db.scalar(
        select(LearningState).where(LearningState.user_id == user_id, LearningState.radical_id == radical_id)
    )
    if state is None:
        state = LearningState(user_id=user_id, radical_id=radical_id)
        db.add(state)
        db.flush()
    return state


def ensure_states(db: Session, user: User, radicals: list[Radical] | None = None) -> dict[int, LearningState]:
    radicals = radicals or list_radicals(db)
    existing = {
        state.radical_id: state
        for state in db.scalars(select(LearningState).where(LearningState.user_id == user.id)).all()
    }
    for radical in radicals:
        if radical.id not in existing:
            state = LearningState(user_id=user.id, radical_id=radical.id)
            db.add(state)
            existing[radical.id] = state
    db.flush()
    return existing


def training_weight(state: LearningState) -> float:
    now = utc_now()
    due_boost = 1.0 if state.next_due is None or state.next_due <= now else 0.15
    weakness = 0.08 + ((1.0 - max(0.0, min(0.98, state.mastery))) ** 2) * 4.0
    lapse_boost = min(1.5, state.lapses * 0.18)
    novelty_boost = 1.0 if state.seen_count == 0 else 0.0
    return max(0.05, weakness + due_boost + lapse_boost + novelty_boost)


def option_count_for_mastery(mastery: float) -> int:
    if mastery < 0.25:
        return 3
    if mastery < 0.5:
        return 4
    if mastery < 0.75:
        return 6
    return 8


def pick_weighted_radical(db: Session, user: User) -> tuple[Radical, LearningState]:
    radicals = list_radicals(db)
    states = ensure_states(db, user, radicals)
    weights = [training_weight(states[radical.id]) for radical in radicals]
    radical = random.choices(radicals, weights=weights, k=1)[0]
    return radical, states[radical.id]


def make_options(db: Session, radical: Radical, count: int) -> list[AnswerOption]:
    radicals = list_radicals(db)
    by_char = {item.character: item for item in radicals}
    selected: list[Radical] = [radical]

    for confusable in radical.confusables:
        candidate = by_char.get(confusable.other_form)
        if candidate and candidate.id != radical.id and candidate not in selected:
            selected.append(candidate)
        if len(selected) >= count:
            break

    same_strokes = [item for item in radicals if item.strokes == radical.strokes and item.id != radical.id]
    random.shuffle(same_strokes)
    for candidate in same_strokes:
        if candidate not in selected:
            selected.append(candidate)
        if len(selected) >= count:
            break

    remaining = [item for item in radicals if item.id != radical.id and item not in selected]
    random.shuffle(remaining)
    for candidate in remaining:
        selected.append(candidate)
        if len(selected) >= count:
            break

    selected = selected[:count]
    random.shuffle(selected)
    return [AnswerOption(radical_id=item.id, label=item.meaning_ru) for item in selected]


def make_training_question(db: Session, user: User) -> TrainingQuestion:
    radical, state = pick_weighted_radical(db, user)
    option_count = option_count_for_mastery(state.mastery)
    return TrainingQuestion(
        radical=radical,
        options=make_options(db, radical, option_count),
        option_count=option_count,
        mastery=round(state.mastery, 3),
    )


def apply_training_answer(db: Session, user: User, radical_id: int, selected_radical_id: int) -> tuple[bool, int, float, str]:
    radical = get_radical(db, radical_id)
    if radical is None:
        raise ValueError("Radical not found")

    state = get_state(db, user.id, radical_id)
    is_correct = radical_id == selected_radical_id
    state.seen_count += 1
    state.last_result = is_correct
    if is_correct:
        state.correct_count += 1
        state.streak += 1
        state.mastery = min(0.98, state.mastery + (1.0 - state.mastery) * 0.18 + min(0.04, state.streak * 0.005))
    else:
        state.streak = 0
        state.lapses += 1
        state.mastery = max(0.0, state.mastery * 0.72 - 0.05)

    interval_minutes = max(3, int((state.mastery**2) * 24 * 60))
    if not is_correct:
        interval_minutes = 2
    state.next_due = utc_now() + timedelta(minutes=interval_minutes)

    explanation = (
        f"Верно: ключ «{radical.character}» означает: {radical.meaning_ru}. {radical.description_ru}"
        if is_correct
        else f"Правильный ответ: «{radical.character}» - {radical.meaning_ru}. {radical.description_ru}"
    )
    db.flush()
    return is_correct, radical_id, round(state.mastery, 3), explanation


def next_overview_radical(db: Session, user: User) -> Radical | None:
    radicals = list_radicals(db)
    if not radicals:
        return None
    states = ensure_states(db, user, radicals)
    return sorted(radicals, key=lambda item: (states[item.id].overview_seen_count, item.number))[0]


def mark_overview_seen(db: Session, user: User, radical_id: int) -> LearningState:
    state = get_state(db, user.id, radical_id)
    state.overview_seen_count += 1
    db.flush()
    return state


def make_exam_question(db: Session, attempt: QuizAttempt) -> ExamQuestion | None:
    if attempt.answered_count >= attempt.total_questions:
        return None
    answered_ids = {answer.radical_id for answer in attempt.answers}
    radicals = [radical for radical in list_radicals(db) if radical.id not in answered_ids]
    if not radicals:
        return None

    states = {
        state.radical_id: state
        for state in db.scalars(select(LearningState).where(LearningState.user_id == attempt.user_id)).all()
    }
    random.shuffle(radicals)
    radicals.sort(key=lambda item: states.get(item.id).mastery if states.get(item.id) else 0.0)
    weak_pool = radicals[: max(8, min(len(radicals), 40))]
    radical = random.choice(weak_pool)
    return ExamQuestion(
        attempt_id=attempt.id,
        index=attempt.answered_count + 1,
        total=attempt.total_questions,
        radical=radical,
        options=make_options(db, radical, 4),
    )


def record_exam_answer(
    db: Session,
    attempt: QuizAttempt,
    radical_id: int,
    selected_radical_id: int,
) -> tuple[bool, int]:
    radical = get_radical(db, radical_id)
    if radical is None:
        raise ValueError("Radical not found")
    if attempt.status != "active":
        raise ValueError("Exam is not active")
    if any(answer.radical_id == radical_id for answer in attempt.answers):
        raise ValueError("Question already answered")

    options = make_options(db, radical, 4)
    is_correct = radical_id == selected_radical_id
    db.add(
        QuizAnswer(
            attempt_id=attempt.id,
            radical_id=radical_id,
            selected_radical_id=selected_radical_id,
            correct_radical_id=radical_id,
            is_correct=is_correct,
            options_json=json.dumps([option.model_dump() for option in options], ensure_ascii=False),
        )
    )
    attempt.answered_count += 1
    if is_correct:
        attempt.correct_count += 1
    db.flush()
    return is_correct, radical_id


def finish_exam(db: Session, attempt: QuizAttempt) -> None:
    if attempt.status == "finished":
        return
    attempt.status = "finished"
    attempt.finished_at = utc_now()
    total = max(1, attempt.total_questions)
    attempt.score_10 = round((attempt.correct_count / total) * 10, 1)

    for answer in attempt.answers:
        state = get_state(db, attempt.user_id, answer.radical_id)
        if answer.is_correct:
            state.mastery = min(0.98, state.mastery + (1.0 - state.mastery) * 0.05)
        else:
            state.lapses += 1
            state.streak = 0
            state.mastery = max(0.0, state.mastery * 0.85 - 0.04)
            state.next_due = utc_now()
    db.flush()


def exam_review(db: Session, attempt: QuizAttempt) -> list[ExamReviewItem]:
    radical_ids = {answer.radical_id for answer in attempt.answers}
    radical_ids.update(answer.selected_radical_id for answer in attempt.answers)
    radicals = {
        radical.id: radical
        for radical in db.scalars(select(Radical).where(Radical.id.in_(radical_ids))).all()
    }
    review: list[ExamReviewItem] = []
    for answer in sorted(attempt.answers, key=lambda item: item.id):
        radical = radicals.get(answer.radical_id)
        selected = radicals.get(answer.selected_radical_id)
        if radical is None:
            continue
        review.append(
            ExamReviewItem(
                radical_id=radical.id,
                number=radical.number,
                character=radical.character,
                meaning_ru=radical.meaning_ru,
                selected_radical_id=answer.selected_radical_id,
                selected_label=selected.meaning_ru if selected else "не найдено",
                correct_label=radical.meaning_ru,
                is_correct=answer.is_correct,
            )
        )
    return review


def progress_rows(db: Session, user: User) -> list[ProgressRadical]:
    radicals = list_radicals(db)
    states = ensure_states(db, user, radicals)
    return [
        ProgressRadical(
            radical_id=radical.id,
            number=radical.number,
            character=radical.character,
            meaning_ru=radical.meaning_ru,
            mastery=round(states[radical.id].mastery, 3),
            streak=states[radical.id].streak,
            lapses=states[radical.id].lapses,
            seen_count=states[radical.id].seen_count,
            correct_count=states[radical.id].correct_count,
            overview_seen_count=states[radical.id].overview_seen_count,
        )
        for radical in radicals
    ]
