import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, ArrowRight, BookOpen, CalendarDays, CircleAlert, GraduationCap, LibraryBig, PackageCheck, PlayCircle, ReceiptText } from "lucide-react";
import { backendUrl } from "../lib/backend-url";
import "./student-history-page.css";

const TYPE_META = {
  mercado: { label: "Mercado", icon: PackageCheck },
  inscricao: { label: "Inscrições", icon: GraduationCap },
  aprendizagem: { label: "Aprendizagem", icon: BookOpen },
};

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("pt-PT", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function StudentHistoryPage({ onNavigate }) {
  const [state, setState] = useState({ loading: true, error: "", data: null });
  const [filter, setFilter] = useState("todos");

  useEffect(() => {
    let active = true;
    fetch(backendUrl("/api/react/aluno/historico/"), { credentials: "same-origin" })
      .then(async (response) => ({ response, payload: await response.json().catch(() => ({})) }))
      .then(({ response, payload }) => {
        if (!active) return;
        if (response.status === 401) return setState({ loading: false, data: null, error: "login" });
        if (!response.ok || !payload.ok) throw new Error(payload.detail || "Não foi possível carregar o seu histórico.");
        setState({ loading: false, data: payload, error: "" });
      })
      .catch((error) => active && setState({ loading: false, data: null, error: error.message }));
    return () => { active = false; };
  }, []);

  const records = useMemo(() => (state.data?.registos || []).filter((record) => filter === "todos" || record.tipo === filter), [state.data, filter]);

  if (state.loading) return <main className="student-history-page"><div className="page-width student-history-loading">A preparar o seu histórico.</div></main>;
  if (state.error === "login") return <main className="student-history-page"><section className="page-width student-history-gate"><GraduationCap size={27} /><h1>Entre para ver o seu histórico.</h1><p>Os seus pedidos, inscrições e actividade de aprendizagem ficam guardados na sua conta.</p><button className="primary-action" onClick={() => onNavigate("/entrar?next=/aluno/historico")}>Entrar <ArrowRight size={17} /></button></section></main>;
  if (state.error) return <main className="student-history-page"><section className="page-width student-history-gate"><CircleAlert size={27} /><h1>Não foi possível abrir o histórico.</h1><p>{state.error}</p><button className="primary-action" onClick={() => window.location.reload()}>Tentar novamente</button></section></main>;

  const { aluno, resumo } = state.data;
  const statistics = [
    { label: "Pedidos do Mercado", value: resumo.pedidos_mercado, icon: ReceiptText, tone: "market" },
    { label: "Inscrições", value: resumo.inscricoes, icon: CalendarDays, tone: "enrollment" },
    { label: "Cursos em vídeo", value: resumo.cursos_em_video, icon: PlayCircle, tone: "learning" },
    { label: "Leituras guardadas", value: resumo.leituras, icon: LibraryBig, tone: "library" },
  ];

  return <main className="student-history-page">
    <section className="student-history-hero"><div className="page-width"><button className="student-history-back" onClick={() => onNavigate("/aluno")}><ArrowLeft size={16} /> Área do aluno</button><span className="eyebrow"><CalendarDays size={15} /> Histórico da conta</span><h1>O seu percurso, num só lugar.</h1><p>{aluno.nome.split(" ")[0]}, acompanhe pedidos, inscrições e os momentos mais recentes da sua aprendizagem.</p><div className="student-history-stats">{statistics.map(({ label, value, icon: Icon, tone }) => <article className={`student-history-stat ${tone}`} key={label}><span><Icon size={19} /></span><div><small>{label}</small><strong>{value}</strong></div></article>)}</div></div></section>

    <section className="page-width student-history-content"><div className="student-history-heading"><div><span className="eyebrow muted">Actividade registada</span><h2>Histórico recente.</h2><p>Selecione uma área para consultar os registos associados à sua conta.</p></div><div className="student-history-filters" aria-label="Filtrar histórico">{[["todos", "Tudo"], ["mercado", "Mercado"], ["inscricao", "Inscrições"], ["aprendizagem", "Aprendizagem"]].map(([key, label]) => <button key={key} type="button" className={filter === key ? "active" : ""} onClick={() => setFilter(key)}>{label}</button>)}</div></div>

      {records.length ? <div className="student-history-list">{records.map((record) => { const meta = TYPE_META[record.tipo] || TYPE_META.aprendizagem; const Icon = meta.icon; return <article className={`student-history-record ${record.tipo}`} key={record.id}><div className="student-history-icon"><Icon size={19} /></div><div className="student-history-record-main"><div className="student-history-record-top"><span>{meta.label}</span><time dateTime={record.ocorrido_em}>{formatDate(record.ocorrido_em)}</time></div><h3>{record.titulo}</h3><p>{record.descricao}</p></div><div className="student-history-record-state"><strong>{record.estado}</strong>{record.valor && <small>{record.valor}</small>}</div>{record.detalhe_url && <button className="student-history-open" onClick={() => onNavigate(record.detalhe_url)} aria-label={`Abrir ${record.titulo}`}><ArrowRight size={17} /></button>}</article>; })}</div> : <div className="student-history-empty"><BookOpen size={27} /><h3>Ainda não existem registos nesta área.</h3><p>Quando houver actividade associada à sua conta, ela aparecerá aqui.</p>{filter !== "todos" && <button className="text-action" onClick={() => setFilter("todos")}>Ver todo o histórico</button>}</div>}
    </section>
  </main>;
}
