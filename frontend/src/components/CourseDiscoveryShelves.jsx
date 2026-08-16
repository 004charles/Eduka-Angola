import { useRef } from "react";
import { ArrowRight, ChevronLeft, ChevronRight, Clock3, Heart } from "lucide-react";
import { etiquetaProduto, rotaDetalheProduto } from "../lib/product-type";
import "./course-discovery-shelves.css";

function ShelfCard({ course }) {
  return <a className="discovery-course-card" href={rotaDetalheProduto(course)}>
    <div className="discovery-course-image"><img src={course.imagem_url} alt="" /><span>{etiquetaProduto(course)}</span></div>
    <div className="discovery-course-body"><small>{course.categoria || "Formação"}</small><strong>{course.titulo}</strong><p>{course.centro || "Edukangola"}</p><footer><span><Clock3 size={14} /> Ver detalhes</span><Heart size={17} /></footer></div>
  </a>;
}

function DiscoveryShelf({ collection, onNavigate }) {
  const trackRef = useRef(null);
  const shift = (direction) => {
    const track = trackRef.current;
    if (!track) return;
    track.scrollBy({ left: direction * Math.max(300, track.clientWidth * 0.78), behavior: "smooth" });
  };

  return <section className="discovery-shelf" aria-labelledby={`shelf-${collection.slug}`}>
    <header><div><span className="eyebrow muted">{collection.eyebrow}</span><h2 id={`shelf-${collection.slug}`}>{collection.title}</h2></div><div className="discovery-shelf-actions"><button className="text-action" onClick={() => onNavigate(collection.href)}>Ver catálogo <ArrowRight size={16} /></button><div><button aria-label={`Cursos anteriores em ${collection.title}`} onClick={() => shift(-1)}><ChevronLeft size={18} /></button><button aria-label={`Próximos cursos em ${collection.title}`} onClick={() => shift(1)}><ChevronRight size={18} /></button></div></div></header>
    <div className="discovery-shelf-track" ref={trackRef}>{collection.courses.map((course) => <ShelfCard course={course} key={`${collection.slug}-${course.id}`} />)}</div>
  </section>;
}

export default function CourseDiscoveryShelves({ collections, onNavigate }) {
  return <div className="course-discovery-shelves">{collections.map((collection) => <DiscoveryShelf collection={collection} onNavigate={onNavigate} key={collection.slug} />)}</div>;
}
