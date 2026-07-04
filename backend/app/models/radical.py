from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Radical(Base):
    __tablename__ = "radicals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    character: Mapped[str] = mapped_column(String(16), nullable=False)
    strokes: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    meaning_ru: Mapped[str] = mapped_column(String(160), nullable=False)
    meaning_en: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    description_ru: Mapped[str] = mapped_column(Text, default="", nullable=False)
    mnemonic_ru: Mapped[str] = mapped_column(Text, default="", nullable=False)
    usage_ru: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)

    variants = relationship("RadicalVariant", back_populates="radical", cascade="all, delete-orphan")
    assets = relationship("RadicalAsset", back_populates="radical", cascade="all, delete-orphan")
    examples = relationship("RadicalExample", back_populates="radical", cascade="all, delete-orphan")
    confusables = relationship("RadicalConfusable", back_populates="radical", cascade="all, delete-orphan")
    learning_states = relationship("LearningState", back_populates="radical", cascade="all, delete-orphan")


class RadicalVariant(Base):
    __tablename__ = "radical_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    radical_id: Mapped[int] = mapped_column(ForeignKey("radicals.id"), index=True, nullable=False)
    form: Mapped[str] = mapped_column(String(16), nullable=False)
    variant_type: Mapped[str] = mapped_column(String(32), default="alternate", nullable=False)
    position: Mapped[str] = mapped_column(String(32), default="any", nullable=False)
    note_ru: Mapped[str] = mapped_column(Text, default="", nullable=False)

    radical = relationship("Radical", back_populates="variants")


class RadicalAsset(Base):
    __tablename__ = "radical_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    radical_id: Mapped[int] = mapped_column(ForeignKey("radicals.id"), index=True, nullable=False)
    asset_type: Mapped[str] = mapped_column(String(32), default="svg", nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(200), default="generated", nullable=False)
    license: Mapped[str] = mapped_column(String(200), default="internal", nullable=False)
    quality_status: Mapped[str] = mapped_column(String(32), default="fallback", nullable=False)

    radical = relationship("Radical", back_populates="assets")


class RadicalExample(Base):
    __tablename__ = "radical_examples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    radical_id: Mapped[int] = mapped_column(ForeignKey("radicals.id"), index=True, nullable=False)
    character: Mapped[str] = mapped_column(String(16), nullable=False)
    pinyin: Mapped[str] = mapped_column(String(80), default="", nullable=False)
    translation_ru: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    note_ru: Mapped[str] = mapped_column(Text, default="", nullable=False)
    sentence_zh: Mapped[str] = mapped_column(Text, default="", nullable=False)
    sentence_pinyin: Mapped[str] = mapped_column(Text, default="", nullable=False)
    sentence_ru: Mapped[str] = mapped_column(Text, default="", nullable=False)

    radical = relationship("Radical", back_populates="examples")


class RadicalConfusable(Base):
    __tablename__ = "radical_confusables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    radical_id: Mapped[int] = mapped_column(ForeignKey("radicals.id"), index=True, nullable=False)
    other_form: Mapped[str] = mapped_column(String(16), nullable=False)
    note_ru: Mapped[str] = mapped_column(Text, default="", nullable=False)

    radical = relationship("Radical", back_populates="confusables")
