import { useEffect, useState, useCallback } from "react";
import { ArrowLeft, BarChart3, CalendarDays, CheckCircle2, ChevronRight, Edit3, Image, MapPin, Plus, Tag, Ticket, Trash2, Users, X, XCircle, AlertCircle, Search, Download } from "lucide-react";
import CheckInPanel from "../components/CheckInPanel";
import "./gestao-eventos-page.css";

const BASE = "/api/public/eventos/gestao";
const csrfToken = () => document.cookie.split(";").map((p) => p.trim()).find((p) => p.startsWith("csrftoken="))?.split("=")[1] || "";

const TABS = [
  { key: "visao_geral", label: "Visão Geral", icon: BarChart3 },
  { key: "informacoes", label: "Informações", icon: Edit3 },
  { key: "bilhetes", label: "Bilhetes", icon: Ticket },
  { key: "vendas", label: "Vendas", icon: Tag },
  { key: "participantes", label: "Participantes", icon: Users },
  { key: "checkin", label: "Check-in", icon: CheckCircle2 },
];

function StatCard({ label, value, sub, color }) {
  return <div className="em-stat-card" style={color ? { borderColor: color } : {}}>
    <span className="em-stat-label">{label}</span>
    <strong className="em-stat-value">{value}</strong>
    {sub && <span className="em-stat-sub">{sub}</span>}
  </div>;
}

