import { ClipboardCheck, RotateCcw } from "lucide-react";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { apiFetch, jsonBody } from "../api/client";
import type { ExamAnswerOut, ExamFinishOut, ExamQuestion, ExamStartOut } from "../api/types";
import { RadicalGlyph } from "../components/RadicalGlyph";

export function ExamPage() {
  const [attemptId, setAttemptId] = useState<number | null>(null);
  const [question, setQuestion] = useState<ExamQuestion | null>(null);
  const [answeredCount, setAnsweredCount] = useState(0);
  const [result, setResult] = useState<ExamFinishOut | null>(null);

  const finish = useMutation({
    mutationFn: (id: number) => apiFetch<ExamFinishOut>(`/exams/${id}/finish`, { method: "POST" }),
    onSuccess: setResult,
  });

  const start = useMutation({
    mutationFn: () => apiFetch<ExamStartOut>("/exams/start", { method: "POST" }),
    onSuccess: (data) => {
      setAttemptId(data.attempt_id);
      setQuestion(data.question);
      setAnsweredCount(0);
      setResult(null);
    },
  });

  const answer = useMutation({
    mutationFn: (selectedId: number) =>
      apiFetch<ExamAnswerOut>(`/exams/${attemptId}/answer`, {
        method: "POST",
        ...jsonBody({ radical_id: question?.radical.id, selected_radical_id: selectedId }),
      }),
    onSuccess: (data) => {
      setAnsweredCount(data.answered_count);
      setQuestion(data.next_question);
      if (!data.next_question && attemptId) {
        finish.mutate(attemptId);
      }
    },
  });

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Экзамен</h1>
          <p>20 вопросов без подсказок; разбор правильных ответов появится после завершения.</p>
        </div>
        <button className="primary" onClick={() => start.mutate()} type="button">
          {attemptId ? <RotateCcw size={18} /> : <ClipboardCheck size={18} />}
          {attemptId ? "Начать заново" : "Начать"}
        </button>
      </header>

      {question ? (
        <section className="drill-card exam">
          <div className="progress-line">
            <span>
              {question.index}/{question.total}
            </span>
            <div>
              <i style={{ width: `${((answeredCount || question.index - 1) / question.total) * 100}%` }} />
            </div>
          </div>
          <RadicalGlyph radical={question.radical} size="lg" />
          <div className="option-grid">
            {question.options.map((option) => (
              <button
                key={option.radical_id}
                className="option"
                disabled={answer.isPending}
                onClick={() => answer.mutate(option.radical_id)}
                type="button"
              >
                {option.label}
              </button>
            ))}
          </div>
        </section>
      ) : result ? (
        <section className="panel result-panel">
          <h2>
            {result.correct_count}/{result.total}
          </h2>
          <p>
            Экзамен завершен. Правильные ответы ниже; общий 10-балльный показатель считается на панели обучения.
          </p>
          <div className="exam-review">
            {result.review.map((item) => (
              <article className={`review-row ${item.is_correct ? "ok" : "bad"}`} key={`${item.radical_id}-${item.selected_radical_id}`}>
                <span className="han-small">{item.character}</span>
                <div>
                  <strong>
                    № {item.number} · {item.meaning_ru}
                  </strong>
                  <span>Ваш ответ: {item.selected_label}</span>
                  {!item.is_correct ? <span>Правильно: {item.correct_label}</span> : null}
                </div>
              </article>
            ))}
          </div>
          <h3>Повторить в первую очередь</h3>
          <div className="weak-list">
            {result.weak_radicals.slice(0, 6).map((item) => (
              <div className="weak-row" key={item.radical_id}>
                <span className="han-small">{item.character}</span>
                <div>
                  <strong>{item.meaning_ru}</strong>
                  <span>{Math.round(item.mastery * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : (
        <div className="panel">Нажмите «Начать».</div>
      )}
    </div>
  );
}
