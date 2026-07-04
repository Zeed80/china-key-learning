from pydantic import BaseModel

from app.schemas.radical import RadicalRead


class AnswerOption(BaseModel):
    radical_id: int
    label: str


class TrainingQuestion(BaseModel):
    radical: RadicalRead
    options: list[AnswerOption]
    option_count: int
    mastery: float


class TrainingAnswerIn(BaseModel):
    radical_id: int
    selected_radical_id: int


class TrainingAnswerOut(BaseModel):
    is_correct: bool
    correct_radical_id: int
    explanation: str
    mastery: float
    next_question: TrainingQuestion | None = None


class OverviewSeenIn(BaseModel):
    radical_id: int


class ProgressRadical(BaseModel):
    radical_id: int
    number: int
    character: str
    meaning_ru: str
    mastery: float
    streak: int
    lapses: int
    seen_count: int
    correct_count: int
    overview_seen_count: int


class ProgressSummary(BaseModel):
    total_radicals: int
    overview_seen: int
    average_mastery: float
    remembered_count: int
    strong_count: int
    weak_count: int
    exams_taken: int
    exam_accuracy: float | None
    learning_score_10: float
    last_score_10: float | None


class ExamQuestion(BaseModel):
    attempt_id: int
    index: int
    total: int
    radical: RadicalRead
    options: list[AnswerOption]


class ExamStartOut(BaseModel):
    attempt_id: int
    total: int
    question: ExamQuestion | None


class ExamAnswerIn(BaseModel):
    radical_id: int
    selected_radical_id: int


class ExamAnswerOut(BaseModel):
    answered_count: int
    total: int
    next_question: ExamQuestion | None


class ExamReviewItem(BaseModel):
    radical_id: int
    number: int
    character: str
    meaning_ru: str
    selected_radical_id: int
    selected_label: str
    correct_label: str
    is_correct: bool


class ExamFinishOut(BaseModel):
    attempt_id: int
    score_10: float
    correct_count: int
    total: int
    weak_radicals: list[ProgressRadical]
    review: list[ExamReviewItem]
