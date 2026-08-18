import { useEffect, useState } from "react";
import { ArrowRight, Sparkles } from "lucide-react";
import CourseCard from "./CourseCard";
import "./recommended-courses-section.css";

function toCard(course) {
  return {
    id: course.id,
    title: course.titulo,
    category: course.categoria,
    centre: course.centro,
    imageUrl: course.imagem_url,
    detailUrl: course.detalhe_url,
    schedule: course.modalidade,
    is_gratuito: course.is_gratuito,
    certificado: course.certificado,
    nivel_label: course.nivel,
    favorito: Boolean(course.favorito),
    pagamento: { agora: course.preco_label, descricao: course.motivo },
  };
}

export default function RecommendedCoursesSection({ onNavigate }) {
  const [items, setItems] = useState([]);
  const [personalized, setPersonalized] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    fetch("/api/react/recomendacoes/?limit=4", { credentials: "same-origin", headers: { Accept: "application/json" }, cache: "no-store" })
      .then((response) => response.ok ? response.json() : { items: [] })
      .then((payload) => { if (active) { setItems(payload.items || []); setPersonalized(Boolean(payload.personalized)); } })
      .catch(() => { if (active) setItems([]); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  if (loading || !items.length) return null;
  return <section className="page-width recommended-section" aria-labelledby="recommended-title"><div className="section-heading"><div><span className="eyebrow muted"><Sparkles size={14} /> {personalized ? "Escolhas para si" : "Para começar"}</span><h2 id="recommended-title">{personalized ? "Cursos recomendados para si" : "Sugestões para explorar"}</h2><p className="recommended-intro">{personalized ? "Sugestões baseadas nos seus interesses, histórico e cursos guardados." : "Descubra formações populares e actuais no catálogo da Edukangola."}</p></div><button className="text-action" onClick={() => onNavigate("/cursos")}>Ver catálogo <ArrowRight size={16} /></button></div><div className="recommended-grid">{items.map((item) => <div className="recommended-card-wrap" key={item.id}><CourseCard course={toCard(item)} onSave={() => {}} /></div>)}</div></section>;
}
