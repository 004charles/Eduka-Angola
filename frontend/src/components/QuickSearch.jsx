import { ArrowRight, Search, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useI18n } from "../lib/i18n";
import "./quick-search.css";

export default function QuickSearch({ onClose, onNavigate, suggestions = [] }) {
  const { t } = useI18n();
  const [query, setQuery] = useState("");
  const inputRef = useRef(null);
  const popular = [...new Set(suggestions.map((course) => course.titulo || course.title).filter(Boolean))].slice(0, 3);
  useEffect(() => { inputRef.current?.focus(); const closeOnEscape = (event) => { if (event.key === "Escape") onClose(); }; window.addEventListener("keydown", closeOnEscape); return () => window.removeEventListener("keydown", closeOnEscape); }, [onClose]);
  const submit = (event) => { event.preventDefault(); const value = query.trim(); onNavigate(`/cursos${value ? `?q=${encodeURIComponent(value)}` : ""}`); onClose(); };
  const chooseSuggestion = (value) => { onNavigate(`/cursos?q=${encodeURIComponent(value)}`); onClose(); };
  return <div className="quick-search-layer" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}><section className="quick-search-panel" role="dialog" aria-modal="true" aria-label={t("search.dialog")}><div className="quick-search-head"><div><span className="eyebrow">{t("search.eyebrow")}</span><strong>{t("search.title")}</strong></div><button onClick={onClose} aria-label={t("search.close")}><X size={19} /></button></div><form onSubmit={submit} className="quick-search-form"><Search size={20} /><input ref={inputRef} value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t("search.placeholder")} aria-label={t("search.dialog")} /><button type="submit">{t("search.submit")} <ArrowRight size={16} /></button></form><div className="quick-search-foot"><div><span>{t("search.try")}</span>{popular.length ? popular.map((item) => <button key={item} onClick={() => chooseSuggestion(item)}>{item}</button>) : <button onClick={() => chooseSuggestion("Informática")}>Informática</button>}</div><small><kbd>Esc</kbd> {t("search.escape")}</small></div></section></div>;
}
