import { ArrowLeft, BellRing, CalendarDays, Check, CircleAlert, GraduationCap, KeyRound, Mail, Send, Settings2, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { backendUrl } from "../lib/backend-url";
import "./student-settings-page.css";

const INITIAL = { receber_na_plataforma: true, receber_por_email: true, novos_cursos: true, novas_turmas: true, novos_livros: true, novos_eventos: true, atualizacoes_aprendizagem: true, calendario_e_feriados: true, resumo_semanal: true };
const AREAS = [
  ["TECNOLOGIA_INFORMACAO", "Tecnologia de Informação"], ["NEGOCIO", "Negócio"], ["LINGUAS", "Línguas"], ["ESPECIALIZADA", "Especializada"], ["CIENCIAS", "Ciências"], ["ARTES", "Artes"], ["ENGENHARIA", "Engenharia"], ["SAUDE", "Saúde"], ["OUTRO", "Outra área"],
];

function csrfToken() { return document.cookie.split(";").map((item) => item.trim()).find((item) => item.startsWith("csrftoken="))?.split("=").slice(1).join("=") || ""; }

function SettingToggle({ label, hint, checked, onChange }) {
  return <label className="settings-toggle"><span><strong>{label}</strong><small>{hint}</small></span><input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} /><i aria-hidden="true" /></label>;
}

function InstructorApplication({ onCompleted }) {
  const [open, setOpen] = useState(false);
  const [state, setState] = useState({ loadingTest: false, sending: false, submitting: false, step: "perfil", questions: [], error: "", message: "", code: "", form: { titulo_profissional: "", area_especializacao: "", biografia: "", proposta_curso: "", respostas_teste: {} } });

  const setField = (field, value) => setState((current) => ({ ...current, error: "", form: { ...current.form, [field]: value } }));
  const setAnswer = (id, value) => setState((current) => ({ ...current, form: { ...current.form, respostas_teste: { ...current.form.respostas_teste, [id]: value } } }));

  const openApplication = async () => {
    setState((current) => ({ ...current, loadingTest: true, error: "", message: "" }));
    try {
      const response = await fetch(backendUrl("/auth/api/react/aluno/formador/teste/"), { credentials: "same-origin", headers: { Accept: "application/json" } });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Não foi possível preparar a candidatura.");
      setState((current) => ({ ...current, open: true, loadingTest: false, questions: data.questoes || [] }));
      setOpen(true);
    } catch (error) { setState((current) => ({ ...current, loadingTest: false, error: error.message })); }
  };

  const sendCode = async () => {
    setState((current) => ({ ...current, sending: true, error: "", message: "" }));
    try {
      const response = await fetch(backendUrl("/auth/api/react/aluno/formador/enviar-codigo/"), { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() }, body: "{}" });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Não foi possível enviar o código.");
      setState((current) => ({ ...current, sending: false, step: "confirmar", message: data.message || "Enviámos o código para o seu e-mail." }));
    } catch (error) { setState((current) => ({ ...current, sending: false, error: error.message })); }
  };

  const submit = async (event) => {
    event.preventDefault();
    setState((current) => ({ ...current, submitting: true, error: "" }));
    try {
      const response = await fetch(backendUrl("/auth/api/react/aluno/formador/candidatar/"), { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() }, body: JSON.stringify({ ...state.form, codigo: state.code }) });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Não foi possível enviar a candidatura.");
      setState((current) => ({ ...current, submitting: false, message: data.message || "Candidatura enviada." }));
      onCompleted();
    } catch (error) { setState((current) => ({ ...current, submitting: false, error: error.message })); }
  };

  return <section className="settings-card instructor-candidacy">
    <div className="settings-card-heading"><span><GraduationCap size={19} /></span><div><h2>Tornar-me formador</h2><p>Partilhe a sua experiência e apresente a sua proposta de curso à equipa Edukangola.</p></div></div>
    {!open && <button className="instructor-candidacy-trigger" type="button" onClick={openApplication} disabled={state.loadingTest}>{state.loadingTest ? "A preparar…" : "Tornar-me formador"}</button>}
    {state.error && <p className="settings-feedback error" role="alert">{state.error}</p>}
    {open && <form className="instructor-candidacy-form" onSubmit={submit}>
      <label>Título profissional<input value={state.form.titulo_profissional} onChange={(event) => setField("titulo_profissional", event.target.value)} placeholder="Ex.: Especialista em análise de dados" required /></label>
      <label>Área de especialização<select value={state.form.area_especializacao} onChange={(event) => setField("area_especializacao", event.target.value)} required><option value="">Seleccione a área</option>{AREAS.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label>
      <label>Experiência e abordagem de ensino<textarea value={state.form.biografia} onChange={(event) => setField("biografia", event.target.value)} placeholder="Descreva a sua experiência relevante e como pretende ensinar." minLength="40" required /></label>
      <label>Proposta inicial de curso<textarea value={state.form.proposta_curso} onChange={(event) => setField("proposta_curso", event.target.value)} placeholder="Que curso pretende criar e que transformação propõe ao aluno?" minLength="40" required /></label>
      <div className="instructor-quiz"><strong>Avaliação de boas práticas</strong><p>Responda às questões antes de enviar a candidatura.</p>{state.questions.map((question) => <fieldset key={question.id}><legend>{question.pergunta}</legend>{question.opcoes.map((option) => <label key={option.id} className="instructor-quiz-option"><input type="radio" name={question.id} checked={state.form.respostas_teste[question.id] === option.id} onChange={() => setAnswer(question.id, option.id)} required /><span>{option.texto}</span></label>)}</fieldset>)}</div>
      {state.step === "perfil" ? <button className="instructor-candidacy-trigger" type="button" onClick={sendCode} disabled={state.sending}>{state.sending ? "A enviar…" : <><Send size={16} /> Enviar código por e-mail</>}</button> : <><label className="instructor-code"><KeyRound size={16} /> Código de confirmação<input value={state.code} onChange={(event) => setState((current) => ({ ...current, code: event.target.value.replace(/\D/g, "").slice(0, 6), error: "" }))} inputMode="numeric" placeholder="000000" required /></label><button className="instructor-candidacy-trigger" type="submit" disabled={state.submitting}>{state.submitting ? "A enviar candidatura…" : "Enviar candidatura"}</button></>}
      {state.message && <p className="settings-feedback success" role="status"><Check size={16} /> {state.message}</p>}
    </form>}
  </section>;
}

