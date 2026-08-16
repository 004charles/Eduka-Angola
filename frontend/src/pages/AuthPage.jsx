import { useEffect, useState } from "react";
import { ArrowLeft, CheckCircle2, ChevronRight, Eye, EyeOff, KeyRound, LockKeyhole, Mail, RefreshCw, ShieldCheck, UserRound, Video } from "lucide-react";
import { authRequest } from "../lib/auth-api";
import "./auth-page.css";

const CONTENT = {
  login: {
    eyebrow: "Área do aluno",
    title: "Continue o seu percurso.",
    description: "Entre para acompanhar inscrições, cursos em vídeo e certificados.",
    action: "Entrar",
  },
  register: {
    eyebrow: "Criar conta",
    title: "A sua aprendizagem começa aqui.",
    description: "Crie a sua conta para guardar cursos, acompanhar inscrições e estudar ao seu ritmo.",
    action: "Criar conta e continuar",
  },
  verify: {
    eyebrow: "Confirmar e-mail",
    title: "Confirme a sua conta.",
    description: "Enviámos um código de seis dígitos para o seu e-mail. Introduza-o para concluir o acesso.",
    action: "Confirmar e entrar",
  },
  recover: {
    eyebrow: "Recuperar acesso",
    title: "Vamos ajudá-lo a entrar.",
    description: "Indique o e-mail da sua conta e enviaremos um código de recuperação.",
    action: "Enviar código",
  },
  reset: {
    eyebrow: "Nova palavra-passe",
    title: "Defina uma nova palavra-passe.",
    description: "Use o código que recebeu por e-mail e escolha uma palavra-passe com pelo menos oito caracteres.",
    action: "Guardar e entrar",
  },
};

function PasswordInput({ id, label, value, onChange, autoComplete = "new-password" }) {
  const [visible, setVisible] = useState(false);
  return <label className="auth-field" htmlFor={id}><span>{label}</span><div className="auth-password"><LockKeyhole size={18} /><input id={id} type={visible ? "text" : "password"} value={value} onChange={onChange} minLength="8" required autoComplete={autoComplete} /><button type="button" onClick={() => setVisible((state) => !state)} aria-label={visible ? "Ocultar palavra-passe" : "Mostrar palavra-passe"}>{visible ? <EyeOff size={18} /> : <Eye size={18} />}</button></div></label>;
}

function CourseShowcase({ courses }) {
  const publishedCourses = (courses || []).filter((course) => course?.titulo).slice(0, 10);
  const [currentIndex, setCurrentIndex] = useState(0);
  const currentCourse = publishedCourses[currentIndex % Math.max(publishedCourses.length, 1)];

  useEffect(() => {
    if (publishedCourses.length < 2) return undefined;
    const interval = window.setInterval(() => setCurrentIndex((index) => (index + 1) % publishedCourses.length), 4800);
    return () => window.clearInterval(interval);
  }, [publishedCourses.length]);

  if (!currentCourse) return <aside className="auth-showcase auth-showcase-empty"><ShieldCheck size={28} /><p>As formações publicadas pela Edukangola aparecerão aqui.</p></aside>;

  const isVideo = Boolean(currentCourse.is_video);
  const image = currentCourse.imagem_url || currentCourse.imageUrl;
  return <aside className="auth-showcase" aria-label="Formações em destaque">
    <div className="auth-showcase-brand"><span className="auth-showcase-mark">E</span><span>Descubra a sua próxima competência</span></div>
    <div className="auth-course-viewport">
      <article className="auth-course-slide" key={`${currentCourse.id}-${currentIndex}`}>
        <div className="auth-course-image">{image ? <img src={image} alt="" /> : <div className="auth-course-image-fallback"><ShieldCheck size={48} /></div>}<span className="auth-course-image-shade" /></div>
        <div className="auth-course-copy"><span className="auth-course-type">{isVideo ? <><Video size={14} /> Curso em vídeo</> : "Curso presencial"}</span><h2>{currentCourse.titulo}</h2><p>{currentCourse.descricao_curta || currentCourse.descricao || "Formação publicada na Edukangola."}</p><div className="auth-course-meta"><span>{currentCourse.categoria || "Formação"}</span>{currentCourse.centro && <span>{currentCourse.centro}</span>}</div></div>
      </article>
    </div>
    {publishedCourses.length > 1 && <div className="auth-course-pagination" aria-label="Selecionar formação em destaque">{publishedCourses.map((course, index) => <button key={course.id || index} className={index === currentIndex ? "active" : ""} type="button" onClick={() => setCurrentIndex(index)} aria-label={`Mostrar ${course.titulo}`} />)}</div>}
    <p className="auth-showcase-note">Uma formação de cada vez, escolhida entre os cursos publicados.</p>
  </aside>;
}

