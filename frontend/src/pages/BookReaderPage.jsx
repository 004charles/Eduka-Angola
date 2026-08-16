import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, Bookmark, ChevronLeft, ChevronRight, List, X } from "lucide-react";
import { authRequest } from "../lib/auth-api";
import "./book-reader-page.css";

export default function BookReaderPage({ slug, student, onNavigate, onAnnounce }) {
  const [book, setBook] = useState(null);
  const [chapter, setChapter] = useState(0);
  const [openContents, setOpenContents] = useState(false);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    if (!student) { onNavigate("/entrar"); return; }
    let active = true;
    fetch(`/backend/api/react/biblioteca/${encodeURIComponent(slug)}/ler/`, { credentials: "same-origin", headers: { Accept: "application/json" } })
      .then((response) => { if (!response.ok) throw new Error(); return response.json(); })
      .then((data) => { if (active) { setBook(data.livro); setChapter(Math.min(Math.floor((data.livro.biblioteca_pessoal?.progresso_leitura || 0) / 25), 3)); setStatus("ready"); } })
      .catch(() => active && setStatus("error"));
    return () => { active = false; };
  }, [slug, student, onNavigate]);

  const sections = useMemo(() => {
    const chunks = (book?.conteudo_leitura || "").split(/\n\n(?=#|## )/).filter(Boolean);
    return chunks.length > 1 && /^#\s+[^\n]+\s*$/.test(chunks[0]) ? chunks.slice(1) : chunks;
  }, [book]);
  const selectChapter = async (index) => { setChapter(index); setOpenContents(false); const progress = Math.round(((index + 1) / Math.max(sections.length, 1)) * 100); try { await authRequest(`/api/react/biblioteca/${encodeURIComponent(slug)}/progresso/`, { progresso: progress }); } catch { onAnnounce("O seu ponto de leitura será actualizado quando a ligação estiver disponível."); } };

  if (status === "loading") return <main className="reader-shell"><p>A abrir a leitura…</p></main>;
  if (status === "error" || !book) return <main className="reader-shell"><p>Não foi possível abrir esta leitura.</p><button onClick={() => onNavigate(`/biblioteca/${slug}`)}>Voltar ao livro</button></main>;
  const content = sections[chapter] || book.conteudo_leitura;
  const renderLine = (line, index) => line.startsWith("# ") ? <h1 key={index}>{line.replace(/^# /, "")}</h1> : line.startsWith("## ") ? <h2 key={index}>{line.replace(/^## /, "")}</h2> : line.trim() ? <p key={index}>{line}</p> : null;
  return <main className="reader-shell">
    <header className="reader-topbar"><button type="button" onClick={() => onNavigate(`/biblioteca/${slug}`)}><ArrowLeft size={18} /> Voltar</button><div><small>{book.autor?.nome}</small><strong>{book.titulo}</strong></div><button type="button" onClick={() => setOpenContents(true)} aria-label="Abrir índice"><List size={19} /></button></header>
    <div className="reader-progress"><span style={{ width: `${Math.round(((chapter + 1) / Math.max(sections.length, 1)) * 100)}%` }} /></div>
    <article className="reader-page">{content.split("\n").map(renderLine)}</article>
    <nav className="reader-navigation"><button type="button" disabled={chapter === 0} onClick={() => selectChapter(chapter - 1)}><ChevronLeft size={18} /> Anterior</button><span>{chapter + 1} de {sections.length}</span><button type="button" disabled={chapter >= sections.length - 1} onClick={() => selectChapter(chapter + 1)}>Seguinte <ChevronRight size={18} /></button></nav>
    {openContents && <aside className="reader-contents"><div><h2>Índice</h2><button type="button" onClick={() => setOpenContents(false)}><X size={19} /></button></div>{sections.map((item, index) => <button type="button" className={chapter === index ? "active" : ""} onClick={() => selectChapter(index)} key={index}>{item.match(/^#\s+(.+)/m)?.[1] || item.match(/^##\s+(.+)/m)?.[1] || `Parte ${index + 1}`}</button>)}<p><Bookmark size={15} /> O seu progresso é guardado na Biblioteca.</p></aside>}
  </main>;
}
