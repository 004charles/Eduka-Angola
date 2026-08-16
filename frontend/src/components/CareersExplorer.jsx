import { ArrowRight, BriefcaseBusiness } from "lucide-react";
import { isVideoCurso } from "../lib/product-type";
import "./careers-explorer.css";

export default function CareersExplorer({ data, onNavigate }) {
  const careers = Object.entries((data?.cursos || []).filter((course) => !isVideoCurso(course)).reduce((groups, course) => {
    const name = course.categoria || "Outras competências";
    groups[name] = [...(groups[name] || []), course];
    return groups;
  }, {})).sort(([, left], [, right]) => right.length - left.length || left[0].categoria.localeCompare(right[0].categoria, "pt-PT")).slice(0, 6);

  if (!careers.length) return null;

  return <section className="careers-explorer" aria-labelledby="careers-explorer-title"><div className="page-width"><div className="careers-explorer-heading"><div><span className="eyebrow muted"><BriefcaseBusiness size={14} /> Cursos para o próximo passo</span><h2 id="careers-explorer-title">Descubra competências para a carreira que quer construir.</h2></div><button className="text-action" onClick={() => onNavigate("/cursos")}>Ver todos os cursos <ArrowRight size={16} /></button></div><div className="careers-explorer-grid">{careers.map(([career, courses]) => <button type="button" className="career-option" key={career} onClick={() => onNavigate(`/cursos?categoria=${encodeURIComponent(career)}`)}><span className="career-option-top"><span>{career.slice(0, 1)}</span><ArrowRight size={18} /></span><strong>{career}</strong><small>{courses.length} {courses.length === 1 ? "curso disponível" : "cursos disponíveis"}</small><em>{courses.slice(0, 2).map((course) => course.titulo).join(" · ")}</em></button>)}</div></div></section>;
}
