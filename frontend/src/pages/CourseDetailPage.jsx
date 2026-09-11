import { ArrowLeft, Award, CalendarDays, CheckCircle2, Clock3, Globe2, GraduationCap, MapPin, MonitorPlay, UsersRound, Video } from "lucide-react";
import { backendUrl } from "../lib/backend-url";
import CourseShelf from "../components/CourseShelf";
import "./course-detail-page.css";

function formatarCentro(nome) {
  return nome?.replace(/Eduka-Angola/gi, "Edukangola") ?? "Centro de formação";
}

function temVideo(curso) {
  return Boolean(curso.is_video);
}

function TurmaCard({ turma, onChoose }) {
  return (
    <article className="detail-class-card">
      <div className="detail-class-heading"><div><span className="detail-class-kicker">{turma.turma_nome || "Turma aberta"}</span><h3>Início em {turma.inicio_formatado}</h3></div><span className="detail-vacancies"><UsersRound size={16} /> {turma.vagas_disponiveis} {turma.vagas_disponiveis === 1 ? "vaga" : "vagas"}</span></div>
      <div className="detail-class-facts">
        <span><CalendarDays size={16} /> {turma.dias || "Dias a confirmar"}</span>
        <span><Clock3 size={16} /> {[turma.turno, turma.horario].filter(Boolean).join(" · ") || "Horário a confirmar"}</span>
        {turma.filial_nome && <span><MapPin size={16} /> Unidade {turma.filial_nome}</span>}
        <span><MapPin size={16} /> {[turma.filial_endereco || turma.local, turma.sala].filter(Boolean).join(" · ") || "Local a confirmar"}</span>
      </div>
      <button className="detail-class-action" type="button" onClick={() => onChoose(turma)}>Escolher esta turma</button>
    </article>
  );
}

