import { useEffect, useState } from "react";
import { ArrowLeft, BookOpenCheck, CalendarDays, CheckCircle2, Clock3, GraduationCap, LockKeyhole, MonitorPlay, PlayCircle, UserRound, UsersRound, Video } from "lucide-react";
import "./video-course-detail-page.css";

export default function VideoCourseDetailPage({ slug, onNavigate }) {
  const [status, setStatus] = useState("loading");
  const [course, setCourse] = useState(null);

  useEffect(() => {
    let active = true;
    setStatus("loading");
    fetch(`/api/public/video-cursos/${encodeURIComponent(slug)}/`)
      .then((response) => {
        if (!response.ok) throw new Error("Vídeo-curso indisponível.");
        return response.json();
      })
      .then((data) => { if (active) { setCourse(data); setStatus("ready"); } })
      .catch(() => { if (active) setStatus("error"); });
    return () => { active = false; };
  }, [slug]);

  if (status === "loading") return <main className="detail-state page-width"><span className="eyebrow muted">Vídeo-curso</span><h1>A carregar o currículo do curso.</h1><p>Estamos a consultar as aulas publicadas pelo backend.</p></main>;
  if (status === "error" || !course) return <main className="detail-state page-width"><span className="eyebrow muted">Vídeo-curso indisponível</span><h1>Não foi possível encontrar este curso em vídeo.</h1><p>Ele pode ter deixado de estar publicado ou ainda não possuir aulas disponíveis.</p><button className="primary-action" onClick={() => onNavigate("/cursos")}>Ver catálogo</button></main>;

  const acaoComercial = course.is_gratuito ? "Aceder gratuitamente" : "Comprar vídeo-curso";
  const resumoComercial = course.is_gratuito ? "Acesso gratuito ao conteúdo completo." : "Compra única para acesso ao vídeo-curso.";
  return <main className="video-course-detail-page">
    <section className="video-detail-hero">
      <div className="page-width">
        <button className="video-detail-back" type="button" onClick={() => onNavigate("/cursos")}><ArrowLeft size={17} /> Voltar ao catálogo</button>
        <div className="video-detail-hero-grid">
          <div><div className="video-detail-badges"><span>{course.categoria}</span><span><Video size={14} /> Curso em vídeo</span><span>{course.origem_label}</span></div><h1>{course.titulo}</h1><p>{course.descricao}</p><div className="video-detail-meta"><span><UserRound size={17} /> {course.instrutor || course.centro}</span><span><BookOpenCheck size={17} /> {course.total_aulas} {course.total_aulas === 1 ? "aula" : "aulas"}</span>{course.duracao_total && <span><Clock3 size={17} /> {course.duracao_total}</span>}</div></div>
          <div className="video-detail-cover">{course.imagem_url ? <img src={course.imagem_url} alt="" /> : <MonitorPlay size={45} />}<span><PlayCircle size={26} /></span></div>
        </div>
      </div>
    </section>
    <section className="page-width video-detail-layout">
      <div className="video-detail-main">
        <section className="video-curriculum"><span className="eyebrow muted">Conteúdo do curso</span><h2>Aulas incluídas nesta formação.</h2><p>O programa abaixo é carregado diretamente das aulas publicadas no backend.</p>{course.aulas.length ? <div className="video-lessons">{course.aulas.map((lesson, index) => <details key={lesson.id} open={index === 0}><summary><span className="video-lesson-number">{String(index + 1).padStart(2, "0")}</span><span className="video-lesson-title">{lesson.titulo}{lesson.tem_exercicio && <small>Inclui exercício</small>}</span><span className="video-lesson-duration"><Clock3 size={15} /> {lesson.duracao}</span><LockKeyhole size={16} /></summary>{lesson.descricao && <p>{lesson.descricao}</p>}</details>)}</div> : <div className="video-empty-curriculum"><MonitorPlay size={22} /><div><b>Ainda não existem aulas publicadas.</b><p>O centro ou instrutor ainda não disponibilizou o programa deste vídeo-curso.</p></div></div>}</section>
        <section className="video-learning-note"><CheckCircle2 size={20} /><div><b>Aprenda no seu ritmo</b><p>Depois da compra ou acesso gratuito, as aulas ficam disponíveis no ambiente de aprendizagem da Edukangola.</p></div></section>
        {course.tem_turmas ? <section className="video-classes" id="turmas"><span className="eyebrow muted">Turmas do centro</span><h2>Acompanhamento disponível para este vídeo-curso.</h2>{course.turmas.length ? <div className="video-class-list">{course.turmas.map((turma) => <article key={turma.id}><div><b>{turma.nome}</b><span><CalendarDays size={15} /> Início em {turma.inicio_formatado}</span><span><Clock3 size={15} /> {turma.dias} · {turma.horario}</span></div><strong><UsersRound size={15} /> {turma.vagas_disponiveis} vagas</strong></article>)}</div> : <div className="video-empty-curriculum"><UsersRound size={22} /><div><b>O centro ainda não abriu uma turma.</b><p>O conteúdo em vídeo está publicado, mas o acompanhamento por turma será anunciado pelo centro.</p></div></div>}</section> : <section className="video-original-note"><MonitorPlay size={20} /><div><b>Vídeo-curso original da Edukangola</b><p>Este curso é publicado pela plataforma e é estudado ao seu ritmo; não depende de turma, horário ou vagas.</p></div></section>}
      </div>
      <aside className="video-detail-aside"><div className="video-enrollment-card"><span>{course.is_gratuito ? 'ACESSO GRATUITO' : 'COMPRA DO VÍDEO-CURSO'}</span><strong>{course.pagamento?.agora}</strong><p>{course.pagamento?.descricao || resumoComercial}</p>{course.tem_turmas && <a className="video-class-link" href="#turmas">Ver turmas de acompanhamento</a>}<button type="button" onClick={() => onNavigate(`/comprar/${encodeURIComponent(slug)}`)}>{acaoComercial}</button><small>{course.tem_turmas ? 'O centro pode associar acompanhamento por turma; a compra dá acesso ao vídeo-curso.' : 'Depois da compra ou acesso gratuito, as aulas ficam disponíveis no ambiente de aprendizagem da Edukangola.'}</small></div></aside>
    </section>
  </main>;
}
