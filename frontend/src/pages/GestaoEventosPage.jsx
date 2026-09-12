import { useEffect, useState } from "react";
import { CalendarDays, MapPin, Plus, Trash2, Pencil, Users, BarChart3 } from "lucide-react";
import "./gestao-eventos-page.css";

const BASE = "/api/public/eventos/gestao";

const csrfToken = () => document.cookie.split(";").map((p) => p.trim()).find((p) => p.startsWith("csrftoken="))?.split("=")[1] || "";

export default function GestaoEventosPage({ onNavigate }) {
  const [loggedIn, setLoggedIn] = useState(false);
  const [codigo, setCodigo] = useState("");
  const [perfil, setPerfil] = useState(null);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState("");
  const [eventos, setEventos] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [editEvent, setEditEvent] = useState(null);
  const [form, setForm] = useState({ titulo: "", descricao: "", data_inicio: "", local: "", cidade: "", modalidade: "PRESENCIAL", categoria: "Geral" });

  useEffect(() => {
    const convite = sessionStorage.getItem("convite_eventos");
    if (convite) {
      const data = JSON.parse(convite);
      setPerfil(data);
      setLoggedIn(true);
    }
  }, []);

  useEffect(() => { if (loggedIn) loadEventos(); }, [loggedIn]);

  const loadEventos = async () => {
    try {
      const res = await fetch(BASE + "/", { credentials: "same-origin" });
      if (res.ok) { const data = await res.json(); setEventos(data.eventos || []); }
    } catch { setEventos([]); }
  };

  const handleLogin = async () => {
    if (!codigo.trim()) { setErro("Digite o código de acesso."); return; }
    setLoading(true); setErro("");
    try {
      const res = await fetch("/backend/gestoreduka/api/react/convites-eventos/validar/", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ codigo: codigo.trim() }),
      });
      const data = await res.json();
      if (!res.ok) { setErro(data.detail || "Código inválido."); setLoading(false); return; }
      sessionStorage.setItem("convite_eventos", JSON.stringify(data.convite));
      setPerfil(data.convite);
      setLoggedIn(true);
    } catch { setErro("Erro de conexão."); }
    setLoading(false);
  };

  const handleLogout = async () => {
    try { await fetch("/backend/gestoreduka/api/react/convites-eventos/logout/", { method: "POST" }); } catch {}
    sessionStorage.removeItem("convite_eventos");
    setLoggedIn(false); setCodigo(""); setPerfil(null); setEventos(null);
  };

  const createEvent = async () => {
    if (!form.titulo.trim() || !form.descricao.trim() || !form.data_inicio) { setErro("Título, descrição e data são obrigatórios."); return; }
    setLoading(true); setErro("");
    try {
      const res = await fetch(BASE + "/criar/", {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) { setErro(data.detail || "Erro ao criar evento."); setLoading(false); return; }
      setShowCreate(false);
      setForm({ titulo: "", descricao: "", data_inicio: "", local: "", cidade: "", modalidade: "PRESENCIAL", categoria: "Geral" });
      loadEventos();
    } catch { setErro("Erro de conexão."); }
    setLoading(false);
  };

  const updateEvent = async () => {
    if (!editEvent) return;
    setLoading(true); setErro("");
    try {
      const res = await fetch(`${BASE}/${editEvent.id}/atualizar/`, {
        method: "PATCH", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) { setErro(data.detail || "Erro ao atualizar."); setLoading(false); return; }
      setEditEvent(null);
      loadEventos();
    } catch { setErro("Erro de conexão."); }
    setLoading(false);
  };

  const deleteEvent = async (ev) => {
    if (!window.confirm(`Remover "${ev.titulo}"?`)) return;
    try {
      await fetch(`${BASE}/${ev.id}/atualizar/`, {
        method: "PATCH", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify({ status: "CANCELADO" }),
      });
      loadEventos();
    } catch {}
  };

  const openEdit = (ev) => {
    setForm({ titulo: ev.titulo, descricao: ev.resumo || "", data_inicio: ev.data_inicio?.slice(0, 16) || "", local: ev.local || "", cidade: ev.cidade || "", modalidade: ev.modalidade || "PRESENCIAL", categoria: ev.categoria || "Geral" });
    setEditEvent(ev);
    setShowCreate(false);
  };

  if (!loggedIn) {
    return (
      <main className="gestao-eventos-page">
        <div className="gestao-eventos-gate">
          <span className="eyebrow">Área independente</span>
          <h1>Gestão de Eventos</h1>
          <p>Insira o código de acesso fornecido pelo administrador para gerir os eventos da sua organização.</p>
          <input type="text" className="gestao-input" placeholder="Ex: A1B2C3D4" value={codigo}
            onChange={(e) => { setCodigo(e.target.value.toUpperCase()); setErro(""); }}
            onKeyDown={(e) => e.key === "Enter" && handleLogin()} maxLength={8} autoFocus />
          {erro && <p className="gestao-error">{erro}</p>}
          <button className="primary-action" onClick={handleLogin} disabled={loading}>
            {loading ? "A validar..." : "Entrar"}
          </button>
        </div>
      </main>
    );
  }

  return (
    <div className="gestao-eventos-page">
      <div className="gestao-eventos-topbar">
        <div className="gestao-eventos-topbar-left">
          {perfil?.logo ? <img src={perfil.logo} alt="" className="gestao-eventos-logo" /> : <div className="gestao-eventos-logo-placeholder" />}
          <div>
            <span className="gestao-eventos-org">{perfil?.nome_organizacao || "Organização"}</span>
            {perfil?.codigo && <span className="gestao-eventos-codigo">{perfil.codigo}</span>}
          </div>
        </div>
        <div className="gestao-eventos-topbar-actions">
          <button className="primary-action" onClick={() => { setShowCreate(true); setEditEvent(null); setForm({ titulo: "", descricao: "", data_inicio: "", local: "", cidade: "", modalidade: "PRESENCIAL", categoria: "Geral" }); }}>
            <Plus size={14} /> Criar Evento
          </button>
          <button className="text-action" onClick={handleLogout}>Sair</button>
        </div>
      </div>

      <div className="gestao-eventos-content">
        {(showCreate || editEvent) && (
          <div className="gestao-event-modal">
            <form className="gestao-event-form" onSubmit={(e) => { e.preventDefault(); editEvent ? updateEvent() : createEvent(); }}>
              <h3>{editEvent ? "Editar Evento" : "Criar Novo Evento"}</h3>
              <label><span>Título</span><input className="gestao-input" required minLength={3} value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} /></label>
              <label><span>Descrição</span><textarea className="gestao-input" required rows={3} value={form.descricao} onChange={(e) => setForm({ ...form, descricao: e.target.value })} /></label>
              <div className="gestao-form-row">
                <label><span>Data de Início</span><input className="gestao-input" required type="datetime-local" value={form.data_inicio} onChange={(e) => setForm({ ...form, data_inicio: e.target.value })} /></label>
                <label><span>Modalidade</span><select className="gestao-input" value={form.modalidade} onChange={(e) => setForm({ ...form, modalidade: e.target.value })}>
                  <option value="PRESENCIAL">Presencial</option><option value="ONLINE">Online</option><option value="HIBRIDO">Híbrido</option>
                </select></label>
              </div>
              <div className="gestao-form-row">
                <label><span>Local</span><input className="gestao-input" value={form.local} onChange={(e) => setForm({ ...form, local: e.target.value })} /></label>
                <label><span>Cidade</span><input className="gestao-input" value={form.cidade} onChange={(e) => setForm({ ...form, cidade: e.target.value })} /></label>
              </div>
              <label><span>Categoria</span><input className="gestao-input" value={form.categoria} onChange={(e) => setForm({ ...form, categoria: e.target.value })} /></label>
              {erro && <p className="gestao-error">{erro}</p>}
              <div className="gestao-form-actions">
                <button type="button" className="text-action" onClick={() => { setShowCreate(false); setEditEvent(null); }}>Cancelar</button>
                <button type="submit" className="primary-action" disabled={loading}>{loading ? "A guardar..." : editEvent ? "Atualizar" : "Criar Evento"}</button>
              </div>
            </form>
          </div>
        )}

        <div className="gestao-events-header">
          <h2>Meus Eventos</h2>
          <span>{eventos ? eventos.length : 0} evento{eventos?.length !== 1 ? "s" : ""}</span>
        </div>

        {eventos === null ? (
          <p className="gestao-loading">A carregar eventos...</p>
        ) : eventos.length === 0 ? (
          <div className="gestao-empty">
            <CalendarDays size={40} />
            <p>Ainda não criou nenhum evento.</p>
            <button className="primary-action" onClick={() => setShowCreate(true)}><Plus size={14} /> Criar primeiro evento</button>
          </div>
        ) : (
          <div className="gestao-events-grid">
            {eventos.map((ev) => (
              <article key={ev.id} className="gestao-event-card">
                <div className="gestao-event-card-cover" style={ev.imagem_url ? { backgroundImage: `url(${ev.imagem_url})` } : {}}>
                  {!ev.imagem_url && <CalendarDays size={28} />}
                  <span className={`gestao-event-status status-${ev.status?.toLowerCase()}`}>{ev.status}</span>
                </div>
                <div className="gestao-event-card-body">
                  <h3>{ev.titulo}</h3>
                  <div className="gestao-event-card-meta">
                    <span><CalendarDays size={13} /> {ev.data_inicio ? new Date(ev.data_inicio).toLocaleDateString("pt-AO", { day: "numeric", month: "short", year: "numeric" }) : "—"}</span>
                    {ev.local && <span><MapPin size={13} /> {ev.local}</span>}
                  </div>
                  <div className="gestao-event-card-stats">
                    <span>{ev.bilhetes_vendidos || 0} vendidos</span>
                    <span>{ev.capacidade || 0} capacidade</span>
                  </div>
                  <div className="gestao-event-card-actions">
                    <button className="primary-action" onClick={() => onNavigate(`/gestao-eventos/${ev.id}`)}>
                      <BarChart3 size={13} /> Gerenciar
                    </button>
                    <button className="text-action" onClick={() => openEdit(ev)}><Pencil size={14} /></button>
                    <button className="text-action gestao-delete-btn" onClick={() => deleteEvent(ev)}><Trash2 size={14} /></button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
