import { BarChart3, BookOpen, CalendarDays, ChevronRight, CreditCard, GraduationCap, Landmark, MessageCircle, Moon, Pencil, Sun, Trash2, UsersRound } from "lucide-react";
import { useEffect, useState } from "react";
import ManagerAnnouncementsPanel from "../components/ManagerAnnouncementsPanel";
import ManagerAnalyticsPanel from "../components/ManagerAnalyticsPanel";
import ManagerBranchesPanel from "../components/ManagerBranchesPanel";
import ManagerChatPanel from "../components/ManagerChatPanel";
import ManagerClassesPanel from "../components/ManagerClassesPanel";
import ManagerCommentsPanel from "../components/ManagerCommentsPanel";
import ManagerCourseForm from "../components/ManagerCourseForm";
import ManagerEnrollmentsPanel from "../components/ManagerEnrollmentsPanel";
import ManagerEventsPanel from "../components/ManagerEventsPanel";
import ManagerFinancePanel from "../components/ManagerFinancePanel";
import ManagerGalleryPanel from "../components/ManagerGalleryPanel";
import ManagerInstructorsPanel from "../components/ManagerInstructorsPanel";
import ManagerInternshipsPanel from "../components/ManagerInternshipsPanel";
import ManagerProfilePanel from "../components/ManagerProfilePanel";
import ManagerStudentsPanel from "../components/ManagerStudentsPanel";
import ManagerSubscriptionPanel from "../components/ManagerSubscriptionPanel";
import ManagerVideoCertificatesPanel from "../components/ManagerVideoCertificatesPanel";
import ManagerVideoCoursesPanel from "../components/ManagerVideoCoursesPanel";
import ManagerLoginPage from "./ManagerLoginPage";
import "./manager-portal-page.css";
import "./manager-modules-page.css";

const money = new Intl.NumberFormat("pt-AO", { maximumFractionDigits: 0 });

const navigation = [
  { key: "visao-geral", label: "Visão geral", href: "/gestoreduka/" },
  { key: "cursos", label: "Cursos presenciais", href: "/gestoreduka/cursos/" },
  { key: "cursos-video", label: "Cursos em vídeo", href: "/gestoreduka/cursos-video/" },
  { key: "inscricoes", label: "Inscrições", href: "/gestoreduka/inscricoes/" },
  { key: "turmas", label: "Turmas", href: "/gestoreduka/turmas/" },
  { key: "formadores", label: "Formadores", href: "/gestoreduka/formadores/" },
  { key: "filiais", label: "Filiais", href: "/gestoreduka/filiais/" },
  { key: "eventos", label: "Eventos", href: "/gestoreduka/eventos/" },
  { key: "estagios", label: "Estágios", href: "/gestoreduka/estagios/" },
  { key: "financeiro", label: "Financeiro", href: "/gestoreduka/financeiro/" },
  { key: "analytics", label: "Analytics", href: "/gestoreduka/analytics/" },
  { key: "mensagens", label: "Mensagens", href: "/gestoreduka/mensagens/" },
  { key: "comunicados", label: "Comunicados", href: "/gestoreduka/comunicados/" },
  { key: "comentarios", label: "Comentários", href: "/gestoreduka/comentarios/" },
  { key: "alunos", label: "Alunos", href: "/gestoreduka/alunos/" },
  { key: "perfil", label: "Perfil público", href: "/gestoreduka/perfil/" },
  { key: "galeria", label: "Galeria", href: "/gestoreduka/galeria/" },
  { key: "assinatura", label: "Assinatura", href: "/gestoreduka/assinatura/" },
];

const pageMeta = {
  cursos: { eyebrow: "Catálogo do centro", title: "Cursos presenciais", copy: "Crie, edite e publique as formações presenciais do seu centro." },
  "cursos-video": { eyebrow: "Formação digital", title: "Cursos em vídeo", copy: "Organize o catálogo em vídeo, as aulas e os certificados digitais." },
  inscricoes: { eyebrow: "Admissões", title: "Inscrições", copy: "Acompanhe pedidos, aprove matrículas e emita certificados presenciais." },
  turmas: { eyebrow: "Operação pedagógica", title: "Turmas e calendário", copy: "Abra turmas, organize horários e acompanhe presenças e notas." },
  formadores: { eyebrow: "Equipa pedagógica", title: "Formadores", copy: "Mantenha a equipa docente do centro organizada e actualizada." },
  filiais: { eyebrow: "Expansão do centro", title: "Filiais", copy: "Gira os locais de formação e os cursos associados a cada filial." },
  eventos: { eyebrow: "Agenda do centro", title: "Eventos", copy: "Publique eventos e mantenha a agenda institucional actualizada." },
  estagios: { eyebrow: "Empregabilidade", title: "Estágios", copy: "Divulgue vagas e oportunidades relevantes para os seus alunos." },
  financeiro: { eyebrow: "Acompanhamento financeiro", title: "Receitas e movimentos", copy: "Consulte pagamentos, comissão da plataforma e movimentos confirmados." },
  analytics: { eyebrow: "Desempenho do centro", title: "Analytics", copy: "Leia os indicadores que ajudam a orientar a actividade do centro." },
  mensagens: { eyebrow: "Atendimento", title: "Mensagens", copy: "Converse com alunos e acompanhe os pedidos activos." },
  comunicados: { eyebrow: "Comunicação", title: "Comunicados", copy: "Informe os seguidores do centro sobre novidades e actividades." },
  comentarios: { eyebrow: "Qualidade e comunidade", title: "Comentários", copy: "Responda a comentários e cuide da confiança no catálogo do centro." },
  alunos: { eyebrow: "Acompanhamento académico", title: "Alunos e dossiês", copy: "Pesquise alunos e acompanhe o histórico académico de cada inscrição." },
  perfil: { eyebrow: "Presença pública", title: "Perfil institucional", copy: "Actualize os dados que os alunos encontram na vitrina pública da Edukangola." },
  galeria: { eyebrow: "Presença pública", title: "Galeria do centro", copy: "Apresente instalações, actividades e ambientes de aprendizagem." },
  assinatura: { eyebrow: "Plano do centro", title: "Assinatura", copy: "Consulte o plano activo e as possibilidades de expansão do GestorEduka." },
};

