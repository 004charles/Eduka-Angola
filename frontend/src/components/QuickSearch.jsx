import { ArrowRight, Search, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useI18n } from "../lib/i18n";
import "./quick-search.css";

export default function QuickSearch({ onClose, onNavigate, suggestions = [] }) {
  const { t } = useI18n();
  const [query, setQuery] = useState("");
  const inputRef = useRef(null);
  const normaliseSuggestion = (item) => ({
    ...item,
    title: item.titulo || item.title || item.nome || "",
    type: item.tipo_pesquisa || (item.video_slug || item.is_video ? "video" : item.perfil_url || item.total_cursos !== undefined ? "center" : "course"),
  });
  const entries = suggestions.map(normaliseSuggestion).filter((item) => item.title);
  const popular = entries.slice(0, 4);
  const normalisedQuery = query.trim().toLocaleLowerCase("pt-PT").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const matching = normalisedQuery.length < 2 ? popular : entries.filter((item) => `${item.title} ${item.categoria || ""} ${item.centro || ""} ${item.cidade || ""} ${item.provincia || ""}`.toLocaleLowerCase("pt-PT").normalize("NFD").replace(/[\u0300-\u036f]/g, "").includes(normalisedQuery)).slice(0, 7);
  useEffect(() => { inputRef.current?.focus(); const closeOnEscape = (event) => { if (event.key === "Escape") onClose(); }; window.addEventListener("keydown", closeOnEscape); return () => window.removeEventListener("keydown", closeOnEscape); }, [onClose]);
  const submit = (event) => { event.preventDefault(); const value = query.trim(); onNavigate(`/cursos${value ? `?q=${encodeURIComponent(value)}` : ""}`); onClose(); };
  const chooseSuggestion = (item) => { if (item.type === "center") onNavigate(`/centros/${item.id}`); else if (item.type === "video") onNavigate(`/video-cursos/${item.video_slug || item.slug}`); else onNavigate(`/cursos/${item.id}`); onClose(); };
  const label = (item) => item.type === "center" ? "Centro de formação" : item.type === "video" ? "Curso em vídeo" : "Formação presencial";
  return <div className="quick-search-layer" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}><section className="quick-search-panel" role="dialog" aria-modal="true" aria-label={t("search.dialog")}><div className="quick-search-head"><div><span className="eyebrow">{t("search.eyebrow")}</span><strong>{t("search.title")}</strong></div><button onClick={onClose} aria-label={t("search.close")}><X size={19} /></button></div><form onSubmit={submit} className="quick-search-form"><Search size={20} /><input ref={inputRef} value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Pesquise cursos, cursos em vídeo ou centros" aria-label={t("search.dialog")} aria-autocomplete="list" /><button type="submit">{t("search.submit")} <ArrowRight size={16} /></button></form><div className="quick-search-foot"><div><span>{normalisedQuery.length >= 2 ? "Sugestões da Edukangola" : t("search.try")}</span>{matching.length ? matching.map((item) => <button key={`${item.type}-${item.id}`} onClick={() => chooseSuggestion(item)}><b>{item.title}</b><small>{label(item)}{item.centro ? ` · ${item.centro}` : ""}{item.cidade ? ` · ${item.cidade}` : ""}</small></button>) : <small>Nenhum curso ou centro corresponde à pesquisa.</small>}</div><small><kbd>Esc</kbd> {t("search.escape")}</small></div></section></div>;
}
