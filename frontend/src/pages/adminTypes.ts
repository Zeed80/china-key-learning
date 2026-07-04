export type VariantInput = {
  form: string;
  variant_type: string;
  position: string;
  note_ru: string;
};

export type ExampleInput = {
  character: string;
  pinyin: string;
  translation_ru: string;
  note_ru: string;
  sentence_zh: string;
  sentence_pinyin: string;
  sentence_ru: string;
};

export type ConfusableInput = {
  other_form: string;
  note_ru: string;
};

export type {
  Radical,
  RadicalAsset,
  RadicalConfusable,
  RadicalExample,
  RadicalVariant,
} from "../api/types";
