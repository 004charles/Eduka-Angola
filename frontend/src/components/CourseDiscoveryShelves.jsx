import { useEffect, useRef, useState } from "react";
import { ArrowRight, ChevronLeft, ChevronRight, Clock3, Heart } from "lucide-react";
import { etiquetaProduto, rotaDetalheProduto } from "../lib/product-type";
import { backendUrl } from "../lib/backend-url";
import "./course-discovery-shelves.css";

function ShelfCard({ course, onAnnounce }) {
  const courseId = String(course.id);
  const initialFavorite = typeof window !== "undefined" && Array.isArray(window.__edukaFavoriteIds)
    ? window.__edukaFavoriteIds.map(String).includes(courseId)
    : Boolean(course.favorito || course.isFavorite);
  const [isFavorite, setIsFavorite] = useState(initialFavorite);
  const [savingFavorite, setSavingFavorite] = useState(false);

  useEffect(() => {
    const syncFavorite = (event) => {
      const ids = event.detail?.ids || window.__edukaFavoriteIds || [];
      setIsFavorite(ids.map(String).includes(courseId));
    };
    window.addEventListener("eduka:favorites-changed", syncFavorite);
    return () => window.removeEventListener("eduka:favorites-changed", syncFavorite);
  }, [courseId]);

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

  return <a className="discovery-course-card" href={rotaDetalheProduto(course)}>
    <div className="discovery-course-image"><img src={course.imagem_url} alt="" /><span>{etiquetaProduto(course)}</span></div>
    <div className="discovery-course-body"><small>{course.categoria || "Formação"}</small><strong>{course.titulo}</strong><p>{course.centro || "Edukangola"}</p><footer><span><Clock3 size={14} /> Ver detalhes</span><button type="button" className={isFavorite ? "is-favorite" : ""} aria-label={isFavorite ? `Remover ${course.titulo} dos guardados` : `Guardar ${course.titulo}`} aria-pressed={isFavorite} disabled={savingFavorite} onClick={toggleFavorite}><Heart size={17} fill={isFavorite ? "currentColor" : "none"} /></button></footer></div>
  </a>;
}

function DiscoveryShelf({ collection, onNavigate, onAnnounce }) {
  const trackRef = useRef(null);
  const shift = (direction) => {
    const track = trackRef.current;
    if (!track) return;
    track.scrollBy({ left: direction * Math.max(300, track.clientWidth * 0.78), behavior: "smooth" });
  };
  return <section className="discovery-shelf" aria-labelledby={`shelf-${collection.slug}`}>
    <header><div><span className="eyebrow muted">{collection.eyebrow}</span><h2 id={`shelf-${collection.slug}`}>{collection.title}</h2></div><div className="discovery-shelf-actions"><button className="text-action" onClick={() => onNavigate(collection.href)}>Ver catálogo <ArrowRight size={16} /></button><div><button aria-label={`Cursos anteriores em ${collection.title}`} onClick={() => shift(-1)}><ChevronLeft size={18} /></button><button aria-label={`Próximos cursos em ${collection.title}`} onClick={() => shift(1)}><ChevronRight size={18} /></button></div></div></header>
    <div className="discovery-shelf-track" ref={trackRef}>{collection.courses.map((course) => <ShelfCard course={course} onAnnounce={onAnnounce} key={`${collection.slug}-${course.id}`} />)}</div>
  </section>;
}

export default function CourseDiscoveryShelves({ collections, onNavigate, onAnnounce }) {
  return <div className="course-discovery-shelves">{collections.map((collection) => <DiscoveryShelf collection={collection} onNavigate={onNavigate} onAnnounce={onAnnounce} key={collection.slug} />)}</div>;
}
