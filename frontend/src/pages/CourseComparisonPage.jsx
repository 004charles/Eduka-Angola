import { ArrowLeft, ArrowRight, BadgeCheck, CalendarDays, CheckCircle2, Clock3, MapPin, Scale, UsersRound, X } from "lucide-react";
import "./course-comparison-page.css";

function labelValue(value, fallback = "A confirmar") {
  return value === 0 || value ? value : fallback;
}

function nextClass(course, classes) {
  return (classes || []).filter((item) => item.id === course.id).sort((a, b) => String(a.inicio).localeCompare(String(b.inicio)))[0] || null;
}

function ComparisonCell({ label, children }) {
  return <div className="course-comparison-cell"><span>{label}</span>{children}</div>;
}

export default function CourseComparisonPage({ courses = [], classes = [], ids = [], onNavigate }) {
  const selected = courses.filter((course) => ids.includes(String(course.id))).slice(0, 3);
  const remove = (id) => {
    const next = ids.filter((current) => current !== String(id));
    onNavigate(next.length ? `/comparar-cursos?ids=${next.join(",")}` : "/cursos");
  };

  if (selected.length < 2) return <main className="comparison-empty page-width"><Scale size={32} /><span className="eyebrow muted">Comparação de cursos</span><h1>Escolha dois ou três cursos para comparar.</h1><p>Veja preço, duração, próxima turma, vagas, modalidade e centro na mesma leitura antes de iniciar a candidatura.</p><button className="primary-action" type="button" onClick={() => onNavigate("/cursos")}><ArrowLeft size={16} /> Voltar ao catálogo</button></main>;

  return <main className="course-comparison-page"><section className="comparison-hero"><div className="page-width"><button className="comparison-back" type="button" onClick={() => onNavigate("/cursos")}><ArrowLeft size={16} /> Catálogo</button><span className="eyebrow"><Scale size={15} /> Decisão informada</span><h1>Compare antes de se candidatar.</h1><p>As condições são publicadas pelos centros. Confirme a turma seleccionada antes de avançar para a inscrição.</p></div></section><section className="page-width comparison-table-wrap"><div className="comparison-table">{selected.map((course) => { const turma = nextClass(course, classes); return <article className="comparison-course" key={course.id}><button className="comparison-remove" type="button" onClick={() => remove(course.id)} aria-label={`Remover ${course.titulo} da comparação`}><X size={16} /></button>{course.imagem_url ? <img src={course.imagem_url} alt="" /> : <div className="comparison-image-fallback">{course.categoria?.slice(0, 1) || "C"}</div>}<span>{course.categoria}</span><h2>{course.titulo}</h2><p>{course.centro || "Centro de formação"}</p><ComparisonCell label="Modalidade"><b>{labelValue(course.modalidade)}</b></ComparisonCell><ComparisonCell label="Nível"><b>{labelValue(course.nivel_label)}</b></ComparisonCell><ComparisonCell label="Duração"><b><Clock3 size={15} /> {course.carga_horaria ? `${course.carga_horaria} horas` : "A confirmar"}</b></ComparisonCell><ComparisonCell label="Preço inicial"><strong className={course.is_gratuito ? "is-free" : ""}>{course.is_gratuito ? "Gratuito" : labelValue(course.pagamento?.agora)}</strong><small>{course.pagamento?.descricao || "Condições a confirmar"}</small></ComparisonCell><ComparisonCell label="Próxima turma">{turma ? <><b><CalendarDays size={15} /> {turma.inicio_formatado}</b><small>{turma.dias || "Dias a confirmar"} · {turma.horario || "Horário a confirmar"}</small></> : <b>Sem turma aberta</b>}</ComparisonCell><ComparisonCell label="Vagas">{turma ? <b><UsersRound size={15} /> {turma.vagas_disponiveis} {turma.vagas_disponiveis === 1 ? "vaga" : "vagas"}</b> : <b>—</b>}</ComparisonCell><ComparisonCell label="Local">{turma?.local || [course.cidade, course.provincia].filter(Boolean).join(", ") ? <b><MapPin size={15} /> {turma?.local || [course.cidade, course.provincia].filter(Boolean).join(", ")}</b> : <b>A confirmar</b>}</ComparisonCell><ComparisonCell label="Confiança"><b><BadgeCheck size={15} /> Centro verificado quando indicado no perfil</b></ComparisonCell><div className="comparison-actions"><button type="button" className="comparison-detail" onClick={() => onNavigate(`/cursos/${course.id}`)}>Ver detalhes <ArrowRight size={15} /></button><button type="button" className="primary-action" onClick={() => onNavigate(`/inscrever/${course.id}${turma?.turma_id ? `?turma=${turma.turma_id}` : ""}`)}><CheckCircle2 size={16} /> Candidatar-me</button></div></article>})}</div></section></main>;
}
