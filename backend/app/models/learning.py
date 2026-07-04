from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class LearningState(Base):
    __tablename__ = "learning_states"
    __table_args__ = (UniqueConstraint("user_id", "radical_id", name="uq_learning_user_radical"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    radical_id: Mapped[int] = mapped_column(ForeignKey("radicals.id"), index=True, nullable=False)
    mastery: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lapses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    seen_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overview_seen_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_due: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_result: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = relationship("User", back_populates="learning_states")
    radical = relationship("Radical", back_populates="learning_states")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    answered_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score_10: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="quiz_attempts")
    answers = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete-orphan")


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("quiz_attempts.id"), index=True, nullable=False)
    radical_id: Mapped[int] = mapped_column(ForeignKey("radicals.id"), index=True, nullable=False)
    selected_radical_id: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_radical_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    options_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    attempt = relationship("QuizAttempt", back_populates="answers")
