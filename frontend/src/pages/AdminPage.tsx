import { Save } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch, jsonBody } from "../api/client";
import { useAuth } from "../api/auth";
import type { ConfusableInput, ExampleInput, Radical, VariantInput } from "./adminTypes";

type Editable = {
  meaning_ru: string;
  meaning_en: string;
  description_ru: string;
  mnemonic_ru: string;
  usage_ru: string;
  status: string;
  variantsText: string;
  examplesText: string;
  confusablesText: string;
};

export function AdminPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [form, setForm] = useState<Editable | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const radicals = useQuery({ queryKey: ["admin-radicals"], queryFn: () => apiFetch<Radical[]>("/admin/radicals") });
  const selected = useMemo(
    () => radicals.data?.find((item) => item.id === selectedId) ?? radicals.data?.[0] ?? null,
    [radicals.data, selectedId],
  );

  useEffect(() => {
    if (!selected) return;
    setSelectedId(selected.id);
    setForm({
      meaning_ru: selected.meaning_ru,
      meaning_en: selected.meaning_en,
      description_ru: selected.description_ru,
      mnemonic_ru: selected.mnemonic_ru,
      usage_ru: selected.usage_ru,
      status: selected.status,
      variantsText: selected.variants.map((item) => `${item.form}|${item.variant_type}|${item.position}|${item.note_ru}`).join("\n"),
      examplesText: selected.examples
        .map(
          (item) =>
            `${item.character}|${item.pinyin}|${item.translation_ru}|${item.note_ru}|${item.sentence_zh}|${item.sentence_pinyin}|${item.sentence_ru}`,
        )
        .join("\n"),
      confusablesText: selected.confusables.map((item) => `${item.other_form}|${item.note_ru}`).join("\n"),
    });
  }, [selected?.id]);

  const save = useMutation({
    mutationFn: async () => {
      if (!selected || !form) return null;
      await apiFetch<Radical>(`/admin/radicals/${selected.id}`, {
        method: "PATCH",
        ...jsonBody({
          meaning_ru: form.meaning_ru,
          meaning_en: form.meaning_en,
          description_ru: form.description_ru,
          mnemonic_ru: form.mnemonic_ru,
          usage_ru: form.usage_ru,
          status: form.status,
        }),
      });
      await apiFetch<Radical>(`/admin/radicals/${selected.id}/variants`, {
        method: "PUT",
        ...jsonBody(parseVariants(form.variantsText)),
      });
      await apiFetch<Radical>(`/admin/radicals/${selected.id}/examples`, {
        method: "PUT",
        ...jsonBody(parseExamples(form.examplesText)),
      });
      return apiFetch<Radical>(`/admin/radicals/${selected.id}/confusables`, {
        method: "PUT",
        ...jsonBody(parseConfusables(form.confusablesText)),
      });
    },
    onSuccess: async () => {
      setMessage("Сохранено");
      await queryClient.invalidateQueries({ queryKey: ["admin-radicals"] });
      await queryClient.invalidateQueries({ queryKey: ["radicals"] });
    },
    onError: (err) => setMessage(err instanceof Error ? err.message : "Ошибка сохранения"),
  });

  if (user?.role !== "admin") {
    return (
      <div className="page">
        <div className="panel">Нужна роль admin.</div>
      </div>
    );
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    save.mutate();
  }

  return (
    <div className="page admin-page">
      <header className="page-header">
        <div>
          <h1>Админка контента</h1>
          <p>Редактирование карточек, вариантов, примеров и похожих форм.</p>
        </div>
      </header>
      <section className="admin-layout">
        <aside className="admin-list">
          {(radicals.data ?? []).map((item) => (
            <button
              className={item.id === selected?.id ? "active" : ""}
              key={item.id}
              onClick={() => setSelectedId(item.id)}
              type="button"
            >
              <span className="han-small">{item.character}</span>
              <span>
                {item.number}. {item.meaning_ru}
              </span>
            </button>
          ))}
        </aside>
        {form && selected ? (
          <form className="editor form" onSubmit={submit}>
            <div className="editor-title">
              <span className="han-large">{selected.character}</span>
              <strong>№ {selected.number}</strong>
            </div>
            <label>
              Значение RU
              <input value={form.meaning_ru} onChange={(event) => setForm({ ...form, meaning_ru: event.target.value })} />
            </label>
            <label>
              Meaning EN
              <input value={form.meaning_en} onChange={(event) => setForm({ ...form, meaning_en: event.target.value })} />
            </label>
            <label>
              Описание
              <textarea
                value={form.description_ru}
                onChange={(event) => setForm({ ...form, description_ru: event.target.value })}
                rows={4}
              />
            </label>
            <label>
              Мнемоника
              <textarea
                value={form.mnemonic_ru}
                onChange={(event) => setForm({ ...form, mnemonic_ru: event.target.value })}
                rows={3}
              />
            </label>
            <label>
              Использование
              <textarea value={form.usage_ru} onChange={(event) => setForm({ ...form, usage_ru: event.target.value })} rows={3} />
            </label>
            <label>
              Статус
              <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })}>
                <option value="draft">draft</option>
                <option value="reviewed">reviewed</option>
                <option value="verified">verified</option>
              </select>
            </label>
            <label>
              Варианты: form|type|position|note
              <textarea
                value={form.variantsText}
                onChange={(event) => setForm({ ...form, variantsText: event.target.value })}
                rows={5}
              />
            </label>
            <label>
              Примеры: character|pinyin|translation|analysis|sentence_zh|sentence_pinyin|sentence_ru
              <textarea
                value={form.examplesText}
                onChange={(event) => setForm({ ...form, examplesText: event.target.value })}
                rows={5}
              />
            </label>
            <label>
              Похожие: form|note
              <textarea
                value={form.confusablesText}
                onChange={(event) => setForm({ ...form, confusablesText: event.target.value })}
                rows={5}
              />
            </label>
            {message ? <div className={message === "Сохранено" ? "success" : "error"}>{message}</div> : null}
            <button className="primary" disabled={save.isPending} type="submit">
              <Save size={18} /> Сохранить
            </button>
          </form>
        ) : (
          <div className="panel">Загрузка</div>
        )}
      </section>
    </div>
  );
}

function splitLines(text: string): string[][] {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => line.split("|").map((item) => item.trim()));
}

function parseVariants(text: string): VariantInput[] {
  return splitLines(text).map(([form, variant_type = "alternate", position = "any", note_ru = ""]) => ({
    form,
    variant_type,
    position,
    note_ru,
  }));
}

function parseExamples(text: string): ExampleInput[] {
  return splitLines(text).map(([character, pinyin = "", translation_ru = "", note_ru = "", sentence_zh = "", sentence_pinyin = "", sentence_ru = ""]) => ({
    character,
    pinyin,
    translation_ru,
    note_ru,
    sentence_zh,
    sentence_pinyin,
    sentence_ru,
  }));
}

function parseConfusables(text: string): ConfusableInput[] {
  return splitLines(text).map(([other_form, note_ru = ""]) => ({ other_form, note_ru }));
}