const csrfToken = () => document.cookie.split(";").map((part) => part.trim()).find((part) => part.startsWith("csrftoken="))?.split("=").slice(1).join("=") || "";

function PageHeader({ page }) {
  const meta = pageMeta[page];
  return <header className="manager-page-heading"><span className="manager-eyebrow">{meta.eyebrow}</span><h1>{meta.title}</h1><p>{meta.copy}</p></header>;
}

function Overview({ data }) {
  const cards = [[BookOpen, "Cursos", data.metricas.cursos], [BarChart3, "Publicados", data.metricas.cursos_publicados], [UsersRound, "Inscrições", data.metricas.inscricoes], [Landmark, "Receita confirmada", `${money.format(data.metricas.receita_confirmada)} Kz`]];
  const shortcuts = [
    { href: "/gestoreduka/cursos/", icon: BookOpen, label: "Gerir cursos", copy: "Crie e publique formações." },
    { href: "/gestoreduka/inscricoes/", icon: GraduationCap, label: "Ver inscrições", copy: "Acompanhe admissões pendentes." },
    { href: "/gestoreduka/turmas/", icon: CalendarDays, label: "Organizar turmas", copy: "Prepare a operação pedagógica." },
    { href: "/gestoreduka/mensagens/", icon: MessageCircle, label: "Responder a alunos", copy: "Mantenha a comunicação activa." },
  ];
  return <><header className="manager-welcome"><span className="manager-eyebrow">{data.gestor.tipo}</span><h1>Bom trabalho, {data.gestor.nome.split(" ")[0]}.</h1><p>Acompanhe a actividade do seu centro e avance para a área certa sem perder o foco.</p></header><div className="manager-metrics">{cards.map(([Icon, label, value]) => <article key={label}><Icon size={19}/><small>{label}</small><strong>{value}</strong></article>)}</div><section className="manager-overview-section"><div className="manager-overview-heading"><div><span className="manager-eyebrow">Acesso rápido</span><h2>O que pretende fazer?</h2></div></div><div className="manager-shortcuts">{shortcuts.map(({ href, icon: Icon, label, copy }) => <a href={href} key={href}><span><Icon size={19}/></span><div><strong>{label}</strong><small>{copy}</small></div><ChevronRight size={17}/></a>)}</div></section><section className="manager-overview-section manager-recent-courses"><div className="manager-overview-heading"><div><span className="manager-eyebrow">Catálogo</span><h2>Cursos recentes</h2></div><a href="/gestoreduka/cursos/">Ver todos <ChevronRight size={15}/></a></div>{data.cursos.length ? <div className="manager-course-list">{data.cursos.slice(0, 5).map((course) => <article key={course.id}><div><strong>{course.titulo}</strong><span>{course.categoria}</span></div><span className={course.publicado ? "published" : "draft"}>{course.publicado ? "Publicado" : "Rascunho"}</span><a href="/gestoreduka/cursos/">Gerir <ChevronRight size={14}/></a></article>)}</div> : <p className="manager-empty-state">Ainda não há cursos criados. Abra a área de cursos para começar o catálogo do centro.</p>}</section></>;
}

