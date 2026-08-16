import { useEffect, useState } from "react";
import { CalendarDays, ChevronRight, MapPin, Search, Ticket, Users } from "lucide-react";
import "./events-page.css";

const formatPrice = (ticket) => `${Number(ticket.preco).toLocaleString("pt-PT")} ${ticket.moeda}`;

export default function EventsPage({ onNavigate }) {
  const [events, setEvents] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    fetch("/api/public/eventos/", { headers: { Accept: "application/json" } })
      .then((response) => {
        if (!response.ok) throw new Error("Não foi possível carregar os eventos.");
        return response.json();
      })
      .then((data) => active && setEvents(data.eventos || []))
      .catch(() => active && setError("Não foi possível carregar os eventos neste momento."))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  const filteredEvents = events.filter((event) => {
    const haystack = `${event.titulo} ${event.categoria} ${event.organizador?.nome} ${event.cidade}`.toLowerCase();
    return haystack.includes(query.trim().toLowerCase());
  });

  return (
    <main className="events-page page-width">
      <section className="events-hero">
        <div>
          <span className="eyebrow"><Ticket size={15} /> Eduka Eventos</span>
          <h1>Encontre o próximo evento que vale a pena viver.</h1>
          <p>Descubra conferências, encontros e experiências organizadas por comunidades e entidades em Angola. Reserve o seu bilhete com a mesma simplicidade com que encontra uma formação.</p>
        </div>
        <div className="events-hero-note"><Users size={20} /><span>Bilhetes digitais, pagamento seguro e confirmação na plataforma.</span></div>
      </section>

      <section className="events-toolbar" aria-label="Pesquisar eventos">
        <label className="events-search"><Search size={18} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Pesquisar eventos, áreas ou organizadores" /></label>
        <span className="events-count">{loading ? "A carregar…" : `${filteredEvents.length} evento${filteredEvents.length === 1 ? "" : "s"}`}</span>
      </section>

      {error && <div className="events-state error" role="alert">{error}</div>}
      {loading && <div className="events-grid">{[1, 2, 3].map((item) => <div className="event-card event-card-skeleton" key={item} />)}</div>}
      {!loading && !error && filteredEvents.length === 0 && <div className="events-state"><Ticket size={28} /><h2>Novos eventos em breve</h2><p>Quando um organizador publicar um evento, ele aparecerá automaticamente nesta área.</p></div>}
      {!loading && !error && filteredEvents.length > 0 && <div className="events-grid">
        {filteredEvents.map((event) => {
          const lowestTicket = event.lotes?.[0];
          return <article className="event-card" key={event.id}>
            <a className="event-card-cover" href={event.detalhe_url} onClick={(click) => { click.preventDefault(); onNavigate(event.detalhe_url); }}>
              {event.imagem_url ? <img src={event.imagem_url} alt="" loading="lazy" decoding="async" /> : <div className="event-card-cover-fallback"><CalendarDays size={34} /></div>}
              <span className="event-card-badge">{event.categoria}</span>
            </a>
            <div className="event-card-body">
              <div className="event-card-organizer">{event.organizador?.verificado && <span className="verified-dot">✓</span>}{event.organizador?.nome}</div>
              <h2><a href={event.detalhe_url} onClick={(click) => { click.preventDefault(); onNavigate(event.detalhe_url); }}>{event.titulo}</a></h2>
              <p className="event-card-summary">{event.resumo}</p>
              <div className="event-card-meta"><span><CalendarDays size={15} /> {event.data_inicio_formatada}</span><span><MapPin size={15} /> {event.cidade || event.local || event.modalidade}</span></div>
              <div className="event-card-footer"><strong>{lowestTicket ? `A partir de ${formatPrice(lowestTicket)}` : "Bilhetes em breve"}</strong><button type="button" onClick={() => onNavigate(event.detalhe_url)} aria-label={`Ver ${event.titulo}`}><ChevronRight size={18} /></button></div>
            </div>
          </article>;
        })}
      </div>}
    </main>
  );
}