function LoteForm({ lote, onClose, onSave, eventoId }) {
  const [form, setForm] = useState(lote || { nome: "", descricao: "", preco: "", quantidade_total: "", moeda: "AOA", cor_primaria: "#0F6B8A", cor_secundaria: "#EAF8FA", activo: true, texto_ingresso: "", beneficios: "", regras: "" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    if (!form.nome.trim() || !form.preco || !form.quantidade_total) { setError("Nome, preço e quantidade são obrigatórios."); return; }
    setSaving(true); setError("");
    try {
      const url = lote ? `${BASE}/${eventoId}/lotes/${lote.id}/` : `${BASE}/${eventoId}/lotes/`;
      const res = await fetch(url, {
        method: lote ? "PATCH" : "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify({ ...form, preco: Number(form.preco), quantidade_total: Number(form.quantidade_total) }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || "Erro ao guardar."); setSaving(false); return; }
      onSave();
    } catch { setError("Erro de conexão."); setSaving(false); }
  };

  return <div className="manager-modal">
    <form onSubmit={submit}>
      <header><div><span className="manager-eyebrow">{lote ? "Editar Tipo" : "Novo Tipo de Bilhete"}</span><h2>{lote ? lote.nome : "Criar Tipo"}</h2></div><button type="button" onClick={onClose}><X size={18} /></button></header>
      <div className="manager-form-grid">
        <label className="wide"><span>Nome</span><input required value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} /></label>
        <label className="wide"><span>Descrição</span><textarea rows={2} value={form.descricao} onChange={(e) => setForm({ ...form, descricao: e.target.value })} /></label>
        <label><span>Preço (Kz)</span><input required type="number" min="0" step="0.01" value={form.preco} onChange={(e) => setForm({ ...form, preco: e.target.value })} /></label>
        <label><span>Quantidade</span><input required type="number" min={lote ? lote.quantidade_vendida || 0 : 1} value={form.quantidade_total} onChange={(e) => setForm({ ...form, quantidade_total: e.target.value })} /></label>
        <label><span>Moeda</span><select value={form.moeda} onChange={(e) => setForm({ ...form, moeda: e.target.value })}><option value="AOA">AOA</option><option value="USD">USD</option><option value="EUR">EUR</option></select></label>
        <label><span>Cor Primária</span><input type="color" value={form.cor_primaria} onChange={(e) => setForm({ ...form, cor_primaria: e.target.value })} /></label>
        <label><span>Cor Secundária</span><input type="color" value={form.cor_secundaria} onChange={(e) => setForm({ ...form, cor_secundaria: e.target.value })} /></label>
        <label className="wide"><span>Texto do Ingresso</span><input value={form.texto_ingresso} onChange={(e) => setForm({ ...form, texto_ingresso: e.target.value })} placeholder="Ex: Acesso VIP" /></label>
        <label className="wide"><span>Benefícios (um por linha)</span><textarea rows={3} value={form.beneficios} onChange={(e) => setForm({ ...form, beneficios: e.target.value })} /></label>
        <label className="wide"><span>Regras (uma por linha)</span><textarea rows={3} value={form.regras} onChange={(e) => setForm({ ...form, regras: e.target.value })} /></label>
      </div>
      <div className="manager-checks"><label><input type="checkbox" checked={form.activo} onChange={(e) => setForm({ ...form, activo: e.target.checked })} />Ativo para venda</label></div>
      {error && <p className="manager-form-error">{error}</p>}
      <footer><button type="button" onClick={onClose}>Cancelar</button><button className="primary" disabled={saving}>{saving ? "A guardar..." : "Guardar"}</button></footer>
    </form>
  </div>;
}

export default function EventManagerPage({ eventoId, onNavigate }) {
  const [tab, setTab] = useState("visao_geral");
  const [data, setData] = useState(null);
  const [lotes, setLotes] = useState(null);
  const [vendas, setVendas] = useState(null);
  const [participantes, setParticipantes] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [loteModal, setLoteModal] = useState(null);
  const [editInfo, setEditInfo] = useState(false);
  const [infoForm, setInfoForm] = useState({});
  const [vendaFilter, setVendaFilter] = useState("");
  const [partFilter, setPartFilter] = useState("");
  const [searchVenda, setSearchVenda] = useState("");
  const [searchPart, setSearchPart] = useState("");

  const loadDashboard = useCallback(async () => {
    try {
      const res = await fetch(`${BASE}/${eventoId}/`, { credentials: "same-origin" });
      if (!res.ok) { setError("Evento não encontrado."); setLoading(false); return; }
      const d = await res.json();
      setData(d);
      setInfoForm(d.evento || {});
      setLoading(false);
    } catch { setError("Erro ao carregar."); setLoading(false); }
  }, [eventoId]);

  const loadLotes = useCallback(async () => {
    try {
      const res = await fetch(`${BASE}/${eventoId}/lotes/`, { credentials: "same-origin" });
      if (res.ok) { const d = await res.json(); setLotes(d.lotes || []); }
    } catch { setLotes([]); }
  }, [eventoId]);

  const loadVendas = useCallback(async () => {
    try {
      const url = `${BASE}/${eventoId}/vendas/?${vendaFilter ? `status=${vendaFilter}` : ""}${searchVenda ? `&q=${searchVenda}` : ""}`;
      const res = await fetch(url, { credentials: "same-origin" });
      if (res.ok) { const d = await res.json(); setVendas(d); }
    } catch { setVendas({ pedidos: [], total: 0 }); }
  }, [eventoId, vendaFilter, searchVenda]);

  const loadParticipantes = useCallback(async () => {
    try {
      const url = `${BASE}/${eventoId}/participantes/?${partFilter ? `status=${partFilter}` : ""}${searchPart ? `&q=${searchPart}` : ""}`;
      const res = await fetch(url, { credentials: "same-origin" });
      if (res.ok) { const d = await res.json(); setParticipantes(d); }
    } catch { setParticipantes({ participantes: [], total: 0, checkins: 0 }); }
  }, [eventoId, partFilter, searchPart]);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);
  useEffect(() => { if (tab === "bilhetes") loadLotes(); }, [tab, loadLotes]);
  useEffect(() => { if (tab === "vendas") loadVendas(); }, [tab, loadVendas]);
  useEffect(() => { if (tab === "participantes") loadParticipantes(); }, [tab, loadParticipantes]);

  const saveInfo = async () => {
    try {
      const res = await fetch(`${BASE}/${eventoId}/atualizar/`, {
        method: "PATCH", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify(infoForm),
      });
      if (res.ok) { setEditInfo(false); loadDashboard(); }
    } catch {}
  };

  const uploadCapa = async (file) => {
    const fd = new FormData();
    fd.append("imagem_capa", file);
    try {
      const res = await fetch(`${BASE}/${eventoId}/capa/`, {
        method: "POST", credentials: "same-origin",
        headers: { "X-CSRFToken": csrfToken() }, body: fd,
      });
      if (res.ok) loadDashboard();
    } catch {}
  };

  const deleteLote = async (lote) => {
    if (!window.confirm(`Remover "${lote.nome}"?`)) return;
    try {
      const res = await fetch(`${BASE}/${eventoId}/lotes/${lote.id}/`, {
        method: "DELETE", credentials: "same-origin",
        headers: { "X-CSRFToken": csrfToken() },
      });
      if (res.ok) loadLotes();
    } catch {}
  };

  if (loading) return <div className="gestao-eventos-page"><div className="gestao-loading">A carregar painel de gestão...</div></div>;
  if (error) return <div className="gestao-eventos-page"><div className="gestao-empty"><p>{error}</p><button className="primary-action" onClick={() => onNavigate("/gestao-eventos")}>Voltar</button></div></div>;

  const ev = data?.evento;
  const stats = data?.stats;

  return (
    <div className="gestao-eventos-page em-layout">
      <aside className="em-sidebar">
        <button className="em-back" onClick={() => onNavigate("/gestao-eventos")}><ArrowLeft size={16} /> Voltar</button>
        <div className="em-event-info">
          <div className="em-event-thumb" style={ev?.imagem_url ? { backgroundImage: `url(${ev.imagem_url})` } : {}}>
            {!ev?.imagen_url && <CalendarDays size={20} />}
          </div>
          <strong>{ev?.titulo}</strong>
          <span className={`em-status-badge status-${ev?.status?.toLowerCase()}`}>{ev?.status}</span>
        </div>
        <nav className="em-tabs">
          {TABS.map((t) => <button key={t.key} className={tab === t.key ? "active" : ""} onClick={() => setTab(t.key)}><t.icon size={15} /> {t.label}</button>)}
        </nav>
      </aside>

      <main className="em-main">
        {tab === "visao_geral" && (
          <section className="em-section">
            <h2>Visão Geral</h2>
            <div className="em-stats-grid">
              <StatCard label="Capacidade" value={stats?.capacidade || 0} />
              <StatCard label="Bilhetes Vendidos" value={stats?.bilhetes_vendidos || 0} color="var(--brand)" />
              <StatCard label="Disponíveis" value={stats?.bilhetes_disponiveis || 0} color="var(--success)" />
              <StatCard label="Check-ins" value={stats?.checkins || 0} />
              <StatCard label="Receita" value={`${Number(stats?.receita || 0).toLocaleString("pt-AO")} ${stats?.moeda || "Kz"}`} color="var(--brand)" />
              <StatCard label="Ocupação" value={`${stats?.ocupacao || 0}%`} />
              <StatCard label="Pedidos" value={stats?.total_pedidos || 0} sub={`${stats?.pedidos_pagos || 0} pagos`} />
              <StatCard label="Cancelados" value={stats?.pedidos_cancelados || 0} />
            </div>
            {data?.lotes?.length > 0 && <div className="em-section-block">
              <h3>Tipos de Bilhete</h3>
              <div className="em-lotes-mini">{data.lotes.map((l) => <div key={l.id} className="em-lote-mini">
                <strong>{l.nome}</strong>
                <span>{Number(l.preco).toLocaleString("pt-AO")} {l.moeda}</span>
                <div className="em-progress-bar"><div style={{ width: `${l.percentual_vendido}%` }} /></div>
                <span>{l.quantidade_vendida}/{l.quantidade_total} vendidos ({l.percentual_vendido}%)</span>
              </div>)}</div>
            </div>}
          </section>
        )}

        {tab === "informacoes" && (
          <section className="em-section">
            <div className="em-section-header"><h2>Informações do Evento</h2>
              {!editInfo && <button className="text-action" onClick={() => { setEditInfo(true); setInfoForm(ev || {}); }}><Edit3 size={14} /> Editar</button>}
            </div>
            <div className="em-cover-area">
              {ev?.imagem_url ? <img src={ev.imagem_url} alt="Capa" className="em-cover-img" /> : <div className="em-cover-placeholder"><Image size={32} /><span>Sem imagem de capa</span></div>}
              <label className="primary-action em-cover-upload"><Image size={14} /> Alterar Capa<input type="file" accept="image/*" hidden onChange={(e) => e.target.files[0] && uploadCapa(e.target.files[0])} /></label>
            </div>
            {editInfo ? (
              <form className="em-info-form" onSubmit={(e) => { e.preventDefault(); saveInfo(); }}>
                <label><span>Título</span><input className="gestao-input" value={infoForm.titulo || ""} onChange={(e) => setInfoForm({ ...infoForm, titulo: e.target.value })} /></label>
                <label><span>Resumo</span><input className="gestao-input" value={infoForm.resumo || ""} onChange={(e) => setInfoForm({ ...infoForm, resumo: e.target.value })} /></label>
                <label><span>Descrição</span><textarea className="gestao-input" rows={4} value={infoForm.descricao || ""} onChange={(e) => setInfoForm({ ...infoForm, descricao: e.target.value })} /></label>
                <div className="gestao-form-row">
                  <label><span>Local</span><input className="gestao-input" value={infoForm.local || ""} onChange={(e) => setInfoForm({ ...infoForm, local: e.target.value })} /></label>
                  <label><span>Cidade</span><input className="gestao-input" value={infoForm.cidade || ""} onChange={(e) => setInfoForm({ ...infoForm, cidade: e.target.value })} /></label>
                </div>
                <div className="gestao-form-row">
                  <label><span>Categoria</span><input className="gestao-input" value={infoForm.categoria || ""} onChange={(e) => setInfoForm({ ...infoForm, categoria: e.target.value })} /></label>
                  <label><span>Modalidade</span><select className="gestao-input" value={infoForm.modalidade || "PRESENCIAL"} onChange={(e) => setInfoForm({ ...infoForm, modalidade: e.target.value })}>
                    <option value="PRESENCIAL">Presencial</option><option value="ONLINE">Online</option><option value="HIBRIDO">Híbrido</option>
                  </select></label>
                </div>
                <label><span>URL Online</span><input className="gestao-input" value={infoForm.url_online || ""} onChange={(e) => setInfoForm({ ...infoForm, url_online: e.target.value })} /></label>
                <label><span>Status</span><select className="gestao-input" value={infoForm.status || "RASCUNHO"} onChange={(e) => setInfoForm({ ...infoForm, status: e.target.value })}>
                  <option value="RASCUNHO">Rascunho</option><option value="PUBLICADO">Publicado</option><option value="ENCERRADO">Encerrado</option><option value="CANCELADO">Cancelado</option>
                </select></label>
                <div className="em-form-actions"><button type="button" className="text-action" onClick={() => setEditInfo(false)}>Cancelar</button><button type="submit" className="primary-action">Guardar</button></div>
              </form>
            ) : (
              <div className="em-info-grid">
                <div><strong>Local</strong><span>{ev?.local || "—"}</span></div>
                <div><strong>Cidade</strong><span>{ev?.cidade || "—"}</span></div>
                <div><strong>Categoria</strong><span>{ev?.categoria || "—"}</span></div>
                <div><strong>Modalidade</strong><span>{ev?.modalidade || "—"}</span></div>
                <div><strong>Data Início</strong><span>{ev?.data_inicio ? new Date(ev.data_inicio).toLocaleString("pt-AO") : "—"}</span></div>
                <div><strong>Data Fim</strong><span>{ev?.data_fim ? new Date(ev.data_fim).toLocaleString("pt-AO") : "—"}</span></div>
                <div><strong>URL Online</strong><span>{ev?.url_online || "—"}</span></div>
              </div>
            )}
          </section>
        )}

        {tab === "bilhetes" && (
          <section className="em-section">
            <div className="em-section-header"><h2>Tipos de Bilhete</h2>
              <button className="primary-action" onClick={() => setLoteModal("new")}><Plus size={14} /> Novo Tipo</button>
            </div>
            {lotes === null ? <p>A carregar...</p> : lotes.length === 0 ? (
              <div className="gestao-empty"><Tag size={32} /><p>Nenhum tipo de bilhete criado.</p></div>
            ) : (
              <div className="em-lotes-list">{lotes.map((l) => (
                <div key={l.id} className="em-lote-card">
                  <div className="em-lote-color" style={{ background: l.cor_primaria }} />
                  <div className="em-lote-info">
                    <div className="em-lote-header"><strong>{l.nome}</strong><span className={`em-status-badge ${l.activo ? "status-publicado" : "status-cancelado"}`}>{l.activo ? "Ativo" : "Inativo"}</span></div>
                    <span className="em-lote-price">{Number(l.preco).toLocaleString("pt-AO")} {l.moeda}</span>
                    <div className="em-progress-bar"><div style={{ width: `${l.percentual_vendido}%`, background: l.cor_primaria }} /></div>
                    <span className="em-lote-stats">{l.quantidade_vendida} vendidos · {l.lugares_disponiveis} disponíveis · {l.percentual_vendido}%</span>
                  </div>
                  <div className="em-lote-actions">
                    <button className="text-action" onClick={() => { setLoteModal(l); }}><Edit3 size={14} /></button>
                    {l.quantidade_vendida === 0 && <button className="text-action gestao-delete-btn" onClick={() => deleteLote(l)}><Trash2 size={14} /></button>}
                  </div>
                </div>
              ))}</div>
            )}
            {loteModal && <LoteForm lote={loteModal === "new" ? null : loteModal} eventoId={eventoId} onClose={() => setLoteModal(null)} onSave={() => { setLoteModal(null); loadLotes(); loadDashboard(); }} />}
          </section>
        )}

        {tab === "vendas" && (
          <section className="em-section">
            <div className="em-section-header"><h2>Vendas</h2>
              <span>{vendas?.total || 0} pedidos</span>
            </div>
            <div className="em-filters">
              <div className="em-search"><Search size={14} /><input placeholder="Buscar por nome, email ou referência..." value={searchVenda} onChange={(e) => setSearchVenda(e.target.value)} onKeyDown={(e) => e.key === "Enter" && loadVendas()} /></div>
              <select value={vendaFilter} onChange={(e) => setVendaFilter(e.target.value)}>
                <option value="">Todos</option><option value="PENDENTE">Pendente</option><option value="PAGO">Pago</option><option value="CANCELADO">Cancelado</option><option value="REEMBOLSADO">Reembolsado</option>
              </select>
            </div>
            {vendas === null ? <p>A carregar...</p> : vendas.pedidos.length === 0 ? (
              <div className="gestao-empty"><Tag size={32} /><p>Nenhuma venda encontrada.</p></div>
            ) : (
              <div className="em-table-wrap">
                <table className="em-table">
                  <thead><tr><th>Referência</th><th>Cliente</th><th>Bilhete</th><th>Qtd</th><th>Valor</th><th>Status</th><th>Data</th></tr></thead>
                  <tbody>{vendas.pedidos.map((p) => (
                    <tr key={p.id}>
                      <td className="em-td-ref">{p.referencia}</td>
                      <td>{p.nome_comprador}<br /><small>{p.email_comprador}</small></td>
                      <td>{p.lote_nome}</td>
                      <td>{p.quantidade}</td>
                      <td>{Number(p.valor_bruto).toLocaleString("pt-AO")} {p.moeda}</td>
                      <td><span className={`em-status-badge status-${p.status?.toLowerCase()}`}>{p.status}</span></td>
                      <td><small>{p.criado_em ? new Date(p.criado_em).toLocaleDateString("pt-AO") : "—"}</small></td>
                    </tr>
                  ))}</tbody>
                </table>
              </div>
            )}
          </section>
        )}

        {tab === "participantes" && (
          <section className="em-section">
            <div className="em-section-header"><h2>Participantes</h2>
              <span>{participantes?.total || 0} total · {participantes?.checkins || 0} check-ins</span>
            </div>
            <div className="em-filters">
              <div className="em-search"><Search size={14} /><input placeholder="Buscar por nome, email ou código..." value={searchPart} onChange={(e) => setSearchPart(e.target.value)} onKeyDown={(e) => e.key === "Enter" && loadParticipantes()} /></div>
              <select value={partFilter} onChange={(e) => setPartFilter(e.target.value)}>
                <option value="">Todos</option><option value="VALIDO">Válido</option><option value="UTILIZADO">Utilizado</option><option value="CANCELADO">Cancelado</option>
              </select>
            </div>
            {participantes === null ? <p>A carregar...</p> : participantes.participantes.length === 0 ? (
              <div className="gestao-empty"><Users size={32} /><p>Nenhum participante encontrado.</p></div>
            ) : (
              <div className="em-table-wrap">
                <table className="em-table">
                  <thead><tr><th>Nome</th><th>Email</th><th>Bilhete</th><th>Código</th><th>Status</th><th>Data</th></tr></thead>
                  <tbody>{participantes.participantes.map((b) => (
                    <tr key={b.id}>
                      <td>{b.nome_participante}</td>
                      <td><small>{b.email_participante}</small></td>
                      <td>{b.lote_nome}</td>
                      <td className="em-td-code">{b.codigo?.slice(0, 8)}...</td>
                      <td><span className={`em-status-badge status-${b.status?.toLowerCase()}`}>{b.status === "UTILIZADO" ? "Check-in" : b.status}</span></td>
                      <td><small>{b.emitido_em ? new Date(b.emitido_em).toLocaleDateString("pt-AO") : "—"}</small></td>
                    </tr>
                  ))}</tbody>
                </table>
              </div>
            )}
          </section>
        )}

        {tab === "checkin" && (
          <section className="em-section">
            <h2>Check-in / Validação</h2>
            <CheckInPanel />
          </section>
        )}
      </main>
    </div>
  );
}
