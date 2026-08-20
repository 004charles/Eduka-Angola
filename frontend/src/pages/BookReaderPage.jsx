import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ArrowLeft, Bookmark, ChevronLeft, ChevronRight, Gauge, List, Pause, Play, RotateCcw, Square, Volume2, X } from "lucide-react";
import { authRequest } from "../lib/auth-api";
import "./book-reader-page.css";

function getSpeechLanguage(language) {
  if (language === "en") return "en-US";
  if (language === "fr") return "fr-FR";
  if (language === "zh") return "zh-CN";
  return "pt-PT";
}

function voiceId(voice) {
  return `${voice.voiceURI}::${voice.name}`;
}

function scoreVoice(voice, language) {
  const requested = language.toLowerCase();
  const voiceLanguage = String(voice.lang || "").toLowerCase();
  const name = String(voice.name || "").toLowerCase();
  const isExactLanguage = voiceLanguage === requested;
  const isSameFamily = voiceLanguage.split("-")[0] === requested.split("-")[0];
  const hasNaturalNarrationHint = /(natural|online|neural|microsoft|google|apple|siri|helena|raquel|joana|fernanda|in[eê]s|duarte)/.test(name);

  if (!isSameFamily) return -1;
  return (isExactLanguage ? 1000 : isSameFamily ? 700 : 0)
    + (hasNaturalNarrationHint ? 160 : 0)
    + (!voice.localService ? 45 : 0)
    + (voice.default ? 8 : 0);
}

function orderVoices(voices, language) {
  return [...voices]
    .filter((voice) => scoreVoice(voice, language) > 0)
    .sort((first, second) => scoreVoice(second, language) - scoreVoice(first, language) || first.name.localeCompare(second.name, "pt-PT"));
}

