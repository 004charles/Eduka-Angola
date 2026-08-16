import { ArrowRight, BookOpen, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";
import "./library-homepage-shelf.css";

function HomepageBook({ book, onNavigate }) {
  return <article className="homepage-library-book">
    <a href={`/biblioteca/${book.slug}`} onClick={(event) => { event.preventDefault(); onNavigate(`/biblioteca/${book.slug}`); }} aria-label={`Abrir ${book.titulo}`}>
      <span className="homepage-library-book-spine" aria-hidden="true" />
      <img src={book.capa_url} alt="" loading="lazy" />
    </a>
    <p>{book.autor?.nome}</p>
    <h3><a href={`/biblioteca/${book.slug}`} onClick={(event) => { event.preventDefault(); onNavigate(`/biblioteca/${book.slug}`); }}>{book.titulo}</a></h3>
    <span>Leitura gratuita</span>
  </article>;
}

export default function LibraryHomepageShelf({ onNavigate }) {
  const [books, setBooks] = useState([]);
  useEffect(() => {
    let active = true;
    fetch("/api/public/biblioteca/", { headers: { Accept: "application/json" } })
      .then((response) => response.ok ? response.json() : Promise.reject(new Error()))
      .then((data) => { if (active) setBooks([data.destaque, ...(data.estante_semana || [])].filter(Boolean).filter((book, index, list) => list.findIndex((item) => item.slug === book.slug) === index).slice(0, 6)); })
      .catch(() => active && setBooks([]));
    return () => { active = false; };
  }, []);

  if (!books.length) return null;
  return <section className="homepage-library-shelf page-width" aria-labelledby="homepage-library-title">
    <div className="homepage-library-heading"><div><span className="homepage-library-eyebrow"><BookOpen size={15} /> Biblioteca Edukangola</span><h2 id="homepage-library-title">Livros para continuar a aprender.</h2><p>Obras próprias, gratuitas e pensadas para ler ao seu ritmo.</p></div><button type="button" onClick={() => onNavigate("/biblioteca")}>Ver toda a Biblioteca <ArrowRight size={17} /></button></div>
    <div className="homepage-library-track" role="list">{books.map((book) => <HomepageBook key={book.slug} book={book} onNavigate={onNavigate} />)}</div>
  </section>;
}
