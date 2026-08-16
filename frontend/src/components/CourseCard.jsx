import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { ArrowRight, Award, CalendarDays, Clock3, Heart, MapPin, UsersRound, Video } from "lucide-react";
import { acaoProduto, etiquetaProduto, isVideoCurso } from "../lib/product-type";
import "./course-card.css";

const PREVIEW_WIDTH = 344;
const PREVIEW_GAP = 14;

function podeMostrarPrevia() {
  return typeof window !== "undefined" && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
}

function resumir(texto) {
  const limpo = (texto || "").replace(/\s+/g, " ").trim();
  return limpo.length > 230 ? `${limpo.slice(0, 227).trimEnd()}…` : limpo;
}

/**
 * Cartão canónico de curso da Edukangola.
 * A prévia é ativada por rato e teclado em ecrãs de ponteiro fino; no toque,
 * o cartão mantém a navegação direta para o detalhe completo do curso.
 */
export default function CourseCard({ course, onSave }) {
  const cardRef = useRef(null);
  const closeTimer = useRef(null);
  const [preview, setPreview] = useState(null);

  const fecharAgora = useCallback(() => {
    window.clearTimeout(closeTimer.current);
    setPreview(null);
  }, []);

  const calcularPosicao = useCallback(() => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const margem = 16;
    const alturaEstimada = 430;
    const cabeDireita = rect.right + PREVIEW_GAP + PREVIEW_WIDTH <= window.innerWidth - margem;
    const cabeEsquerda = rect.left - PREVIEW_GAP - PREVIEW_WIDTH >= margem;
    const esquerda = cabeDireita
      ? rect.right + PREVIEW_GAP
      : cabeEsquerda
        ? rect.left - PREVIEW_GAP - PREVIEW_WIDTH
        : Math.max(margem, Math.min(rect.left, window.innerWidth - PREVIEW_WIDTH - margem));
    const topo = Math.max(margem, Math.min(rect.top - 4, window.innerHeight - alturaEstimada - margem));
    setPreview({ left: esquerda, top: topo, placement: cabeDireita ? "right" : "left" });
  }, []);

  const abrirPrevia = useCallback(() => {
    if (!podeMostrarPrevia()) return;
    window.clearTimeout(closeTimer.current);
    calcularPosicao();
  }, [calcularPosicao]);

  const agendarFecho = useCallback(() => {
    window.clearTimeout(closeTimer.current);
    closeTimer.current = window.setTimeout(() => setPreview(null), 120);
  }, []);

  useEffect(() => {
    if (!preview) return undefined;
    const reposicionar = () => calcularPosicao();
    window.addEventListener("resize", reposicionar);
    window.addEventListener("scroll", reposicionar, true);
    return () => {
      window.removeEventListener("resize", reposicionar);
      window.removeEventListener("scroll", reposicionar, true);
    };
  }, [preview, calcularPosicao]);

  useEffect(() => () => window.clearTimeout(closeTimer.current), []);

  const turma = course.turma;
  const descricao = resumir(course.descricao_curta || course.descricao);
  const localizacao = turma?.local || [course.cidade, course.provincia].filter(Boolean).join(", ");
  const meta = [course.carga_horaria ? `${course.carga_horaria} horas` : "", course.nivel_label, course.idioma_label].filter(Boolean).join(" · ");
  const temVideo = isVideoCurso(course);
  const etiqueta = course.productLabel || etiquetaProduto(course);
  const acao = course.ctaLabel || acaoProduto(course);
  const pagamentoAgora = course.is_gratuito ? "Gratuito" : (course.pagamento?.agora || "Condições a confirmar");
  const condicaoPagamento = course.is_gratuito ? "Acesso sem pagamento" : course.pagamento?.descricao;

  return (
    <article
      ref={cardRef}
      className={`course-card-shell${preview ? " is-preview-open" : ""}`}
      onMouseEnter={abrirPrevia}
      onMouseLeave={agendarFecho}
      onFocusCapture={abrirPrevia}
      onBlurCapture={agendarFecho}
    >
      <div className="course-card">
        <div className={`course-image ${course.image || ""}`}>
          {course.imageUrl && <img src={course.imageUrl} alt="" />}
          <span className="course-mode-badge">{etiqueta}</span>
          {temVideo && <span className="course-video-indicator" title={course.mode === "Híbrido" ? "Inclui aulas por vídeo" : "Curso em vídeo"} aria-label={course.mode === "Híbrido" ? "Inclui aulas por vídeo" : "Curso em vídeo"}><Video size={16} strokeWidth={2.4} /></span>}
        </div>
        <div className="course-content">
          <small>{course.category}</small>
          <h3 title={course.title}>{course.detailUrl ? <a href={course.detailUrl}>{course.title}</a> : course.title}</h3>
          <p title={course.centre}>{course.centre}</p>
          <div className={`course-price${course.is_gratuito ? " is-free" : ""}`}><strong>{pagamentoAgora}</strong>{condicaoPagamento && <span>{condicaoPagamento}</span>}</div>
          <div className="course-footer">
            <span title={course.schedule}><Clock3 size={14} /> {course.schedule}</span>
            <button type="button" aria-label={`Guardar ${course.title}`} onClick={() => onSave(course.title)}>
              <Heart size={18} />
            </button>
          </div>
        </div>
      </div>

      {preview && createPortal(
        <aside
          className={`course-preview course-preview--${preview.placement}`}
          style={{ left: preview.left, top: preview.top }}
          aria-label={`Pré-visualização: ${course.title}`}
          onMouseEnter={abrirPrevia}
          onMouseLeave={agendarFecho}
          onFocusCapture={abrirPrevia}
          onBlurCapture={agendarFecho}
        >
          <span className="course-preview-kicker">Pré-visualização</span>
          <h3>{course.title}</h3>
          {meta && <p className="course-preview-meta">{meta}</p>}
          <p className={`course-preview-price${course.is_gratuito ? " is-free" : ""}`}><strong>{pagamentoAgora}</strong>{condicaoPagamento && <span>{condicaoPagamento}</span>}</p>
          {descricao && <p className="course-preview-description">{descricao}</p>}
          <ul className="course-preview-facts">
            {temVideo ? <><li><Video size={16} /><span><b>Conteúdo</b>{course.total_aulas || 0} {(course.total_aulas || 0) === 1 ? "aula" : "aulas"}{course.duracao_total ? ` · ${course.duracao_total}` : ""}</span></li>{course.pagamento?.descricao && <li><Clock3 size={16} /><span><b>{course.is_gratuito ? "Acesso" : "Compra"}</b>{course.pagamento.descricao}</span></li>}</> : <>{turma && <li><CalendarDays size={16} /><span><b>Próxima turma</b>{turma.inicio_formatado}{turma.turno ? ` · ${turma.turno}` : ""}{turma.horario ? ` · ${turma.horario}` : ""}</span></li>}{turma?.vagas_disponiveis > 0 && <li><UsersRound size={16} /><span><b>Vagas disponíveis</b>{turma.vagas_disponiveis} {turma.vagas_disponiveis === 1 ? "vaga" : "vagas"} nesta turma</span></li>}{localizacao && <li><MapPin size={16} /><span><b>Local</b>{localizacao}</span></li>}{course.pagamento?.descricao && <li><Clock3 size={16} /><span><b>Inscrição</b>{course.pagamento.descricao}</span></li>}</>}
            {course.certificado && <li><Award size={16} /><span><b>Certificado</b>Emitido pelo centro de formação</span></li>}
          </ul>
          {course.detailUrl && <a className="course-preview-action" href={course.detailUrl}>{acao} <ArrowRight size={16} /></a>}
        </aside>,
        document.body,
      )}
    </article>
  );
}
