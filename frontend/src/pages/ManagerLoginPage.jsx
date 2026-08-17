import { useEffect, useState } from "react";
import { ArrowRight, BookOpen, Building2, Eye, EyeOff, LockKeyhole, Mail, Moon, RefreshCw, ShieldCheck, Sun } from "lucide-react";
import "./manager-login-page.css";

function csrfToken() {
  return document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith("csrftoken="))
    ?.split("=")
    .slice(1)
    .join("=") || "";
}

function CoursePreview({ course }) {
  return <article className="manager-login-course">
    <div className="manager-login-course-image">{course.imagem_url ? <img src={course.imagem_url} alt="" /> : <BookOpen size={18} />}</div>
    <div><strong>{course.titulo}</strong><span>{course.centro || "Centro de formação"}</span></div>
  </article>;
}

export default function ManagerLoginPage({ theme, onToggleTheme, onAuthenticated }) {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [courses, setCourses] = useState([]);
  const [status, setStatus] = useState({ type: "", message: "" });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;
    fetch("/api/public/home/", { credentials: "same-origin", headers: { Accept: "application/json" } })
      .then((response) => response.ok ? response.json() : Promise.reject(new Error("catalogue unavailable")))
      .then((payload) => {
        const catalogue = payload.turmas_abertas || payload.cursos || [];
        if (active) setCourses(catalogue.filter((course, index, list) => list.findIndex((item) => item.id === course.id) === index).slice(0, 3));
      })
      .catch(() => { if (active) setCourses([]); });
    return () => { active = false; };
  }, []);

  const submit = async (event) => {
    event.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    setStatus({ type: "", message: "" });
    try {
      if (!csrfToken()) await fetch("/backend/gestoreduka/login_gestor/", { credentials: "same-origin" });
      const body = new URLSearchParams({ email, senha, csrfmiddlewaretoken: decodeURIComponent(csrfToken()) });
      const response = await fetch("/backend/gestoreduka/login_gestor/", {
        method: "POST",
        credentials: "same-origin",
        redirect: "follow",
        headers: { "Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": decodeURIComponent(csrfToken()) },
        body,
      });
      const finalPath = new URL(response.url).pathname.replace(/\/+$/, "") || "/";
      if (response.ok && finalPath === "/gestoreduka") {
        onAuthenticated();
        return;
      }
      setStatus({ type: "error", message: "Não foi possível validar o acesso. Confirme o e-mail e a palavra-passe." });
    } catch {
      setStatus({ type: "error", message: "Não foi possível contactar o GestorEduka. Tente novamente dentro de instantes." });
    } finally {
      setSubmitting(false);
    }
  };

  return <main className="manager-login-page">
    <header className="manager-login-topbar">
      <a href="/" className="manager-login-brand" aria-label="Voltar à Edukangola"><span>E</span> Edukangola <b>Gestor</b></a>
      <div><a href="/" className="manager-login-back">Voltar ao site</a><button type="button" onClick={onToggleTheme} aria-label="Alternar tema">{theme === "light" ? <Moon size={17} /> : <Sun size={17} />}</button></div>
    </header>
    <section className="manager-login-shell">
      <aside className={courses.length ? "manager-login-discovery has-courses" : "manager-login-discovery"}>
        <div className="manager-login-discovery-copy">
          <span className="manager-login-overline"><ShieldCheck size={15} /> Gestão educacional</span>
          <h1>O lugar certo para fazer o seu centro avançar.</h1>
          <p>Organize formações, turmas, inscrições e a relação com os seus alunos num único espaço.</p>
        </div>
        {courses.length ? <div className="manager-login-course-list"><div className="manager-login-list-heading"><span>Cursos em destaque</span><small>Publicados na Edukangola</small></div>{courses.map((course) => <CoursePreview key={course.id} course={course} />)}</div> : <div className="manager-login-empty-catalogue"><div><Building2 size={21} /><strong>O seu espaço de gestão</strong></div><p>Assim que publicar a primeira formação, ela passa a poder ser descoberta por alunos em toda a plataforma.</p><ul><li><i>01</i> Crie os seus cursos</li><li><i>02</i> Organize as turmas</li><li><i>03</i> Acompanhe inscrições</li></ul></div>}
        <p className="manager-login-credit">GestorEduka · Administração para centros de formação</p>
      </aside>
      <section className="manager-login-form-area">
        <div className="manager-login-form-wrap">
          <div className="manager-login-heading"><span>Área reservada</span><h2>Bem-vindo de volta.</h2><p>Entre para gerir o seu centro de formação.</p></div>
          <form onSubmit={submit} noValidate>
            <label><span>E-mail profissional</span><div className="manager-login-field"><Mail size={18} /><input type="email" autoComplete="email" placeholder="nome@instituicao.ao" value={email} onChange={(event) => setEmail(event.target.value)} required /></div></label>
            <label><span>Palavra-passe</span><div className="manager-login-field"><LockKeyhole size={18} /><input type={showPassword ? "text" : "password"} autoComplete="current-password" placeholder="Introduza a sua palavra-passe" value={senha} onChange={(event) => setSenha(event.target.value)} required /><button type="button" aria-label={showPassword ? "Ocultar palavra-passe" : "Mostrar palavra-passe"} onClick={() => setShowPassword((value) => !value)}>{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button></div></label>
            {status.message && <p className={`manager-login-status ${status.type}`} role="alert">{status.message}</p>}
            <button className="manager-login-submit" disabled={submitting}>{submitting ? <><RefreshCw size={17} className="spinning" /> A validar acesso…</> : <>Entrar no GestorEduka <ArrowRight size={17} /></>}</button>
          </form>
          <div className="manager-login-first-access"><strong>Primeiro acesso?</strong><p>O cadastro do centro começa pelo processo de verificação da Edukangola. Use o convite recebido por e-mail para concluir o acesso.</p><a href="/para-centros">Conhecer o processo para centros <ArrowRight size={15} /></a></div>
          <p className="manager-login-help">Precisa de ajuda? Contacte o suporte da Edukangola.</p>
        </div>
      </section>
    </section>
  </main>;
}
