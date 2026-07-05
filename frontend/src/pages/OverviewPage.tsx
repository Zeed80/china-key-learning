import { ArrowRight, Check, ChevronLeft, ChevronRight, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch, jsonBody } from "../api/client";
import type { Radical, RadicalConfusable, RadicalExample, RadicalListItem } from "../api/types";
import { RadicalGlyph } from "../components/RadicalGlyph";

export function OverviewPage() {
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [search, setSearch] = useState("");

  const nextQuery = useQuery({
    queryKey: ["overview-next"],
    queryFn: () => apiFetch<Radical | null>("/study/overview/next"),
  });
  const radicalsQuery = useQuery({
    queryKey: ["radicals"],
    queryFn: () => apiFetch<RadicalListItem[]>("/radicals"),
  });
  const detailQuery = useQuery({
    queryKey: ["radical-detail", selectedId],
    queryFn: () => apiFetch<Radical>(`/radicals/${selectedId}`),
    enabled: selectedId !== null,
  });

  const selectedIndex = useMemo(() => {
    return (radicalsQuery.data ?? []).findIndex((item) => item.id === selectedId);
  }, [radicalsQuery.data, selectedId]);

  function selectByIndex(index: number) {
    const items = radicalsQuery.data ?? [];
    if (!items.length) return;
    const safeIndex = (index + items.length) % items.length;
    setSelectedId(items[safeIndex].id);
  }

  function selectRelative(delta: number) {
    const items = radicalsQuery.data ?? [];
    if (!items.length) return;
    const current = selectedIndex >= 0 ? selectedIndex : 0;
    selectByIndex(current + delta);
  }

  useEffect(() => {
    if (selectedId === null && nextQuery.data?.id) {
      setSelectedId(nextQuery.data.id);
    }
  }, [nextQuery.data?.id, selectedId]);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      if (target?.tagName === "INPUT" || target?.tagName === "TEXTAREA" || target?.tagName === "SELECT") return;
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        selectRelative(-1);
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        selectRelative(1);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [radicalsQuery.data, selectedIndex]);

  const filteredRadicals = useMemo(() => {
    const value = search.trim().toLowerCase();
    const items = radicalsQuery.data ?? [];
    if (!value) return items;
    return items.filter((item) => {
      return (
        item.character.includes(value) ||
        item.meaning_ru.toLowerCase().includes(value) ||
        String(item.number) === value ||
        String(item.strokes) === value
      );
    });
  }, [radicalsQuery.data, search]);

  const seen = useMutation({
    mutationFn: (radicalId: number) =>
      apiFetch<Radical>("/study/overview/seen", { method: "POST", ...jsonBody({ radical_id: radicalId }) }),
    onSuccess: async () => {
      setSelectedId(null);
      await queryClient.invalidateQueries({ queryKey: ["overview-next"] });
      await queryClient.invalidateQueries({ queryKey: ["summary"] });
      await queryClient.invalidateQueries({ queryKey: ["radicals"] });
    },
  });

  const radical = detailQuery.data ?? (selectedId === nextQuery.data?.id ? nextQuery.data : null);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Ключи</h1>
          <p>Полный каталог 214 ключей с фокусом на форму, смысл и похожие начертания.</p>
        </div>
        {radical && radicalsQuery.data ? (
          <div className="top-controls">
            <button className="icon-button" onClick={() => selectRelative(-1)} type="button" aria-label="Предыдущий ключ" title="Предыдущий ключ">
              <ChevronLeft size={20} />
            </button>
            <span>
              {selectedIndex + 1}/{radicalsQuery.data.length}
            </span>
            <button className="icon-button" onClick={() => selectRelative(1)} type="button" aria-label="Следующий ключ" title="Следующий ключ">
              <ChevronRight size={20} />
            </button>
            <button className="primary" disabled={seen.isPending} onClick={() => seen.mutate(radical.id)} type="button">
              <Check size={18} /> Просмотрен
            </button>
          </div>
        ) : null}
      </header>

      <section className="radical-stage">
        <aside className="catalog-panel">
          <div className="catalog-toolbar">
            <div className="catalog-search">
              <Search size={18} />
              <input
                aria-label="Поиск ключа"
                placeholder="Номер, ключ, значение, черты"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>
            <span className="catalog-count">
              {filteredRadicals.length}/{radicalsQuery.data?.length ?? 214}
            </span>
          </div>
          <div className="catalog-list" aria-label="Каталог ключей">
            {filteredRadicals.map((item) => (
              <button
                className={item.id === selectedId ? "active" : ""}
                key={item.id}
                onClick={() => setSelectedId(item.id)}
                type="button"
                aria-label={`${item.number}. ${item.character}: ${item.meaning_ru}`}
                aria-current={item.id === selectedId ? "true" : undefined}
                title={`${item.number}. ${item.character}: ${item.meaning_ru}`}
              >
                <span className="catalog-number">{item.number}</span>
                <span className="han-small">{item.character}</span>
              </button>
            ))}
          </div>
        </aside>

        {radical ? (
          <section className="focus-layout" aria-live="polite">
            <div className="focus-glyph">
              <button className="hero-nav prev" onClick={() => selectRelative(-1)} type="button" aria-label="Предыдущий ключ" title="Предыдущий ключ">
                <ChevronLeft size={24} />
              </button>
              <RadicalGlyph radical={radical} size="lg" />
              <button className="hero-nav next" onClick={() => selectRelative(1)} type="button" aria-label="Следующий ключ" title="Следующий ключ">
                <ChevronRight size={24} />
              </button>
              <div className="radical-meta">
                <span>№ {radical.number}</span>
                <span>{radical.strokes} черт</span>
                <span>{Math.round(((radicalsQuery.data ?? [])[selectedIndex]?.mastery ?? 0) * 100)}%</span>
              </div>
              <VariantStrip radical={radical} />
            </div>

            <article className="focus-summary">
              <span className="focus-kicker">Ключ {radical.number}</span>
              <h2>{radical.meaning_ru}</h2>
              <p className="memory-cue">{radical.mnemonic_ru}</p>
              <p>{radical.description_ru}</p>
              <p className="usage-line">{radical.usage_ru}</p>
            </article>

            <ConfusableBlock current={radical.character} confusables={radical.confusables} />
            <ExampleBlock radical={radical} examples={radical.examples} />
            <FormsBlock radical={radical} />

            <div className="focus-actions">
              <button className="secondary" disabled={seen.isPending} onClick={() => seen.mutate(radical.id)} type="button">
                Далее <ArrowRight size={18} />
              </button>
            </div>
          </section>
        ) : nextQuery.isLoading || detailQuery.isLoading ? (
          <div className="panel">Загрузка</div>
        ) : (
          <div className="panel">Ключи не найдены. Запустите seed backend.</div>
        )}
      </section>
    </div>
  );
}

