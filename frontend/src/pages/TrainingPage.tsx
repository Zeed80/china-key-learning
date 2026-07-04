import { ArrowRight, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { apiFetch, jsonBody } from "../api/client";
import type { TrainingAnswerOut, TrainingQuestion } from "../api/types";
import { RadicalGlyph } from "../components/RadicalGlyph";

export function TrainingPage() {
  const [question, setQuestion] = useState<TrainingQuestion | null>(null);
  const [feedback, setFeedback] = useState<TrainingAnswerOut | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const next = useMutation({
    mutationFn: () => apiFetch<TrainingQuestion>("/training/next", { method: "POST" }),
    onSuccess: (data) => {
      setQuestion(data);
      setFeedback(null);
      setSelectedId(null);
    },
  });

  const answer = useMutation({
    mutationFn: (selectedId: number) =>
      apiFetch<TrainingAnswerOut>("/training/answer", {
        method: "POST",
        ...jsonBody({ radical_id: question?.radical.id, selected_radical_id: selectedId }),
      }),
    onSuccess: (data) => {
      setFeedback(data);
    },
  });

  useEffect(() => {
    if (!question && !next.isPending) next.mutate();
  }, []);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      if (target?.tagName === "INPUT" || target?.tagName === "TEXTAREA" || target?.tagName === "SELECT") return;
      if (!feedback || next.isPending) return;
      if (event.key === " " || event.key === "ArrowRight" || event.key === "ArrowLeft") {
        event.preventDefault();
        next.mutate();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [feedback, next.isPending]);

  function chooseAnswer(radicalId: number) {
    if (feedback || answer.isPending) return;
    setSelectedId(radicalId);
    answer.mutate(radicalId);
  }

  function optionClass(radicalId: number) {
    if (!feedback) return "option";
    if (radicalId === feedback.correct_radical_id) return "option correct";
    if (radicalId === selectedId) return "option wrong";
    return "option dimmed";
  }

  return (
    <div className="page drill-page">
      <header className="page-header">
        <div>
          <h1>Тренировка</h1>
          <p>Количество вариантов растет вместе с уверенностью по ключу.</p>
        </div>
        <button className="secondary" onClick={() => next.mutate()} type="button">
          <RotateCcw size={18} /> Новый ключ
        </button>
      </header>

      {question ? (
        <section className="drill-card">
          <div className="drill-topline">
            <span>№ {question.radical.number}</span>
            <span>mastery {Math.round(question.mastery * 100)}%</span>
            <span>{question.option_count} варианта</span>
          </div>
          <RadicalGlyph radical={question.radical} size="lg" />
          <div className="option-grid">
            {question.options.map((option) => (
              <button
                key={option.radical_id}
                className={optionClass(option.radical_id)}
                disabled={answer.isPending || Boolean(feedback)}
                onClick={() => chooseAnswer(option.radical_id)}
                type="button"
              >
                {option.label}
              </button>
            ))}
          </div>
        </section>
      ) : (
        <div className="panel">Загрузка</div>
      )}

      {feedback ? (
        <div className={`feedback ${feedback.is_correct ? "ok" : "bad"}`}>
          <strong>{feedback.is_correct ? "Верно" : "Ошибка"}</strong>
          <span>{feedback.explanation}</span>
          <button className="primary" disabled={next.isPending} onClick={() => next.mutate()} type="button">
            Далее <ArrowRight size={18} />
          </button>
        </div>
      ) : null}
    </div>
  );
}
