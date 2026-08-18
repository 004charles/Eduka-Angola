import { BookOpen, CircleHelp, GraduationCap, Layers3, Plus, Send, UsersRound, Video } from "lucide-react";
import { useEffect, useState } from "react";
import { authRequest } from "../lib/auth-api";
import "./instructor-portal-page.css";

const initialCourse = { titulo: "", descricao: "", categoria_id: "", is_pago: false, preco: "" };

function InstructorCourseShowcase({ courses = [] }) {
  const publishedCourses = courses.filter((course) => course?.titulo).slice(0, 10);
  const [currentIndex, setCurrentIndex] = useState(0);
  const currentCourse = publishedCourses[currentIndex % Math.max(publishedCourses.length, 1)];

  useEffect(() => {
    if (publishedCourses.length < 2) return undefined;
    const interval = window.setInterval(() => setCurrentIndex((index) => (index + 1) % publishedCourses.length), 4800);
    return () => window.clearInterval(interval);
  }, [publishedCourses.length]);

  if (!currentCourse) {
    return <aside className="instructor-showcase instructor-showcase-empty">
      <div className="instructor-showcase-brand"><span className="instructor-showcase-mark">E</span><span>Edukangola para formadores</span></div>
      <div className="instructor-showcase-empty-copy"><Video size={30} /><h2>Partilhe o que sabe.</h2><p>Os cursos publicados na Edukangola vão aparecer aqui.</p></div>
    </aside>;
  }

  const image = currentCourse.imagem_url || currentCourse.imageUrl || currentCourse.capa_url;
  const type = currentCourse.is_video ? "Curso em vídeo" : "Formação presencial";

  return <aside className="instructor-showcase" aria-label="Cursos publicados em destaque">
    <div className="instructor-showcase-brand"><span className="instructor-showcase-mark">E</span><span>Conhecimento que chega mais longe</span></div>
    <div className="instructor-course-viewport">
      <article className="instructor-course-slide" key={`${currentCourse.id || currentCourse.titulo}-${currentIndex}`}>
        <div className="instructor-course-image">
          {image ? <img src={image} alt="" /> : <div className="instructor-course-image-fallback"><Video size={46} /></div>}
          <span className="instructor-course-image-shade" />
        </div>
        <div className="instructor-course-copy">
          <span className="instructor-course-type"><Video size={14} /> {type}</span>
          <h2>{currentCourse.titulo}</h2>
          <p>{currentCourse.descricao_curta || currentCourse.descricao || "Uma formação publicada na Edukangola."}</p>
          <div className="instructor-course-meta"><span>{currentCourse.categoria || "Formação"}</span>{currentCourse.centro && <span>{currentCourse.centro}</span>}</div>
        </div>
      </article>
    </div>
    {publishedCourses.length > 1 && <div className="instructor-course-pagination" aria-label="Selecionar curso em destaque">
      {publishedCourses.map((course, index) => <button key={course.id || `${course.titulo}-${index}`} className={index === currentIndex ? "active" : ""} type="button" onClick={() => setCurrentIndex(index)} aria-label={`Mostrar ${course.titulo}`} />)}
    </div>}
    <p className="instructor-showcase-note">Cursos da comunidade Edukangola, sempre em movimento.</p>
  </aside>;
}

