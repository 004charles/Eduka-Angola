import { useEffect, useMemo, useState } from "react";
import { ArrowRight, BookOpenCheck, Building2, MapPin } from "lucide-react";
import "./home-centres-showcase.css";

const FALLBACK_COVERS = [
  "/static/img/banners/training_center_lab_1_1769959754699.png",
  "/static/img/banners/training_center_student_3_1769959820838.png",
  "/static/img/banners/training_center_workshop_2_1769959789358.png",
];

function displayName(value) { return value?.replace(/Eduka-Angola/gi, "Edukangola") || "Centro de formação"; }
function safeUrl(value) { if (!value) return null; try { const parsed = new URL(value, window.location.origin); return parsed.origin === window.location.origin ? parsed.href : `${parsed.pathname}${parsed.search}`; } catch { return value; } }
function centreCover(centre) { return safeUrl(centre.banner_url) || FALLBACK_COVERS[Number(centre.id || 0) % FALLBACK_COVERS.length]; }
function courseCount(centre) { return Number(centre.total_cursos || 0); }

function CentreCard({ centre, featured, onNavigate }) {
  const open = (event) => { event.preventDefault(); onNavigate(`/centros/${centre.id}`); };
  const name = displayName(centre.nome);
  const count = courseCount(centre);
  const location = [centre.cidade, centre.provincia].filter(Boolean).join(", ") || "Angola";
  return <a href={`/centros/${centre.id}`} onClick={open} className={featured ? "home-centre-card is-featured" : "home-centre-card"}>
    <img src={centreCover(centre)} alt="" />
    <div className="home-centre-overlay" />
    <div className="home-centre-copy">
      <span className="home-centre-kicker">{featured ? "Centro em destaque" : "Centro de formação"}</span>
      <h3>{name}</h3>
      <div className="home-centre-location"><MapPin size={14} /> {location}</div>
      <div className="home-centre-footer"><span><BookOpenCheck size={15} /> {count} {count === 1 ? "curso" : "cursos"}</span><span className="home-centre-open">Conhecer <ArrowRight size={15} /></span></div>
    </div>
  </a>;
}

export default function HomeCentresShowcase({ data, onNavigate }) {
  const [remoteCentres, setRemoteCentres] = useState(null);
  useEffect(() => {
    let active = true;
    fetch("/api/v1/centros/").then((response) => response.ok ? response.json() : Promise.reject(new Error("centres unavailable"))).then((payload) => {
      if (active) setRemoteCentres(Array.isArray(payload) ? payload : payload.results || []);
    }).catch(() => active && setRemoteCentres([]));
    return () => { active = false; };
  }, []);
  const centres = useMemo(() => {
    const source = remoteCentres === null ? (data?.centros || data?.centros_destaque || []) : remoteCentres;
    return [...source].sort((a, b) => Number(b.verificado) - Number(a.verificado) || courseCount(b) - courseCount(a)).slice(0, 3);
  }, [data, remoteCentres]);
  if (!centres.length) return null;
  return <section className="home-centres" aria-labelledby="home-centres-title"><div className="page-width">
    <header className="home-centres-heading"><div><span className="eyebrow muted"><Building2 size={14} /> Centros de formação</span><h2 id="home-centres-title">Encontre um centro para começar bem.</h2><p>Conheça instituições activas, veja a formação publicada e avance com mais confiança.</p></div><button onClick={() => onNavigate("/centros")}>Ver todos os centros <ArrowRight size={16} /></button></header>
    <div className="home-centres-grid"><CentreCard centre={centres[0]} featured onNavigate={onNavigate} />{centres.slice(1).map((centre) => <CentreCard key={centre.id} centre={centre} onNavigate={onNavigate} />)}</div>
  </div></section>;
}