export default function StudentSettingsPage({ onNavigate, onLogout }) {
  const [state, setState] = useState({ loading: true, saving: false, error: "", message: "", account: null, formador: null, values: INITIAL });
  const load = () => fetch(backendUrl("/auth/api/react/aluno/configuracoes/"), { credentials: "same-origin", headers: { Accept: "application/json" } }).then(async (response) => { const data = await response.json().catch(() => ({})); if (response.status === 401) throw new Error("login"); if (!response.ok) throw new Error(data.detail || "Não foi possível carregar as configurações."); return data; }).then((data) => setState((current) => ({ ...current, loading: false, account: data.conta, formador: data.formador || null, values: { ...INITIAL, ...(data.notificacoes || {}) } }))).catch((error) => setState((current) => ({ ...current, loading: false, error: error.message })));
  useEffect(() => { load(); }, []);
  const setValue = (field, value) => setState((current) => ({ ...current, values: { ...current.values, [field]: value }, message: "", error: "" }));
  const save = async (event) => { event.preventDefault(); setState((current) => ({ ...current, saving: true, message: "", error: "" })); try { const response = await fetch(backendUrl("/auth/api/react/aluno/configuracoes/actualizar/"), { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", Accept: "application/json", "X-CSRFToken": csrfToken() }, body: JSON.stringify(state.values) }); const data = await response.json().catch(() => ({})); if (!response.ok) throw new Error(data.detail || "Não foi possível guardar as configurações."); setState((current) => ({ ...current, saving: false, values: { ...current.values, ...(data.notificacoes || {}) }, message: data.message || "Configurações guardadas." })); } catch (error) { setState((current) => ({ ...current, saving: false, error: error.message })); } };
  if (state.loading) return <main className="settings-page"><div className="page-width settings-loading">A carregar as suas configurações…</div></main>;
  if (state.error === "login") return <main className="settings-page"><section className="page-width settings-gate"><h1>Entre para gerir as suas configurações.</h1><button className="primary-action" onClick={() => onNavigate("/entrar?next=/aluno/configuracoes")}>Entrar</button></section></main>;
  if (state.error && !state.account) return <main className="settings-page"><section className="page-width settings-gate"><CircleAlert size={25} /><h1>Não foi possível abrir as configurações.</h1><p>{state.error}</p><button className="primary-action" onClick={() => window.location.reload()}>Tentar novamente</button></section></main>;
  return <main className="settings-page"><section className="settings-hero"><div className="page-width"><button className="settings-back" type="button" onClick={() => onNavigate("/aluno")}><ArrowLeft size={17} /> Voltar à área do aluno</button><span className="eyebrow"><Settings2 size={15} /> Conta do aluno</span><h1>Configurações</h1><p>Escolha as novidades que são realmente úteis para o seu percurso. Pode alterar estas escolhas quando quiser.</p></div></section><form className="page-width settings-form" onSubmit={save}><section className="settings-profile"><span><ShieldCheck size={19} /></span><div><strong>{state.account?.nome}</strong><small>{state.account?.email}</small></div></section>{state.formador?.estado === "ELEGIVEL" && <InstructorApplication onCompleted={load} />}{state.formador?.estado === "PENDENTE_ANALISE" && <section className="settings-card instructor-status"><GraduationCap size={20} /><div><strong>Candidatura de formador em análise</strong><p>A equipa Edukangola está a analisar a sua candidatura.</p></div></section>}{state.formador?.estado === "APROVADA" && <section className="settings-card instructor-status approved"><Check size={20} /><div><strong>Perfil de formador aprovado</strong><p>A sua conta de aluno recebeu também a permissão de formador.</p></div></section>}<section className="settings-card"><div className="settings-card-heading"><span><BellRing size={19} /></span><div><h2>Como quer receber?</h2><p>As notificações importantes da sua conta continuam visíveis na plataforma.</p></div></div><SettingToggle label="Notificações na plataforma" hint="Avisos no sino e na área do aluno." checked={state.values.receber_na_plataforma} onChange={(value) => setValue("receber_na_plataforma", value)} /><SettingToggle label="Resumo por e-mail" hint="Receba um resumo útil, sem excesso de mensagens." checked={state.values.receber_por_email} onChange={(value) => setValue("receber_por_email", value)} /></section><section className="settings-card"><div className="settings-card-heading"><span><Mail size={19} /></span><div><h2>Novidades para descobrir</h2><p>Seleccione apenas os assuntos que gostaria de acompanhar.</p></div></div><SettingToggle label="Novos cursos" hint="Cursos publicados que podem corresponder aos seus interesses." checked={state.values.novos_cursos} onChange={(value) => setValue("novos_cursos", value)} /><SettingToggle label="Turmas abertas" hint="Novas datas, vagas e turmas de cursos presenciais." checked={state.values.novas_turmas} onChange={(value) => setValue("novas_turmas", value)} /><SettingToggle label="Novos livros" hint="Obras novas e gratuitas na Biblioteca Edukangola." checked={state.values.novos_livros} onChange={(value) => setValue("novos_livros", value)} /><SettingToggle label="Eventos" hint="Eventos publicados, alterações relevantes e bilhetes." checked={state.values.novos_eventos} onChange={(value) => setValue("novos_eventos", value)} /></section><section className="settings-card"><div className="settings-card-heading"><span><CalendarDays size={19} /></span><div><h2>O seu ritmo</h2><p>Lembretes orientados à aprendizagem e informação de calendário.</p></div></div><SettingToggle label="Lembretes de aprendizagem" hint="Retomar cursos e livros, prazos e progresso importante." checked={state.values.atualizacoes_aprendizagem} onChange={(value) => setValue("atualizacoes_aprendizagem", value)} /><SettingToggle label="Calendário e feriados" hint="Avisos de calendário nacional confirmados pela equipa Edukangola." checked={state.values.calendario_e_feriados} onChange={(value) => setValue("calendario_e_feriados", value)} /><SettingToggle label="Resumo semanal" hint="Uma síntese por semana com novidades seleccionadas." checked={state.values.resumo_semanal} onChange={(value) => setValue("resumo_semanal", value)} /></section>{state.error && <p className="settings-feedback error" role="alert">{state.error}</p>}{state.message && <p className="settings-feedback success" role="status"><Check size={16} /> {state.message}</p>}<div className="settings-actions"><button className="primary-action" type="submit" disabled={state.saving}>{state.saving ? "A guardar…" : "Guardar configurações"}</button><button type="button" className="settings-cancel" onClick={() => onNavigate("/aluno")}>Cancelar</button></div><div className="settings-logout"><p>Quer sair da sua conta neste dispositivo?</p><button type="button" onClick={onLogout}>Terminar sessão</button></div></form></main>;
}
