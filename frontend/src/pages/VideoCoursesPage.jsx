import { ArrowRight, BookOpen, ChevronLeft, ChevronRight, Clock3, Layers3, PlayCircle, Sparkles } from "lucide-react";
import { useMemo, useRef, useState } from "react";
import "./video-courses-page.css";

function formatAccess(course) {
  return course.is_gratuito ? "Acesso gratuito" : course.pagamento?.agora || "Disponível agora";
}

function VideoProgrammeCard({ course, onNavigate }) {
  return (
    <article className="video-programme-card">
      <button type="button" onClick={() => onNavigate(`/video-cursos/${course.video_slug}`)}>
        <div className="video-programme-image">
          {course.imagem_url && <img src={course.imagem_url} alt="" />}
          <span><PlayCircle size={15} /> Curso em vídeo</span>
        </div>
        <div className="video-programme-copy">
          <div className="video-programme-topline"><small>{course.categoria || "Edukangola"}</small><em>{formatAccess(course)}</em></div>
          <h3>{course.titulo}</h3>
          <p>{course.instrutor || course.centro || "Edukangola"}</p>
          <div className="video-programme-meta"><span><Layers3 size={13} /> {course.total_aulas || 0} aulas</span><span><Clock3 size={13} /> {course.duracao_total || "Ao seu ritmo"}</span></div>
          <strong>Ver programa <ArrowRight size={14} /></strong>
        </div>
      </button>
    </article>
  );
}

function VideoShelf({ eyebrow, title, courses, onNavigate }) {
  const railRef = useRef(null);
  if (!courses.length) return null;
  const scrollRail = (direction) => railRef.current?.scrollBy({ left: direction * Math.max(280, railRef.current.clientWidth * .72), behavior: "smooth" });
  return (
    <section className="video-shelf" aria-labelledby="video-shelf-title">
      <div className="video-shelf-heading">
        <div><span className="eyebrow muted">{eyebrow}</span><h2 id="video-shelf-title">{title}</h2></div>
        {courses.length > 1 && <div className="video-shelf-controls" aria-label={`Navegar ${title}`}><button type="button" onClick={() => scrollRail(-1)} aria-label="Ver cursos anteriores"><ChevronLeft size={18} /></button><button type="button" onClick={() => scrollRail(1)} aria-label="Ver próximos cursos"><ChevronRight size={18} /></button></div>}
      </div>
      <div ref={railRef} className="video-shelf-rail">{courses.map((course) => <VideoProgrammeCard key={course.id} course={course} onNavigate={onNavigate} />)}</div>
    </section>
  );
}

export default function VideoCoursesPage({ data, loading, onNavigate }) {
  const courses = data?.video_cursos || [];
  const [activeCategory, setActiveCategory] = useState("Todos");
  const categories = useMemo(() => Object.entries(courses.reduce((groups, course) => {
    const category = course.categoria || "Outras áreas";
    groups[category] = [...(groups[category] || []), course];
    return groups;
  }, {})).filter(([, items]) => items.length), [courses]);
  const featuredCourse = courses.find((course) => course.destaque) || courses[0];
  const visibleCourses = activeCategory === "Todos" ? courses : categories.find(([category]) => category === activeCategory)?.[1] || [];
  const chooseCategory = (category) => {
    setActiveCategory(category);
    document.getElementById("programas-video")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  if (loading) return <main className="video-page"><div className="page-width video-page-loading">A preparar os cursos em vídeo…</div></main>;
  if (!courses.length) return <main className="video-page"><section className="page-width video-page-empty"><BookOpen size={34} /><span className="eyebrow">Cursos em vídeo</span><h1>A biblioteca está a ser preparada.</h1><p>Enquanto os primeiros programas são publicados, explore as formações presenciais dos centros.</p><button className="primary-action" onClick={() => onNavigate("/cursos")}>Ver cursos presenciais <ArrowRight size={16} /></button></section></main>;

  return (
    <main className="video-page">
      <header className="video-page-hero">
        <div className="page-width video-page-hero-inner">
          <span className="eyebrow"><Sparkles size={15} /> Edukangola vídeo</span>
          <h1>Aprenda ao seu ritmo, com programas que acompanham o seu futuro.</h1>
          <p>Explore cursos em vídeo publicados por centros e formadores, assista quando quiser e retome o que começou.</p>
          <button className="primary-action" onClick={() => document.getElementById("programas-video")?.scrollIntoView({ behavior: "smooth" })}>Explorar programas <ArrowRight size={17} /></button>
        </div>
      </header>

      <section className="page-width video-featured-section" aria-labelledby="video-featured-title">
        <div className="video-featured-copy">
          <span className="eyebrow">Programa em destaque</span>
          <h2 id="video-featured-title">{featuredCourse.titulo}</h2>
          <p>{featuredCourse.descricao_curta || featuredCourse.descricao || "Um programa para desenvolver competências de forma prática, no seu próprio ritmo."}</p>
          <div className="video-featured-details"><span>{featuredCourse.instrutor || featuredCourse.centro || "Edukangola"}</span><span>{formatAccess(featuredCourse)}</span></div>
          <button className="primary-action" onClick={() => onNavigate(`/video-cursos/${featuredCourse.video_slug}`)}>Ver programa <PlayCircle size={17} /></button>
        </div>
        <button type="button" className="video-featured-media" onClick={() => onNavigate(`/video-cursos/${featuredCourse.video_slug}`)} aria-label={`Abrir ${featuredCourse.titulo}`}>
          {featuredCourse.imagem_url && <img src={featuredCourse.imagem_url} alt="" />}
          <span><PlayCircle size={26} /></span>
        </button>
      </section>

      <section className="video-library-section" id="programas-video">
        <div className="page-width">
          <div className="video-library-heading"><div><span className="eyebrow muted">Biblioteca de programas</span><h2>Encontre um curso para começar agora.</h2></div><p>{courses.length} {courses.length === 1 ? "curso publicado" : "cursos publicados"}</p></div>
          <div className="video-category-tabs" role="tablist" aria-label="Filtrar cursos em vídeo por área"><button type="button" role="tab" aria-selected={activeCategory === "Todos"} className={activeCategory === "Todos" ? "is-active" : ""} onClick={() => setActiveCategory("Todos")}>Todos</button>{categories.map(([category]) => <button key={category} type="button" role="tab" aria-selected={activeCategory === category} className={activeCategory === category ? "is-active" : ""} onClick={() => setActiveCategory(category)}>{category}</button>)}</div>
          <VideoShelf eyebrow={activeCategory === "Todos" ? "Todos os programas" : `Área · ${activeCategory}`} title={activeCategory === "Todos" ? "Cursos em vídeo disponíveis." : `Cursos em ${activeCategory}.`} courses={visibleCourses} onNavigate={onNavigate} />
          {categories.length > 1 && <section className="video-area-section" aria-labelledby="video-area-title"><div><span className="eyebrow muted">Explorar por área</span><h2 id="video-area-title">Escolha uma área de aprendizagem.</h2></div><div className="video-area-grid">{categories.map(([category, items]) => <button key={category} type="button" onClick={() => chooseCategory(category)}><span><PlayCircle size={17} /></span><div><strong>{category}</strong><small>{items.length} {items.length === 1 ? "curso em vídeo" : "cursos em vídeo"}</small></div><ArrowRight size={17} /></button>)}</div></section>}
        </div>
      </section>
    </main>
  );
}
