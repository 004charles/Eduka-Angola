import { useEffect, useState } from "react";
import {
  ArrowLeft, ArrowRight, BadgeCheck, Bell, BookOpen, BriefcaseBusiness,
  Building2, CalendarDays, Check, ChevronRight, CirclePlay, Clock3,
  ExternalLink, Globe2, GraduationCap, Heart, ImageIcon, Landmark, Mail,
  MapPin, MessageCircle, Phone, Play, Share2, ShieldCheck, Sparkles,
  Star, Trophy, UsersRound, Wrench,
} from "lucide-react";
import { authRequest } from "../lib/auth-api";
import { backendUrl } from "../lib/backend-url";
import "./center-profile-page.css";
import "./center-profile-messages.css";

function textoLimpo(valor) { return String(valor || "").trim(); }
function mapsSearchUrl(center) { const query = [center.endereco, center.cidade, center.provincia, center.pais_nome].filter(Boolean).join(", "); return query ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}` : ""; }

function CenterInitial({ name }) {
  return <span className="center-profile-initial" aria-hidden="true">{textoLimpo(name).slice(0, 1).toUpperCase() || "C"}</span>;
}

function SectionHeading({ eyebrow, title, children, icon: Icon }) {
  return <div className="center-profile-section-heading"><div><span className="center-section-eyebrow">{eyebrow}</span><h2>{title}</h2>{children}</div>{Icon && <Icon size={20} />}</div>;
}

function CourseTile({ course, onNavigate }) {
  return <article className="center-course-tile"><div className="center-course-image">{course.imagem_url ? <img src={course.imagem_url} alt="" /> : <div className="center-course-image-fallback"><BookOpen size={28} /></div>}<span>{course.categoria}</span></div><div className="center-course-copy"><p className="center-course-level">{course.nivel || "Formação profissional"}</p><h3>{course.titulo}</h3>{course.descricao_curta && <p className="center-course-description">{course.descricao_curta}</p>}<div className="center-course-details"><span>{course.carga_horaria && <><Clock3 size={14} /> {course.carga_horaria}</>}</span><strong>{course.pagamento?.agora}</strong></div><button type="button" onClick={() => onNavigate(`/cursos/${course.id}`)}>Ver formação <ArrowRight size={15} /></button></div></article>;
}

function VideoCourseTile({ course, onNavigate }) {
  return <article className="center-media-course"><div>{course.imagem_url ? <img src={course.imagem_url} alt="" /> : <CirclePlay size={27} />}<span><Play size={12} /> {course.total_aulas} {course.total_aulas === 1 ? "aula" : "aulas"}</span></div><section><p>{course.categoria}</p><h3>{course.titulo}</h3><small>{course.preco}</small><button type="button" onClick={() => onNavigate(`/video-cursos/${course.slug}`)}>Ver curso em vídeo <ArrowRight size={14} /></button></section></article>;
}

function ImageOrInitial({ src, label, className = "" }) {
  return src ? <img className={className} src={src} alt="" /> : <span className={className}>{textoLimpo(label).slice(0, 1).toUpperCase()}</span>;
}

export default function CenterProfilePage({ centerId, onNavigate }) {
  const [center, setCenter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [followPending, setFollowPending] = useState(false);
  const [actionMessage, setActionMessage] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true); setError("");
    fetch(backendUrl(`/api/public/centros/${centerId}/`), { credentials: "same-origin", cache: "no-store" })
      .then(async (response) => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.detail || "Não foi possível carregar este centro.");
        return data;
      })
      .then((data) => active && setCenter(data))
      .catch((requestError) => active && setError(requestError.message || "Não foi possível carregar este centro."))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [centerId]);

  async function toggleFollow() {
    if (!center) return;
    if (!center.seguimento?.autenticado) {
      onNavigate(`/entrar?next=/centros/${center.id}`);
      return;
    }
    setFollowPending(true); setActionMessage("");
    try {
      const result = await authRequest(`/api/v1/centros/${center.id}/seguir/`);
      setCenter((current) => ({
        ...current,
        seguimento: {
          ...current.seguimento,
          seguindo: result.seguindo,
          total_seguidores: Math.max(0, current.seguimento.total_seguidores + (result.seguindo ? 1 : -1)),
        },
      }));
      setActionMessage(result.mensagem || (result.seguindo ? "Centro seguido." : "Seguimento removido."));
    } catch (requestError) {
      if (requestError.status === 401 || requestError.status === 403) {
        onNavigate(`/entrar?next=/centros/${center.id}`);
        return;
      }
      setActionMessage(requestError.message || "Não foi possível atualizar o seguimento.");
    } finally { setFollowPending(false); }
  }

  async function shareProfile() {
    const url = window.location.href;
    try {
      if (navigator.share) await navigator.share({ title: center.nome, url });
      else { await navigator.clipboard.writeText(url); setActionMessage("Link copiado para a área de transferência."); }
    } catch { /* a partilha pode ser cancelada pelo utilizador */ }
  }

  function contactCenter() {
    if (!center.seguimento?.autenticado) {
      onNavigate(`/entrar?next=/centros/${center.id}`);
      return;
    }
    onNavigate(`/aluno/mensagens?centro=${center.id}`);
  }

  if (loading) return <main className="center-profile-state page-width"><div className="center-profile-loading"><span /><span /><span /></div><p>A preparar o perfil do centro.</p></main>;
  if (error || !center) return <main className="center-profile-state page-width"><ShieldCheck size={28} /><h1>Centro indisponível</h1><p>{error || "Não encontrámos este perfil de centro."}</p><button type="button" className="center-back-button" onClick={() => onNavigate("/centros")}><ArrowLeft size={16} /> Voltar aos centros</button></main>;

  const hasContact = center.telefone || center.email || center.site || center.whatsapp;
  const socialEntries = Object.entries(center.sociais || {});
  const details = [center.modalidade && { label: "Modalidade", value: center.modalidade }, center.tipo && { label: "Tipo de centro", value: center.tipo }, center.ano_fundacao && { label: "Fundado em", value: center.ano_fundacao }].filter(Boolean);
  const following = Boolean(center.seguimento?.seguindo);
  const centerMapsUrl = mapsSearchUrl(center);

  return <main className="center-profile-page">
    <section className="center-profile-hero">
      <div className="center-profile-cover">{center.banner_url ? <img src={center.banner_url} alt="" /> : <div className="center-profile-cover-fallback"><span>{center.nome}</span></div>}<div className="center-profile-cover-shade" /></div>
      <div className="page-width center-profile-hero-content"><button type="button" className="center-profile-back" onClick={() => onNavigate("/centros")}><ArrowLeft size={16} /> Centros</button><div className="center-profile-identity"><div className="center-profile-logo">{center.logo_url ? <img src={center.logo_url} alt={`Logótipo de ${center.nome}`} /> : <CenterInitial name={center.nome} />}</div><div className="center-profile-title"><div className="center-profile-kicker"><span>Centro de formação</span>{center.verificado && <span className="center-profile-verified"><BadgeCheck size={15} /> Verificado</span>}</div><h1>{center.nome}</h1><div className="center-profile-location">{center.localizacao && <span><MapPin size={15} /> {center.localizacao}</span>}{center.total_cursos > 0 && <span><BookOpen size={15} /> {center.total_cursos} {center.total_cursos === 1 ? "formação publicada" : "formações publicadas"}</span>}{center.seguimento?.total_seguidores > 0 && <span><UsersRound size={15} /> {center.seguimento.total_seguidores} {center.seguimento.total_seguidores === 1 ? "seguidor" : "seguidores"}</span>}</div></div></div></div>
    </section>

    <section className="center-profile-actions-wrap"><div className="page-width center-profile-actions"><div className="center-profile-tags">{center.categorias?.slice(0, 4).map((category) => <span key={category}>{category}</span>)}</div><div className="center-profile-action-links"><button type="button" className={`center-follow-button ${following ? "is-following" : ""}`} onClick={toggleFollow} disabled={followPending}>{following ? <Check size={15} /> : <Heart size={15} fill="currentColor" />} {followPending ? "A atualizar" : following ? "A seguir" : "Seguir centro"}</button><button type="button" className="center-message-button" onClick={contactCenter}><MessageCircle size={15} /> Enviar mensagem</button><a href="#formacoes">Explorar formações <ChevronRight size={15} /></a>{center.whatsapp && <a href={`https://wa.me/${center.whatsapp.replace(/\D/g, "")}`} target="_blank" rel="noreferrer"><MessageCircle size={15} /> WhatsApp</a>}{center.site && <a href={center.site} target="_blank" rel="noreferrer"><Globe2 size={15} /> Website</a>}<button type="button" className="center-share-button" onClick={shareProfile} aria-label="Partilhar perfil"><Share2 size={16} /></button></div></div>{actionMessage && <p className="page-width center-profile-action-message" role="status">{actionMessage}</p>}</section>

    <section className="page-width center-profile-layout">
      <div className="center-profile-main">
        {center.video_apresentacao_url && <section className="center-profile-section center-presentation-video"><div><span className="center-section-eyebrow">Apresentação</span><h2>Conheça o centro</h2><p>{center.descricao || "Veja a apresentação publicada pelo centro."}</p></div><video controls preload="metadata" src={center.video_apresentacao_url} /> </section>}

        {center.anuncios?.length > 0 && <section className="center-profile-section"><SectionHeading eyebrow="Novidades" title="Atualizações do centro" icon={Bell}><p>Publicações recentes do centro para a sua comunidade.</p></SectionHeading><div className="center-profile-news-grid">{center.anuncios.map((item) => <article key={item.id} className={`center-profile-news ${item.importante ? "is-important" : ""}`}>{item.imagem_url && <img src={item.imagem_url} alt="" />}<div>{item.importante && <span>Importante</span>}<h3>{item.titulo}</h3><p>{item.conteudo}</p></div></article>)}</div></section>}

        <section id="sobre" className="center-profile-section center-profile-introduction"><span className="center-section-eyebrow">Identidade institucional</span><h2>Conheça {center.nome}</h2><p>{center.descricao || "Este centro ainda não publicou uma apresentação institucional."}</p>{details.length > 0 && <dl className="center-profile-facts">{details.map((detail) => <div key={detail.label}><dt>{detail.label}</dt><dd>{detail.value}</dd></div>)}</dl>}</section>

        {center.estatisticas?.length > 0 && <section className="center-profile-section"><div className="center-profile-stat-grid">{center.estatisticas.map((item) => <article key={item.id}><strong>{item.valor}</strong><span>{item.titulo}</span></article>)}</div></section>}

        {(center.missao || center.visao || center.valores) && <section className="center-profile-section center-profile-principles"><div className="center-profile-principles-header"><span className="center-section-eyebrow">A instituição</span><h2>O que orienta este centro</h2></div><div className="center-profile-principles-grid">{center.missao && <article><span>Missão</span><p>{center.missao}</p></article>}{center.visao && <article><span>Visão</span><p>{center.visao}</p></article>}{center.valores && <article><span>Valores</span><p>{center.valores}</p></article>}</div></section>}

        {center.diferenciais?.length > 0 && <section className="center-profile-section"><SectionHeading eyebrow="Porquê este centro" title="Diferenciais institucionais" icon={Sparkles} /><div className="center-profile-feature-grid">{center.diferenciais.map((item) => <article key={item.id}><Sparkles size={18} /><h3>{item.titulo}</h3><p>{item.descricao}</p></article>)}</div></section>}

        {center.areas_formacao?.length > 0 && <section className="center-profile-section"><SectionHeading eyebrow="Áreas de atuação" title="Áreas de formação" icon={GraduationCap} /><div className="center-profile-chip-grid">{center.areas_formacao.map((item) => <article key={item.id}><GraduationCap size={17} /><div><h3>{item.nome}</h3>{item.descricao && <p>{item.descricao}</p>}</div></article>)}</div></section>}

        <section id="formacoes" className="center-profile-section"><SectionHeading eyebrow="Formações" title="Formações publicadas" icon={BookOpen}><p>Informações, condições e inscrições são geridas pelo próprio centro.</p></SectionHeading>{center.cursos?.length ? <div className="center-profile-course-grid">{center.cursos.map((course) => <CourseTile key={course.id} course={course} onNavigate={onNavigate} />)}</div> : <div className="center-profile-empty"><BookOpen size={24} /><p>Este centro ainda não tem formações públicas para apresentar.</p></div>}</section>

        {center.cursos_video?.length > 0 && <section className="center-profile-section"><SectionHeading eyebrow="Aprendizagem em vídeo" title="Cursos em vídeo do centro" icon={CirclePlay} /><div className="center-media-course-grid">{center.cursos_video.map((course) => <VideoCourseTile key={course.id} course={course} onNavigate={onNavigate} />)}</div></section>}

        {center.eventos?.length > 0 && <section className="center-profile-section"><SectionHeading eyebrow="Agenda" title="Próximos eventos" icon={CalendarDays} /><div className="center-profile-event-grid">{center.eventos.map((event) => <article key={event.id}><div>{event.imagem_url ? <img src={event.imagem_url} alt="" /> : <CalendarDays size={26} />}</div><section><span>{event.tipo}</span><h3>{event.titulo}</h3><p><CalendarDays size={14} /> {event.inicio_formatado}</p><p><MapPin size={14} /> {event.local}</p>{event.link_inscricao && <a href={event.link_inscricao} target="_blank" rel="noreferrer">Mais informações <ArrowRight size={14} /></a>}</section></article>)}</div></section>}

        {center.estagios?.length > 0 && <section className="center-profile-section"><SectionHeading eyebrow="Oportunidades" title="Estágios abertos" icon={BriefcaseBusiness} /><div className="center-profile-opportunity-grid">{center.estagios.map((item) => <article key={item.id}>{item.imagem_url && <img src={item.imagem_url} alt="" />}<div><span>{item.area || item.modalidade}</span><h3>{item.titulo}</h3><p>{item.resumo}</p><small>{item.vagas_restantes} vagas · candidatura até {item.data_limite}</small></div></article>)}</div></section>}

        {center.formadores?.length > 0 && <section id="formadores" className="center-profile-section"><SectionHeading eyebrow="Equipa pedagógica" title="Formadores do centro" icon={UsersRound} /><div className="center-profile-teacher-grid">{center.formadores.map((teacher) => <article key={teacher.id} className="center-profile-teacher"><ImageOrInitial src={teacher.foto_url} label={teacher.nome} className="center-profile-person-photo" /><div><h3>{teacher.nome}</h3><p>{teacher.titulo}</p>{teacher.biografia && <small>{teacher.biografia}</small>}</div></article>)}</div></section>}

        {center.equipa?.length > 0 && <section className="center-profile-section"><SectionHeading eyebrow="Gestão e apoio" title="Equipa do centro" icon={Building2} /><div className="center-profile-team-grid">{center.equipa.map((member) => <article key={member.id}><ImageOrInitial src={member.foto_url} label={member.nome} className="center-profile-team-photo" /><div><h3>{member.nome}</h3><p>{member.cargo}</p>{member.biografia && <small>{member.biografia}</small>}{member.linkedin && <a href={member.linkedin} target="_blank" rel="noreferrer">LinkedIn <ExternalLink size={12} /></a>}</div></article>)}</div></section>}

        {center.recursos?.length > 0 && <section className="center-profile-section"><SectionHeading eyebrow="Infraestruturas" title="Recursos do centro" icon={Wrench} /><div className="center-profile-chip-grid">{center.recursos.map((item) => <article key={item.id}><Wrench size={17} /><div><h3>{item.nome}</h3><p>{item.descricao}</p></div></article>)}</div></section>}

        {center.certificacoes?.length > 0 && <section className="center-profile-section"><SectionHeading eyebrow="Reconhecimento" title="Certificações" icon={Trophy} /><div className="center-profile-certification-grid">{center.certificacoes.map((item) => <article key={item.id}>{item.logo_url ? <img src={item.logo_url} alt="" /> : <Trophy size={23} />}<div><h3>{item.nome}</h3><span>{item.orgao_emissor}</span>{item.descricao && <p>{item.descricao}</p>}</div></article>)}</div></section>}

        {center.depoimentos?.length > 0 && <section className="center-profile-section"><SectionHeading eyebrow="Experiências" title="Depoimentos aprovados" icon={Star} /><div className="center-profile-testimonial-grid">{center.depoimentos.map((item) => <article key={item.id}><div className="center-profile-rating">{Array.from({ length: item.nota }).map((_, index) => <Star key={index} size={13} fill="currentColor" />)}</div><p>“{item.texto}”</p><footer><ImageOrInitial src={item.foto_url} label={item.nome} className="center-profile-testimonial-photo" /><div><strong>{item.nome}</strong><span>{item.cargo}</span></div></footer></article>)}</div></section>}

        {center.parcerias?.length > 0 && <section className="center-profile-section"><SectionHeading eyebrow="Rede institucional" title="Parcerias ativas" icon={Landmark} /><div className="center-profile-partner-grid">{center.parcerias.map((item) => <article key={item.id}>{item.logo_url ? <img src={item.logo_url} alt="" /> : <Landmark size={22} />}<div><span>{item.tipo}</span><h3>{item.nome}</h3>{item.descricao && <p>{item.descricao}</p>}{item.website && <a href={item.website} target="_blank" rel="noreferrer">Visitar parceiro <ExternalLink size={12} /></a>}</div></article>)}</div></section>}

        {center.galeria?.length > 0 && <section id="galeria" className="center-profile-section"><SectionHeading eyebrow="Espaços e experiências" title="Galeria do centro" icon={ImageIcon} /><div className="center-profile-gallery">{center.galeria.map((item) => <figure key={item.id}><img src={item.imagem_url} alt={item.titulo || "Imagem do centro"} /><figcaption><span>{item.categoria}</span><strong>{item.titulo}</strong></figcaption></figure>)}</div></section>}
      </div>

      <aside className="center-profile-aside"><div className="center-profile-contact-card"><span className="center-section-eyebrow">Informações práticas</span><h2>Fale com o centro</h2>{center.is_internacional && <p><Globe2 size={17} /> Centro internacional em {center.pais_nome}</p>}{center.endereco && <p><MapPin size={17} /> {center.endereco}</p>}{centerMapsUrl && <div className="center-profile-contact-links"><a href={centerMapsUrl} target="_blank" rel="noreferrer"><MapPin size={16} /> Ver no Google Maps <ExternalLink size={14} /></a></div>}{center.horario_funcionamento && <p><Clock3 size={17} /> {center.horario_funcionamento}</p>}{hasContact ? <div className="center-profile-contact-links">{center.telefone && <a href={`tel:${center.telefone}`}><Phone size={16} /> {center.telefone}</a>}{center.email && <a href={`mailto:${center.email}`}><Mail size={16} /> {center.email}</a>}{center.site && <a href={center.site} target="_blank" rel="noreferrer"><ExternalLink size={16} /> Visitar website</a>}</div> : <p className="center-profile-contact-muted">Os contactos deste centro ainda não foram publicados.</p>}</div>{center.filiais?.length > 0 && <div className="center-profile-branch-card"><span>Outros locais</span>{center.filiais.map((branch) => <article key={branch.id}><Building2 size={15} /><div><strong>{branch.nome}</strong><small>{branch.endereco}</small></div></article>)}</div>}{socialEntries.length > 0 && <div className="center-profile-social-card"><span>Siga o centro</span><div>{socialEntries.map(([name, url]) => <a key={name} href={url} target="_blank" rel="noreferrer">{name}</a>)}</div></div>}<div className="center-profile-trust"><ShieldCheck size={20} /><p>As condições de cada formação são apresentadas antes da inscrição.</p></div></aside>
    </section>
  </main>;
}
