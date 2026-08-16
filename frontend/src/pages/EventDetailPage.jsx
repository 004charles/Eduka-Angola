import { useEffect, useMemo, useState } from "react";
import { authRequest } from "../lib/auth-api";
import { ArrowLeft, CalendarDays, CheckCircle2, Clock3, MapPin, ShieldCheck, Ticket, Users } from "lucide-react";
import "./events-page.css";

const formatPrice = (ticket) => `${Number(ticket.preco).toLocaleString("pt-PT")} ${ticket.moeda}`;

export default function EventDetailPage({ slug, student, onNavigate, onAnnounce }) {
  const [event, setEvent] = useState(null);
  const [selectedLot, setSelectedLot] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;
    fetch(`/api/public/eventos/${encodeURIComponent(slug)}/`, { headers: { Accept: "application/json" } })
      .then((response) => {
        if (!response.ok) throw new Error("Evento não encontrado.");
        return response.json();
      })
      .then((data) => {
        if (!active) return;
        setEvent(data);
        setSelectedLot(data.lotes?.[0] || null);
      })
      .catch(() => active && setError("Não foi possível abrir este evento."))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [slug]);

  const total = useMemo(() => selectedLot ? Number(selectedLot.preco) * quantity : 0, [selectedLot, quantity]);

  const startCheckout = async () => {
    if (!student) {
      onNavigate(`/entrar?next=${encodeURIComponent(`/eventos/${slug}`)}`);
      return;
    }
    if (!selectedLot || submitting) return;
    setSubmitting(true);
    try {
      const result = await authRequest("/api/public/eventos/pedido/", { evento_id: event.id, lote_id: selectedLot.id, quantidade: quantity });
      if (result.url_pagamento) window.location.assign(result.url_pagamento);
      else onAnnounce?.("O pedido foi criado, mas o checkout ainda não devolveu um link.");
    } catch (reason) {
      onAnnounce?.(reason?.data?.erro || reason.message || "Não foi possível iniciar o pagamento.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <main className="event-detail-page page-width"><div className="event-detail-loading" /></main>;
  if (error || !event) return <main className="event-detail-page page-width"><div className="events-state error">{error || "Evento não encontrado."}<button className="secondary-action" onClick={() => onNavigate("/eventos")}>Voltar aos eventos</button></div></main>;

  const startDate = new Date(event.data_inicio);
  const endDate = event.data_fim ? new Date(event.data_fim) : null;

  return <main className="event-detail-page">
    <section className="event-detail-hero page-width">
      <button className="back-link" type="button" onClick={() => onNavigate("/eventos")}><ArrowLeft size={17} /> Voltar aos eventos</button>
      <div className="event-detail-hero-grid">
        <div className="event-detail-cover">{event.imagem_url ? <img src={event.imagem_url} alt="" /> : <div className="event-detail-cover-fallback"><Ticket size={56} /></div>}</div>
        <div className="event-detail-intro"><span className="eyebrow"><Ticket size={15} /> {event.categoria}</span><h1>{event.titulo}</h1><p>{event.resumo}</p><div className="event-detail-organizer"><div className="organizer-avatar">{event.organizador?.nome?.slice(0, 1)}</div><div><small>Organizado por</small><strong>{event.organizador?.nome}</strong></div>{event.organizador?.verificado && <span className="verified-label"><CheckCircle2 size={15} /> Verificado</span>}</div></div>
      </div>
    </section>

    <section className="event-detail-content page-width">
      <div className="event-detail-main"><div className="event-detail-facts"><div><CalendarDays size={20} /><span><small>Data</small><strong>{startDate.toLocaleDateString("pt-PT", { day: "2-digit", month: "long", year: "numeric" })}</strong></span></div><div><Clock3 size={20} /><span><small>Horário</small><strong>{startDate.toLocaleTimeString("pt-PT", { hour: "2-digit", minute: "2-digit" })}{endDate ? ` – ${endDate.toLocaleTimeString("pt-PT", { hour: "2-digit", minute: "2-digit" })}` : ""}</strong></span></div><div><MapPin size={20} /><span><small>Local</small><strong>{event.local || event.cidade || event.modalidade}</strong></span></div></div><article className="event-description"><h2>Sobre este evento</h2><p>{event.descricao}</p></article><div className="event-trust-note"><ShieldCheck size={20} /><span>O pagamento é processado de forma segura. O bilhete só será emitido depois da confirmação do pagamento.</span></div></div>
      <aside className="ticket-selector"><div className="ticket-selector-heading"><span className="eyebrow"><Ticket size={15} /> Escolha o seu bilhete</span><strong>{event.bilhetes_disponiveis} disponíveis</strong></div><div className="ticket-lots">{event.lotes.map((lot) => <button type="button" className={`ticket-lot ${selectedLot?.id === lot.id ? "selected" : ""}`} style={{ "--ticket-primary": lot.cor_primaria, "--ticket-secondary": lot.cor_secundaria }} key={lot.id} onClick={() => { setSelectedLot(lot); setQuantity(1); }}><span className="ticket-lot-paper"><span className="ticket-lot-main"><span className="ticket-lot-topline"><small>ACESSO INDIVIDUAL</small><small>{lot.texto_ingresso || "BILHETE DIGITAL"}</small></span><strong className="ticket-lot-brand">edukangola</strong><em>Educação e formação · Angola</em><span className="ticket-lot-event-label">{event.organizador?.nome || "Eduka Eventos"}</span><strong className="ticket-lot-name">{lot.nome}</strong><span className="ticket-lot-meta"><span>{event.cidade || "Luanda"}</span><span>{event.modalidade}</span><b>{formatPrice(lot)}</b></span></span><span className="ticket-lot-stub"><small>BILHETE</small><strong>edukangola</strong><span>{selectedLot?.id === lot.id ? "OK" : "—"}</span><em>{selectedLot?.id === lot.id ? "ESCOLHIDO" : "SELECCIONAR"}</em></span></span></button>)}</div>{selectedLot && <div className="ticket-purchase-summary"><label>Quantidade<select value={quantity} onChange={(change) => setQuantity(Number(change.target.value))}>{Array.from({ length: Math.min(5, selectedLot.lugares_disponiveis) }, (_, index) => <option value={index + 1} key={index}>{index + 1}</option>)}</select></label><div><span>Total</span><strong>{total.toLocaleString("pt-PT")} {selectedLot.moeda}</strong></div><button className="primary-action" type="button" disabled={submitting} onClick={startCheckout}>{submitting ? "A preparar pagamento…" : student ? "Ir para pagamento" : "Entrar e comprar"}</button><small className="ticket-checkout-note">Checkout seguro Edukangola · Prontu</small></div>}</aside>
    </section>
  </main>;
}
