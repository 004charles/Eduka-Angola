import { createPortal } from "react-dom";
import { useCallback, useEffect, useRef, useState } from "react";
import { ArrowRight, Check, ChevronLeft, ChevronRight, Clock3, Heart, MapPin, Video } from "lucide-react";
import { etiquetaProduto, isVideoCurso, rotaDetalheProduto } from "../lib/product-type";
import { backendUrl } from "../lib/backend-url";
import "./course-discovery-shelves.css";

const PREVIEW_WIDTH = 364;
const PREVIEW_HEIGHT = 468;
const PREVIEW_GAP = 14;

function canPreviewCourse() {
  return typeof window !== "undefined" && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
}

function compactText(value, length = 220) {
  const text = (value || "").replace(/\s+/g, " ").trim();
  return text.length > length ? `${text.slice(0, length - 1).trimEnd()}…` : text;
}

function coursePriceLines(course, videoCourse) {
  if (course.is_gratuito) return [["Acesso", "Gratuito"]];
  if (videoCourse) return [["Compra única", course.preco_formatado || course.pagamento?.agora || "Preço no detalhe"]];
  const financeiro = course.financeiro || {};
  const linhas = [["Inscrição", Number(financeiro.inscricao?.valor) > 0 ? financeiro.inscricao.formatado : "Sem taxa"]];
  if (Number(financeiro.mensalidade?.valor) > 0) linhas.push(["Mensalidade", financeiro.mensalidade.formatado]);
  if (!Number(financeiro.inscricao?.valor) && !Number(financeiro.mensalidade?.valor)) linhas.push(["Preço total", financeiro.preco_total_formatado || course.preco_formatado || "Preço no detalhe"]);
  return linhas;
}

function enrollmentSummary(course, videoCourse) {
  if (videoCourse) return "Compra única";
  return course.pagamento?.descricao || (course.turma ? "Inscrições abertas" : "Consulte a disponibilidade");
}

