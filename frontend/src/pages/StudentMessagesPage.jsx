import { ArrowLeft, Bell, CircleAlert, MessageCircle, Send } from "lucide-react";
import { useEffect, useState } from "react";
import { backendUrl } from "../lib/backend-url";
import { authRequest } from "../lib/auth-api";
import "./student-messages-page.css";
import "./student-messages-spacing.css";

export default function StudentMessagesPage({ centerId, conversationId, onNavigate }) {
  const [state, setState] = useState({ loading: true, error: "", conversations: [], selected: conversationId, detail: null, unread: 0 });
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);

  const loadList = async (preferredId = null) => {
    const response = await fetch(backendUrl("/auth/api/react/aluno/conversas/"), { credentials: "include", cache: "no-store" });
    const data = await response.json().catch(() => ({}));
    if (response.status === 401) throw Object.assign(new Error("login"), { code: "login" });
    if (!response.ok || !data.ok) throw new Error(data.message || "Não foi possível carregar as suas mensagens.");
    setState((current) => ({
      ...current,
      loading: false,
      error: "",
      conversations: data.conversas || [],
      unread: data.total_nao_lidas || 0,
      selected: preferredId && data.conversas?.some((item) => item.id === preferredId)
        ? preferredId
        : (current.selected && data.conversas?.some((item) => item.id === current.selected)
          ? current.selected
          : (data.conversas?.[0]?.id || null)),
    }));
    return data;
  };

  const loadDetail = async (id) => {
    if (!id) return;
    const response = await fetch(backendUrl(`/auth/api/react/aluno/conversas/${id}/`), { credentials: "include", cache: "no-store" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || !data.ok) throw new Error(data.message || "Não foi possível abrir a conversa.");
    setState((current) => ({ ...current, detail: data, unread: 0 }));
    window.dispatchEvent(new CustomEvent("eduka:notifications-changed"));
  };

  const handleConversationSelect = (id) => {
    setState((current) => {
      if (current.selected === id && current.detail) return current;
      return { ...current, selected: id, detail: null };
    });
    loadDetail(id).catch((error) => setState((current) => ({ ...current, error: error.message })));
  };

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        let preferredId = conversationId;
        if (centerId) {
          const data = await authRequest("/auth/api/react/aluno/conversas/iniciar/", { centro_id: centerId });
          preferredId = data.conversa.id;
        }
        await loadList(preferredId);
      } catch (error) {
        if (active) setState((current) => ({ ...current, loading: false, error: error.code === "login" || error.message === "login" ? "login" : error.message }));
      }
    })();
    return () => { active = false; };
  }, [centerId, conversationId]);

  useEffect(() => {
    if (!state.selected) return undefined;
    loadDetail(state.selected).catch((error) => setState((current) => ({ ...current, error: error.message })));
    const timer = window.setInterval(() => loadDetail(state.selected).catch(() => {}), 15000);
    return () => window.clearInterval(timer);
  }, [state.selected]);

  const send = async (event) => {
    event.preventDefault();
    if (!state.selected || !text.trim()) return;
    setSending(true);
    try {
      await authRequest(`/auth/api/react/aluno/conversas/${state.selected}/mensagens/`, { mensagem: text });
      setText("");
      await Promise.all([loadDetail(state.selected), loadList()]);
    } catch (error) {
      setState((current) => ({ ...current, error: error.message }));
    } finally {
      setSending(false);
    }
  };

  if (state.loading) return <main className="student-messages-page"><div className="page-width student-messages-state">A preparar as suas mensagens.</div></main>;
  if (state.error === "login") return <main className="student-messages-page"><section className="page-width student-messages-gate"><MessageCircle size={25} /><h1>Entre para falar com um centro.</h1><p>As conversas ficam associadas à sua conta, para poder acompanhar cada resposta.</p><button onClick={() => onNavigate(`/entrar?next=/aluno/mensagens${centerId ? `?centro=${centerId}` : ""}`)}>Entrar</button></section></main>;
  if (state.error && !state.detail && !state.conversations.length) return <main className="student-messages-page"><section className="page-width student-messages-gate"><CircleAlert size={25} /><h1>Não foi possível abrir as mensagens.</h1><p>{state.error}</p><button onClick={() => window.location.reload()}>Tentar novamente</button></section></main>;

  return <main className="student-messages-page">
    <section className="student-messages-hero">
      <div className="page-width">
        <button className="student-messages-back" onClick={() => onNavigate("/aluno")}><ArrowLeft size={16} /> Área do aluno</button>
        <span><Bell size={15} /> Atendimento do centro</span>
        <h1>Mensagens</h1>
        <p>Fale directamente com os centros onde encontrou a formação certa para si.</p>
      </div>
    </section>
    <section className="page-width student-messages-shell">
      <aside className="student-message-list">
        <header><div><strong>Conversas</strong><small>{state.conversations.length} activas</small></div>{state.unread > 0 && <span>{state.unread} novas</span>}</header>
        {state.conversations.length ? state.conversations.map((item) => <button key={item.id} className={state.selected === item.id ? "active" : ""} onClick={() => handleConversationSelect(item.id)}><span>{item.centro.charAt(0)}</span><div><strong>{item.centro}</strong><small>{item.ultima_mensagem || "Inicie a conversa com este centro."}</small></div>{item.nao_lidas > 0 && <b>{item.nao_lidas}</b>}</button>) : <div className="student-message-empty"><MessageCircle size={22} /><p>Ainda não iniciou nenhuma conversa.</p><button onClick={() => onNavigate("/centros")}>Explorar centros</button></div>}
      </aside>
      <section className="student-message-thread">
        {state.detail ? <>
          <header><span>{state.detail.conversa.centro.charAt(0)}</span><div><strong>{state.detail.conversa.centro}</strong><small>Centro de formação · respostas actualizadas automaticamente</small></div></header>
          <div className="student-message-history">
            {state.detail.mensagens.length ? state.detail.mensagens.map((message) => <article key={message.id} className={message.autor === "ALUNO" ? "from-student" : "from-center"}><p>{message.texto}</p><small>{message.autor === "ALUNO" ? "Você · " : "Centro · "}{new Date(message.data).toLocaleString("pt-AO")}</small></article>) : <div className="student-thread-empty"><MessageCircle size={26} /><h2>Envie a primeira mensagem.</h2><p>Explique a sua dúvida ao centro e receberá a resposta aqui.</p></div>}
          </div>
          <form onSubmit={send}><input value={text} onChange={(event) => setText(event.target.value)} placeholder="Escreva uma mensagem para o centro…" maxLength="4000" /><button disabled={sending || !text.trim()}><Send size={16} />{sending ? "A enviar…" : "Enviar"}</button></form>
        </> : <div className="student-thread-empty"><MessageCircle size={26} /><h2>Escolha uma conversa.</h2><p>Abra uma conversa existente ou contacte um centro no respectivo perfil.</p></div>}
      </section>
    </section>
    {state.error && <p className="page-width student-message-feedback">{state.error}</p>}
  </main>;
}
