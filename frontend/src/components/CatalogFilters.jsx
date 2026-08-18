import { RotateCcw, Search, SlidersHorizontal, X } from "lucide-react";
import { useState } from "react";
import { useI18n } from "../lib/i18n";
import "./catalog-filters.css";

function SelectFilter({ label, value, onChange, options, allLabel }) {
  return <label className="filter-select"><span>{label}</span><select value={value || ""} onChange={(event) => onChange(event.target.value)}><option value="">{allLabel}</option>{options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>;
}

export default function CatalogFilters({ filters, options, resultCount, totalCount, onChange, onReset, presentialOnly = false, searchSuggestions = [], onSuggestionChoose }) {
  const { t } = useI18n();
  const [suggestionsOpen, setSuggestionsOpen] = useState(false);
  const activeCount = [!presentialOnly && filters.tipo, filters.categoria, filters.modalidade, filters.provincia, filters.nivel, filters.preco, filters.inicio, filters.pagamento, filters.turma].filter(Boolean).length;
  const showClassFilters = presentialOnly || filters.tipo !== "video";
  const chooseSuggestion = (suggestion) => {
    setSuggestionsOpen(false);
    if (onSuggestionChoose?.(suggestion)) return;
    onChange("q", suggestion.query || suggestion.title);
  };

  return <section className="catalog-filter-deck" aria-label={t("filters.title")}>
    <div className="catalog-filter-summary"><div><span className="eyebrow muted"><SlidersHorizontal size={14} /> {t("filters.eyebrow")}</span><strong>{t("filters.title")}</strong><small>{resultCount} {t("catalog.of")} {totalCount} {t("filters.class").toLowerCase()}</small></div><button className="reset-filter" onClick={onReset} disabled={!activeCount && !filters.q}><RotateCcw size={15} /> {t("filters.clear")}</button></div>
    <div className="filter-search-wrap"><div className="filter-search"><Search size={18} /><input value={filters.q} onFocus={() => setSuggestionsOpen(true)} onBlur={() => window.setTimeout(() => setSuggestionsOpen(false), 120)} onChange={(event) => { onChange("q", event.target.value); setSuggestionsOpen(true); }} placeholder="Pesquise cursos, cursos em vídeo ou centros" aria-label="Pesquisar cursos, cursos em vídeo ou centros" aria-autocomplete="list" aria-expanded={suggestionsOpen && searchSuggestions.length > 0} />{filters.q && <button aria-label={t("filters.clear")} onClick={() => onChange("q", "")}><X size={16} /></button>}</div>{suggestionsOpen && searchSuggestions.length > 0 && <div className="catalog-search-suggestions" role="listbox" aria-label="Sugestões de cursos e centros">{searchSuggestions.map((suggestion) => <button key={suggestion.id} type="button" role="option" onMouseDown={(event) => event.preventDefault()} onClick={() => chooseSuggestion(suggestion)}><strong>{suggestion.title}</strong><small>{suggestion.meta}</small></button>)}</div>}</div>
    <div className="filter-group"><span className="filter-group-label">{t("filters.area")}</span><div className="filter-category-row" aria-label={t("filters.area")}><button className={!filters.categoria ? "selected" : ""} onClick={() => onChange("categoria", "")}>{t("filters.allAreas")}</button>{options.categorias.map((categoria) => <button className={filters.categoria === categoria ? "selected" : ""} key={categoria} onClick={() => onChange("categoria", categoria)}>{categoria}</button>)}</div></div>
    <div className="filter-controls-row">
      {!presentialOnly && <SelectFilter label={t("filters.product")} value={filters.tipo} onChange={(value) => onChange("tipo", value)} options={[{ value: "formacao", label: t("filters.class") }, { value: "video", label: t("filters.video") }]} allLabel={t("filters.all")} />}
      {showClassFilters && <SelectFilter label={t("filters.province")} value={filters.provincia} onChange={(value) => onChange("provincia", value)} options={options.provincias.map((item) => ({ value: item, label: item }))} allLabel={t("filters.allF")} />}
      {showClassFilters && <SelectFilter label="Modalidade" value={filters.modalidade} onChange={(value) => onChange("modalidade", value)} options={(options.modalidades || []).map((item) => ({ value: item, label: item }))} allLabel="Todas" />}
      {showClassFilters && <SelectFilter label="Nível" value={filters.nivel} onChange={(value) => onChange("nivel", value)} options={(options.niveis || []).map((item) => ({ value: item, label: item }))} allLabel="Todos" />}
      <SelectFilter label="Preço" value={filters.preco} onChange={(value) => onChange("preco", value)} options={[{ value: "gratuito", label: "Gratuito" }, { value: "ate-25000", label: "Até 25.000 Kz" }, { value: "ate-50000", label: "Até 50.000 Kz" }]} allLabel="Qualquer valor" />
      {showClassFilters && <SelectFilter label="Início" value={filters.inicio} onChange={(value) => onChange("inicio", value)} options={[{ value: "30", label: "Próximos 30 dias" }, { value: "90", label: "Próximos 90 dias" }]} allLabel="Qualquer data" />}
      <SelectFilter label={t("filters.payment")} value={filters.pagamento} onChange={(value) => onChange("pagamento", value)} options={[{ value: "gratuito", label: t("filters.free") }, { value: "sem-pagamento-agora", label: t("filters.noneNow") }, { value: "com-pagamento-agora", label: t("filters.payNow") }]} allLabel={t("filters.all")} />
      {showClassFilters && <label className="filter-checkbox"><input type="checkbox" checked={filters.turma === "aberta"} onChange={(event) => onChange("turma", event.target.checked ? "aberta" : "")} /><span>{t("filters.openClass")}</span></label>}
    </div>
  </section>;
}
