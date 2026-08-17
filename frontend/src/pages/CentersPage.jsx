import { useEffect, useMemo, useState } from "react";
import { ArrowRight, BookOpenCheck, Building2, CheckCircle2, Filter, Globe2, MapPin, Search, ShieldCheck, UsersRound } from "lucide-react";
import "./public-pages.css";

function displayName(name) { return name?.replace(/Eduka-Angola/gi, "Edukangola") || "Centro de formação"; }
function safeImageUrl(url) { if (!url) return null; try { const parsed = new URL(url, window.location.origin); return parsed.origin === window.location.origin ? parsed.href : `${parsed.pathname}${parsed.search}`; } catch { return url; } }
function totalCourses(centre) { return Number(centre.total_cursos || 0); }
const CENTRE_FALLBACK_COVERS = ["/static/img/banners/training_center_lab_1_1769959754699.png", "/static/img/banners/training_center_student_3_1769959820838.png", "/static/img/banners/training_center_workshop_2_1769959789358.png"];
function centreCover(centre) { return safeImageUrl(centre.banner_url) || CENTRE_FALLBACK_COVERS[Number(centre.id || 0) % CENTRE_FALLBACK_COVERS.length]; }
function centreLocation(centre) { return centre.localizacao || [centre.cidade, centre.provincia, centre.is_internacional ? centre.pais_nome : ""].filter(Boolean).join(", "); }
function mapsSearchUrl(centre) { const query = [centre.endereco, centre.cidade, centre.provincia, centre.pais_nome].filter(Boolean).join(", "); return query ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}` : ""; }
function normalise(value) { return String(value || "").toLocaleLowerCase("pt-PT").normalize("NFD").replace(/[\u0300-\u036f]/g, ""); }

export default function CentersPage({ data, loading: homeLoading, onNavigate }) {
  const [centres, setCentres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [country, setCountry] = useState("");
  const [province, setProvince] = useState("");
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [locationSuggestionsOpen, setLocationSuggestionsOpen] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 7;

  useEffect(() => {
    let active = true;
    fetch("/api/v1/centros/")
      .then((response) => response.ok ? response.json() : Promise.reject(new Error("Falha ao carregar centros")))
      .then((payload) => { const rows = Array.isArray(payload) ? payload : payload.results || []; if (active) setCentres(rows); })
      .catch(() => { if (active) setCentres(data?.centros || data?.centros_destaque || []); })
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [data]);

  const countries = useMemo(() => [...new Map(centres.filter((centre) => centre.pais).map((centre) => [centre.pais, centre.pais_nome || centre.pais])).entries()].sort(([codeA, nameA], [codeB, nameB]) => (codeA === "AO" ? -1 : codeB === "AO" ? 1 : nameA.localeCompare(nameB))), [centres]);
  const provinces = useMemo(() => [...new Set(centres.filter((centre) => !country || centre.pais === country).map((centre) => centre.provincia).filter(Boolean))].sort((a, b) => a.localeCompare(b)), [centres, country]);
  const provinceCounts = useMemo(() => provinces.map((name) => ({ name, count: centres.filter((centre) => (!country || centre.pais === country) && centre.provincia === name).length })), [centres, provinces, country]);
  const locationSuggestions = useMemo(() => {
    const term = normalise(search.trim());
    if (term.length < 2) return [];
    const cities = new Map();
    centres.forEach((centre) => {
      if (centre.cidade && normalise(`${centre.cidade} ${centre.provincia} ${centre.pais_nome}`).includes(term)) {
        const key = `${centre.cidade}-${centre.provincia}-${centre.pais}`;
        if (!cities.has(key)) cities.set(key, { key, cidade: centre.cidade, provincia: centre.provincia, pais: centre.pais_nome });
      }
    });
    return [...cities.values()].slice(0, 5);
  }, [centres, search]);
  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();
    return centres.filter((centre) => {
      const matchesTerm = !term || [centre.nome, centre.cidade, centre.provincia, centre.pais_nome, centre.endereco, ...(centre.modalidades || [])].join(" ").toLowerCase().includes(term);
      return matchesTerm && (!country || centre.pais === country) && (!province || centre.provincia === province) && (!verifiedOnly || centre.verificado);
    });
  }, [centres, country, province, search, verifiedOnly]);
  const ranked = useMemo(() => [...filtered].sort((a, b) => Number(b.verificado) - Number(a.verificado) || totalCourses(b) - totalCourses(a)), [filtered]);
  const featured = ranked[0];
  const remaining = ranked.filter((centre) => centre.id !== featured?.id);
  const totalPages = Math.max(1, Math.ceil(remaining.length / pageSize));
  const visible = remaining.slice((page - 1) * pageSize, page * pageSize);
  useEffect(() => { setPage(1); }, [country, search, province, verifiedOnly]);

  const openCentre = (event, id) => { event.preventDefault(); onNavigate(`/centros/${id}`); };
  const chooseLocationSuggestion = (suggestion) => { setSearch(suggestion.cidade); setLocationSuggestionsOpen(false); };
  const isLoading = loading || homeLoading;
  const hasActiveFilters = Boolean(search || country || province || verifiedOnly);
  const featuredMapsUrl = featured ? mapsSearchUrl(featured) : "";

  return <main className="centres-vitrine-page">
    <section className="subpage-hero centres-page-hero"><div className="page-width"><span className="eyebrow"><UsersRound size={15} /> Centros de formação</span><h1>Descubra onde o seu próximo passo pode começar.</h1><p>Conheça centros ativos, compare a formação disponível e encontre uma instituição próxima dos seus objetivos — em Angola e noutros países da CPLP.</p><div className="centres-vitrine-search"><Search size={18} /><input value={search} onFocus={() => setLocationSuggestionsOpen(true)} onBlur={() => window.setTimeout(() => setLocationSuggestionsOpen(false), 120)} onChange={(event) => { setSearch(event.target.value); setLocationSuggestionsOpen(true); }} placeholder="Pesquisar centro, cidade, país ou modalidade" aria-label="Pesquisar centros" aria-autocomplete="list" aria-expanded={locationSuggestionsOpen && locationSuggestions.length > 0} />{locationSuggestionsOpen && locationSuggestions.length > 0 && <div className="centre-search-suggestions" role="listbox" aria-label="Sugestões de cidade">{locationSuggestions.map((suggestion) => <button key={suggestion.key} type="button" role="option" onMouseDown={(event) => event.preventDefault()} onClick={() => chooseLocationSuggestion(suggestion)}><MapPin size={15} /><span><strong>{suggestion.cidade}</strong><small>{[suggestion.provincia, suggestion.pais].filter(Boolean).join(" · ")}</small></span></button>)}</div>}</div></div></section>
    <section className="page-width centres-vitrine-content">
      <div className="centres-overview"><div><span className="eyebrow muted"><ShieldCheck size={14} /> Vitrine Edukangola</span><h2>Centros para conhecer agora.</h2><p>{filtered.length} {filtered.length === 1 ? "centro encontrado" : "centros encontrados"} com informação publicada pelos próprios centros.</p></div><div className="centres-filters"><label><span>País</span><select value={country} onChange={(event) => { setCountry(event.target.value); setProvince(""); }}><option value="">Todos</option>{countries.map(([code, name]) => <option key={code} value={code}>{name}</option>)}</select></label><label><span>Província ou região</span><select value={province} onChange={(event) => setProvince(event.target.value)}><option value="">Todas</option>{provinces.map((item) => <option key={item} value={item}>{item}</option>)}</select></label><label className="filter-check"><input type="checkbox" checked={verifiedOnly} onChange={(event) => setVerifiedOnly(event.target.checked)} /><Filter size={14} /> Só verificados</label></div></div>
      {!isLoading && provinceCounts.length > 0 && <div className="province-discovery"><div className="province-copy"><span className="eyebrow muted"><MapPin size={14} /> Explorar por região</span><strong>Comece pela região que faz sentido para si.</strong></div><div className="province-chips"><button className={!province ? "active" : ""} onClick={() => setProvince("")}>Todas <small>{country ? filtered.length : centres.length}</small></button>{provinceCounts.map((item) => <button key={item.name} className={province === item.name ? "active" : ""} onClick={() => setProvince(item.name)}>{item.name} <small>{item.count}</small></button>)}</div></div>}
      {isLoading ? <p className="page-empty">A carregar centros publicados.</p> : !featured ? <div className="page-empty centres-empty"><ShieldCheck size={24} /><strong>Nenhum centro corresponde aos filtros.</strong><span>Tente remover uma condição ou pesquisar por outra cidade.</span></div> : <>
        <section className="centres-featured"><div className="centres-featured-copy"><span className="eyebrow"><Building2 size={15} /> Centro em destaque</span>{featured.is_internacional && <span className="international-centre-label"><Globe2 size={14} /> Centro internacional · {featured.pais_nome}</span>}<div className="featured-location"><MapPin size={14} /> {centreLocation(featured) || "Localização a confirmar"}</div><h2>{displayName(featured.nome)}</h2><p>{featured.descricao_curta || "Explore a formação, os cursos publicados e as modalidades disponíveis neste centro."}</p><div className="featured-stats"><span><BookOpenCheck size={16} /><b>{totalCourses(featured)}</b> cursos publicados</span><span><ShieldCheck size={16} /><b>{featured.verificado ? "Verificado" : "Centro ativo"}</b></span></div><div className="featured-actions"><a className="primary-action" href={`/centros/${featured.id}`} onClick={(event) => openCentre(event, featured.id)}>Conhecer o centro <ArrowRight size={16} /></a>{featuredMapsUrl && <a className="centre-map-link" href={featuredMapsUrl} target="_blank" rel="noreferrer"><MapPin size={15} /> Ver localização</a>}</div></div><div className="centres-featured-visual"><img className="centres-featured-cover" src={centreCover(featured)} alt="" /><div className="featured-logo">{safeImageUrl(featured.logo_url) ? <img src={safeImageUrl(featured.logo_url)} alt="" /> : displayName(featured.nome).slice(0, 1)}</div>{featured.verificado && <span className="verified-label"><CheckCircle2 size={13} /> Centro verificado</span>}<div className="featured-visual-meta"><small>Modalidades</small><strong>{(featured.modalidades || []).join(" · ") || "Formação disponível"}</strong></div></div></section>
        <section className="centres-directory"><div className="directory-heading"><div><span className="eyebrow muted">Mais centros</span><h2>{hasActiveFilters ? "Resultados da sua pesquisa." : "Outros centros para explorar."}</h2></div><span>{remaining.length} {remaining.length === 1 ? "opção" : "opções"}</span></div><div className="centres-compact-list">{visible.map((centre) => <a key={centre.id} className="centre-compact-row" href={`/centros/${centre.id}`} onClick={(event) => openCentre(event, centre.id)}><img className="centre-row-cover" src={centreCover(centre)} alt="" /><span className="centre-compact-logo">{safeImageUrl(centre.logo_url) ? <img src={safeImageUrl(centre.logo_url)} alt="" /> : displayName(centre.nome).slice(0, 1)}</span><span className="centre-compact-copy"><strong>{displayName(centre.nome)}</strong><small><MapPin size={13} /> {centreLocation(centre) || "Localização a confirmar"}</small>{centre.is_internacional && <em className="centre-compact-international"><Globe2 size={12} /> Internacional · {centre.pais_nome}</em>}</span><span className="centre-compact-meta"><b>{totalCourses(centre)}</b><small>{totalCourses(centre) === 1 ? "curso" : "cursos"}</small></span>{centre.verificado && <span className="centre-compact-verified"><CheckCircle2 size={14} /></span>}<ArrowRight size={17} /></a>)}</div></section>
        {totalPages > 1 && <nav className="centres-pagination" aria-label="Paginação de centros"><button disabled={page === 1} onClick={() => setPage((current) => current - 1)}>Anterior</button><span>Página {page} de {totalPages}</span><button disabled={page === totalPages} onClick={() => setPage((current) => current + 1)}>Seguinte</button></nav>}
      </>}
    </section>
  </main>;
}
