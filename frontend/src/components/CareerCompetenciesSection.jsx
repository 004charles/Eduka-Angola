import { useMemo, useState } from "react";
import { ArrowRight, BriefcaseBusiness } from "lucide-react";
import { etiquetaProduto, isVideoCurso, rotaDetalheProduto } from "../lib/product-type";
import "./career-competencies-section.css";

function groupsByCategory(data) {
  return Object.entries((data?.cursos || []).filter((course) => !isVideoCurso(course)).reduce((groups, course) => {
    const category = course.categoria || "Outras competências";
    groups[category] = [...(groups[category] || []), course];
    return groups;
  }, {})).sort(([left], [right]) => left.localeCompare(right, "pt-PT"));
}

export default function CareerCompetenciesSection({ data, onNavigate }) {
  const groups = useMemo(() => groupsByCategory(data), [data]);
  const [activeCategory, setActiveCategory] = useState("");
  const currentGroup = groups.find(([category]) => category === activeCategory) || groups[0] || ["", []];

  if (!groups.length) return null;

  return (
    <section className="page-width career-competencies" aria-labelledby="career-competencies-title">
      <aside className="career-competencies-intro">
        <span className="eyebrow"><BriefcaseBusiness size={14} /> Carreiras e competências</span>
        <h2 id="career-competencies-title">Prepare-se para o próximo passo da sua carreira.</h2>
        <p>Escolha uma área e explore os cursos disponíveis.</p>
        <button type="button" onClick={() => onNavigate("/cursos")}>Explorar todos <ArrowRight size={16} /></button>
      </aside>
      <div className="career-competencies-content">
        <div className="career-competencies-tabs" role="tablist" aria-label="Áreas de carreira">
          {groups.slice(0, 6).map(([category]) => <button key={category} type="button" role="tab" aria-selected={currentGroup[0] === category} className={currentGroup[0] === category ? "is-active" : ""} onClick={() => setActiveCategory(category)}>{category}</button>)}
        </div>
        <div className="career-competencies-cards">
          {currentGroup[1].slice(0, 3).map((course) => <a href={rotaDetalheProduto(course)} className="career-competencies-card" key={course.id}><img src={course.imagem_url} alt="" /><span><small>{course.centro || "Edukangola"}</small><strong>{course.titulo}</strong><em>{etiquetaProduto(course)}</em></span></a>)}
        </div>
      </div>
    </section>
  );
}