export default function CourseDetailPage({ course, courses, turmas, loading, onNavigate, onAnnounce }) {
  if (loading) return <main className="detail-state page-width"><span className="eyebrow muted">Curso</span><h1>A carregar informação do curso.</h1><p>Estamos a preparar as turmas e condições de inscrição.</p></main>;
  if (!course) return <main className="detail-state page-width"><span className="eyebrow muted">Curso não encontrado</span><h1>Este curso não está disponível no catálogo público.</h1><p>O curso pode ter sido removido ou deixado de estar publicado.</p><button className="primary-action" onClick={() => onNavigate("/cursos")}>Ver cursos publicados</button></main>;

  const centro = formatarCentro(course.centro);
  const turmasDoCurso = (turmas || []).filter((turma) => turma.id === course.id).sort((a, b) => a.inicio.localeCompare(b.inicio));
  const iniciarInscricao = (turma) => onNavigate(`/inscrever/${course.slug}${turma?.turma_id ? `?turma=${turma.turma_id}` : ""}`);
  const video = temVideo(course);
  const localizacao = [course.cidade, course.provincia].filter(Boolean).join(", ");
  const proximaTurmaPorCurso = new Map();
  (turmas || []).forEach((turma) => {
    const atual = proximaTurmaPorCurso.get(turma.id);
    if (!atual || turma.inicio < atual.inicio) proximaTurmaPorCurso.set(turma.id, turma);
  });
  const paraCartao = (curso) => {
    const turma = proximaTurmaPorCurso.get(curso.id);
    return { ...curso, title: curso.titulo, category: curso.categoria, centre: formatarCentro(curso.centro), mode: curso.modalidade, imageUrl: curso.imagem_url, detailUrl: curso.is_video ? `/video-cursos/${curso.video_slug}` : `/cursos/${curso.slug}`, inscricaoUrl: backendUrl(curso.inscricao_url), schedule: turma ? `Início ${turma.inicio_formatado}` : curso.pagamento?.agora || "Condições a confirmar", turma };
  };
  const outrosCursos = (courses || []).filter((item) => item.id !== course.id);
  const recomendados = [
    ...outrosCursos.filter((item) => item.categoria === course.categoria),
    ...outrosCursos.filter((item) => item.categoria !== course.categoria && item.centro === course.centro),
    ...outrosCursos.filter((item) => item.categoria !== course.categoria && item.centro !== course.centro),
  ].filter((item, index, lista) => lista.findIndex((outro) => outro.id === item.id) === index).slice(0, 8).map(paraCartao);

  return (
    <main className="course-detail-page">
      <section className="course-detail-hero">
        <div className="page-width">
          <button className="detail-back" type="button" onClick={() => onNavigate("/cursos")}><ArrowLeft size={17} /> Voltar ao catálogo</button>
          <div className="course-detail-hero-grid">
            <div className="course-detail-hero-copy">
              <div className="detail-badges"><span>{course.categoria}</span><span>{course.modalidade}</span>{video && <span><Video size={14} /> Inclui vídeo</span>}</div>
              <h1>{course.titulo}</h1>
              <p>{course.descricao_curta || course.descricao}</p>
              <div className="detail-hero-meta"><span><GraduationCap size={17} /> {centro}</span>{course.centro_verificado && <span><CheckCircle2 size={17} /> Centro verificado</span>}{localizacao && <span><MapPin size={17} /> {localizacao}</span>}{course.certificado && <span><Award size={17} /> Certificado</span>}</div>
            </div>
            <div className="course-detail-hero-image">
              {course.imagem_url ? <img src={course.imagem_url} alt="" /> : <div className="course-detail-image-fallback"><GraduationCap size={42} /></div>}
              {video && <span className="course-detail-play"><Video size={25} /></span>}
            </div>
          </div>
        </div>
      </section>

      <section className="page-width course-detail-layout">
        <div className="course-detail-main">
          <section className="detail-section"><span className="eyebrow muted">Sobre esta formação</span><h2>Construa competências para o seu próximo passo.</h2><p className="detail-long-copy">{course.descricao || course.descricao_curta || "O centro ainda não publicou uma descrição completa para esta formação."}</p></section>

          <section className="detail-section detail-specs-section"><span className="eyebrow muted">Informações essenciais</span><div className="detail-specs-grid"><div><Clock3 size={20} /><span><b>Duração</b>{course.carga_horaria ? `${course.carga_horaria} horas` : "A confirmar"}</span></div><div><GraduationCap size={20} /><span><b>Nível</b>{course.nivel_label || "A confirmar"}</span></div><div><Globe2 size={20} /><span><b>Idioma</b>{course.idioma_label || "A confirmar"}</span></div><div><MonitorPlay size={20} /><span><b>Modalidade</b>{course.modalidade || "A confirmar"}</span></div></div></section>

          <section className="detail-section" id="turmas"><div className="detail-section-heading"><div><span className="eyebrow muted">Turmas disponíveis</span><h2>Escolha a turma que se adapta à sua rotina.</h2></div><span>{turmasDoCurso.length} {turmasDoCurso.length === 1 ? "turma aberta" : "turmas abertas"}</span></div>{turmasDoCurso.length ? <div className="detail-class-list">{turmasDoCurso.map((turma) => <TurmaCard key={turma.turma_id} turma={turma} onChoose={iniciarInscricao} />)}</div> : <div className="detail-empty-class"><CalendarDays size={21} /><div><b>Ainda não há turmas abertas.</b><p>Consulte o centro para saber quando haverá uma nova turma.</p></div></div>}</section>

          <section className="detail-section detail-centre-section"><span className="eyebrow muted">Centro de formação</span><div className="detail-centre-card"><div className="detail-centre-mark">{centro.slice(0, 1)}</div><div><h2>{centro}</h2><p>{localizacao || "Localização a confirmar pelo centro."}</p>{course.centro_atualizado_em && <small>Informação actualizada em {new Date(`${course.centro_atualizado_em}T12:00:00`).toLocaleDateString("pt-PT")}</small>}</div>{course.centro_verificado && <CheckCircle2 size={22} />}</div></section>
        </div>

        <aside className="course-detail-aside">
          <div className="detail-enrollment-card">
            <span className="detail-enrollment-kicker">Condições de inscrição</span><strong>{course.pagamento?.agora || "Valor a confirmar"}</strong>{!course.is_gratuito && <div className="detail-enrollment-breakdown"><span>Inscrição <b>{Number(course.financeiro?.inscricao?.valor) > 0 ? course.financeiro.inscricao.formatado : "Sem taxa"}</b></span>{Number(course.financeiro?.mensalidade?.valor) > 0 && <span>Mensalidade <b>{course.financeiro.mensalidade.formatado}</b></span>}</div>}<p>{course.pagamento?.descricao || "Consulte o centro para confirmar as condições de pagamento."}</p>
            <button className="detail-enrollment-action" type="button" onClick={() => iniciarInscricao(turmasDoCurso[0])}>Iniciar inscrição</button>
            <small>Não precisa iniciar sessão para começar a inscrição. A informação é confirmada antes do pagamento.</small>
          </div>
          <div className="detail-assurance"><CheckCircle2 size={17} /><span><b>Informação do centro</b>Datas, vagas e condições são publicadas pelo centro de formação.</span></div>
        </aside>
      </section>
      {recomendados.length > 0 && <div className="detail-recommendations"><CourseShelf id={`recomendados-${course.id}`} eyebrow="Também pode gostar" title="Cursos recomendados para continuar a aprender." description={`Formações relacionadas com ${course.categoria || "o seu interesse"}, escolhidas a partir dos cursos atualmente publicados.`} courses={recomendados} collectionHref={course.categoria ? `/cursos?categoria=${encodeURIComponent(course.categoria)}` : "/cursos"} onAnnounce={onAnnounce} /></div>}
    </main>
  );
}