function VariantStrip({ radical }: { radical: Radical }) {
  const forms = [radical.character, ...radical.variants.map((item) => item.form)];
  const uniqueForms = Array.from(new Set(forms)).slice(0, 6);
  return (
    <div className="variant-strip">
      {uniqueForms.map((form) => (
        <span key={form}>{form}</span>
      ))}
    </div>
  );
}

function ExampleBlock({ radical, examples }: { radical: Radical; examples: RadicalExample[] }) {
  const forms = radicalForms(radical);
  const visible = examples.slice(0, 6);
  return (
    <div className="example-block">
      <div className="section-title">
        <h3>Примеры</h3>
        <span>{examples.length}</span>
      </div>
      {visible.length ? (
        <div className="example-list">
          {visible.map((item) => (
            <article className="example-card" key={`${item.character}-${item.pinyin}-${item.translation_ru}`}>
              <div className="example-head">
                <span className="example-character">
                  <HighlightForms text={item.character} forms={forms} />
                </span>
                <div>
                  <strong>{item.translation_ru}</strong>
                  <span>{item.pinyin || "pinyin уточняется"}</span>
                </div>
              </div>
              <p>
                <HighlightForms text={item.note_ru} forms={forms} />
              </p>
              {item.sentence_zh || item.sentence_ru ? (
                <div className="sentence-box">
                  <strong>
                    <HighlightForms text={item.sentence_zh} forms={forms} />
                  </strong>
                  <span>{item.sentence_pinyin}</span>
                  <span>
                    <HighlightForms text={item.sentence_ru} forms={forms} />
                  </span>
                </div>
              ) : null}
            </article>
          ))}
        </div>
      ) : (
        <span className="muted">Примеры еще не добавлены.</span>
      )}
    </div>
  );
}

