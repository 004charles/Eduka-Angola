import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ArrowLeft, Bookmark, ChevronLeft, ChevronRight, Gauge, List, LoaderCircle, Pause, Play, RotateCcw, Square, Volume2, X } from "lucide-react";
import { authBlobRequest, authRequest } from "../lib/auth-api";
import "./book-reader-page.css";

export default function BookReaderPage({ slug, student, onNavigate, onAnnounce }) {
  const [book, setBook] = useState(null);
  const [chapter, setChapter] = useState(0);
  const [resumePage, setResumePage] = useState(0);
  const [resumePrompt, setResumePrompt] = useState(false);
  const [openContents, setOpenContents] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [speechPaused, setSpeechPaused] = useState(false);
  const [speechRate, setSpeechRate] = useState(0.9);
  const [speechLoading, setSpeechLoading] = useState(false);
  const [status, setStatus] = useState("loading");
  const speechRunRef = useRef(0);
  const audioRef = useRef(null);
  const audioUrlRef = useRef("");

  const stopSpeech = useCallback(() => {
    speechRunRef.current += 1;
    if (audioRef.current) {
      audioRef.current.onplay = null;
      audioRef.current.onpause = null;
      audioRef.current.onended = null;
      audioRef.current.onerror = null;
      audioRef.current.pause();
      audioRef.current.src = "";
      audioRef.current = null;
    }
    if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);
    audioUrlRef.current = "";
    setSpeaking(false);
    setSpeechPaused(false);
    setSpeechLoading(false);
  }, []);

  useEffect(() => {
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
    return () => { active = false; stopSpeech(); };
  }, [slug, student, onNavigate, stopSpeech]);

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

  const requestNarration = async (preview = false) => {
    if (speechLoading) return;
    stopSpeech();
    const currentRun = ++speechRunRef.current;
    setSpeechLoading(true);
    try {
      const audioBlob = await authBlobRequest(`/api/react/biblioteca/${encodeURIComponent(slug)}/voz/`, { capitulo: chapter, velocidade: speechRate, amostra: preview });
      if (currentRun !== speechRunRef.current) return;
      const url = URL.createObjectURL(audioBlob);
      const audio = new Audio(url);
      audioRef.current = audio;
      audioUrlRef.current = url;
      audio.onplay = () => currentRun === speechRunRef.current && (setSpeaking(true), setSpeechPaused(false));
      audio.onpause = () => currentRun === speechRunRef.current && !audio.ended && setSpeechPaused(true);
      audio.onended = () => { if (currentRun === speechRunRef.current) stopSpeech(); };
      audio.onerror = () => { if (currentRun === speechRunRef.current) { stopSpeech(); onAnnounce("Não foi possível reproduzir a narração deste trecho. Tente novamente."); } };
      await audio.play();
    } catch (error) {
      if (currentRun === speechRunRef.current) onAnnounce(error.message || "Não foi possível preparar a narração agora.");
    } finally {
      if (currentRun === speechRunRef.current) setSpeechLoading(false);
    }
  };

  const pauseOrResumeSpeech = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (speechPaused) audio.play().catch(() => onAnnounce("Não foi possível retomar a narração."));
    else audio.pause();
  };

  if (status === "loading") return <main className="reader-shell"><p>A abrir a leitura…</p></main>;
  if (status === "error" || !book) return <main className="reader-shell"><p>Não foi possível abrir esta leitura.</p><button onClick={() => onNavigate(`/biblioteca/${slug}`)}>Voltar ao livro</button></main>;

  const content = sections[chapter] || book.conteudo_leitura;
  const renderLine = (line, index) => line.startsWith("# ") ? <h1 key={index}>{line.replace(/^# /, "")}</h1> : line.startsWith("## ") ? <h2 key={index}>{line.replace(/^## /, "")}</h2> : line.trim() ? <p key={index}>{line}</p> : null;
  return <main className="reader-shell">
    <header className="reader-topbar"><button type="button" onClick={() => { stopSpeech(); onNavigate(`/biblioteca/${slug}`); }}><ArrowLeft size={18} /> Voltar</button><div><small>{book.autor?.nome}</small><strong>{book.titulo}</strong></div><button type="button" onClick={() => setOpenContents(true)} aria-label="Abrir índice"><List size={19} /></button></header>
    <div className="reader-progress"><span style={{ width: `${Math.round(((chapter + 1) / Math.max(sections.length, 1)) * 100)}%` }} /></div>
    <section className="reader-tools" aria-label="Controlos de leitura em voz alta">
      <div className="reader-voice-label"><Volume2 size={17} /><span>Narração natural</span></div>
      <button type="button" className={speaking ? "active" : ""} onClick={speaking ? pauseOrResumeSpeech : () => requestNarration(false)} disabled={speechLoading}>{speechLoading ? <><LoaderCircle size={16} className="reader-audio-loader" /> A preparar voz…</> : speaking ? speechPaused ? <><Play size={16} /> Retomar</> : <><Pause size={16} /> Pausar</> : <><Volume2 size={16} /> Ler em voz alta</>}</button>
      {speaking && <button type="button" onClick={stopSpeech}><Square size={14} /> Parar</button>}
      <button type="button" className="reader-voice-preview" onClick={() => requestNarration(true)} disabled={speechLoading}><Volume2 size={14} /> Ouvir amostra</button>
      <label><Gauge size={15} /> <span>Velocidade</span><select value={speechRate} onChange={(event) => { stopSpeech(); setSpeechRate(Number(event.target.value)); }} disabled={speechLoading}><option value="0.8">0,8×</option><option value="0.9">0,9×</option><option value="1">1×</option><option value="1.15">1,15×</option><option value="1.3">1,3×</option></select></label>
      <p className="reader-voice-note">Voz portuguesa natural, protegida pela sua sessão de leitura.</p>
    </section>
    <article className="reader-page">{content.split("\n").map(renderLine)}</article>
    <nav className="reader-navigation"><button type="button" disabled={chapter === 0} onClick={() => selectChapter(chapter - 1)}><ChevronLeft size={18} /> Anterior</button><span>{chapter + 1} de {sections.length}</span><button type="button" disabled={chapter >= sections.length - 1} onClick={() => selectChapter(chapter + 1)}>Seguinte <ChevronRight size={18} /></button></nav>
    {resumePrompt && <div className="reader-resume-backdrop"><section className="reader-resume-dialog" role="dialog" aria-modal="true" aria-labelledby="resume-title"><div className="reader-resume-icon"><RotateCcw size={21} /></div><h2 id="resume-title">Quer continuar a leitura?</h2><p>Encontrámos o seu ponto guardado. Pode continuar na página {resumePage + 1} ou começar o livro novamente.</p><div className="reader-resume-actions"><button type="button" className="reader-resume-primary" onClick={continueReading}>Continuar onde parei</button><button type="button" className="reader-resume-secondary" onClick={restartReading}>Começar novamente</button></div></section></div>}
    {openContents && <aside className="reader-contents"><div><h2>Índice</h2><button type="button" onClick={() => setOpenContents(false)}><X size={19} /></button></div>{sections.map((item, index) => <button type="button" className={chapter === index ? "active" : ""} onClick={() => selectChapter(index)} key={index}>{item.match(/^#\s+(.+)/m)?.[1] || item.match(/^##\s+(.+)/m)?.[1] || `Parte ${index + 1}`}</button>)}<p><Bookmark size={15} /> O seu progresso é guardado na Biblioteca.</p></aside>}
  </main>;
}
