import { ArrowRight, Building2, CalendarClock, PlayCircle } from "lucide-react";
import { isVideoCurso } from "../lib/product-type";
import "./learning-entry-points.css";

export default function LearningEntryPoints({ data, onNavigate }) {
  const courses = data?.cursos || [];
  const turmas = data?.turmas_abertas || [];
  const centres = data?.centros_destaque || [];
  const videoCourses = courses.filter(isVideoCurso);

  const points = [
    {
      icon: CalendarClock,
      eyebrow: "Com data para começar",
      title: turmas.length ? `${turmas.length} turmas abertas` : "Turmas a confirmar",
      description: "Compare início, horário, vagas e condições de inscrição antes de decidir.",
      action: "Ver próximas turmas",
      href: "/cursos?turma=aberta",
    },
    {
      icon: PlayCircle,
      eyebrow: "Ao seu ritmo",
      title: videoCourses.length ? `${videoCourses.length} vídeo-cursos` : "Aprendizagem em vídeo",
      description: "Aceda a aulas gravadas e escolha quando quer estudar, sem depender de calendário.",
      action: "Explorar vídeo-cursos",
      href: "/cursos?tipo=video",
    },
    {
      icon: Building2,
      eyebrow: "Para comparar com confiança",
      title: centres.length ? `${centres.length} centros em destaque` : "Centros de formação",
      description: "Conheça quem publica, onde forma e as modalidades que cada centro disponibiliza.",
      action: "Conhecer os centros",
      href: "/centros",
    },
  ];

  return <section className="home-entry-section" aria-labelledby="home-entry-title"><div className="page-width"><div className="home-entry-heading"><span className="eyebrow muted">Comece pela sua necessidade</span><h2 id="home-entry-title">A próxima decisão não começa por percorrer um catálogo.</h2><p>Escolha a forma como quer avançar. A Edukangola mostra-lhe as opções reais antes de chegar ao curso.</p></div><div className="home-entry-grid">{points.map((point) => { const Icon = point.icon; return <button type="button" key={point.href} className="home-entry-card" onClick={() => onNavigate(point.href)}><span className="home-entry-icon"><Icon size={22} /></span><span className="home-entry-copy"><small>{point.eyebrow}</small><strong>{point.title}</strong><em>{point.description}</em><span className="home-entry-action">{point.action} <ArrowRight size={16} /></span></span></button>; })}</div></div></section>;
}
