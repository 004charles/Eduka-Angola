import { useEffect, useMemo, useState } from "react";
import { CalendarDays, CheckCircle2, MapPin, ShieldCheck, Ticket } from "lucide-react";
import { authRequest } from "../lib/auth-api";
import "./events-page.css";

const formatPrice = (ticket) => `${Number(ticket.preco).toLocaleString("pt-PT")} ${ticket.moeda}`;

export default function EventTicketsPage({ student, onNavigate, onAnnounce }) {
  const [events, setEvents] = useState([]);
  const [selected, setSelected] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    fetch("/api/public/eventos/", { headers: { Accept: "application/json" } })
      .then((response) => {
        if (!response.ok) throw new Error("Não foi possível carregar os bilhetes.");
        return response.json();
      })
      .then((data) => {
        if (!active) return;
        const availableEvents = data.eventos || [];
        setEvents(availableEvents);
        const firstEvent = availableEvents[0];
        const firstLot = firstEvent?.lotes?.[0];
        if (firstEvent && firstLot) setSelected({ event: firstEvent, lot: firstLot });
      })
      .catch(() => active && setError("Não foi possível carregar os bilhetes neste momento."))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  const lots = useMemo(() => events.flatMap((event) => (event.lotes || []).map((lot) => ({ event, lot }))), [events]);
  const total = selected ? Number(selected.lot.preco) * quantity : 0;

  const selectLot = (event, lot) => {
    setSelected({ event, lot });
    setQuantity(1);
  };

  const startCheckout = async () => {
    if (!student) {
      onNavigate(`/entrar?next=${encodeURIComponent("/eventosv")}`);
      return;
    }
    if (!selected || submitting) return;
    setSubmitting(true);
    try {
      const result = await authRequest("/api/public/eventos/pedido/", {
        evento_id: selected.event.id,
        lote_id: selected.lot.id,
        quantidade: quantity,
      });
      if (result.url_pagamento) window.location.assign(result.url_pagamento);
      else onAnnounce?.("O pedido foi criado, mas o checkout ainda não devolveu um link.");
    } catch (reason) {
      onAnnounce?.(reason?.data?.erro || reason.message || "Não foi possível iniciar o pagamento.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <main className="events-page page-width"><div className="event-detail-loading" /></main>;
  if (error) return <main className="events-page page-width"><div className="events-state error">{error}</div></main>;

  return (
    <main className="events-page page-width">
      <section className="events-hero events-tickets-hero">
        <div>
          <span className="eyebrow"><Ticket size={15} /> Bilhetes Edukangola</span>
          <h1>Garanta o seu lugar.</h1>
          <p>Descubra experiências, encontros e eventos em Angola. Escolha o bilhete certo e confirme a sua presença de forma simples e segura.</p>
        </div>
        <div className="events-hero-note"><ShieldCheck size={20} /><span>Pague com segurança. O seu bilhete é emitido após a confirmação.</span></div>
      </section>

      {lots.length === 0 ? (
        <div className="events-state"><Ticket size={28} /><h2>Bilhetes em breve</h2><p>Quando um evento publicar bilhetes, eles aparecerão aqui.</p></div>
      ) : (
        <section className="event-tickets-layout" aria-label="Bilhetes disponíveis">
          <div className="event-tickets-list">
            <div className="event-tickets-list-heading"><span className="eyebrow"><Ticket size={15} /> Escolha o seu bilhete</span><strong>{lots.length} bilhete{lots.length === 1 ? "" : "s"}</strong></div>
            {lots.map(({ event, lot }) => {
              const isSelected = selected?.lot.id === lot.id;
              return (
                <button className={`ticket-lot event-ticket-row ${isSelected ? "selected" : ""}`} type="button" key={`${event.id}-${lot.id}`} style={{ "--ticket-primary": lot.cor_primaria, "--ticket-secondary": lot.cor_secundaria }} onClick={() => selectLot(event, lot)}>
                  <span className="ticket-lot-paper">
                    <span className="ticket-lot-main">
                      <span className="ticket-lot-topline"><small>ACESSO INDIVIDUAL</small><small>{lot.texto_ingresso || "BILHETE DIGITAL"}</small></span>
                      <strong className="ticket-lot-brand">edukangola</strong>
                      <em>Educação e formação · Angola</em>
                      <span className="ticket-lot-event-label">{event.organizador?.nome || "Eduka Eventos"}</span>
                      <strong className="ticket-lot-name">{lot.nome}</strong>
                      <span className="ticket-lot-meta"><span>{event.cidade || "Luanda"}</span><span>{event.modalidade || "Presencial"}</span><b>{formatPrice(lot)}</b></span>
                    </span>
                    <span className="ticket-lot-stub"><small>BILHETE</small><strong>edukangola</strong><span>{isSelected ? "OK" : "—"}</span><em>{isSelected ? "ESCOLHIDO" : "SELECCIONAR"}</em></span>
                  </span>
                </button>
              );
            })}
          </div>

          {selected && <aside className="event-tickets-checkout">
            <span className="eyebrow"><Ticket size={15} /> Resumo da compra</span>
            <h2>{selected.event.titulo}</h2>
            <p><CalendarDays size={15} /> {selected.event.data_inicio_formatada}</p>
            <p><MapPin size={15} /> {selected.event.cidade || selected.event.local || "Angola"}</p>
            <div className="event-tickets-selected"><span>Bilhete seleccionado</span><strong>{selected.lot.nome}</strong></div>
            <label>Quantidade<select value={quantity} onChange={(change) => setQuantity(Number(change.target.value))}>{Array.from({ length: Math.min(5, selected.lot.lugares_disponiveis || 5) }, (_, index) => <option value={index + 1} key={index}>{index + 1}</option>)}</select></label>
            <div className="event-tickets-total"><span>Total</span><strong>{total.toLocaleString("pt-PT")} {selected.lot.moeda}</strong></div>
            <button className="primary-action" type="button" disabled={submitting} onClick={startCheckout}>{submitting ? "A preparar pagamento…" : student ? "Ir para pagamento" : "Entrar e comprar"}</button>
            <small>Checkout seguro Edukangola · Prontu</small>
            <button className="secondary-action" type="button" onClick={() => onNavigate(`/eventos/${selected.event.slug}`)}>Conhecer o evento</button>
          </aside>}
        </section>
      )}
    </main>
  );
}
