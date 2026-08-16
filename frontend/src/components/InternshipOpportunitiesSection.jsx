import { ArrowRight, BriefcaseBusiness, CalendarDays, Clock3, MapPin, UsersRound } from "lucide-react";
import "./internship-opportunities-section.css";

function remuneracao(estagio) {
  if (estagio.valor_remuneracao) return `${estagio.valor_remuneracao.toLocaleString("pt-PT")} Kz`;
  return estagio.tipo_remuneracao || "Condições a confirmar";
}

function localizacao(estagio) {
  return [estagio.cidade, estagio.provincia].filter(Boolean).join(", ") || estagio.local_trabalho || "Local a confirmar";
}

export default function InternshipOpportunitiesSection({ data, onNavigate }) {
  const estagios = data?.estagios || [];

  return (
    <section className={`internship-section page-width${estagios.length ? "" : " internship-section-empty"}`} aria-labelledby="internship-title">
      <div className="internship-heading">
        <div>
          <span className="eyebrow muted"><BriefcaseBusiness size={14} /> Oportunidades práticas</span>
          <h2 id="internship-title">Estágios para dar o próximo passo.</h2>
          <p>Encontre oportunidades publicadas pelos centros e transforme a sua formação em experiência profissional.</p>
        </div>
        <button className="text-action" type="button" onClick={() => onNavigate("/centros")}>Explorar centros <ArrowRight size={16} /></button>
      </div>

      {estagios.length ? <div className="internship-grid">
        {estagios.map((estagio) => (
          <article className="internship-card" key={estagio.id}>
            <div className="internship-card-image">
              {estagio.imagem_url ? <img src={estagio.imagem_url} alt="" loading="lazy" decoding="async" /> : <div className="internship-image-fallback"><BriefcaseBusiness size={30} /></div>}
              <span className="internship-mode-badge">{estagio.modalidade}</span>
            </div>
            <div className="internship-card-content">
              <small className="internship-area">{estagio.area}</small>
              <h3 title={estagio.titulo}>{estagio.titulo}</h3>
              <p className="internship-centre" title={estagio.centro}>{estagio.centro}</p>
              <div className="internship-price"><strong>{remuneracao(estagio)}</strong><span>{estagio.valor_remuneracao ? estagio.tipo_remuneracao : "Tipo de oportunidade"}</span></div>
              <div className="internship-facts">
                <span><MapPin size={14} /> {localizacao(estagio)}</span>
                <span><CalendarDays size={14} /> Início {estagio.data_inicio_formatada}</span>
                <span><UsersRound size={14} /> {estagio.vagas_restantes} {estagio.vagas_restantes === 1 ? "vaga" : "vagas"} · candidatura até {estagio.data_limite_formatada}</span>
                <span><Clock3 size={14} /> {estagio.duracao_meses} meses · {estagio.carga_horaria_semanal}h/semana</span>
              </div>
              <div className="internship-card-footer"><button type="button" onClick={() => onNavigate(estagio.detalhe_url)}>Conhecer centro <ArrowRight size={15} /></button></div>
            </div>
          </article>
        ))}
      </div> : <div className="internship-empty-state"><BriefcaseBusiness size={28} /><h3>Novas oportunidades em breve.</h3><p>Os centros poderão publicar estágios nesta área assim que abrirem candidaturas.</p><button className="text-action" type="button" onClick={() => onNavigate("/centros")}>Conhecer centros <ArrowRight size={16} /></button></div>}
    </section>
  );
}