function radicalForms(radical: Radical): string[] {
  return Array.from(new Set([radical.character, ...radical.variants.map((item) => item.form)])).sort((a, b) => b.length - a.length);
}

function HighlightForms({ text, forms }: { text: string; forms: string[] }) {
  if (!text || !forms.length) return <>{text}</>;
  const escaped = forms.map((form) => form.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const pattern = new RegExp(`(${escaped.join("|")})`, "g");
  return (
    <>
      {text.split(pattern).map((part, index) =>
        forms.includes(part) ? (
          <mark className="radical-mark" key={`${part}-${index}`}>
            {part}
          </mark>
        ) : (
          <span key={`${part}-${index}`}>{part}</span>
        ),
      )}
    </>
  );
}

function ConfusableBlock({ current, confusables }: { current: string; confusables: RadicalConfusable[] }) {
  const visible = confusables.slice(0, 2);
  return (
    <div className="confusable-block">
      <div className="section-title">
        <h3>Отличия</h3>
        <span>{confusables.length}</span>
      </div>
      {visible.length ? (
        <div className="confusable-list">
          {visible.map((item) => (
            <article className="confusable-card" key={`${current}-${item.other_form}-${item.note_ru}`}>
              <div className="confusable-pair">
                <span>{current}</span>
                <i />
                <span>{item.other_form}</span>
              </div>
              <p>
                <MarkedText text={item.note_ru} />
              </p>
            </article>
          ))}
        </div>
      ) : (
        <span className="muted">Похожие формы еще не добавлены.</span>
      )}
    </div>
  );
}

function MarkedText({ text }: { text: string }) {
  const marked = text.includes("[[") ? text.split(/(\[\[.*?\]\])/g) : autoMark(text);
  return (
    <>
      {marked.map((part, index) => {
        const explicit = part.startsWith("[[") && part.endsWith("]]");
        const auto = part.startsWith("__MARK__");
        if (explicit || auto) {
          const clean = explicit ? part.slice(2, -2) : part.replace("__MARK__", "");
          return (
            <mark className="diff-mark" key={`${part}-${index}`}>
              {clean}
            </mark>
          );
        }
        return <span key={`${part}-${index}`}>{part}</span>;
      })}
    </>
  );
}

export function autoMark(text: string): string[] {
  const patterns = [
    "нижняя горизонталь",
    "верхняя горизонталь",
    "три точки",
    "две точки",
    "дополнительный штрих",
    "внешняя рамка",
    "маленький рот",
    "левая форма",
    "правая форма",
    "слева",
    "справа",
    "шире",
    "уже",
  ];
  let parts = [text];
  for (const pattern of patterns) {
    parts = parts.flatMap((part) => {
      if (part.startsWith("__MARK__")) return [part];
      const next: string[] = [];
      let rest = part;
      let idx = rest.toLowerCase().indexOf(pattern.toLowerCase());
      while (idx >= 0) {
        if (idx > 0) next.push(rest.slice(0, idx));
        next.push(`__MARK__${rest.slice(idx, idx + pattern.length)}`);
        rest = rest.slice(idx + pattern.length);
        idx = rest.toLowerCase().indexOf(pattern.toLowerCase());
      }
      if (rest) next.push(rest);
      return next;
    });
  }
  return parts;
}

function FormsBlock({ radical }: { radical: Radical }) {
  const forms = [
    { form: radical.character, position: "base", note_ru: "Базовая форма ключа." },
    ...radical.variants,
  ].slice(0, 6);
  return (
    <div className="info-block forms-block">
      <div className="section-title">
        <h3>Формы</h3>
        <span>{forms.length}</span>
      </div>
      {forms.length ? (
        <div className="form-list">
          {forms.map((item) => (
            <article className="form-card" key={`${item.form}-${item.position}`}>
              <span>{item.form}</span>
              <div>
                <strong>{positionLabel(item.position)}</strong>
                <p>{item.note_ru}</p>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <span className="muted">Нет данных</span>
      )}
    </div>
  );
}

function positionLabel(position: string) {
  const labels: Record<string, string> = {
    base: "основа",
    left: "слева",
    right: "справа",
    top: "сверху",
    bottom: "снизу",
    enclosure: "рамка",
    any: "вариант",
  };
  return labels[position] ?? position;
}
