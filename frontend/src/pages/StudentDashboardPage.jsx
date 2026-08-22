import { useEffect, useState } from "react";
import { ArrowRight, BadgeCheck, BookOpen, CalendarDays, CircleAlert, Clock3, GraduationCap, History, PlayCircle, Settings2, SlidersHorizontal, Ticket, WalletCards } from "lucide-react";
import { backendUrl } from "../lib/backend-url";
import "./student-dashboard-page.css";

function Stat({ icon: Icon, label, value, tone }) {
  return <article className={`student-stat ${tone}`}><span><Icon size={20} /></span><div><small>{label}</small><strong>{value}</strong></div></article>;
}

function statusClass(status) {
  return status === "A" ? "active" : status === "P" ? "pending" : status === "N" ? "denied" : "cancelled";
}

function SectionHeading({ eyebrow, title, copy, children }) {
  return <div className="student-section-heading"><div><span className="eyebrow muted">{eyebrow}</span><h2>{title}</h2><p>{copy}</p></div>{children && <div className="student-section-actions">{children}</div>}</div>;
}

export default function StudentDashboardPage({ onNavigate }) {
  const [state, setState] = useState({ loading: true, error: "", data: null, favoritos: [], livros: [] });

  useEffect(() => {
    let active = true;
    Promise.all([
      fetch(backendUrl("/api/react/aluno/dashboard/"), { credentials: "same-origin" }),
      fetch(backendUrl("/auth/api/react/aluno/favoritos/"), { credentials: "same-origin" }),
      fetch(backendUrl("/api/react/biblioteca/minha/"), { credentials: "same-origin" }),
    ])
      .then(async ([dashboardResponse, favoritesResponse, libraryResponse]) => ({ dashboardResponse, dashboard: await dashboardResponse.json().catch(() => ({})), favoritesResponse, favorites: await favoritesResponse.json().catch(() => ({})), libraryResponse, library: await libraryResponse.json().catch(() => ({}) ) }))
      .then(({ dashboardResponse, dashboard, favoritesResponse, favorites, libraryResponse, library }) => {
        if (!active) return;
        if (dashboardResponse.status === 401) return setState({ loading: false, data: null, favoritos: [], livros: [], error: "login" });
        if (!dashboardResponse.ok || !dashboard.ok) throw new Error(dashboard.message || "Não foi possível carregar a sua área.");
        setState({ loading: false, data: dashboard, favoritos: favoritesResponse.ok ? favorites.cursos || [] : [], livros: libraryResponse.ok ? library.livros || [] : [], error: "" });
      })
      .catch((error) => active && setState({ loading: false, data: null, favoritos: [], livros: [], error: error.message }));
    return () => { active = false; };
  }, []);

  if (state.loading) return <main className="student-page"><div className="page-width student-loading">A preparar a sua área de aprendizagem.</div></main>;
  if (state.error === "login") return <main className="student-page"><section className="page-width student-gate"><span className="eyebrow"><GraduationCap size={15} /> Área do aluno</span><h1>Entre para acompanhar o seu percurso.</h1><p>Os seus cursos, inscrições e subscrição ficam reunidos aqui.</p><button className="primary-action" onClick={() => onNavigate("/entrar?next=/aluno")}>Entrar <ArrowRight size={17} /></button></section></main>;
  if (state.error) return <main className="student-page"><section className="page-width student-gate"><CircleAlert size={26} /><h1>Não foi possível abrir a sua área.</h1><p>{state.error}</p><button className="primary-action" onClick={() => window.location.reload()}>Tentar novamente</button></section></main>;

  const { aluno, resumo, subscricao_video: subscricaoVideo, continuar_aprender: cursos = [], inscricoes = [] } = state.data;
  const favoritos = state.favoritos || [];
  const livros = state.livros || [];
  const subscriptionEnds = subscricaoVideo?.termina_em ? new Date(subscricaoVideo.termina_em).toLocaleDateString("pt-PT") : "";

  return <main className="student-page">
    <section className="student-hero"><div className="page-width"><span className="eyebrow"><GraduationCap size={15} /> Área do aluno</span><h1>Olá, {aluno.nome.split(" ")[0]}.</h1><p>Acompanhe as suas formações, inscrições e próximos passos num só lugar.</p><div className="student-stats"><Stat icon={BookOpen} label="Cursos activos" value={resumo.cursos_ativos} tone="purple" /><Stat icon={Clock3} label="Inscrições pendentes" value={resumo.inscricoes_pendentes} tone="amber" /><Stat icon={BadgeCheck} label="Certificados emitidos" value={resumo.certificados} tone="green" /></div></div></section>

    <section className="page-width student-section">
      <div className="student-empty compact"><PlayCircle size={23} /><h3>{subscricaoVideo?.ativa ? `Subscrição de vídeo activa: ${subscricaoVideo.plano}.` : "Ainda não tem uma subscrição de vídeo activa."}</h3><p>{subscricaoVideo?.ativa ? `Todo o catálogo de cursos em vídeo está disponível até ${subscriptionEnds}.` : "Active um plano mensal para aceder a todos os cursos em vídeo da Edukangola."}</p><button className="primary-action" onClick={() => onNavigate("/cursos-em-video")}>{subscricaoVideo?.ativa ? "Abrir cursos em vídeo" : "Ver planos de vídeo"} <ArrowRight size={16} /></button></div>
      <SectionHeading eyebrow="A sua aprendizagem" title="Continue de onde parou." copy="Mostramos os cursos que já começou e as inscrições associadas à sua conta."><button className="text-action" onClick={() => onNavigate("/aluno/historico")}><History size={16} /> Histórico</button><button className="text-action" onClick={() => onNavigate("/aluno/configuracoes")}><Settings2 size={16} /> Configurações</button><button className="text-action" onClick={() => onNavigate("/aluno/preferencias")}><SlidersHorizontal size={16} /> Preferências</button><button className="text-action" onClick={() => onNavigate("/aluno/bilhetes")}><Ticket size={16} /> Bilhetes</button><button className="text-action" onClick={() => onNavigate("/aluno/certificados")}><BadgeCheck size={16} /> Certificados</button></SectionHeading>
      {cursos.length ? <div className="student-course-grid">{cursos.map((curso) => <article className="student-course" key={curso.id}><div className="student-course-image">{curso.imagem_url && <img src={curso.imagem_url} alt="" />}{curso.is_video ? <span><PlayCircle size={15} /> Curso em vídeo</span> : <span><CalendarDays size={15} /> Presencial</span>}</div><div className="student-course-body"><p>{curso.centro}</p><h3>{curso.titulo}</h3>{curso.is_video ? <><div className="student-progress"><span><i style={{ width: `${curso.progresso}%` }} /></span><small>{curso.progresso}% concluído · {curso.aulas_concluidas}/{curso.total_aulas} aulas</small></div><button onClick={() => onNavigate(curso.aprendizagem_url)}>Continuar a aprender <ArrowRight size={15} /></button></> : <><small className="student-course-status">Inscrição confirmada</small><button onClick={() => onNavigate(curso.detalhe_url)}>Ver curso <ArrowRight size={15} /></button></>}</div></article>)}</div> : <div className="student-empty"><BookOpen size={25} /><h3>Ainda não começou um curso.</h3><p>Explore cursos em vídeo ou formações presenciais para começar o seu percurso.</p><button className="primary-action" onClick={() => onNavigate("/cursos-em-video")}>Explorar cursos em vídeo <ArrowRight size={16} /></button></div>}
    </section>

    <section className="page-width student-section student-saved-courses"><SectionHeading eyebrow="Cursos guardados" title="Volte a analisar quando estiver pronto." copy="Guarde formações para as comparar mais tarde." /><div className="student-course-grid">{favoritos.map((curso) => <article className="student-course" key={curso.id}><div className="student-course-image">{curso.imagem_url && <img src={curso.imagem_url} alt="" />}<span>{curso.modalidade}</span></div><div className="student-course-body"><p>{curso.centro}</p><h3>{curso.titulo}</h3><small className="student-course-status">{curso.preco_label}</small><button onClick={() => onNavigate(curso.detalhe_url)}>Ver curso <ArrowRight size={15} /></button></div></article>)}</div>{!favoritos.length && <div className="student-empty compact"><BookOpen size={23} /><h3>Ainda não guardou cursos.</h3><p>Use o coração nos cartões para criar a sua lista pessoal.</p></div>}</section>

    <section className="page-width student-section student-reading-library"><SectionHeading eyebrow="Biblioteca Edukangola" title="As suas leituras." copy="Retome os livros guardados e continue de onde parou." /><div className="student-reading-shelf">{livros.map((livro) => <article className="student-reading-book" key={livro.slug}><button type="button" onClick={() => onNavigate(`/ler/${livro.slug}`)}><img src={livro.capa_url} alt="" /><span className="student-reading-spine" /></button><div><p>{livro.autor?.nome}</p><h3>{livro.titulo}</h3><small>{livro.biblioteca_pessoal?.progresso_leitura || 0}% lido</small></div></article>)}</div>{!livros.length && <div className="student-empty compact"><BookOpen size={23} /><h3>Ainda não guardou livros.</h3><p>Na Biblioteca pode encontrar obras para estudar ao seu ritmo.</p></div>}</section>

    <section className="page-width student-section student-enrollments"><SectionHeading eyebrow="Inscrições presenciais" title="Acompanhe cada inscrição." copy="Veja o estado da aprovação e os dados da turma escolhida." />{inscricoes.length ? <div className="student-enrollment-list">{inscricoes.map((inscricao) => <article key={inscricao.id} className="student-enrollment"><div className="student-enrollment-main"><img src={inscricao.imagem_url} alt="" /><div><span className={`student-status ${statusClass(inscricao.status)}`}>{inscricao.status_label}</span><h3>{inscricao.titulo}</h3><p>{inscricao.centro}{inscricao.turma ? ` · ${inscricao.turma}` : ""}</p></div></div><div className="student-enrollment-payment"><small>Pagamento registado</small><strong>{inscricao.valor_pago_formatado}</strong></div><div className="student-enrollment-actions"><button onClick={() => onNavigate(inscricao.detalhe_url)}>Ver curso</button>{inscricao.ficha_url && <a href={backendUrl(inscricao.ficha_url)}><WalletCards size={15} /> Ficha</a>}</div></article>)}</div> : <div className="student-empty compact"><CalendarDays size={23} /><h3>Nenhuma inscrição presencial encontrada.</h3><p>Quando se inscrever numa turma, o estado aparecerá aqui.</p></div>}</section>
  </main>;
}