function splitSpeechText(value) {
  const text = String(value || "")
    .replace(/^#{1,6}\s*/gm, "")
    .replace(/[•·]/g, ". ")
    .replace(/\n+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (!text) return [];

  const sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [text];
  const chunks = [];
  let current = "";
  sentences.forEach((sentence) => {
    const cleanSentence = sentence.trim();
    if (!cleanSentence) return;
    if (current && `${current} ${cleanSentence}`.length > 260) {
      chunks.push(current);
      current = cleanSentence;
      return;
    }
    current = current ? `${current} ${cleanSentence}` : cleanSentence;
  });
  if (current) chunks.push(current);
  return chunks;
}

export default function BookReaderPage({ slug, student, onNavigate, onAnnounce }) {
  const [book, setBook] = useState(null);
  const [chapter, setChapter] = useState(0);
  const [resumePage, setResumePage] = useState(0);
  const [resumePrompt, setResumePrompt] = useState(false);
  const [openContents, setOpenContents] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [speechPaused, setSpeechPaused] = useState(false);
  const [speechRate, setSpeechRate] = useState(0.9);
  const [speechAvailable, setSpeechAvailable] = useState(false);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoiceId, setSelectedVoiceId] = useState("recommended");
  const [status, setStatus] = useState("loading");
  const speechChunksRef = useRef([]);
  const speechChunkIndexRef = useRef(0);
  const speechRunRef = useRef(0);
  const speakNextRef = useRef(null);

  const speechLanguage = getSpeechLanguage(book?.idioma);
  const recommendedVoices = useMemo(() => orderVoices(availableVoices, speechLanguage), [availableVoices, speechLanguage]);
  const selectedVoice = useMemo(() => {
    if (selectedVoiceId !== "recommended") return availableVoices.find((voice) => voiceId(voice) === selectedVoiceId) || recommendedVoices[0] || null;
    return recommendedVoices[0] || null;
  }, [availableVoices, recommendedVoices, selectedVoiceId]);
  const canSpeakBookLanguage = speechAvailable && Boolean(selectedVoice);

  const stopSpeech = useCallback(() => {
    speechRunRef.current += 1;
    speechChunksRef.current = [];
    speechChunkIndexRef.current = 0;
    if (typeof window !== "undefined") window.speechSynthesis?.cancel();
    setSpeaking(false);
    setSpeechPaused(false);
  }, []);

  const speakNext = useCallback(() => {
    if (!canSpeakBookLanguage || typeof window === "undefined") return;
    const currentRun = speechRunRef.current;
    const text = speechChunksRef.current[speechChunkIndexRef.current];
    if (!text) {
      setSpeaking(false);
      setSpeechPaused(false);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = selectedVoice?.lang || speechLanguage;
    utterance.rate = speechRate;
    utterance.pitch = 1;
    if (selectedVoice) utterance.voice = selectedVoice;
    utterance.onstart = () => {
      if (currentRun !== speechRunRef.current) return;
      setSpeaking(true);
      setSpeechPaused(false);
    };
    utterance.onpause = () => currentRun === speechRunRef.current && setSpeechPaused(true);
    utterance.onresume = () => currentRun === speechRunRef.current && setSpeechPaused(false);
    utterance.onend = () => {
      if (currentRun !== speechRunRef.current) return;
      speechChunkIndexRef.current += 1;
      speakNextRef.current?.();
    };
    utterance.onerror = (event) => {
      if (currentRun !== speechRunRef.current || event.error === "interrupted" || event.error === "canceled") return;
      setSpeaking(false);
      setSpeechPaused(false);
      onAnnounce("Não foi possível reproduzir esta voz. Escolha outra voz e tente novamente.");
    };
    window.speechSynthesis.speak(utterance);
  }, [canSpeakBookLanguage, onAnnounce, selectedVoice, speechLanguage, speechRate]);

  useEffect(() => {
    speakNextRef.current = speakNext;
  }, [speakNext]);

  useEffect(() => {
    const supported = typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
    setSpeechAvailable(supported);
    if (!supported) return undefined;

    const updateVoices = () => setAvailableVoices(window.speechSynthesis.getVoices());
    updateVoices();
    window.speechSynthesis.addEventListener?.("voiceschanged", updateVoices);
    return () => window.speechSynthesis.removeEventListener?.("voiceschanged", updateVoices);
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

  const speakText = (text) => {
    if (!speechAvailable) {
      onAnnounce("A leitura em voz alta não está disponível neste navegador.");
      return;
    }
    if (!selectedVoice) {
      onAnnounce("Não existe uma voz compatível com o idioma deste livro. Active uma voz em português nas definições do dispositivo e recarregue esta página.");
      return;
    }
    const chunks = splitSpeechText(text);
    if (!chunks.length) {
      onAnnounce("Não existe texto disponível para ouvir nesta página.");
      return;
    }
    stopSpeech();
    speechChunksRef.current = chunks;
    speechChunkIndexRef.current = 0;
    setSpeaking(true);
    speakNextRef.current?.();
  };

  const speakCurrent = () => speakText(sections[chapter] || book?.conteudo_leitura || "");
  const previewVoice = () => speakText("Olá. Esta é uma amostra da voz escolhida para ler os livros da Biblioteca Edukangola.");
  const pauseOrResumeSpeech = () => {
    if (typeof window === "undefined") return;
    if (speechPaused) {
      window.speechSynthesis.resume();
      setSpeechPaused(false);
    } else {
      window.speechSynthesis.pause();
      setSpeechPaused(true);
    }
  };

  if (status === "loading") return <main className="reader-shell"><p>A abrir a leitura…</p></main>;
  if (status === "error" || !book) return <main className="reader-shell"><p>Não foi possível abrir esta leitura.</p><button onClick={() => onNavigate(`/biblioteca/${slug}`)}>Voltar ao livro</button></main>;

  const content = sections[chapter] || book.conteudo_leitura;
  const renderLine = (line, index) => line.startsWith("# ") ? <h1 key={index}>{line.replace(/^# /, "")}</h1> : line.startsWith("## ") ? <h2 key={index}>{line.replace(/^## /, "")}</h2> : line.trim() ? <p key={index}>{line}</p> : null;
  const voiceName = selectedVoice?.name || "Voz recomendada pelo dispositivo";

  return <main className="reader-shell">
    <header className="reader-topbar"><button type="button" onClick={() => { stopSpeech(); onNavigate(`/biblioteca/${slug}`); }}><ArrowLeft size={18} /> Voltar</button><div><small>{book.autor?.nome}</small><strong>{book.titulo}</strong></div><button type="button" onClick={() => setOpenContents(true)} aria-label="Abrir índice"><List size={19} /></button></header>
    <div className="reader-progress"><span style={{ width: `${Math.round(((chapter + 1) / Math.max(sections.length, 1)) * 100)}%` }} /></div>
    <section className="reader-tools" aria-label="Controlos de leitura em voz alta">
      <div className="reader-voice-label"><Volume2 size={17} /><span>Ouvir esta página</span></div>
      <button type="button" className={speaking ? "active" : ""} onClick={speaking ? pauseOrResumeSpeech : speakCurrent} disabled={!canSpeakBookLanguage}>{speaking ? speechPaused ? <><Play size={16} /> Retomar</> : <><Pause size={16} /> Pausar</> : <><Volume2 size={16} /> Ler em voz alta</>}</button>
      {speaking && <button type="button" onClick={stopSpeech}><Square size={14} /> Parar</button>}
      <label className="reader-voice-select"><span>Voz</span><select value={selectedVoiceId} onChange={(event) => { stopSpeech(); setSelectedVoiceId(event.target.value); }} disabled={!canSpeakBookLanguage}><option value="recommended">Recomendada · {voiceName}</option>{recommendedVoices.slice(1).map((voice) => <option value={voiceId(voice)} key={voiceId(voice)}>{voice.name} · {voice.lang}</option>)}</select></label>
      <button type="button" className="reader-voice-preview" onClick={previewVoice} disabled={!canSpeakBookLanguage}><Volume2 size={14} /> Ouvir amostra</button>
      <label><Gauge size={15} /> <span>Velocidade</span><select value={speechRate} onChange={(event) => setSpeechRate(Number(event.target.value))}><option value="0.8">0,8×</option><option value="0.9">0,9×</option><option value="1">1×</option><option value="1.15">1,15×</option><option value="1.3">1,3×</option></select></label>
      {!recommendedVoices.length && speechAvailable && <p className="reader-voice-note">Nenhuma voz em português foi encontrada. Active ou transfira uma voz em Português nas definições de texto para voz do dispositivo e volte a abrir esta página.</p>}
    </section>
    <article className="reader-page">{content.split("\n").map(renderLine)}</article>
    <nav className="reader-navigation"><button type="button" disabled={chapter === 0} onClick={() => selectChapter(chapter - 1)}><ChevronLeft size={18} /> Anterior</button><span>{chapter + 1} de {sections.length}</span><button type="button" disabled={chapter >= sections.length - 1} onClick={() => selectChapter(chapter + 1)}>Seguinte <ChevronRight size={18} /></button></nav>
    {resumePrompt && <div className="reader-resume-backdrop"><section className="reader-resume-dialog" role="dialog" aria-modal="true" aria-labelledby="resume-title"><div className="reader-resume-icon"><RotateCcw size={21} /></div><h2 id="resume-title">Quer continuar a leitura?</h2><p>Encontrámos o seu ponto guardado. Pode continuar na página {resumePage + 1} ou começar o livro novamente.</p><div className="reader-resume-actions"><button type="button" className="reader-resume-primary" onClick={continueReading}>Continuar onde parei</button><button type="button" className="reader-resume-secondary" onClick={restartReading}>Começar novamente</button></div></section></div>}
    {openContents && <aside className="reader-contents"><div><h2>Índice</h2><button type="button" onClick={() => setOpenContents(false)}><X size={19} /></button></div>{sections.map((item, index) => <button type="button" className={chapter === index ? "active" : ""} onClick={() => selectChapter(index)} key={index}>{item.match(/^#\s+(.+)/m)?.[1] || item.match(/^##\s+(.+)/m)?.[1] || `Parte ${index + 1}`}</button>)}<p><Bookmark size={15} /> O seu progresso é guardado na Biblioteca.</p></aside>}
  </main>;
}
