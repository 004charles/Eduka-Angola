import {
  ArrowLeft,
  ArrowRight,
  BadgeCheck,
  CalendarDays,
  CheckCircle2,
  Clock3,
  MapPin,
  Scale,
  UsersRound,
  X,
} from "lucide-react";
import "./course-comparison-page.css";

function labelValue(value, fallback = "A confirmar") {
  return value === 0 || value ? value : fallback;
}

function nextClass(course, classes) {
  return (classes || [])
    .filter((item) => item.id === course.id)
    .sort((a, b) => String(a.inicio).localeCompare(String(b.inicio)))[0] || null;
}

function MetricRow({ icon: Icon, label, hint, records, children }) {
  return (
    <div className="comparison-metric-row">
      <div className="comparison-metric-label">
        <Icon size={17} />
        <div>
          <b>{label}</b>
          {hint && <small>{hint}</small>}
        </div>
      </div>
      {records.map((record) => (
        <div className="comparison-metric-value" key={record.course.id}>
          {children(record)}
        </div>
      ))}
    </div>
  );
}

export default function CourseComparisonPage({ courses = [], classes = [], ids = [], onNavigate }) {
  const selected = courses.filter((course) => ids.includes(String(course.id))).slice(0, 3);
  const records = selected.map((course) => ({ course, turma: nextClass(course, classes) }));
  const remove = (id) => {
    const next = ids.filter((current) => current !== String(id));
    onNavigate(next.length ? `/comparar-cursos?ids=${next.join(",")}` : "/cursos");
  };

  if (selected.length < 2) {
    return <main className="comparison-empty page-width"><Scale size={32} /><span className="eyebrow muted">Comparação de cursos</span><h1>Escolha dois ou três cursos para comparar.</h1><p>Veja preço, duração, próxima turma, vagas, modalidade e centro na mesma leitura antes de iniciar a candidatura.</p><button className="primary-action" type="button" onClick={() => onNavigate("/cursos")}><ArrowLeft size={16} /> Voltar ao catálogo</button></main>;
  }

  return (
    <main className="course-comparison-page">
      <section className="comparison-intro">
        <div className="page-width">
          <button className="comparison-back" type="button" onClick={() => onNavigate("/cursos")}><ArrowLeft size={16} /> Voltar ao catálogo</button>
          <div className="comparison-intro-copy">
            <span className="eyebrow muted"><Scale size={15} /> Escolha com clareza</span>
            <h1>Coloque as formações lado a lado.</h1>
            <p>Compare apenas o que importa antes de se candidatar: o centro, o investimento, a próxima turma e as condições de participação.</p>
          </div>
          <p className="comparison-intro-note"><CheckCircle2 size={17} /> Dados publicados pelos próprios centros e actualizados no catálogo Edukangola.</p>
        </div>
      </section>
      <section className="page-width comparison-sheet-wrap">
        <div className="comparison-sheet-scroll">
          <div className={`comparison-sheet comparison-columns-${records.length}`}>
            <div className="comparison-sheet-corner"><span>O que comparar</span><b>{records.length} formações seleccionadas</b></div>
            {records.map(({ course }) => (
              <article key={course.id} className="comparison-course-head">
                <button className="comparison-remove" type="button" onClick={() => remove(course.id)} aria-label={`Remover ${course.titulo} da comparação`}><X size={15} /></button>
                <div className="comparison-course-thumb">{course.imagem_url ? <img src={course.imagem_url} alt="" /> : <span>{course.categoria?.slice(0, 1) || "C"}</span>}</div>
                <div><span>{course.categoria}</span><h2>{course.titulo}</h2><p>{course.centro || "Centro de formação"}</p></div>
              </article>
            ))}
            <MetricRow icon={Clock3} label="Formato e duração" hint="Como e quanto tempo" records={records}>
              {({ course }) => <><b>{labelValue(course.modalidade)}</b><small>{course.carga_horaria ? `${course.carga_horaria} horas` : "Carga horária a confirmar"} · {labelValue(course.nivel_label)}</small></>}
            </MetricRow>
            <MetricRow icon={Scale} label="Investimento inicial" hint="O valor apresentado agora" records={records}>
              {({ course }) => <><strong className={course.is_gratuito ? "is-free" : ""}>{course.is_gratuito ? "Gratuito" : labelValue(course.pagamento?.agora)}</strong><small>{course.pagamento?.descricao || "Condições a confirmar"}</small></>}
            </MetricRow>
            <MetricRow icon={CalendarDays} label="Próxima turma" hint="Data e horário disponíveis" records={records}>
              {({ turma }) => turma ? <><b>{turma.inicio_formatado}</b><small>{turma.dias || "Dias a confirmar"} · {turma.horario || "Horário a confirmar"}</small></> : <b className="is-muted">Ainda sem turma aberta</b>}
            </MetricRow>
            <MetricRow icon={UsersRound} label="Vagas" hint="Disponibilidade actual" records={records}>
              {({ turma }) => turma ? <b>{turma.vagas_disponiveis} {turma.vagas_disponiveis === 1 ? "vaga disponível" : "vagas disponíveis"}</b> : <b className="is-muted">—</b>}
            </MetricRow>
            <MetricRow icon={MapPin} label="Local" hint="Onde decorre a formação" records={records}>
              {({ course, turma }) => <b>{turma?.local || [course.cidade, course.provincia].filter(Boolean).join(", ") || "A confirmar"}</b>}
            </MetricRow>
            <MetricRow icon={BadgeCheck} label="Confiança" hint="Sinal de transparência" records={records}>
              {({ course }) => course.centro_verificado ? <b className="is-verified"><BadgeCheck size={15} /> Centro verificado</b> : <b className="is-muted">Perfil publicado no catálogo</b>}
            </MetricRow>
            <div className="comparison-actions-label"><b>Próximo passo</b><small>Confirme os detalhes antes da candidatura.</small></div>
            {records.map(({ course, turma }) => (
              <div className="comparison-course-actions" key={course.id}>
                <button type="button" className="comparison-detail" onClick={() => onNavigate(`/cursos/${course.id}`)}>Ver curso <ArrowRight size={15} /></button>
                <button type="button" className="primary-action" onClick={() => onNavigate(`/inscrever/${course.id}${turma?.turma_id ? `?turma=${turma.turma_id}` : ""}`)}>Candidatar-me</button>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