export default function AuthPage({ mode, onNavigate, onSessionReady, courses = [] }) {
  const query = new URLSearchParams(window.location.search);
  const next = query.get("next") || "/";
  const [form, setForm] = useState({ nome: "", email: query.get("email") || "", senha: "", confirmar_senha: "", codigo: "" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [transitioning, setTransitioning] = useState(false);
  const content = CONTENT[mode];
  const setValue = (field) => (event) => setForm((current) => ({ ...current, [field]: event.target.value }));
  const routeWithNext = (path) => `${path}${path.includes("?") ? "&" : "?"}next=${encodeURIComponent(next)}`;
  const transitionTo = (destination) => {
    if (transitioning) return;
    const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (reducedMotion) { onNavigate(destination); return; }
    setTransitioning(true);
    window.setTimeout(() => onNavigate(destination), 180);
  };
  const redirectAfterAuth = (destination) => {
    const target = destination === "/" ? "/aluno" : (destination || next || "/aluno");
    if (target.startsWith("/backend/")) window.location.assign(target);
    else onNavigate(target);
  };
  const request = async (path, payload) => {
    setSubmitting(true); setError(""); setMessage("");
    try { return await authRequest(path, payload); }
    catch (requestError) {
      const details = requestError?.data || {};
      if (details.code === "EMAIL_NAO_VERIFICADO") { transitionTo(routeWithNext(`/verificar-email?email=${encodeURIComponent(form.email)}`)); return null; }
      setError(details.message || requestError.message || "Não foi possível concluir esta ação."); return null;
    } finally { setSubmitting(false); }
  };
  const submit = async (event) => {
    event.preventDefault();
    let result;
    if (mode === "login") {
      result = await request("/auth/api/react/login/", { email: form.email, senha: form.senha, next });
      if (result?.ok) { await onSessionReady?.(); redirectAfterAuth(result.redirect); }
    }
    if (mode === "register") {
      result = await request("/auth/api/react/registro/", { ...form, next });
      if (result?.ok) transitionTo(`/verificar-email?email=${encodeURIComponent(result.email || form.email)}&next=${encodeURIComponent(next)}`);
    }
    if (mode === "verify") {
      result = await request("/auth/api/react/verificar-email/", { codigo: form.codigo });
      if (result?.ok) { await onSessionReady?.(); redirectAfterAuth(result.redirect); }
    }
    if (mode === "recover") {
      result = await request("/auth/api/react/recuperar-senha/", { email: form.email, next });
      if (result?.ok) { setMessage(result.message); window.setTimeout(() => transitionTo(routeWithNext("/redefinir-palavra-passe")), 700); }
    }
    if (mode === "reset") {
      result = await request("/auth/api/react/redefinir-senha/", { codigo: form.codigo, senha: form.senha, confirmar_senha: form.confirmar_senha });
      if (result?.ok) { await onSessionReady?.(); redirectAfterAuth(result.redirect); }
    }
  };
  const resend = async () => {
    const result = await request("/auth/api/react/reenviar-codigo/");
    if (result?.ok) setMessage(result.message);
  };

  return <main className={`auth-page auth-page-${mode}${transitioning ? " auth-is-leaving" : ""}`} aria-busy={transitioning}><div className="page-width auth-shell"><button className="auth-back" type="button" onClick={() => onNavigate("/")}><ArrowLeft size={17} /> Voltar ao catálogo</button><CourseShowcase courses={courses} /><div className="auth-right"><section className="auth-intro"><span className="eyebrow"><ShieldCheck size={15} /> {content.eyebrow}</span><h1>{content.title}</h1><p>{content.description}</p></section><section className="auth-card" aria-labelledby="auth-title"><div className="auth-card-icon">{mode === "register" ? <UserRound size={24} /> : mode === "verify" ? <ShieldCheck size={24} /> : mode === "recover" || mode === "reset" ? <KeyRound size={24} /> : <Mail size={24} />}</div><h2 id="auth-title">{mode === "login" ? "Entrar" : mode === "register" ? "Criar conta" : mode === "verify" ? "Verificar e-mail" : mode === "recover" ? "Recuperar palavra-passe" : "Nova palavra-passe"}</h2>{mode === "verify" && form.email && <p className="auth-email-note">Código enviado para <strong>{form.email}</strong></p>}<form className="auth-form" onSubmit={submit}>{mode === "register" && <label className="auth-field" htmlFor="auth-name"><span>Nome completo</span><div className="auth-input"><UserRound size={18} /><input id="auth-name" value={form.nome} onChange={setValue("nome")} required autoComplete="name" /></div></label>}{["login", "register", "recover"].includes(mode) && <label className="auth-field" htmlFor="auth-email"><span>E-mail</span><div className="auth-input"><Mail size={18} /><input id="auth-email" type="email" value={form.email} onChange={setValue("email")} required autoComplete="email" placeholder="nome@email.com" /></div></label>}{["verify", "reset"].includes(mode) && <label className="auth-field" htmlFor="auth-code"><span>Código de seis dígitos</span><div className="auth-input"><KeyRound size={18} /><input id="auth-code" inputMode="numeric" autoComplete="one-time-code" value={form.codigo} onChange={setValue("codigo")} pattern="[0-9]{6}" maxLength="6" required placeholder="000000" /></div></label>}{["login", "register", "reset"].includes(mode) && <PasswordInput id="auth-password" label="Palavra-passe" value={form.senha} onChange={setValue("senha")} autoComplete={mode === "login" ? "current-password" : "new-password"} />}{["register", "reset"].includes(mode) && <PasswordInput id="auth-password-confirm" label="Confirmar palavra-passe" value={form.confirmar_senha} onChange={setValue("confirmar_senha")} />}{error && <p className="auth-feedback error" role="alert">{error}</p>}{message && <p className="auth-feedback success" role="status">{message}</p>}<button className="primary-action auth-submit" disabled={submitting} type="submit">{submitting ? "A processar…" : content.action}<ChevronRight size={17} /></button></form>{mode === "login" && <div className="auth-card-footer"><button type="button" onClick={() => transitionTo(routeWithNext("/recuperar-palavra-passe"))}>Esqueci-me da palavra-passe</button><p>Ainda não tem conta? <button type="button" onClick={() => transitionTo(routeWithNext("/criar-conta"))}>Criar conta</button></p></div>}{mode === "register" && <div className="auth-card-footer"><p>Já tem conta? <button type="button" onClick={() => transitionTo(routeWithNext("/entrar"))}>Entrar</button></p><small>Depois deste passo, enviamos um código para confirmar o seu e-mail. Ao criar a conta, declara que leu a <a href="/politica-de-privacidade" target="_blank" rel="noreferrer">Política de privacidade</a>.</small></div>}{mode === "verify" && <div className="auth-card-footer"><button className="resend-button" type="button" onClick={resend} disabled={submitting}><RefreshCw size={14} /> Reenviar código</button><p>Introduziu outro e-mail? <button type="button" onClick={() => transitionTo(routeWithNext("/criar-conta"))}>Voltar ao cadastro</button></p></div>}{mode === "recover" && <div className="auth-card-footer"><p>Lembrou-se da palavra-passe? <button type="button" onClick={() => transitionTo(routeWithNext("/entrar"))}>Entrar</button></p></div>}{mode === "reset" && <div className="auth-card-footer"><p>Não recebeu o código? <button type="button" onClick={() => transitionTo(routeWithNext("/recuperar-palavra-passe"))}>Pedir novo código</button></p></div>}</section></div></div></main>;
}
