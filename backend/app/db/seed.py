from __future__ import annotations

import argparse

from sqlalchemy import inspect, text
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.seed_data import (
    RADICALS,
    VARIANTS,
    confusables_for,
    default_description,
    default_mnemonic,
    default_usage,
    examples_for,
    generated_svg,
)
from app.db.session import Base, SessionLocal, engine
from app.models.all_models import Radical, RadicalAsset, RadicalConfusable, RadicalExample, RadicalVariant, User


GENERATED_EXAMPLE_NOTE_PREFIX = "Базовая форма ключа;"


def has_generated_examples(radical: Radical) -> bool:
    return any(example.note_ru.startswith(GENERATED_EXAMPLE_NOTE_PREFIX) for example in radical.examples)


def replace_examples(db: Session, radical: Radical, examples: list[tuple[str, str, str, str, str, str, str]]) -> None:
    for item in list(radical.examples):
        db.delete(item)
    db.flush()
    for character, pinyin, translation_ru, note_ru, sentence_zh, sentence_pinyin, sentence_ru in examples:
        db.add(
            RadicalExample(
                radical_id=radical.id,
                character=character,
                pinyin=pinyin,
                translation_ru=translation_ru,
                note_ru=note_ru,
                sentence_zh=sentence_zh,
                sentence_pinyin=sentence_pinyin,
                sentence_ru=sentence_ru,
            )
        )


def seed_radicals(db: Session) -> None:
    for number, character, strokes, meaning_ru, meaning_en in RADICALS:
        radical = db.scalar(select(Radical).where(Radical.number == number))
        if radical is None:
            radical = Radical(
                number=number,
                character=character,
                strokes=strokes,
                meaning_ru=meaning_ru,
                meaning_en=meaning_en,
                description_ru=default_description(number, character, meaning_ru),
                mnemonic_ru=default_mnemonic(number, character, meaning_ru),
                usage_ru=default_usage(number, strokes),
                status="draft",
            )
            db.add(radical)
            db.flush()
        else:
            radical.character = character
            radical.strokes = strokes
            radical.meaning_en = radical.meaning_en or meaning_en
            radical.meaning_ru = radical.meaning_ru or meaning_ru
            if radical.status == "draft":
                radical.description_ru = default_description(number, character, radical.meaning_ru)
                radical.mnemonic_ru = default_mnemonic(number, character, radical.meaning_ru)
                radical.usage_ru = default_usage(number, strokes)
            else:
                radical.description_ru = radical.description_ru or default_description(number, character, meaning_ru)
                radical.mnemonic_ru = radical.mnemonic_ru or default_mnemonic(number, character, meaning_ru)
                radical.usage_ru = radical.usage_ru or default_usage(number, strokes)

        if radical.status == "draft":
            for asset in radical.assets:
                if asset.asset_type == "svg" and asset.quality_status == "fallback":
                    asset.payload = generated_svg(character)

        if not radical.assets:
            db.add(
                RadicalAsset(
                    radical_id=radical.id,
                    asset_type="svg",
                    payload=generated_svg(character),
                    source="generated-font-fallback; replaceable with MakeMeAHanzi/HanziWriter paths",
                    license="project-generated fallback glyph; verify font/license for production exports",
                    quality_status="fallback",
                )
            )

        generated_examples = examples_for(number, character, radical.meaning_ru)
        if radical.status == "draft" or not radical.examples or has_generated_examples(radical):
            replace_examples(db, radical, generated_examples)
        elif not radical.examples:
            db.add(
                RadicalExample(
                    radical_id=radical.id,
                    character=character,
                    translation_ru=meaning_ru,
                    note_ru=f"{GENERATED_EXAMPLE_NOTE_PREFIX} для этого ключа еще нужен редакторский пример с разбором в админке.",
                    sentence_zh=f"“{character}”是一个部首。",
                    sentence_pinyin=f"{character} shi4 yi1 ge bu4shou3.",
                    sentence_ru=f"«{character}» — это ключ.",
                )
            )

        existing_variants = {variant.form for variant in radical.variants}
        for form, variant_type, position, note_ru in VARIANTS.get(number, []):
            if form not in existing_variants:
                db.add(
                    RadicalVariant(
                        radical_id=radical.id,
                        form=form,
                        variant_type=variant_type,
                        position=position,
                        note_ru=note_ru,
                    )
                )

        generated_confusables = confusables_for(number, character, strokes)
        if radical.status == "draft":
            for item in list(radical.confusables):
                db.delete(item)
            db.flush()
            for other_form, note_ru in generated_confusables:
                db.add(RadicalConfusable(radical_id=radical.id, other_form=other_form, note_ru=note_ru))
        else:
            existing_confusables = {confusable.other_form for confusable in radical.confusables}
            for other_form, note_ru in generated_confusables:
                if other_form not in existing_confusables:
                    db.add(RadicalConfusable(radical_id=radical.id, other_form=other_form, note_ru=note_ru))


def seed_admin(db: Session, email: str | None, password: str | None) -> None:
    if not email or not password:
        return
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user is None:
        db.add(User(email=email.lower(), password_hash=hash_password(password), role="admin"))
    else:
        user.password_hash = hash_password(password)
        user.role = "admin"


def run_seed(admin_email: str | None = None, admin_password: str | None = None) -> None:
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    with SessionLocal() as db:
        seed_radicals(db)
        seed_admin(db, admin_email, admin_password)
        db.commit()


def ensure_schema() -> None:
    inspector = inspect(engine)
    if "radical_examples" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("radical_examples")}
    statements = []
    if "sentence_zh" not in columns:
        statements.append("ALTER TABLE radical_examples ADD COLUMN sentence_zh TEXT NOT NULL DEFAULT ''")
    if "sentence_pinyin" not in columns:
        statements.append("ALTER TABLE radical_examples ADD COLUMN sentence_pinyin TEXT NOT NULL DEFAULT ''")
    if "sentence_ru" not in columns:
        statements.append("ALTER TABLE radical_examples ADD COLUMN sentence_ru TEXT NOT NULL DEFAULT ''")
    if not statements:
        return
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--admin-email")
    parser.add_argument("--admin-password")
    args = parser.parse_args()
    run_seed(args.admin_email, args.admin_password)


if __name__ == "__main__":
    main()
