from pydantic import BaseModel, Field


class RadicalVariantRead(BaseModel):
    id: int
    form: str
    variant_type: str
    position: str
    note_ru: str

    model_config = {"from_attributes": True}


class RadicalAssetRead(BaseModel):
    id: int
    asset_type: str
    payload: str
    source: str
    license: str
    quality_status: str

    model_config = {"from_attributes": True}


class RadicalExampleRead(BaseModel):
    id: int
    character: str
    pinyin: str
    translation_ru: str
    note_ru: str
    sentence_zh: str
    sentence_pinyin: str
    sentence_ru: str

    model_config = {"from_attributes": True}


class RadicalConfusableRead(BaseModel):
    id: int
    other_form: str
    note_ru: str

    model_config = {"from_attributes": True}


class RadicalRead(BaseModel):
    id: int
    number: int
    character: str
    strokes: int
    meaning_ru: str
    meaning_en: str
    description_ru: str
    mnemonic_ru: str
    usage_ru: str
    status: str
    variants: list[RadicalVariantRead] = []
    assets: list[RadicalAssetRead] = []
    examples: list[RadicalExampleRead] = []
    confusables: list[RadicalConfusableRead] = []

    model_config = {"from_attributes": True}


class RadicalListItem(BaseModel):
    id: int
    number: int
    character: str
    strokes: int
    meaning_ru: str
    status: str
    mastery: float | None = None
    asset_svg: str | None = None

    model_config = {"from_attributes": True}


class RadicalUpdate(BaseModel):
    meaning_ru: str | None = Field(default=None, min_length=1, max_length=160)
    meaning_en: str | None = Field(default=None, max_length=160)
    description_ru: str | None = None
    mnemonic_ru: str | None = None
    usage_ru: str | None = None
    status: str | None = Field(default=None, pattern="^(draft|reviewed|verified)$")


class VariantInput(BaseModel):
    form: str = Field(min_length=1, max_length=16)
    variant_type: str = "alternate"
    position: str = "any"
    note_ru: str = ""


class ExampleInput(BaseModel):
    character: str = Field(min_length=1, max_length=16)
    pinyin: str = ""
    translation_ru: str = ""
    note_ru: str = ""
    sentence_zh: str = ""
    sentence_pinyin: str = ""
    sentence_ru: str = ""


class ConfusableInput(BaseModel):
    other_form: str = Field(min_length=1, max_length=16)
    note_ru: str = ""
