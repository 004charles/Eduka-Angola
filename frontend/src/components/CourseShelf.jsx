import { useEffect, useRef, useState } from "react";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import CourseCard from "./CourseCard";
import "./course-shelf.css";

/**
 * Prateleira horizontal reutilizável da Eduka-Angola.
 * Cada instância mantém a sua própria posição e nunca altera a rolagem vertical da página.
 */
export default function CourseShelf({
  id,
  eyebrow,
  title,
  description,
  courses,
  featured = false,
  autoAdvance = false,
  onAnnounce,
  collectionHref,
}) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const trackRef = useRef(null);
  const headingId = `${id}-title`;

  const selectSlide = (index) => {
    const track = trackRef.current;
    const target = track?.querySelector(`[data-course-index="${index}"]`);

    if (track && target) {
      const targetLeft = target.getBoundingClientRect().left - track.getBoundingClientRect().left + track.scrollLeft;
      track.scrollTo({ left: targetLeft, behavior: "smooth" });
    }

    setActiveIndex(index);
  };

  const moveCarousel = (direction) => {
    const nextIndex = (activeIndex + direction + courses.length) % courses.length;
    selectSlide(nextIndex);
  };

  useEffect(() => {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!autoAdvance || paused || reducedMotion) return undefined;

    const interval = window.setInterval(() => moveCarousel(1), 4600);
    return () => window.clearInterval(interval);
  }, [activeIndex, autoAdvance, paused]);

  return (
    <section id={id} className={`page-width course-shelf ${featured ? "course-shelf-featured" : ""}`} aria-labelledby={headingId}>
      <div className="section-heading">
        <div>
          <span className="eyebrow muted">{eyebrow}</span>
          <h2 id={headingId}>{title}</h2>
          {description && <p>{description}</p>}
        </div>
        <div className="heading-actions">
          {collectionHref ? <a className="text-action" href={collectionHref}>Ver coleção <ArrowRight size={16} /></a> : <button className="text-action" onClick={() => onAnnounce?.("A listagem completa de cursos está disponível no catálogo.")}>Ver coleção <ArrowRight size={16} /></button>}
          <div className="carousel-controls" aria-label={`Controlos da coleção ${title}`}>
            <button className="carousel-arrow" onClick={() => moveCarousel(-1)} aria-label={`Ver cursos anteriores em ${title}`}><ChevronLeft size={18} /></button>
            <button className="carousel-arrow" onClick={() => moveCarousel(1)} aria-label={`Ver próximos cursos em ${title}`}><ChevronRight size={18} /></button>
          </div>
        </div>
      </div>
      <div className="course-carousel" onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)}>
        <div className="course-track" ref={trackRef} aria-label={title} aria-roledescription="carrossel">
          {courses.map((course, index) => (
            <div className="course-slide" data-course-index={index} key={`${id}-${course.title}-${index}`}>
              <CourseCard course={course} onSave={(message) => onAnnounce?.(message === "AUTH_REQUIRED" ? "Os cursos guardados estarão disponíveis após o login." : message)} />
            </div>
          ))}
        </div>
        <div className="carousel-pagination" aria-label={`Selecionar curso em ${title}`}>
          {courses.map((course, index) => (
            <button key={`${id}-${course.title}-${index}`} className={index === activeIndex ? "active" : ""} onClick={() => selectSlide(index)} aria-label={`Mostrar ${course.title}`} aria-current={index === activeIndex ? "true" : undefined} />
          ))}
        </div>
      </div>
    </section>
  );
}