export default function InstructorPortalPage({ onNavigate, courses = [] }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [courseForm, setCourseForm] = useState(initialCourse);
  const [creating, setCreating] = useState(false);
  const [lessonFor, setLessonFor] = useState(null);
  const [lessonForm, setLessonForm] = useState({ titulo: "", video_url: "", descricao: "" });
  const [answering, setAnswering] = useState(null);
  const [answerText, setAnswerText] = useState("");
  const [credentials, setCredentials] = useState({ email: "", password: "" });
  const [applicationOpen, setApplicationOpen] = useState(false);
  const [applicationAreas, setApplicationAreas] = useState([]);
  const [applicationForm, setApplicationForm] = useState({ nome_completo: "", email: "", password: "", confirm_password: "", area_especializacao: "", biografia: "" });
  const [applicationFeedback, setApplicationFeedback] = useState("");
  const [applicationSubmitting, setApplicationSubmitting] = useState(false);

  const load = async () => {
    try {
      const response = await fetch("/backend/instrutor/api/react/dashboard/", { credentials: "same-origin", headers: { Accept: "application/json" } });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || "Não foi possível abrir o painel de formador.");
      setData(payload);
      setError("");
    } catch (reason) {
      setError(reason.message);
    }
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    if (!applicationOpen || applicationAreas.length) return;
    fetch("/backend/instrutor/api/react/candidatura/opcoes/", { headers: { Accept: "application/json" } })
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((payload) => setApplicationAreas(payload.areas || []))
      .catch(() => setApplicationFeedback("Não foi possível preparar a candidatura. Atualize a página e tente novamente."));
  }, [applicationOpen, applicationAreas.length]);

  const createCourse = async (event) => {
    event.preventDefault();
    setCreating(true);
    try {
      await authRequest("/instrutor/api/react/cursos/", { ...courseForm, categoria_id: Number(courseForm.categoria_id), preco: courseForm.preco || 0 });
      setCourseForm(initialCourse);
      await load();
    } catch (reason) {
      setError(reason.message || "Não foi possível criar o curso.");
    } finally {
      setCreating(false);
    }
  };

  const createLesson = async (event) => {
    event.preventDefault();
    try {
      await authRequest(`/instrutor/api/react/cursos/${lessonFor}/aulas/`, lessonForm);
      setLessonFor(null);
      setLessonForm({ titulo: "", video_url: "", descricao: "" });
      await load();
    } catch (reason) {
      setError(reason.message || "Não foi possível adicionar a aula.");
    }
  };

  const answerQuestion = async (event) => {
    event.preventDefault();
    try {
      await authRequest(`/instrutor/api/react/duvidas/${answering}/responder/`, { texto: answerText });
      setAnswering(null);
      setAnswerText("");
      await load();
    } catch (reason) {
      setError(reason.message || "Não foi possível enviar a resposta.");
    }
  };

  const loginInstructor = async (event) => {
    event.preventDefault();
    try {
      await authRequest("/instrutor/api/react/login/", credentials);
      await load();
    } catch (reason) {
      setError(reason.message || "Não foi possível iniciar sessão.");
    }
  };

  const submitApplication = async (event) => {
    event.preventDefault();
    setApplicationSubmitting(true);
    setApplicationFeedback("");
    try {
      const result = await authRequest("/instrutor/api/react/candidatura/", applicationForm);
      setApplicationFeedback(result.message);
    } catch (reason) {
      const fieldErrors = reason.data?.errors || {};
      const firstError = Object.values(fieldErrors).flat().at(0);
      setApplicationFeedback(firstError || reason.message || "Não foi possível enviar a candidatura.");
    } finally {
      setApplicationSubmitting(false);
    }
  };

  if (!data && !error) return <main className="instructor-portal"><p>A preparar o painel do formador…</p></main>;

  if (error && !data) {
    return <main className="instructor-portal instructor-login-layout">
      <section className="instructor-access">
        <GraduationCap size={30} />
        {applicationOpen ? <>
          <span>Candidatura a formador</span>
          <h1>Partilhe o que sabe.</h1>
          <p>Envie o seu perfil. Depois da análise da equipa, receberá acesso para publicar cursos em vídeo.</p>
          {applicationFeedback && <p className={`instructor-application-feedback${applicationFeedback.startsWith("Recebemos") ? " success" : ""}`} role="status">{applicationFeedback}</p>}
          {!applicationFeedback.startsWith("Recebemos") && <form className="instructor-application-form" onSubmit={submitApplication}>
            <label>Nome completo<input value={applicationForm.nome_completo} onChange={(event) => setApplicationForm({ ...applicationForm, nome_completo: event.target.value })} required autoComplete="name" placeholder="O seu nome" /></label>
            <label>E-mail profissional<input type="email" value={applicationForm.email} onChange={(event) => setApplicationForm({ ...applicationForm, email: event.target.value })} required autoComplete="email" placeholder="nome@email.com" /></label>
            <div className="instructor-application-passwords"><label>Palavra-passe<input type="password" value={applicationForm.password} onChange={(event) => setApplicationForm({ ...applicationForm, password: event.target.value })} required minLength="8" autoComplete="new-password" /></label><label>Confirmar<input type="password" value={applicationForm.confirm_password} onChange={(event) => setApplicationForm({ ...applicationForm, confirm_password: event.target.value })} required minLength="8" autoComplete="new-password" /></label></div>
            <label>Área de especialização<select value={applicationForm.area_especializacao} onChange={(event) => setApplicationForm({ ...applicationForm, area_especializacao: event.target.value })} required><option value="">Selecionar área</option>{applicationAreas.map((area) => <option value={area.valor} key={area.valor}>{area.nome}</option>)}</select></label>
            <label>Experiência e abordagem de ensino<textarea value={applicationForm.biografia} onChange={(event) => setApplicationForm({ ...applicationForm, biografia: event.target.value })} required minLength="20" placeholder="Conte brevemente a sua experiência e o que pretende ensinar." /></label>
            <button disabled={applicationSubmitting || !applicationAreas.length}>{applicationSubmitting ? "A enviar candidatura…" : "Enviar candidatura"}</button>
          </form>}
          <div className="instructor-access-footer"><button type="button" onClick={() => { setApplicationOpen(false); setApplicationFeedback(""); }}>Já é formador? Entrar</button></div>
        </> : <>
          <span>Área do formador</span>
          <h1>Entre para gerir os seus cursos</h1>
          <p>Esta área é exclusiva para formadores aprovados.</p>
          <form onSubmit={loginInstructor}>
            <label>E-mail<input type="email" value={credentials.email} onChange={(event) => setCredentials({ ...credentials, email: event.target.value })} required autoComplete="email" placeholder="nome@email.com" /></label>
            <label>Palavra-passe<input type="password" value={credentials.password} onChange={(event) => setCredentials({ ...credentials, password: event.target.value })} required autoComplete="current-password" placeholder="A sua palavra-passe" /></label>
            <button>Entrar como formador</button>
          </form>
          <div className="instructor-access-footer"><span>Ainda não é formador?</span><button type="button" onClick={() => setApplicationOpen(true)}>Candidate-se para ensinar</button></div>
        </>}
      </section>
      <InstructorCourseShowcase courses={courses} />
    </main>;
  }

  const metrics = [
    [BookOpen, "Cursos", data.metricas.cursos],
    [UsersRound, "Alunos", data.metricas.alunos],
    [Video, "Aulas", data.metricas.aulas],
    [CircleHelp, "Dúvidas pendentes", data.metricas.duvidas_pendentes],
  ];

  return <main className="instructor-portal">
    <header className="instructor-hero">
      <div><span>Área do formador</span><h1>Olá, {data.instrutor.nome.split(" ")[0]}.</h1><p>Publique conhecimento, acompanhe os alunos e responda às dúvidas que fazem cada aula avançar.</p></div>
      <div className="instructor-profile"><GraduationCap size={21} /><div><strong>{data.instrutor.titulo}</strong><small>{data.instrutor.nota_media ? `${data.instrutor.nota_media} de avaliação média` : "Perfil pronto para publicar"}</small></div></div>
    </header>
    {error && <p className="instructor-error">{error}</p>}
    <section className="instructor-metrics">{metrics.map(([Icon, label, value]) => <article key={label}><Icon size={19} /><span>{label}</span><strong>{value}</strong></article>)}</section>
    <section className="instructor-section">
      <div className="instructor-heading"><div><span>Catálogo digital</span><h2>Publique o seu próximo curso</h2></div></div>
      <form className="instructor-course-form" onSubmit={createCourse}>
        <input value={courseForm.titulo} onChange={(event) => setCourseForm({ ...courseForm, titulo: event.target.value })} placeholder="Título do curso" required minLength="3" />
        <select value={courseForm.categoria_id} onChange={(event) => setCourseForm({ ...courseForm, categoria_id: event.target.value })} required><option value="">Escolha a categoria</option>{data.categorias.map((category) => <option value={category.id} key={category.id}>{category.nome}</option>)}</select>
        <textarea value={courseForm.descricao} onChange={(event) => setCourseForm({ ...courseForm, descricao: event.target.value })} placeholder="Explique o que o aluno vai aprender" required minLength="20" />
        <label className="instructor-price"><input type="checkbox" checked={courseForm.is_pago} onChange={(event) => setCourseForm({ ...courseForm, is_pago: event.target.checked })} /> Curso pago</label>
        {courseForm.is_pago && <input type="number" min="0" value={courseForm.preco} onChange={(event) => setCourseForm({ ...courseForm, preco: event.target.value })} placeholder="Preço em Kz" />}
        <button disabled={creating}><Plus size={17} />{creating ? "A criar…" : "Criar curso"}</button>
      </form>
    </section>
    <section className="instructor-section">
      <div className="instructor-heading"><div><span>O seu catálogo</span><h2>Cursos em vídeo</h2></div></div>
      <div className="instructor-courses">{data.cursos.length ? data.cursos.map((course) => <article key={course.id}>
        <div className="instructor-cover">{course.capa_url ? <img src={course.capa_url} alt="" /> : <Layers3 />}</div>
        <div><span>{course.categoria}</span><h3>{course.titulo}</h3><p>{course.aulas} aulas · {course.inscritos} alunos · {course.avaliacao_media || "Sem"} avaliação</p></div>
        <button onClick={() => setLessonFor(course.id)}><Plus size={16} />Adicionar aula</button>
        {lessonFor === course.id && <form className="instructor-lesson-form" onSubmit={createLesson}>
          <input value={lessonForm.titulo} onChange={(event) => setLessonForm({ ...lessonForm, titulo: event.target.value })} placeholder="Título da aula" required />
          <input value={lessonForm.video_url} onChange={(event) => setLessonForm({ ...lessonForm, video_url: event.target.value })} type="url" placeholder="Ligação YouTube, Vimeo ou vídeo externo" required />
          <textarea value={lessonForm.descricao} onChange={(event) => setLessonForm({ ...lessonForm, descricao: event.target.value })} placeholder="Resumo opcional" />
          <div><button type="button" onClick={() => setLessonFor(null)}>Cancelar</button><button>Guardar aula</button></div>
        </form>}
      </article>) : <p className="instructor-empty">Ainda não publicou cursos. Use o formulário acima para criar o primeiro.</p>}</div>
    </section>
    <section className="instructor-section">
      <div className="instructor-heading"><div><span>Comunidade de aprendizagem</span><h2>Dúvidas dos alunos</h2></div></div>
      <div className="instructor-questions">{data.duvidas.length ? data.duvidas.map((question) => <article key={question.id}>
        <div><span>{question.curso} · {question.aula}</span><h3>{question.aluno} perguntou {question.resolvida && <em className="instructor-resolved">Resolvida</em>}</h3><p>{question.texto}</p>{question.respostas.map((answer) => <blockquote key={answer.id}><strong>{answer.autor}</strong><br />{answer.texto}</blockquote>)}</div>
        {answering === question.id ? <form onSubmit={answerQuestion}><textarea value={answerText} onChange={(event) => setAnswerText(event.target.value)} placeholder="Escreva uma resposta clara para o aluno" required /><button><Send size={15} />Enviar resposta</button></form> : <button onClick={() => setAnswering(question.id)}>{question.respondida ? "Adicionar resposta" : "Responder"}</button>}
      </article>) : <p className="instructor-empty">As dúvidas dos alunos aparecerão aqui assim que forem enviadas durante as aulas.</p>}</div>
    </section>
  </main>;
}
