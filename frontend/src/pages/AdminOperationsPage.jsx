import { Activity, ArrowLeft, BarChart3, Building2, CircleDollarSign, ClipboardList, FileText, GraduationCap, Moon, Package, ReceiptText, RefreshCw, Settings2, ShieldCheck, ShoppingBag, Sun, UsersRound, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { authRequest } from "../lib/auth-api";
import useAdminAutoRefresh from "../lib/useAdminAutoRefresh";
import AdminAccessPage from "./AdminAccessPage";
import "./admin-console-page.css";

const SECTIONS = [
  { key: "centros", label: "Centros e filiais", icon: Building2, group: "Oferta" },
  { key: "cursos", label: "Cursos presenciais", icon: GraduationCap, group: "Oferta" },
  { key: "video-cursos", label: "Cursos em vídeo", icon: Activity, group: "Oferta" },
  { key: "planos-video", label: "Planos de vídeo", icon: CircleDollarSign, group: "Oferta" },
  { key: "subscricoes-video", label: "Subscrições de vídeo", icon: ClipboardList, group: "Oferta" },
  { key: "utilizadores", label: "Utilizadores", icon: UsersRound, group: "Pessoas" },
  { key: "inscricoes", label: "Inscrições", icon: ClipboardList, group: "Pessoas" },
  { key: "pagamentos", label: "Pagamentos", icon: CircleDollarSign, group: "Comercial" },
  { key: "lojas", label: "Lojas parceiras", icon: ShoppingBag, group: "Comercial" },
  { key: "produtos", label: "Produtos", icon: Package, group: "Comercial" },
  { key: "pedidos", label: "Pedidos do Mercado", icon: ReceiptText, group: "Comercial" },
  { key: "contactos", label: "Contactos", icon: FileText, group: "Suporte" },
  { key: "perguntas", label: "Perguntas frequentes", icon: FileText, group: "Suporte" },
  { key: "bolsas", label: "Bolsas atribuídas", icon: GraduationCap, group: "Conteúdo" },
  { key: "candidaturas-bolsas", label: "Candidaturas a bolsas", icon: ClipboardList, group: "Conteúdo" },
  { key: "estagios", label: "Estágios", icon: Activity, group: "Conteúdo" },
  { key: "candidaturas-estagios", label: "Candidaturas a estágios", icon: ClipboardList, group: "Conteúdo" },
  { key: "escolas", label: "Escolas", icon: Building2, group: "Conteúdo" },
  { key: "biblioteca", label: "Biblioteca", icon: FileText, group: "Conteúdo" },
  { key: "noticias", label: "Notícias", icon: FileText, group: "Conteúdo" },
  { key: "configuracoes", label: "Configurações", icon: Settings2, group: "Plataforma" },
  { key: "auditoria", label: "Auditoria", icon: ShieldCheck, group: "Plataforma" },
];

const groupedSections = SECTIONS.reduce((groups, item) => ({ ...groups, [item.group]: [...(groups[item.group] || []), item] }), {});

export default function AdminOperationsPage({ onNavigate, theme, onThemeChange, initialSection }) {
  const selected = SECTIONS.some((item) => item.key === initialSection) ? initialSection : "centros";
  const [section, setSection] = useState(selected);
  const [search, setSearch] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");
  const [detail, setDetail] = useState(null);
  const [form, setForm] = useState({});

  const load = useCallback(async (nextSection = section, term = search) => {
    setError("");
    try {
      const response = await fetch(`/backend/api/react/administracao/operacoes/${nextSection}/?pesquisa=${encodeURIComponent(term)}`, { credentials: "include", cache: "no-store" });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw Object.assign(new Error(payload.detail || "Não foi possível carregar esta operação."), { status: response.status });
      if (nextSection === "planos-video") payload.items = [{ id: "__novo_plano__", title: "Criar novo plano mensal", subtitle: "Defina preço, moeda, duração e disponibilidade", status: "NOVO", status_label: "Nova configuração", details: ["Abrir formulário"], readonly: true }, ...payload.items];
      setData(payload); return true;
    } catch (reason) {
      setError(reason.message || "Não foi possível carregar esta operação.");
      setData(null); return false;
    }
  }, [search, section]);

  useEffect(() => { setSearch(""); setData(null); setDetail(null); load(section, ""); }, [section, load]);
  const { refreshNow, lastUpdated, syncing } = useAdminAutoRefresh(() => load(), { interval: 15000 });

  const changeSection = (key) => { setSection(key); onNavigate(`/admin/operacoes?secao=${key}`); };
  const update = async (item, field, value) => {
    setBusy(`${item.id}:${field}`);
    setError("");
    try {
      await authRequest(`/api/react/administracao/operacoes/${section}/`, { id: item.id, field, value });
      await refreshNow();
    } catch (reason) {
      setError(reason.message || "Não foi possível guardar a alteração.");
    } finally {
      setBusy("");
    }
  };

  const openDetail = async (item) => { if (item.id === "__novo_plano__") { openCreate(); return; } setError(""); try { const response = await fetch(`/backend/api/react/administracao/operacoes/${section}/${item.id}/`, { credentials: "include", cache: "no-store" }); const payload = await response.json().catch(() => ({})); if (!response.ok) throw new Error(payload.detail || "Não foi possível abrir o detalhe."); setDetail(payload); setForm(Object.fromEntries(payload.fields.map((field) => [field.field, field.value ?? ""]))); } catch (reason) { setError(reason.message || "Não foi possível abrir o detalhe."); } };
  const openCreate = () => { const fields = [{ field: "nome", label: "Nome do plano", control: "text", value: "" }, { field: "descricao", label: "Descrição", control: "textarea", value: "" }, { field: "preco", label: "Preço mensal", control: "decimal", value: "" }, { field: "moeda", label: "Moeda", control: "text", value: "AOA" }, { field: "periodo_dias", label: "Duração em dias", control: "number", value: 30 }, { field: "ordem", label: "Ordem de apresentação", control: "number", value: 0 }, { field: "ativo", label: "Disponível para novas subscrições", control: "boolean", value: true }, { field: "destaque", label: "Plano em destaque", control: "boolean", value: false }]; setDetail({ creating: true, title: "Novo plano de vídeo", summary: { status: "NOVO", status_label: "Em configuração", details: ["O plano ficará disponível após guardar."] }, fields }); setForm(Object.fromEntries(fields.map((field) => [field.field, field.value]))); };
  const saveDetail = async () => { if (!detail) return; setBusy("detail"); setError(""); try { if (detail.creating) { await authRequest(`/api/react/administracao/operacoes/${section}/`, { create: true, values: form }); await refreshNow(); setDetail(null); return; } for (const field of detail.fields) { const next = form[field.field]; if (String(next) === String(field.value ?? "")) continue; await authRequest(`/api/react/administracao/operacoes/${section}/`, { id: detail.id, field: field.field, value: field.control === "boolean" ? Boolean(next) : next }); } await refreshNow(); await openDetail({ id: detail.id }); } catch (reason) { setError(reason.message || "Não foi possível guardar as alterações."); } finally { setBusy(""); } };
  const activeNavigation = useMemo(() => SECTIONS.find((item) => item.key === section), [section]);
  if (error && !data) return <AdminAccessPage message={error} onAuthenticated={() => load(section, "")} />;

  return <main className="admin-console admin-overview admin-operations"><aside className="admin-sidebar"><div className="admin-brand"><span><ShieldCheck size={20}/></span><div><strong>Edukangola</strong><small>Administração</small></div></div><button className="admin-back" onClick={() => onNavigate("/admin")}><ArrowLeft size={16}/>Visão geral</button><div className="admin-operations-nav">{Object.entries(groupedSections).map(([group, entries]) => <div key={group}><p>{group}</p>{entries.map(({ key, label, icon: Icon }) => <button className={key === section ? "active" : ""} onClick={() => changeSection(key)} key={key}><Icon size={16}/>{label}</button>)}</div>)}</div><button className="admin-theme" onClick={onThemeChange}>{theme === "light" ? <Moon size={17}/> : <Sun size={17}/>} {theme === "light" ? "Modo escuro" : "Modo claro"}</button></aside><section className="admin-workspace"><header className="admin-top admin-operations-top"><div><span>Operação administrativa</span><h1>{data?.title || activeNavigation?.label}</h1><p>{data?.description || "A carregar controlos administrativos…"}</p></div><button onClick={refreshNow}><RefreshCw size={17}/>{syncing ? "A actualizar…" : "Actualizar"}</button></header>{error && <p className="admin-error">{error}</p>}<section className="admin-operations-toolbar"><label><span>Pesquisar</span><input value={search} onChange={(event) => setSearch(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") load(); }} placeholder="Nome, referência ou e-mail" /></label><button onClick={() => load()}>Procurar</button><small>{data ? `${data.total} registo(s) encontrados · ${lastUpdated ? `Actualizado às ${lastUpdated.toLocaleTimeString("pt-AO", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}` : "a sincronizar"}` : "A carregar registos…"}</small></section>{data ? <section className="admin-operation-list">{data.items.length ? data.items.map((item) => <article key={item.id} className="admin-operation-row"><button className="admin-operation-open" onClick={() => openDetail(item)}><div className="admin-operation-main"><div className="admin-operation-heading"><div><h2>{item.title}</h2><p>{item.subtitle}</p></div><span className={`admin-status admin-status-${String(item.status || "").toLowerCase()}`}>{item.status_label}</span></div><div className="admin-operation-details">{(item.details || []).map((detail, index) => <span key={`${item.id}-${index}`}>{detail}</span>)}</div></div><span>Ver detalhe</span></button>{!item.readonly && <div className="admin-operation-actions">{(item.switches || []).map((control) => <button key={control.field} className={control.value ? "admin-operation-switch on" : "admin-operation-switch"} disabled={busy === `${item.id}:${control.field}`} onClick={() => update(item, control.field, !control.value)}><i />{busy === `${item.id}:${control.field}` ? "A guardar…" : control.label}</button>)}{item.select && <label className="admin-operation-select"><span>{item.select.label}</span><select value={item.select.value} disabled={busy === `${item.id}:${item.select.field}`} onChange={(event) => update(item, item.select.field, event.target.value)}>{item.select.options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>}</div>}</article>) : <div className="admin-operation-empty"><ShieldCheck size={28}/><h2>Sem registos nesta secção</h2><p>Quando existirem dados operacionais, eles aparecerão aqui com as acções permitidas.</p></div>}</section> : <div className="admin-operation-empty"><BarChart3 size={28}/><h2>A preparar a operação</h2><p>A consultar dados reais da plataforma.</p></div>}{detail && <aside className="admin-detail-drawer" role="dialog" aria-modal="true"><header><div><span>Detalhe administrativo</span><h2>{detail.title}</h2></div><button onClick={() => setDetail(null)} aria-label="Fechar detalhe"><X size={19}/></button></header><div className="admin-detail-summary"><span className={`admin-status admin-status-${String(detail.summary.status || "").toLowerCase()}`}>{detail.summary.status_label}</span>{(detail.summary.details || []).map((value, index) => <small key={index}>{value}</small>)}</div><div className="admin-detail-form">{detail.fields.map((field) => <label key={field.field}><span>{field.label}</span>{field.control === "textarea" ? <textarea value={form[field.field] ?? ""} onChange={(event) => setForm({ ...form, [field.field]: event.target.value })} /> : field.control === "select" ? <select value={form[field.field] ?? ""} onChange={(event) => setForm({ ...form, [field.field]: event.target.value })}>{field.options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select> : field.control === "boolean" ? <button type="button" className={form[field.field] ? "admin-detail-toggle on" : "admin-detail-toggle"} onClick={() => setForm({ ...form, [field.field]: !form[field.field] })}>{form[field.field] ? "Activo" : "Inactivo"}</button> : <input type={field.control === "decimal" ? "number" : field.control} value={form[field.field] ?? ""} onChange={(event) => setForm({ ...form, [field.field]: event.target.value })} />}</label>)}</div><footer><button className="admin-detail-cancel" onClick={() => setDetail(null)}>Cancelar</button><button className="admin-detail-save" disabled={busy === "detail"} onClick={saveDetail}>{busy === "detail" ? "A guardar…" : "Guardar alterações"}</button></footer></aside>}</section></main>;
}
