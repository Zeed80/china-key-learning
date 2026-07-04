export type User = {
  id: number;
  email: string;
  role: "user" | "admin" | string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type RadicalVariant = {
  id: number;
  form: string;
  variant_type: string;
  position: string;
  note_ru: string;
};

export type RadicalAsset = {
  id: number;
  asset_type: string;
  payload: string;
  source: string;
  license: string;
  quality_status: string;
};

export type RadicalExample = {
  id: number;
  character: string;
  pinyin: string;
  translation_ru: string;
  note_ru: string;
  sentence_zh: string;
  sentence_pinyin: string;
  sentence_ru: string;
};

export type RadicalConfusable = {
  id: number;
  other_form: string;
  note_ru: string;
};

export type Radical = {
  id: number;
  number: number;
  character: string;
  strokes: number;
  meaning_ru: string;
  meaning_en: string;
  description_ru: string;
  mnemonic_ru: string;
  usage_ru: string;
  status: string;
  variants: RadicalVariant[];
  assets: RadicalAsset[];
  examples: RadicalExample[];
  confusables: RadicalConfusable[];
};

export type RadicalListItem = {
  id: number;
  number: number;
  character: string;
  strokes: number;
  meaning_ru: string;
  status: string;
  mastery: number | null;
  asset_svg: string | null;
};

export type AnswerOption = {
  radical_id: number;
  label: string;
};

export type TrainingQuestion = {
  radical: Radical;
  options: AnswerOption[];
  option_count: number;
  mastery: number;
};

export type TrainingAnswerOut = {
  is_correct: boolean;
  correct_radical_id: number;
  explanation: string;
  mastery: number;
  next_question: TrainingQuestion | null;
};

export type ProgressSummary = {
  total_radicals: number;
  overview_seen: number;
  average_mastery: number;
  remembered_count: number;
  strong_count: number;
  weak_count: number;
  exams_taken: number;
  exam_accuracy: number | null;
  learning_score_10: number;
  last_score_10: number | null;
};

export type ProgressRadical = {
  radical_id: number;
  number: number;
  character: string;
  meaning_ru: string;
  mastery: number;
  streak: number;
  lapses: number;
  seen_count: number;
  correct_count: number;
  overview_seen_count: number;
};

export type ExamQuestion = {
  attempt_id: number;
  index: number;
  total: number;
  radical: Radical;
  options: AnswerOption[];
};

export type ExamStartOut = {
  attempt_id: number;
  total: number;
  question: ExamQuestion | null;
};

export type ExamAnswerOut = {
  answered_count: number;
  total: number;
  next_question: ExamQuestion | null;
};

export type ExamReviewItem = {
  radical_id: number;
  number: number;
  character: string;
  meaning_ru: string;
  selected_radical_id: number;
  selected_label: string;
  correct_label: string;
  is_correct: boolean;
};

export type ExamFinishOut = {
  attempt_id: number;
  score_10: number;
  correct_count: number;
  total: number;
  weak_radicals: ProgressRadical[];
  review: ExamReviewItem[];
};
