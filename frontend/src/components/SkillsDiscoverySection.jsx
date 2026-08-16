import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowRight, ChevronLeft, ChevronRight, Sparkles } from "lucide-react";
import CourseCard from "./CourseCard";
import { backendUrl } from "../lib/backend-url";
import { etiquetaProduto, isVideoCurso, rotaDetalheProduto, textoRodapeProduto, tipoProduto } from "../lib/product-type";
import "./skills-discovery-section.css";

function formatarCentro(nome) {
  return nome?.replace(/Eduka-Angola/gi, "Edukangola") ?? "Centro de formação";
}

function criarCartoes(data) {
  const proximaTurmaPorCurso = new Map();
  (data?.turmas_abertas || []).forEach((turma) => {
    const atual = proximaTurmaPorCurso.get(turma.id);
    if (!atual || turma.inicio < atual.inicio) proximaTurmaPorCurso.set(turma.id, turma);
  });

  return (data?.cursos || []).filter((curso) => !isVideoCurso(curso)).map((curso) => {
    const turma = proximaTurmaPorCurso.get(curso.id);
    return {
      ...curso,
      title: curso.titulo,
      category: curso.categoria,
      centre: formatarCentro(curso.centro),
      productType: tipoProduto(curso),
      productLabel: etiquetaProduto(curso),
      mode: curso.modalidade,
      imageUrl: curso.imagem_url,
      detailUrl: rotaDetalheProduto(curso),
      inscricaoUrl: backendUrl(curso.inscricao_url),
      schedule: textoRodapeProduto(curso, turma),
      turma,
    };
  });
}

/**
 * Descoberta temática inspirada em prateleiras de competências, mas preenchida
 * exclusivamente por categorias e cursos que já estão publicados no Django.
 */
export default function SkillsDiscoverySection({ data, onAnnounce }) {
  const trackRef = useRef(null);
  const cards = useMemo(() => criarCartoes(data), [data]);
  const temas = useMemo(
    () => [...new Set(cards.map((curso) => curso.category).filter(Boolean))].sort((a, b) => a.localeCompare(b, "pt-PT")),
    [cards],
  );
  const [temaAtivo, setTemaAtivo] = useState("todos");

  useEffect(() => {
    if (temaAtivo !== "todos" && !temas.includes(temaAtivo)) setTemaAtivo("todos");
  }, [temaAtivo, temas]);

  if (!cards.length) return null;

  const cursosVisiveis = temaAtivo === "todos" ? cards : cards.filter((curso) => curso.category === temaAtivo);
  const destinoCatalogo = temaAtivo === "todos" ? "/cursos?tipo=formacao" : `/cursos?tipo=formacao&categoria=${encodeURIComponent(temaAtivo)}`;
  const avancar = (direcao) => {
    trackRef.current?.scrollBy({ left: direcao * Math.max(240, trackRef.current.clientWidth * 0.76), behavior: "smooth" });
  };

  return (
    <section className="skills-discovery-section" aria-labelledby="skills-discovery-title">
      <div className="page-width">
        <div className="skills-discovery-heading">
          <div>
            <span className="eyebrow muted"><Sparkles size={14} /> Descubra por competência</span>
            <h2 id="skills-discovery-title">Competências que podem abrir novas oportunidades.</h2>
            <p>Explore formações publicadas por centros, com turma, horários e vagas antes de decidir.</p>
          </div>
          <a className="text-action" href={destinoCatalogo}>Ver formações com turma <ArrowRight size={16} /></a>
        </div>

        <div className="skills-tabs" role="tablist" aria-label="Áreas de competência">
          <button id="competencia-todos" role="tab" type="button" aria-selected={temaAtivo === "todos"} aria-controls="competencia-painel" className={temaAtivo === "todos" ? "is-active" : ""} onClick={() => setTemaAtivo("todos")}>Todas as formações</button>
          {temas.map((tema) => <button key={tema} id={`competencia-${tema}`} role="tab" type="button" aria-selected={temaAtivo === tema} aria-controls="competencia-painel" className={temaAtivo === tema ? "is-active" : ""} onClick={() => setTemaAtivo(tema)}>{tema}</button>)}
        </div>

        <div id="competencia-painel" role="tabpanel" aria-labelledby={temaAtivo === "todos" ? "competencia-todos" : `competencia-${temaAtivo}`} className="skills-courses-panel">
          <div className="skills-courses-head">
            <p>{temaAtivo === "todos" ? "Formações publicadas com turma e acompanhamento do centro." : `Formações publicadas em ${temaAtivo}.`}</p>
            {cursosVisiveis.length > 1 && <div className="carousel-controls" aria-label={`Controlos dos cursos em ${temaAtivo === "todos" ? "todas as competências" : temaAtivo}`}><button className="carousel-arrow" type="button" onClick={() => avancar(-1)} aria-label="Ver cursos anteriores"><ChevronLeft size={18} /></button><button className="carousel-arrow" type="button" onClick={() => avancar(1)} aria-label="Ver próximos cursos"><ChevronRight size={18} /></button></div>}
          </div>
          <div ref={trackRef} className="skills-courses-track" aria-label="Cursos por competência">
            {cursosVisiveis.map((curso) => <div className="skills-course-slide" key={curso.id}><CourseCard course={curso} onSave={() => onAnnounce?.("Os cursos guardados estarão disponíveis após o login.")} /></div>)}
          </div>
        </div>
      </div>
    </section>
  );
}