function ShelfCard({ course, onAnnounce }) {
  const courseId = String(course.id);
  const initialFavorite = typeof window !== "undefined" && Array.isArray(window.__edukaFavoriteIds)
    ? window.__edukaFavoriteIds.map(String).includes(courseId)
    : Boolean(course.favorito || course.isFavorite);
  const [isFavorite, setIsFavorite] = useState(initialFavorite);
  const [savingFavorite, setSavingFavorite] = useState(false);
  const [preview, setPreview] = useState(null);
  const cardRef = useRef(null);
  const closeTimer = useRef(null);
  const videoCourse = isVideoCurso(course);
  const detailUrl = rotaDetalheProduto(course);
  const description = compactText(course.descricao_curta || course.descricao);
  const schedule = course.turma?.inicio_formatado || course.turma?.horario || course.carga_horaria ? (course.turma?.inicio_formatado || course.turma?.horario || `${course.carga_horaria} horas`) : "Informação no detalhe";

  const positionPreview = useCallback(() => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const margin = 16;
    const fitsRight = rect.right + PREVIEW_GAP + PREVIEW_WIDTH <= window.innerWidth - margin;
    const fitsLeft = rect.left - PREVIEW_GAP - PREVIEW_WIDTH >= margin;
    const left = fitsRight ? rect.right + PREVIEW_GAP : fitsLeft ? rect.left - PREVIEW_GAP - PREVIEW_WIDTH : Math.max(margin, Math.min(rect.left, window.innerWidth - PREVIEW_WIDTH - margin));
    const top = Math.max(margin, Math.min(rect.top - 8, window.innerHeight - PREVIEW_HEIGHT - margin));
    setPreview({ left, top, placement: fitsRight ? "right" : "left" });
  }, []);

  const openPreview = useCallback(() => {
    if (!canPreviewCourse()) return;
    window.clearTimeout(closeTimer.current);
    positionPreview();
  }, [positionPreview]);
  const closePreview = useCallback(() => {
    window.clearTimeout(closeTimer.current);
    closeTimer.current = window.setTimeout(() => setPreview(null), 150);
  }, []);

  useEffect(() => {
    const syncFavorite = (event) => setIsFavorite((event.detail?.ids || window.__edukaFavoriteIds || []).map(String).includes(courseId));
    window.addEventListener("eduka:favorites-changed", syncFavorite);
    return () => window.removeEventListener("eduka:favorites-changed", syncFavorite);
  }, [courseId]);
  useEffect(() => {
    if (!preview) return undefined;
    const reposition = () => positionPreview();
    window.addEventListener("resize", reposition);
    window.addEventListener("scroll", reposition, true);
    return () => { window.removeEventListener("resize", reposition); window.removeEventListener("scroll", reposition, true); };
  }, [preview, positionPreview]);
  useEffect(() => () => window.clearTimeout(closeTimer.current), []);

  const toggleFavorite = async (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (savingFavorite) return;
    if (!document.cookie.includes("csrftoken=")) await fetch(backendUrl("/auth/api/react/aluno/favoritos/"), { credentials: "same-origin" });
    const token = document.cookie.split(";").map((item) => item.trim()).find((item) => item.startsWith("csrftoken="))?.split("=").slice(1).join("=") || "";
    setSavingFavorite(true);
    try {
      const response = await fetch(backendUrl("/auth/api/react/aluno/favoritos/alternar/"), { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", Accept: "application/json", "X-CSRFToken": token }, body: JSON.stringify({ curso_id: course.id }) });
      const payload = await response.json().catch(() => ({}));
      if (response.status === 401) { onAnnounce?.("AUTH_REQUIRED"); return; }
      if (!response.ok) throw new Error(payload.detail || "Não foi possível guardar o curso.");
      const favorite = Boolean(payload.favorito);
      setIsFavorite(favorite);
      const ids = new Set((window.__edukaFavoriteIds || []).map(String));
      if (favorite) ids.add(courseId); else ids.delete(courseId);
      window.__edukaFavoriteIds = [...ids];
      window.dispatchEvent(new CustomEvent("eduka:favorites-changed", { detail: { ids: window.__edukaFavoriteIds } }));
      onAnnounce?.(payload.message);
    } catch (error) { onAnnounce?.(error.message); } finally { setSavingFavorite(false); }
  };

  const pricing = coursePriceLines(course, videoCourse);
  return <article ref={cardRef} className={`discovery-card-shell${preview ? " is-preview-open" : ""}`} onMouseEnter={openPreview} onMouseLeave={closePreview} onFocusCapture={openPreview} onBlurCapture={closePreview}>
    <a className="discovery-course-card" href={detailUrl}>
      <div className="discovery-course-image"><img src={course.imagem_url} alt="" /><span>{etiquetaProduto(course)}</span></div>
      <div className="discovery-course-body"><small>{course.categoria || "Formação"}</small><strong>{course.titulo}</strong><p>{course.centro || "Edukangola"}</p><div className="discovery-course-price">{pricing.map(([rotulo, valor]) => <span key={rotulo}><small>{rotulo}</small><b>{valor}</b></span>)}<em>{enrollmentSummary(course, videoCourse)}</em></div><footer><span><Clock3 size={14} /> Ver detalhes</span><button type="button" className={isFavorite ? "is-favorite" : ""} aria-label={isFavorite ? `Remover ${course.titulo} dos guardados` : `Guardar ${course.title} dos guardados`} aria-pressed={isFavorite} disabled={savingFavorite} onClick={toggleFavorite}><Heart size={17} fill={isFavorite ? "currentColor" : "none"} /></button></footer></div>
    </a>
    {preview && createPortal(<aside className={`discovery-course-preview discovery-course-preview--${preview.placement}`} style={{ left: preview.left, top: preview.top }} aria-label={`Pré-visualização: ${course.titulo}`} onMouseEnter={openPreview} onMouseLeave={closePreview} onFocusCapture={openPreview} onBlurCapture={closePreview}>
      <span className="discovery-preview-kicker">Pré-visualização</span><h3>{course.titulo}</h3><p className="discovery-preview-meta"><b>{etiquetaProduto(course)}</b>{course.categoria ? ` · ${course.categoria}` : ""}</p>
      {description && <p className="discovery-preview-description">{description}</p>}
      <ul><li><Check size={16} /><span><b>{videoCourse ? "Conteúdo em vídeo" : "Formação orientada"}</b>{videoCourse ? `${course.total_aulas || 0} aulas${course.duracao_total ? ` · ${course.duracao_total}` : ""}` : course.centro || "Centro de formação"}</span></li><li><Clock3 size={16} /><span><b>{videoCourse ? "Acesso" : "Informação da turma"}</b>{schedule}</span></li>{!videoCourse && (course.turma?.local || course.provincia || course.cidade) && <li><MapPin size={16} /><span><b>Local</b>{course.turma?.local || [course.cidade, course.provincia].filter(Boolean).join(", ")}</span></li>}{videoCourse && <li><Video size={16} /><span><b>Estude ao seu ritmo</b>Aprenda onde e quando quiser.</span></li>}</ul>
      <a href={detailUrl} className="discovery-preview-action">Ver detalhes do curso <ArrowRight size={16} /></a>
    </aside>, document.body)}
  </article>;
}

function DiscoveryShelf({ collection, onNavigate, onAnnounce }) {
  const trackRef = useRef(null);
  const shift = (direction) => trackRef.current?.scrollBy({ left: direction * Math.max(300, trackRef.current.clientWidth * 0.78), behavior: "smooth" });
  return <section className="discovery-shelf" aria-labelledby={`shelf-${collection.slug}`}><header><div><span className="eyebrow muted">{collection.eyebrow}</span><h2 id={`shelf-${collection.slug}`}>{collection.title}</h2></div><div className="discovery-shelf-actions"><button className="text-action" onClick={() => onNavigate(collection.href)}>Ver catálogo <ArrowRight size={16} /></button><div><button aria-label={`Cursos anteriores em ${collection.title}`} onClick={() => shift(-1)}><ChevronLeft size={18} /></button><button aria-label={`Próximos cursos em ${collection.title}`} onClick={() => shift(1)}><ChevronRight size={18} /></button></div></div></header><div className="discovery-shelf-track" ref={trackRef}>{collection.courses.map((course) => <ShelfCard course={course} onAnnounce={onAnnounce} key={`${collection.slug}-${course.id}`} />)}</div></section>;
}

export default function CourseDiscoveryShelves({ collections, onNavigate, onAnnounce }) { return <div className="course-discovery-shelves">{collections.map((collection) => <DiscoveryShelf collection={collection} onNavigate={onNavigate} onAnnounce={onAnnounce} key={collection.slug} />)}</div>; }
