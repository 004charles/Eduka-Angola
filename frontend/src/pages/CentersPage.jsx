import { useEffect, useMemo, useState } from "react";
import { ArrowRight, CheckCircle2, Filter, MapPin, Search, ShieldCheck, UsersRound } from "lucide-react";
import "./public-pages.css";

function displayName(name) { return name?.replace(/Eduka-Angola/gi, "Edukangola") || "Centro de formação"; }

export default function CentersPage({ data, loading: homeLoading, onNavigate }) {
  const [centres, setCentres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [province, setProvince] = useState("");
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 9;

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
  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();
    return centres.filter((centre) => {
      const matchesTerm = !term || [centre.nome, centre.cidade, centre.provincia, ...(centre.modalidades || [])].join(" ").toLowerCase().includes(term);
      return matchesTerm && (!province || centre.provincia === province) && (!verifiedOnly || centre.verificado);
    });
  }, [centres, province, search, verifiedOnly]);
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const visible = filtered.slice((page - 1) * pageSize, page * pageSize);
  useEffect(() => { setPage(1); }, [search, province, verifiedOnly]);

  const openCentre = (event, id) => { event.preventDefault(); onNavigate(`/centros/${id}`); };
  const isLoading = loading || homeLoading;
  return <main><section className="subpage-hero centres-page-hero"><div className="page-width"><span className="eyebrow"><UsersRound size={15} /> Centros de formação</span><h1>Encontre um centro que combina com o seu próximo passo.</h1><p>Explore centros ativos no Edukangola, compare a oferta publicada e abra cada perfil para conhecer a instituição antes de escolher um curso.</p><div className="centres-vitrine-search"><Search size={18} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Pesquisar centro, cidade ou modalidade" aria-label="Pesquisar centros" /></div></div></section><section className="page-width centres-directory"><div className="centres-toolbar"><div><span className="eyebrow muted"><ShieldCheck size={14} /> Vitrine pública</span><h2>Centros publicados no portal.</h2><p>{filtered.length} {filtered.length === 1 ? "centro encontrado" : "centros encontrados"} com dados reais do GestorEduka.</p></div><div className="centres-filters"><label><span>Província</span><select value={province} onChange={(event) => setProvince(event.target.value)}><option value="">Todas</option>{provinces.map((item) => <option key={item} value={item}>{item}</option>)}</select></label><label className="filter-check"><input type="checkbox" checked={verifiedOnly} onChange={(event) => setVerifiedOnly(event.target.checked)} /><Filter size={14} /> Só verificados</label></div></div>{isLoading ? <p className="page-empty">A carregar centros publicados.</p> : !visible.length ? <div className="page-empty centres-empty"><ShieldCheck size={24} /><strong>Nenhum centro corresponde aos filtros.</strong><span>Tente remover uma condição ou pesquisar por outra cidade.</span></div> : <div className="centres-showcase-grid">{visible.map((centre) => <a key={centre.id} className="centre-showcase-card" href={`/centros/${centre.id}`} onClick={(event) => openCentre(event, centre.id)}><div className="centre-cover" style={centre.banner_url ? { backgroundImage: `linear-gradient(125deg,rgba(32,10,74,.08),rgba(13,7,24,.46)),url(${centre.banner_url})` } : undefined}><span className="centre-logo">{centre.logo_url ? <img src={centre.logo_url} alt="" /> : displayName(centre.nome).slice(0, 1)}</span>{centre.verificado && <span className="verified-label"><CheckCircle2 size={13} /> Verificado</span>}</div><div className="centre-showcase-body"><h3>{displayName(centre.nome)}</h3><p className="centre-location"><MapPin size={14} /> {[centre.cidade, centre.provincia].filter(Boolean).join(", ") || "Localização a confirmar"}</p><div className="centre-card-meta"><span>{centre.total_cursos || 0} {(centre.total_cursos || 0) === 1 ? "curso" : "cursos"}</span><span>{(centre.modalidades || []).join(" · ") || "Modalidades a confirmar"}</span></div><span className="centre-open-link">Ver perfil <ArrowRight size={15} /></span></div></a>)}</div>} {!isLoading && totalPages > 1 && <nav className="centres-pagination" aria-label="Paginação de centros"><button disabled={page === 1} onClick={() => setPage((current) => current - 1)}>Anterior</button><span>Página {page} de {totalPages}</span><button disabled={page === totalPages} onClick={() => setPage((current) => current + 1)}>Seguinte</button></nav>}</section></main>;
}
