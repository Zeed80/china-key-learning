import { BookOpen, ClipboardCheck, Dumbbell } from "lucide-react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "../api/client";
import type { ProgressRadical, ProgressSummary, RadicalListItem } from "../api/types";
import { RadicalGlyph } from "../components/RadicalGlyph";

export function DashboardPage() {
  const summary = useQuery({ queryKey: ["summary"], queryFn: () => apiFetch<ProgressSummary>("/progress/summary") });
  const radicals = useQuery({ queryKey: ["radicals"], queryFn: () => apiFetch<RadicalListItem[]>("/radicals") });
  const progress = useQuery({
    queryKey: ["progress-radicals"],
    queryFn: () => apiFetch<ProgressRadical[]>("/progress/radicals"),
  });

  const weak = [...(progress.data ?? [])].sort((a, b) => a.mastery - b.mastery).slice(0, 8);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Панель обучения</h1>
          <p>214 ключей, адаптивная выдача, экзамены и редактор контента.</p>
        </div>
      </header>

      <section className="stat-grid">
        <div className="stat">
          <span>Просмотрено</span>
          <strong>
            {summary.data?.overview_seen ?? 0}/{summary.data?.total_radicals ?? 214}
          </strong>
        </div>
        <div className="stat">
          <span>Общий балл</span>
          <strong>{summary.data?.learning_score_10 ?? 0}/10</strong>
        </div>
        <div className="stat">
          <span>Запомнено</span>
          <strong>
            {summary.data?.remembered_count ?? 0}/{summary.data?.total_radicals ?? 214}
          </strong>
        </div>
        <div className="stat">
          <span>Точность экзаменов</span>
          <strong>{summary.data?.exam_accuracy === null || summary.data?.exam_accuracy === undefined ? "—" : `${Math.round(summary.data.exam_accuracy * 100)}%`}</strong>
        </div>
      </section>

      <section className="actions-row">
        <Link className="action" to="/overview">
          <BookOpen size={22} />
          <span>Обзор ключей</span>
        </Link>
        <Link className="action" to="/training">
          <Dumbbell size={22} />
          <span>Тренировка</span>
        </Link>
        <Link className="action" to="/exam">
          <ClipboardCheck size={22} />
          <span>Экзамен</span>
        </Link>
      </section>

      <section className="split">
        <div className="panel">
          <h2>Слабые ключи</h2>
          <div className="weak-list">
            {weak.map((item) => (
              <div className="weak-row" key={item.radical_id}>
                <span className="han-small">{item.character}</span>
                <div>
                  <strong>{item.meaning_ru}</strong>
                  <span>{Math.round(item.mastery * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="panel">
          <h2>Карта ключей ({radicals.data?.length ?? 0})</h2>
          <div className="radical-grid compact">
            {(radicals.data ?? []).map((item) => (
              <div className="tile" key={item.id} title={`${item.number}. ${item.meaning_ru}`}>
                <RadicalGlyph radical={item} size="sm" />
                <span>{Math.round((item.mastery ?? 0) * 100)}%</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
