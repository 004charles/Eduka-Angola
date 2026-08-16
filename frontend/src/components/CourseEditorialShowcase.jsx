import { useMemo, useState } from "react";
import { ArrowRight, ArrowUpRight, BriefcaseBusiness, PlayCircle, Sparkles } from "lucide-react";
import { etiquetaProduto, isVideoCurso, rotaDetalheProduto } from "../lib/product-type";
import "./course-editorial-showcase.css";
import CourseDiscoveryShelves from "./CourseDiscoveryShelves";

function courseGroups(data) {
  return Object.entries((data?.cursos || []).filter((course) => !isVideoCurso(course)).reduce((groups, course) => {
    const name = course.categoria || "Outras competências";
    groups[name] = [...(groups[name] || []), course];
    return groups;
  }, {})).sort(([left], [right]) => left.localeCompare(right, "pt-PT"));
}

function MiniCourse({ course }) {
  return <a className="editorial-mini-course" href={rotaDetalheProduto(course)}><img src={course.imagem_url} alt="" /><span><small>{course.centro || "Edukangola"}</small><strong>{course.titulo}</strong><em>{etiquetaProduto(course)}</em></span><ArrowUpRight size={16} /></a>;
}

function takeUnique(candidates, usedIds, limit = 3) {
  const selected = [];
  for (const course of candidates) {
    if (usedIds.has(course.id)) continue;
    selected.push(course);
    usedIds.add(course.id);
    if (selected.length === limit) break;
  }
  return selected;
}

export default function CourseEditorialShowcase({ data, onNavigate, onAnnounce }) {
  const groups = useMemo(() => courseGroups(data), [data]);
  const [activeCareer, setActiveCareer] = useState("");
  const currentCareer = groups.find(([name]) => name === activeCareer) || groups[0] || ["", []];
  const allCourses = data?.cursos || [];
  const usedIds = new Set(currentCareer[1].slice(0, 3).map((course) => course.id));
  const newest = [...allCourses].sort((left, right) => new Date(right.data_publicacao) - new Date(left.data_publicacao));
  const spotlightCourses = takeUnique([...allCourses.filter((course) => course.destaque), ...allCourses], usedIds, 2);
  const popular = takeUnique([...allCourses.filter((course) => course.destaque), ...allCourses], usedIds, 4);
  const videoCourses = takeUnique(allCourses.filter(isVideoCurso), usedIds, 4);
  const newCourses = takeUnique(newest, usedIds, 4);
  const exploreCourses = takeUnique(allCourses, usedIds, 4);
  const collections = [
    { slug: "mais-procurados", eyebrow: "Cursos em destaque", title: "Mais procurados", href: "/cursos", courses: popular },
    { slug: "novidades", eyebrow: "Formações recentes", title: "Novidades", href: "/cursos?ordem=recentes", courses: newCourses },
    { slug: "aprenda-ao-seu-ritmo", eyebrow: "Estude como preferir", title: "Aprenda ao seu ritmo", href: "/cursos?tipo=video", courses: videoCourses },
    { slug: "para-explorar", eyebrow: "Descoberta orientada", title: "Para explorar agora", href: "/cursos", courses: exploreCourses },
  ].filter((collection) => collection.courses.length);

  if (!allCourses.length) return null;

  return <section className="course-editorial" aria-label="Descoberta de cursos">
    <div className="page-width">
      <nav className="editorial-category-nav editorial-category-nav--top" aria-label="Explorar cursos por categoria"><span>Explorar por área</span><div>{groups.slice(0, 6).map(([name]) => <a href={`/cursos?categoria=${encodeURIComponent(name)}`} key={name}>{name}</a>)}</div></nav>
      {groups.length > 0 && <section className="career-program" aria-labelledby="career-program-title">
        <aside className="career-program-intro"><span className="eyebrow"><BriefcaseBusiness size={14} /> Carreiras e competências</span><h2 id="career-program-title">Prepare-se para o próximo passo da sua carreira.</h2><p>Escolha uma área e explore os cursos disponíveis.</p><button className="editorial-light-action" onClick={() => onNavigate("/cursos")}>Explorar todos <ArrowRight size={16} /></button></aside>
        <div className="career-program-content"><div className="career-tabs" role="tablist" aria-label="Áreas de carreira">{groups.slice(0, 6).map(([name]) => <button key={name} type="button" role="tab" aria-selected={currentCareer[0] === name} className={currentCareer[0] === name ? "is-active" : ""} onClick={() => setActiveCareer(name)}>{name}</button>)}</div><div className="career-program-cards">{currentCareer[1].slice(0, 3).map((course) => <a href={rotaDetalheProduto(course)} className="career-program-card" key={course.id}><img src={course.imagem_url} alt="" /><span><small>{course.centro || "Edukangola"}</small><strong>{course.titulo}</strong><em>{etiquetaProduto(course)}</em></span></a>)}</div></div>
      </section>}

      {spotlightCourses.length > 0 && <section className="course-spotlights" aria-label="Cursos em destaque"><div className="course-spotlight-list">{spotlightCourses.map((course, index) => <a className={`course-spotlight spotlight-${index}`} href={rotaDetalheProduto(course)} key={course.id}><div><span className="eyebrow">{etiquetaProduto(course)}</span><h2>{course.titulo}</h2><p>Com {course.centro || "Edukangola"}</p><strong>Ver curso <ArrowRight size={17} /></strong></div><img src={course.imagem_url} alt="" /></a>)}</div></section>}

      <section className="editorial-trending" aria-labelledby="trending-title"><div className="editorial-section-title"><span className="eyebrow muted"><Sparkles size={14} /> Cursos em alta</span><h2 id="trending-title">Encontre algo novo para aprender.</h2></div><CourseDiscoveryShelves collections={collections} onNavigate={onNavigate} onAnnounce={onAnnounce} /></section>


      <section className="editorial-promo" aria-label="Explorar cursos"><div><span className="eyebrow">Edukangola</span><h2>Cursos para começar, mudar ou avançar.</h2><button onClick={() => onNavigate("/cursos")}>Explorar cursos <ArrowRight size={17} /></button></div><div className="editorial-promo-art" aria-hidden="true"><span /><span /><PlayCircle size={48} /></div></section>
    </div>
  </section>;
}