function CoursesPage({ data, onRefresh }) {
  const [creating, setCreating] = useState(false);
  const [editingCourseId, setEditingCourseId] = useState(null);
  const [error, setError] = useState("");
  const changePublication = async (course) => { try { const response = await fetch(`/backend/gestoreduka/api/react/cursos/${course.id}/publicacao/`, { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() }, body: JSON.stringify({ publicado: !course.publicado }) }); if (!response.ok) throw new Error(); onRefresh(); } catch { setError("Não foi possível actualizar a publicação do curso."); } };
  const deleteCourse = async (course) => { if (!window.confirm(`Pretende remover definitivamente o curso “${course.titulo}”?`)) return; try { const response = await fetch(`/backend/gestoreduka/api/react/cursos/${course.id}/remover/`, { method: "POST", credentials: "same-origin", headers: { "X-CSRFToken": csrfToken() } }); if (!response.ok) throw new Error(); onRefresh(); } catch { setError("Não foi possível remover o curso."); } };
  return <><PageHeader page="cursos"/><section className="manager-courses manager-module-card"><button className="manager-create-course" onClick={() => setCreating(true)}>Criar curso</button>{error && <p className="manager-form-error">{error}</p>}<div className="manager-course-list">{data.cursos.length ? data.cursos.map((course) => <article key={course.id}><div><strong>{course.titulo}</strong><span>{course.categoria}</span></div><span className={course.publicado ? "published" : "draft"}>{course.publicado ? "Publicado" : "Rascunho"}</span><button onClick={() => changePublication(course)}>{course.publicado ? "Retirar" : "Publicar"}</button><button onClick={() => setEditingCourseId(course.id)} aria-label={`Editar ${course.titulo}`}><Pencil size={16}/></button><button className="manager-course-delete" onClick={() => deleteCourse(course)} aria-label={`Remover ${course.titulo}`}><Trash2 size={16}/></button></article>) : <p className="manager-empty-state">Ainda não existem cursos no centro. Crie a primeira formação para iniciar o catálogo.</p>}</div></section>{creating && <ManagerCourseForm onClose={() => setCreating(false)} onCreated={() => { setCreating(false); onRefresh(); }} />}{editingCourseId && <ManagerCourseForm courseId={editingCourseId} onClose={() => setEditingCourseId(null)} onUpdated={() => { setEditingCourseId(null); onRefresh(); }} />}</>;
}

function ModulePage({ page, data, onRefresh }) {
  if (page === "visao-geral") return <Overview data={data} />;
  if (page === "cursos") return <CoursesPage data={data} onRefresh={onRefresh} />;
  const body = {
    "cursos-video": <><ManagerVideoCoursesPanel/><ManagerVideoCertificatesPanel/></>,
    inscricoes: <ManagerEnrollmentsPanel/>,
    turmas: <ManagerClassesPanel/>,
    formadores: <ManagerInstructorsPanel embedded />,
    filiais: <ManagerBranchesPanel/>,
    eventos: <ManagerEventsPanel/>,
    estagios: <ManagerInternshipsPanel/>,
    financeiro: <ManagerFinancePanel/>,
    analytics: <ManagerAnalyticsPanel/>,
    mensagens: <ManagerChatPanel/>,
    comunicados: <ManagerAnnouncementsPanel/>,
    comentarios: <ManagerCommentsPanel/>,
    alunos: <ManagerStudentsPanel/>,
    perfil: <ManagerProfilePanel/>,
    galeria: <ManagerGalleryPanel/>,
    assinatura: <ManagerSubscriptionPanel/>,
  }[page];
  return <div className="manager-module-page">{body}</div>;
}

export default function ManagerPortalPage({ route = "/gestoreduka/" }) {
  const [theme, setTheme] = useState(() => localStorage.getItem("gestor-theme") || "light");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const segment = route.replace(/^\/gestoreduka\/?/, "").replace(/\/+$/, "");
  const activePage = navigation.some((item) => item.key === segment) ? segment : "visao-geral";
  useEffect(() => { document.documentElement.dataset.theme = theme; localStorage.setItem("gestor-theme", theme); }, [theme]);
  const load = () => fetch("/backend/gestoreduka/api/react/dashboard/", { credentials: "same-origin" }).then(async (response) => { const contentType = response.headers.get("content-type") || ""; if (response.redirected || !contentType.includes("application/json")) throw Object.assign(new Error("A sua sessão de gestor terminou."), { status: 401 }); const payload = await response.json().catch(() => ({})); if (!response.ok) throw Object.assign(new Error(payload.detail || "Não foi possível abrir o GestorEduka."), { status: response.status }); return payload; }).then(setData).catch((reason) => setError(reason));
  useEffect(() => { load(); }, [route]);
  if (error && error.status === 401) return <ManagerLoginPage theme={theme} onToggleTheme={() => setTheme(theme === "light" ? "dark" : "light")} onAuthenticated={() => { setError(""); setData(null); load(); }} />;
  if (error) return <main className="manager-auth"><h1>Não foi possível abrir a gestão.</h1><p>{error.message}</p><button onClick={() => { setError(""); load(); }}>Tentar novamente</button></main>;
  if (!data) return <main className="manager-auth"><span className="manager-mark">E</span><p>A preparar o GestorEduka…</p></main>;
  return <main className="manager-shell"><header><a className="manager-brand" href="/gestoreduka/">Edukangola <b>Gestor</b></a><div><span>{data.centro.nome}</span><button onClick={() => setTheme(theme === "light" ? "dark" : "light")} aria-label="Alternar tema">{theme === "light" ? <Moon size={18} /> : <Sun size={18} />}</button></div></header><aside><strong>Gestão do centro</strong>{navigation.map((item) => <a key={item.key} className={activePage === item.key ? "active" : ""} href={item.href}>{item.label}</a>)}</aside><section className="manager-content manager-module-content" aria-live="polite"><ModulePage page={activePage} data={data} onRefresh={load} /></section></main>;
}
