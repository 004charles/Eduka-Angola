import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, Bookmark, ChevronLeft, ChevronRight, Gauge, List, Pause, RotateCcw, Square, Volume2, X } from "lucide-react";
import { authRequest } from "../lib/auth-api";
import "./book-reader-page.css";

function getSpeechLanguage(language) {
  if (language === "en") return "en-US";
  if (language === "fr") return "fr-FR";
  if (language === "zh") return "zh-CN";
  return "pt-PT";
}

export default function BookReaderPage({ slug, student, onNavigate, onAnnounce }) {
  const [book, setBook] = useState(null);
  const [chapter, setChapter] = useState(0);
  const [resumePage, setResumePage] = useState(0);
  const [resumePrompt, setResumePrompt] = useState(false);
  const [openContents, setOpenContents] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [speechRate, setSpeechRate] = useState(1);
  const [speechAvailable, setSpeechAvailable] = useState(false);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    setSpeechAvailable(typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window);
    if (!student) { onNavigate("/entrar"); return undefined; }
    let active = true;
    fetch(`/backend/api/react/biblioteca/${encodeURIComponent(slug)}/ler/`, { credentials: "same-origin", headers: { Accept: "application/json" } })
      .then((response) => { if (!response.ok) throw new Error(); return response.json(); })
      .then((data) => {
        if (!active) return;
        const savedPage = data.livro.biblioteca_pessoal?.pagina_leitura || 0;
        setBook(data.livro);
        setResumePage(savedPage);
        setChapter(0);
        setResumePrompt(savedPage > 0);
        setStatus("ready");
      })
      .catch(() => active && setStatus("error"));
    return () => { active = false; window.speechSynthesis?.cancel(); };
  }, [slug, student, onNavigate]);

  const sections = useMemo(() => {
    const chunks = (book?.conteudo_leitura || "").split(/\n\n(?=#|## )/).filter(Boolean);
    return chunks.length > 1 && /^#\s+[^\n]+\s*$/.test(chunks[0]) ? chunks.slice(1) : chunks;
  }, [book]);

  const saveProgress = async (index) => {
    const progress = Math.round(((index + 1) / Math.max(sections.length, 1)) * 100);
    try {
      await authRequest(`/api/react/biblioteca/${encodeURIComponent(slug)}/progresso/`, { progresso: progress, pagina: index });
    } catch {
      onAnnounce("O ponto de leitura será sincronizado quando a ligação estiver disponível.");
    }
  };

  const selectChapter = async (index) => {
    stopSpeech();
    setChapter(index);
    setOpenContents(false);
    setResumePrompt(false);
    await saveProgress(index);
  };

  const continueReading = () => {
    const target = Math.min(resumePage, Math.max(sections.length - 1, 0));
    setChapter(target);
    setResumePrompt(false);
  };

  const restartReading = async () => {
    setChapter(0);
    setResumePrompt(false);
    await saveProgress(0);
  };

  const speakCurrent = () => {
    if (!speechAvailable) {
      onAnnounce("A leitura em voz alta não está disponível neste navegador.");
      return;
    }
    window.speechSynthesis.cancel();
    const text = (sections[chapter] || book?.conteudo_leitura || "").replace(/^#+\s*/gm, "").replace(/\n+/g, ". ");
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = getSpeechLanguage(book?.idioma);
    utterance.rate = speechRate;
    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeech = () => {
    if (typeof window !== "undefined") window.speechSynthesis?.cancel();
    setSpeaking(false);
  };

  if (status === "loading") return <main className="reader-shell"><p>A abrir a leitura…</p></main>;
  if (status === "error" || !book) return <main className="reader-shell"><p>Não foi possível abrir esta leitura.</p><button onClick={() => onNavigate(`/biblioteca/${slug}`)}>Voltar ao livro</button></main>;

  const content = sections[chapter] || book.conteudo_leitura;
  const renderLine = (line, index) => line.startsWith("# ") ? <h1 key={index}>{line.replace(/^# /, "")}</h1> : line.startsWith("## ") ? <h2 key={index}>{line.replace(/^## /, "")}</h2> : line.trim() ? <p key={index}>{line}</p> : null;
  return <main className="reader-shell">
    <header className="reader-topbar"><button type="button" onClick={() => { stopSpeech(); onNavigate(`/biblioteca/${slug}`); }}><ArrowLeft size={18} /> Voltar</button><div><small>{book.autor?.nome}</small><strong>{book.titulo}</strong></div><button type="button" onClick={() => setOpenContents(true)} aria-label="Abrir índice"><List size={19} /></button></header>
    <div className="reader-progress"><span style={{ width: `${Math.round(((chapter + 1) / Math.max(sections.length, 1)) * 100)}%` }} /></div>
    <section className="reader-tools" aria-label="Controlos de leitura em voz alta"><div className="reader-voice-label"><Volume2 size={17} /><span>Ouvir esta página</span></div><button type="button" className={speaking ? "active" : ""} onClick={speaking ? stopSpeech : speakCurrent} disabled={!speechAvailable}>{speaking ? <><Pause size={16} /> Pausar</> : <><Volume2 size={16} /> Ler em voz alta</>}</button>{speaking && <button type="button" onClick={stopSpeech}><Square size={14} /> Parar</button>}<label><Gauge size={15} /> <span>Velocidade</span><select value={speechRate} onChange={(event) => setSpeechRate(Number(event.target.value))}><option value="0.8">0,8×</option><option value="1">1×</option><option value="1.2">1,2×</option><option value="1.5">1,5×</option></select></label></section>
    <article className="reader-page">{content.split("\n").map(renderLine)}</article>
    <nav className="reader-navigation"><button type="button" disabled={chapter === 0} onClick={() => selectChapter(chapter - 1)}><ChevronLeft size={18} /> Anterior</button><span>{chapter + 1} de {sections.length}</span><button type="button" disabled={chapter >= sections.length - 1} onClick={() => selectChapter(chapter + 1)}>Seguinte <ChevronRight size={18} /></button></nav>
    {resumePrompt && <div className="reader-resume-backdrop"><section className="reader-resume-dialog" role="dialog" aria-modal="true" aria-labelledby="resume-title"><div className="reader-resume-icon"><RotateCcw size={21} /></div><h2 id="resume-title">Quer continuar a leitura?</h2><p>Encontrámos o seu ponto guardado. Pode continuar na página {resumePage + 1} ou começar o livro novamente.</p><div className="reader-resume-actions"><button type="button" className="reader-resume-primary" onClick={continueReading}>Continuar onde parei</button><button type="button" className="reader-resume-secondary" onClick={restartReading}>Começar novamente</button></div></section></div>}
    {openContents && <aside className="reader-contents"><div><h2>Índice</h2><button type="button" onClick={() => setOpenContents(false)}><X size={19} /></button></div>{sections.map((item, index) => <button type="button" className={chapter === index ? "active" : ""} onClick={() => selectChapter(index)} key={index}>{item.match(/^#\s+(.+)/m)?.[1] || item.match(/^##\s+(.+)/m)?.[1] || `Parte ${index + 1}`}</button>)}<p><Bookmark size={15} /> O seu progresso é guardado na Biblioteca.</p></aside>}
  </main>;
}
