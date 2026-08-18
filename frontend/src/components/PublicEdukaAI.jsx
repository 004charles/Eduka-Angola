import { useEffect, useRef, useState } from "react";
import { BotMessageSquare, ChevronRight, LoaderCircle, Send, ShieldCheck, Sparkles, X } from "lucide-react";
import { authRequest } from "../lib/auth-api";
import "./public-eduka-ai.css";

const STARTERS = [
  "Que curso pode combinar comigo?",
  "Como faço uma inscrição?",
  "Onde encontro cursos em vídeo?",
];

export default function PublicEdukaAI({ onNavigate, path }) {
  const [isOpen, setIsOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState([{ role: "assistant", content: "Olá, sou a Eduka AI. Posso orientar a sua descoberta de cursos, centros, biblioteca, inscrições e eventos." }]);
  const inputRef = useRef(null);
  const historyRef = useRef(null);
  const hiddenRoutes = ["/entrar", "/criar-conta", "/verificar-email", "/recuperar-palavra-passe", "/redefinir-palavra-passe"];

  useEffect(() => {
    if (isOpen) window.setTimeout(() => inputRef.current?.focus(), 80);
  }, [isOpen]);
  useEffect(() => {
    if (historyRef.current) historyRef.current.scrollTop = historyRef.current.scrollHeight;
  }, [messages, isSending]);
  useEffect(() => {
    const closeOnEscape = (event) => { if (event.key === "Escape") setIsOpen(false); };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, []);

  if (hiddenRoutes.includes(path)) return null;

  const ask = async (question) => {
    const text = question.trim();
    if (!text || isSending) return;
    const priorHistory = messages.slice(-6).map((message) => ({ role: message.role, content: message.content }));
    setMessages((current) => [...current, { role: "user", content: text }]);
    setDraft("");
    setError("");
    setIsSending(true);
    try {
      const data = await authRequest("/api/public/eduka-ai/perguntar/", { question: text, history: priorHistory });
      setMessages((current) => [...current, { role: "assistant", content: data.answer, links: data.links || [] }]);
    } catch (reason) {
      setError(reason.message || "Não foi possível obter uma resposta da Eduka AI.");
    } finally {
      setIsSending(false);
    }
  };

  return <div className="public-eduka-ai">
    {isOpen && <section className="public-ai-panel" role="dialog" aria-modal="false" aria-label="Eduka AI">
      <header className="public-ai-header"><div><span><Sparkles size={14} /> Assistente da plataforma</span><strong>Eduka AI</strong></div><button type="button" onClick={() => setIsOpen(false)} aria-label="Fechar Eduka AI"><X size={19} /></button></header>
      <div className="public-ai-history" ref={historyRef} aria-live="polite">{messages.map((message, index) => <article className={`public-ai-message ${message.role}`} key={`${message.role}-${index}`}><div className="public-ai-message-icon">{message.role === "assistant" ? <BotMessageSquare size={15} /> : "Você"}</div><div><p>{message.content}</p>{message.links?.length > 0 && <div className="public-ai-links">{message.links.map((link) => <button type="button" key={link.path} onClick={() => { setIsOpen(false); onNavigate(link.path); }}>{link.label}<ChevronRight size={14} /></button>)}</div>}</div></article>)}{isSending && <article className="public-ai-message assistant"><div className="public-ai-message-icon"><BotMessageSquare size={15} /></div><p className="public-ai-thinking"><LoaderCircle size={15} /> A preparar uma resposta…</p></article>}</div>
      {messages.length === 1 && <div className="public-ai-starters"><small>Perguntas rápidas</small>{STARTERS.map((starter) => <button key={starter} type="button" disabled={isSending} onClick={() => ask(starter)}>{starter}<ChevronRight size={14} /></button>)}</div>}
      {error && <p className="public-ai-error" role="alert">{error}</p>}
      <form className="public-ai-form" onSubmit={(event) => { event.preventDefault(); ask(draft); }}><label className="sr-only" htmlFor="eduka-ai-question">Pergunte à Eduka AI</label><textarea ref={inputRef} id="eduka-ai-question" value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Pergunte sobre a Edukangola…" rows={2} maxLength={700} disabled={isSending} /><button type="submit" aria-label="Enviar pergunta" disabled={isSending || !draft.trim()}><Send size={17} /></button></form>
      <p className="public-ai-notice"><ShieldCheck size={13} /> Respostas de orientação. Confirme detalhes importantes na página do curso ou centro.</p>
    </section>}
    <button type="button" className="public-ai-launcher" onClick={() => setIsOpen((open) => !open)} aria-expanded={isOpen} aria-controls="eduka-ai-question"><BotMessageSquare size={21} /><span>Eduka AI</span>{!isOpen && <b>Pergunte-nos</b>}</button>
  </div>;
}
