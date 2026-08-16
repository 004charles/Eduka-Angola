import { CalendarDays, CheckCircle2, ChevronRight, CircleDollarSign, Clock3, MapPin, ShieldCheck, UsersRound } from "lucide-react";
import "./home-decision-sections.css";

function EmptyState({ children }) {
  return <p className="decision-empty">{children}</p>;
}

function formatarMarca(nome) {
  return nome?.replace(/Eduka-Angola/gi, "Edukangola") ?? "";
}

export default function HomeDecisionSections({ data, loading, error, onAnnounce }) {
  const turmas = data?.turmas_abertas ?? [];
  const centros = data?.centros_destaque ?? [];

  return (
    <>
      <section className="page-width decision-section decision-section-first" id="turmas-abertas">
          <div className="section-heading">
          <div><span className="eyebrow muted"><CalendarDays size={14} /> Próximas oportunidades</span><h2>Turmas abertas que permitem decidir com clareza.</h2><p>Veja a data, o horário, as vagas e o pagamento configurados pelo centro antes de abrir o curso.</p></div>
          <span className="data-status">{loading ? "A atualizar" : "Dados do portal"}</span>
        </div>
        {error ? <EmptyState>Não foi possível carregar as turmas neste momento.</EmptyState> : turmas.length === 0 ? <EmptyState>Não existem turmas abertas neste momento.</EmptyState> : (
          <div className="open-class-grid">
            {turmas.slice(0, 3).map((turma) => (
              <article className="open-class-card" key={turma.turma_id}>
                <div className="open-class-head"><span className="date-chip">Início {turma.inicio_formatado}</span><span className="seat-chip">{turma.vagas_disponiveis} vagas</span></div>
                <span className="class-category">{turma.categoria}</span>
                <h3>{turma.titulo}</h3>
                <p className="class-centre"><MapPin size={15} /> {formatarMarca(turma.centro)} · {turma.provincia || turma.cidade}</p>
                <div className="class-details"><span><Clock3 size={14} /> {turma.dias}, {turma.horario}</span><span><UsersRound size={14} /> {turma.turno}{turma.sala ? ` · ${turma.sala}` : ""}</span></div>
                <div className="class-payment"><CircleDollarSign size={16} /><span><strong>{turma.pagamento.agora}</strong><small>{turma.pagamento.descricao}</small></span></div>
                <a className="decision-link" href={turma.inscricao_url}>Ver turma e inscrever-se <ChevronRight size={17} /></a>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="page-width decision-section" id="centros-destaque">
        <div className="section-heading"><div><span className="eyebrow muted"><ShieldCheck size={14} /> Centros no portal</span><h2>Escolha também quem vai acompanhar a sua formação.</h2><p>Compare os centros que já publicam cursos, modalidades e informação de localização no portal.</p></div></div>
        {loading ? <EmptyState>A carregar centros publicados.</EmptyState> : centros.length === 0 ? <EmptyState>Ainda não existem centros com cursos publicados para apresentar.</EmptyState> : (
          <div className="centre-discovery-grid">
            {centros.slice(0, 4).map((centro) => <a className="centre-discovery-card" href={centro.perfil_url} key={centro.id}><div className="centre-initial">{centro.nome.slice(0, 1)}</div><div className="centre-discovery-main"><div><h3>{formatarMarca(centro.nome)}</h3>{centro.verificado && <span className="verified-label"><CheckCircle2 size={13} /> Verificado</span>}</div><p>{[centro.cidade, centro.provincia].filter(Boolean).join(", ") || "Localização a confirmar"}</p><span>{centro.total_cursos} {centro.total_cursos === 1 ? "curso publicado" : "cursos publicados"} · {centro.modalidades.join(", ") || "Modalidade a confirmar"}</span></div><ChevronRight size={19} /></a>)}
          </div>
        )}
      </section>

      <section className="enrolment-clarity-section">
        <div className="page-width">
          <div className="section-heading center-heading"><span className="eyebrow muted">Inscrição sem surpresa</span><h2>Veja as condições antes de avançar.</h2><p>O fluxo acompanha a regra configurada pelo centro para cada curso.</p></div>
          <div className="clarity-steps">
            <div><b>01</b><h3>Escolha a turma</h3><p>Confirme data, horário, local e vagas disponíveis.</p></div>
            <div><b>02</b><h3>Envie os dados</h3><p>Preencha apenas os dados necessários para a inscrição.</p></div>
            <div><b>03</b><h3>Veja o pagamento</h3><p>Saiba se paga agora, qual o valor e o que ele inclui.</p></div>
            <div><b>04</b><h3>Acompanhe o processo</h3><p>Receba a confirmação conforme as condições definidas pelo centro.</p></div>
          </div>
          <button className="text-action process-action" onClick={() => onAnnounce("O detalhe de cada curso mostrará a turma e as condições reais antes da inscrição.")}>Entender o processo de inscrição <ChevronRight size={16} /></button>
        </div>
      </section>
    </>
  );
}
