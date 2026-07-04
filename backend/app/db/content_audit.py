from __future__ import annotations

from app.db.seed_data import (
    RADICALS,
    confusables_for,
    default_description,
    default_mnemonic,
    default_usage,
    examples_for,
    generated_svg,
)


def audit_seed_data() -> dict[str, int]:
    issues: list[str] = []
    numbers = [number for number, *_ in RADICALS]
    characters = [character for _, character, *_ in RADICALS]

    if len(RADICALS) != 214:
        issues.append(f"Expected 214 radicals, got {len(RADICALS)}")
    if len(set(numbers)) != len(numbers):
        issues.append("Radical numbers are not unique")
    if numbers != list(range(1, 215)):
        issues.append("Radical numbers must be continuous 1..214")
    if len(set(characters)) != len(characters):
        issues.append("Radical characters are not unique")

    total_examples = 0
    total_confusables = 0
    fallback_examples = 0
    for number, character, strokes, meaning_ru, _ in RADICALS:
        if not character or strokes <= 0 or not meaning_ru:
            issues.append(f"Radical {number} has incomplete base data")

        description = default_description(number, character, meaning_ru)
        usage = default_usage(number, strokes)
        mnemonic = default_mnemonic(number, character, meaning_ru)
        if len(description) < 180 or "смысловой ориентир" not in description:
            issues.append(f"Radical {number} has weak description")
        if len(usage) < 100:
            issues.append(f"Radical {number} has weak usage")
        if len(mnemonic) < 80:
            issues.append(f"Radical {number} has weak mnemonic")

        svg = generated_svg(character)
        required_svg_parts = [
            "<svg",
            'viewBox="0 0 128 128"',
            'role="img"',
            "aria-label=",
            "<title>",
            "<rect",
            "<path",
            "<text",
            'text-anchor="middle"',
            character,
        ]
        if any(part not in svg for part in required_svg_parts):
            issues.append(f"Radical {number} has invalid fallback SVG")

        examples = examples_for(number, character, meaning_ru)
        total_examples += len(examples)
        if not examples:
            issues.append(f"Radical {number} has no examples")
        for example in examples:
            if len(example) != 7:
                issues.append(f"Radical {number} example has invalid shape")
                continue
            ex_char, _, ex_translation, note, sentence_zh, _, sentence_ru = example
            if not ex_char or not ex_translation or "Разбор:" not in note:
                issues.append(f"Radical {number} example is missing analysis")
            if not sentence_zh or not sentence_ru:
                issues.append(f"Radical {number} example is missing sentence")
            if "редакторской вычитке" in note:
                fallback_examples += 1

        confusables = confusables_for(number, character, strokes)
        total_confusables += len(confusables)
        if not confusables:
            issues.append(f"Radical {number} has no confusables")
        for other_form, note in confusables:
            if not other_form or not note:
                issues.append(f"Radical {number} has invalid confusable")

    if issues:
        joined = "\n".join(f"- {issue}" for issue in issues)
        raise SystemExit(f"Content audit failed:\n{joined}")

    return {
        "radicals": len(RADICALS),
        "examples": total_examples,
        "confusables": total_confusables,
        "fallback_examples": fallback_examples,
    }


def main() -> None:
    print(audit_seed_data())


if __name__ == "__main__":
    main()
