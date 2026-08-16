import { useEffect, useMemo, useState } from "react";
import { ArrowRight, BookOpenCheck, Building2, CheckCircle2, Filter, MapPin, Search, ShieldCheck, UsersRound } from "lucide-react";
import "./public-pages.css";

function displayName(name) { return name?.replace(/Eduka-Angola/gi, "Edukangola") || "Centro de formação"; }
function safeImageUrl(url) { if (!url) return null; try { const parsed = new URL(url, window.location.origin); return parsed.origin === window.location.origin ? parsed.href : `${parsed.pathname}${parsed.search}`; } catch { return url; } }
function totalCourses(centre) { return Number(centre.total_cursos || 0); }
const CENTRE_FALLBACK_COVERS = ["/static/img/banners/training_center_lab_1_1769959754699.png", "/static/img/banners/training_center_student_3_1769959820838.png", "/static/img/banners/training_center_workshop_2_1769959789358.png"];
function centreCover(centre) { return safeImageUrl(centre.banner_url) || CENTRE_FALLBACK_COVERS[Number(centre.id || 0) % CENTRE_FALLBACK_COVERS.length]; }

export default function CentersPage({ data, loading: homeLoading, onNavigate }) {
  const [centres, setCentres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [province, setProvince] = useState("");
  const [verifiedOnly, setVerifiedOnly] = useState(false);
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

  const provinces = useMemo(() => [...new Set(centres.map((centre) => centre.provincia).filter(Boolean))].sort((a, b) => a.localeCompare(b)), [centres]);
  const provinceCounts = useMemo(() => provinces.map((name) => ({ name, count: centres.filter((centre) => centre.provincia === name).length })), [centres, provinces]);
  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();
    return centres.filter((centre) => {
      const matchesTerm = !term || [centre.nome, centre.cidade, centre.provincia, ...(centre.modalidades || [])].join(" ").toLowerCase().includes(term);
      return matchesTerm && (!province || centre.provincia === province) && (!verifiedOnly || centre.verificado);
    });
  }, [centres, province, search, verifiedOnly]);
  const ranked = useMemo(() => [...filtered].sort((a, b) => Number(b.verificado) - Number(a.verificado) || totalCourses(b) - totalCourses(a)), [filtered]);
  const featured = ranked[0];
  const remaining = ranked.filter((centre) => centre.id !== featured?.id);
  const totalPages = Math.max(1, Math.ceil(remaining.length / pageSize));
  const visible = remaining.slice((page - 1) * pageSize, page * pageSize);
  useEffect(() => { setPage(1); }, [search, province, verifiedOnly]);

  const openCentre = (event, id) => { event.preventDefault(); onNavigate(`/centros/${id}`); };
  const isLoading = loading || homeLoading;
  const hasActiveFilters = Boolean(search || province || verifiedOnly);

  return <main className="centres-vitrine-page">
    <section className="subpage-hero centres-page-hero"><div className="page-width"><span className="eyebrow"><UsersRound size={15} /> Centros de formação</span><h1>Descubra onde o seu próximo passo pode começar.</h1><p>Conheça centros ativos, compare a formação disponível e encontre uma instituição próxima dos seus objetivos.</p><div className="centres-vitrine-search"><Search size={18} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Pesquisar centro, cidade ou modalidade" aria-label="Pesquisar centros" /></div></div></section>
    <section className="page-width centres-vitrine-content">
      <div className="centres-overview"><div><span className="eyebrow muted"><ShieldCheck size={14} /> Vitrine Edukangola</span><h2>Centros para conhecer agora.</h2><p>{filtered.length} {filtered.length === 1 ? "centro encontrado" : "centros encontrados"} com informação publicada pelos próprios centros.</p></div><div className="centres-filters"><label><span>Província</span><select value={province} onChange={(event) => setProvince(event.target.value)}><option value="">Todas</option>{provinces.map((item) => <option key={item} value={item}>{item}</option>)}</select></label><label className="filter-check"><input type="checkbox" checked={verifiedOnly} onChange={(event) => setVerifiedOnly(event.target.checked)} /><Filter size={14} /> Só verificados</label></div></div>
      {!isLoading && provinceCounts.length > 0 && <div className="province-discovery"><div className="province-copy"><span className="eyebrow muted"><MapPin size={14} /> Explorar por província</span><strong>Comece pela região que faz sentido para si.</strong></div><div className="province-chips"><button className={!province ? "active" : ""} onClick={() => setProvince("")}>Todas <small>{centres.length}</small></button>{provinceCounts.map((item) => <button key={item.name} className={province === item.name ? "active" : ""} onClick={() => setProvince(item.name)}>{item.name} <small>{item.count}</small></button>)}</div></div>}
      {isLoading ? <p className="page-empty">A carregar centros publicados.</p> : !featured ? <div className="page-empty centres-empty"><ShieldCheck size={24} /><strong>Nenhum centro corresponde aos filtros.</strong><span>Tente remover uma condição ou pesquisar por outra cidade.</span></div> : <>
        <section className="centres-featured"><div className="centres-featured-copy"><span className="eyebrow"><Building2 size={15} /> Centro em destaque</span><div className="featured-location"><MapPin size={14} /> {[featured.cidade, featured.provincia].filter(Boolean).join(", ") || "Localização a confirmar"}</div><h2>{displayName(featured.nome)}</h2><p>{featured.descricao_curta || "Explore a formação, os cursos publicados e as modalidades disponíveis neste centro."}</p><div className="featured-stats"><span><BookOpenCheck size={16} /><b>{totalCourses(featured)}</b> cursos publicados</span><span><ShieldCheck size={16} /><b>{featured.verificado ? "Verificado" : "Centro ativo"}</b></span></div><a className="primary-action" href={`/centros/${featured.id}`} onClick={(event) => openCentre(event, featured.id)}>Conhecer o centro <ArrowRight size={16} /></a></div><div className="centres-featured-visual"><img className="centres-featured-cover" src={centreCover(featured)} alt="" /><div className="featured-logo">{safeImageUrl(featured.logo_url) ? <img src={safeImageUrl(featured.logo_url)} alt="" /> : displayName(featured.nome).slice(0, 1)}</div>{featured.verificado && <span className="verified-label"><CheckCircle2 size={13} /> Centro verificado</span>}<div className="featured-visual-meta"><small>Modalidades</small><strong>{(featured.modalidades || []).join(" · ") || "Formação disponível"}</strong></div></div></section>
        <section className="centres-directory"><div className="directory-heading"><div><span className="eyebrow muted">Mais centros</span><h2>{hasActiveFilters ? "Resultados da sua pesquisa." : "Outros centros para explorar."}</h2></div><span>{remaining.length} {remaining.length === 1 ? "opção" : "opções"}</span></div><div className="centres-compact-list">{visible.map((centre) => <a key={centre.id} className="centre-compact-row" href={`/centros/${centre.id}`} onClick={(event) => openCentre(event, centre.id)}><img className="centre-row-cover" src={centreCover(centre)} alt="" /><span className="centre-compact-logo">{safeImageUrl(centre.logo_url) ? <img src={safeImageUrl(centre.logo_url)} alt="" /> : displayName(centre.nome).slice(0, 1)}</span><span className="centre-compact-copy"><strong>{displayName(centre.nome)}</strong><small><MapPin size={13} /> {[centre.cidade, centre.provincia].filter(Boolean).join(", ") || "Localização a confirmar"}</small></span><span className="centre-compact-meta"><b>{totalCourses(centre)}</b><small>{totalCourses(centre) === 1 ? "curso" : "cursos"}</small></span>{centre.verificado && <span className="centre-compact-verified"><CheckCircle2 size={14} /></span>}<ArrowRight size={17} /></a>)}</div></section>
        {totalPages > 1 && <nav className="centres-pagination" aria-label="Paginação de centros"><button disabled={page === 1} onClick={() => setPage((current) => current - 1)}>Anterior</button><span>Página {page} de {totalPages}</span><button disabled={page === totalPages} onClick={() => setPage((current) => current + 1)}>Seguinte</button></nav>}
      </>}
    </section>
  </main>;
}
