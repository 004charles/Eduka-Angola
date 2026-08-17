import { useEffect, useState } from "react";
import { ArrowLeft, BookOpenCheck, CalendarDays, CheckCircle2, Clock3, GraduationCap, LockKeyhole, MonitorPlay, PlayCircle, Star, UserRound, UsersRound, Video } from "lucide-react";
import "./video-course-detail-page.css";

function csrfToken() {
  return document.cookie.split(";").map((item) => item.trim()).find((item) => item.startsWith("csrftoken="))?.split("=").slice(1).join("=") || "";
}

function RatingStars({ value = 0, onChange, label = "Avaliação" }) {
  return <div className={`rating-stars ${onChange ? "is-selectable" : ""}`} aria-label={label}>{[1, 2, 3, 4, 5].map((star) => <button key={star} type="button" disabled={!onChange} onClick={() => onChange?.(star)} aria-label={`${star} ${star === 1 ? "estrela" : "estrelas"}`} aria-pressed={value === star}><Star size={18} fill={star <= value ? "currentColor" : "none"} /></button>)}</div>;
}

export default function VideoCourseDetailPage({ slug, student, onNavigate }) {
  const [status, setStatus] = useState("loading");
  const [course, setCourse] = useState(null);
  const [review, setReview] = useState({ avaliacao: 0, comentario: "" });
  const [reviewState, setReviewState] = useState({ saving: false, message: "", error: "" });

  useEffect(() => {
    let active = true;
    setStatus("loading");
    fetch(`/api/public/video-cursos/${encodeURIComponent(slug)}/`)
      .then((response) => {
        if (!response.ok) throw new Error("Curso em vídeo indisponível.");
        return response.json();
      })
      .then((data) => { if (active) { setCourse(data); setReview({ avaliacao: data.minha_avaliacao?.avaliacao || 0, comentario: data.minha_avaliacao?.comentario || "" }); setStatus("ready"); } })
      .catch(() => { if (active) setStatus("error"); });
    return () => { active = false; };
  }, [slug]);

  const submitReview = async (event) => {
    event.preventDefault();
    setReviewState({ saving: true, message: "", error: "" });
    try {
      const response = await fetch(`/api/react/video-cursos/${encodeURIComponent(slug)}/avaliacao/`, { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", Accept: "application/json", "X-CSRFToken": csrfToken() }, body: JSON.stringify(review) });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || "Não foi possível guardar a sua avaliação.");
      const detailResponse = await fetch(`/api/public/video-cursos/${encodeURIComponent(slug)}/`, { credentials: "same-origin", headers: { Accept: "application/json" }, cache: "no-store" });
      if (detailResponse.ok) setCourse(await detailResponse.json());
      setReviewState({ saving: false, message: payload.message || "Avaliação guardada.", error: "" });
    } catch (error) { setReviewState({ saving: false, message: "", error: error.message }); }
  };

  if (status === "loading") return <main className="detail-state page-width"><span className="eyebrow muted">Curso em vídeo</span><h1>A carregar o currículo do curso.</h1><p>Estamos a consultar as aulas publicadas pelo backend.</p></main>;
  if (status === "error" || !course) return <main className="detail-state page-width"><span className="eyebrow muted">Curso em vídeo indisponível</span><h1>Não foi possível encontrar este curso em vídeo.</h1><p>Ele pode ter deixado de estar publicado ou ainda não possuir aulas disponíveis.</p><button className="primary-action" onClick={() => onNavigate("/cursos")}>Ver catálogo</button></main>;

  const acaoComercial = course.is_gratuito ? "Aceder gratuitamente" : "Comprar curso em vídeo";
  const resumoComercial = course.is_gratuito ? "Acesso gratuito ao conteúdo completo." : "Compra única para acesso ao curso em vídeo.";
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
        <section className="video-curriculum"><span className="eyebrow muted">Conteúdo do curso</span><h2>Aulas incluídas nesta formação.</h2><p>O programa abaixo é carregado diretamente das aulas publicadas no backend.</p>{course.aulas.length ? <div className="video-lessons">{course.aulas.map((lesson, index) => <details key={lesson.id} open={index === 0}><summary><span className="video-lesson-number">{String(index + 1).padStart(2, "0")}</span><span className="video-lesson-title">{lesson.titulo}{lesson.tem_exercicio && <small>Inclui exercício</small>}</span><span className="video-lesson-duration"><Clock3 size={15} /> {lesson.duracao}</span><LockKeyhole size={16} /></summary>{lesson.descricao && <p>{lesson.descricao}</p>}</details>)}</div> : <div className="video-empty-curriculum"><MonitorPlay size={22} /><div><b>Ainda não existem aulas publicadas.</b><p>O centro ou instrutor ainda não disponibilizou o programa deste curso em vídeo.</p></div></div>}</section>
        <section className="video-learning-note"><CheckCircle2 size={20} /><div><b>Aprenda no seu ritmo</b><p>Depois da compra ou acesso gratuito, as aulas ficam disponíveis no ambiente de aprendizagem da Edukangola.</p></div></section>
        <section className="video-course-reviews" aria-labelledby="video-reviews-title"><div className="video-reviews-heading"><div><span className="eyebrow muted">Opiniões de alunos</span><h2 id="video-reviews-title">Avaliações e comentários.</h2><p>Partilhe a sua experiência depois de começar a aprender.</p></div><div className="video-rating-summary"><strong>{course.avaliacoes?.total ? course.avaliacoes.media.toFixed(1) : "—"}</strong><RatingStars value={Math.round(course.avaliacoes?.media || 0)} label="Média de avaliações" /><small>{course.avaliacoes?.total ? `${course.avaliacoes.total} ${course.avaliacoes.total === 1 ? "avaliação" : "avaliações"}` : "Ainda sem avaliações"}</small></div></div>{course.avaliacoes?.total > 0 && <div className="video-rating-bars">{course.avaliacoes.distribuicao.map((item) => <div key={item.estrelas}><span>{item.estrelas} <Star size={11} fill="currentColor" /></span><i><b style={{ width: `${item.percentagem}%` }} /></i><small>{item.quantidade}</small></div>)}</div>}{course.permissao_avaliacao?.pode_avaliar ? <form className="video-review-form" onSubmit={submitReview}><div><strong>{course.minha_avaliacao ? "Actualize a sua avaliação" : "Como avalia este curso?"}</strong><RatingStars value={review.avaliacao} onChange={(avaliacao) => setReview((current) => ({ ...current, avaliacao }))} label="Escolha uma avaliação entre uma e cinco estrelas" /></div><label>O seu comentário<textarea value={review.comentario} maxLength={1000} minLength={10} onChange={(event) => setReview((current) => ({ ...current, comentario: event.target.value }))} placeholder="Conte como foi a sua experiência neste curso." required /></label>{reviewState.error && <p className="review-feedback is-error">{reviewState.error}</p>}{reviewState.message && <p className="review-feedback is-success">{reviewState.message}</p>}<button type="submit" className="primary-action" disabled={reviewState.saving || !review.avaliacao}>{reviewState.saving ? "A guardar…" : course.minha_avaliacao ? "Actualizar avaliação" : "Publicar avaliação"}</button></form> : <div className="video-review-gate"><Star size={20} /><div><b>Avaliações disponíveis para alunos que começaram o curso.</b><p>{course.permissao_avaliacao?.mensagem || "Aceda ao curso para poder partilhar a sua experiência."}</p>{course.permissao_avaliacao?.estado === "INICIE_SESSAO" && <button type="button" className="video-learning-link" onClick={() => onNavigate(`/entrar?next=/video-cursos/${encodeURIComponent(slug)}`)}>Entrar para avaliar</button>}</div></div>}<div className="video-review-list">{course.avaliacoes?.comentarios?.map((item) => <article key={item.id}><div><strong>{item.autor}</strong><RatingStars value={item.avaliacao} label={`${item.avaliacao} estrelas`} /><small>{item.data}</small></div><p>{item.comentario}</p>{item.resposta && <aside><b>Resposta da equipa</b><p>{item.resposta}</p></aside>}</article>)}</div></section>
        {course.tem_turmas ? <section className="video-classes" id="turmas"><span className="eyebrow muted">Turmas do centro</span><h2>Acompanhamento disponível para este curso em vídeo.</h2>{course.turmas.length ? <div className="video-class-list">{course.turmas.map((turma) => <article key={turma.id}><div><b>{turma.nome}</b><span><CalendarDays size={15} /> Início em {turma.inicio_formatado}</span><span><Clock3 size={15} /> {turma.dias} · {turma.horario}</span></div><strong><UsersRound size={15} /> {turma.vagas_disponiveis} vagas</strong></article>)}</div> : <div className="video-empty-curriculum"><UsersRound size={22} /><div><b>O centro ainda não abriu uma turma.</b><p>O conteúdo em vídeo está publicado, mas o acompanhamento por turma será anunciado pelo centro.</p></div></div>}</section> : <section className="video-original-note"><MonitorPlay size={20} /><div><b>Curso em vídeo original da Edukangola</b><p>Este curso é publicado pela plataforma e é estudado ao seu ritmo; não depende de turma, horário ou vagas.</p></div></section>}
      </div>
      <aside className="video-detail-aside"><div className="video-enrollment-card"><span>{course.is_gratuito ? 'ACESSO GRATUITO' : 'COMPRA DO CURSO EM VÍDEO'}</span><strong>{course.pagamento?.agora}</strong><p>{course.pagamento?.descricao || resumoComercial}</p>{course.tem_turmas && <a className="video-class-link" href="#turmas">Ver turmas de acompanhamento</a>}<button type="button" className="video-enrollment-action" onClick={() => onNavigate(`/comprar/${encodeURIComponent(slug)}`)}>{acaoComercial}</button>{student && <button type="button" className="video-learning-link" onClick={() => onNavigate(`/aprender/video/${encodeURIComponent(slug)}`)}>Abrir sala de aprendizagem</button>}<small>{course.tem_turmas ? 'O centro pode associar acompanhamento por turma; a compra dá acesso ao curso em vídeo.' : 'Depois da compra ou acesso gratuito, as aulas ficam disponíveis no ambiente de aprendizagem da Edukangola.'}</small></div></aside>
    </section>
  </main>;
}
