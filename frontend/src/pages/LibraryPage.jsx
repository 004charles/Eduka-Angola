import { useEffect, useMemo, useState } from "react";
import { ArrowRight, BookOpen, ChevronRight, Headphones, Search, Sparkles } from "lucide-react";
import "./library-page.css";

function BookObject({ book, onNavigate, priority = false }) {
  return <article className="library-book-object">
    <a className="library-book-visual" href={`/biblioteca/${book.slug}`} onClick={(event) => { event.preventDefault(); onNavigate(`/biblioteca/${book.slug}`); }} aria-label={`Abrir ${book.titulo}`}>
      <span className="library-book-spine" aria-hidden="true" />
      <span className="library-book-cover">{book.capa_url ? <img src={book.capa_url} alt="" loading={priority ? "eager" : "lazy"} /> : <span className="library-book-monogram">{book.titulo.slice(0, 1)}</span>}</span>
    </a>
    <div className="library-book-copy">
      <p>{book.autor?.nome}</p>
      <h3><a href={`/biblioteca/${book.slug}`} onClick={(event) => { event.preventDefault(); onNavigate(`/biblioteca/${book.slug}`); }}>{book.titulo}</a></h3>
      <span>{book.gratuito ? "Leitura gratuita" : book.acesso_label}</span>
    </div>
  </article>;
}

function Shelf({ eyebrow, title, books, onNavigate, emptyCopy }) {
  return <section className="library-shelf-section">
    <div className="library-section-heading"><div><span className="library-eyebrow">{eyebrow}</span><h2>{title}</h2></div><button type="button" onClick={() => onNavigate("/biblioteca?explorar=1")}>Ver selecção <ArrowRight size={17} /></button></div>
    {books?.length ? <div className="library-shelf" role="list">{books.map((book, index) => <BookObject key={book.slug} book={book} onNavigate={onNavigate} priority={index < 3} />)}</div> : <p className="library-empty-shelf">{emptyCopy}</p>}
  </section>;
}

export default function LibraryPage({ onNavigate }) {
  const [data, setData] = useState(null);
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("Todos");
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    let active = true;
    fetch("/api/public/biblioteca/", { headers: { Accept: "application/json" } })
      .then((response) => { if (!response.ok) throw new Error(); return response.json(); })
      .then((payload) => { if (active) { setData(payload); setStatus("ready"); } })
      .catch(() => active && setStatus("error"));
    return () => { active = false; };
  }, []);

  const allBooks = useMemo(() => [data?.destaque, ...(data?.estante_semana || []), ...(data?.por_carreira || [])].filter(Boolean).filter((book, index, list) => list.findIndex((item) => item.slug === book.slug) === index), [data]);
  const filteredBooks = useMemo(() => allBooks.filter((book) => {
    const text = `${book.titulo} ${book.autor?.nome} ${book.categoria} ${book.temas?.join(" ")}`.toLowerCase();
    return text.includes(query.trim().toLowerCase()) && (activeCategory === "Todos" || book.categoria === activeCategory);
  }), [allBooks, query, activeCategory]);

  if (status === "loading") return <main className="library-page page-width"><div className="library-loading"><BookOpen size={28} /><p>A preparar a estante…</p></div></main>;
  if (status === "error") return <main className="library-page page-width"><div className="library-loading"><BookOpen size={28} /><h1>Não foi possível abrir a Biblioteca.</h1><p>Tente novamente dentro de instantes.</p></div></main>;

  const featured = data?.destaque;
  return <main className="library-page page-width">
    <section className="library-intro">
      <div><span className="library-eyebrow"><BookOpen size={15} /> Biblioteca Edukangola</span><h1>Leituras para avançar<br />ao seu ritmo.</h1><p>Obras próprias, digitais e gratuitas para estudar, pensar e construir o próximo passo.</p></div>
      <a href="#estante" className="library-intro-link"><span>Conheça a estante</span><ArrowRight size={19} /></a>
    </section>

    {featured && <section className="library-feature" aria-label="Livro em destaque">
      <div className="library-feature-art"><span className="library-feature-spine" /><img src={featured.capa_url} alt={`Capa de ${featured.titulo}`} /></div>
      <div className="library-feature-copy"><span className="library-eyebrow"><Sparkles size={15} /> Escolha da semana</span><p className="library-feature-author">{featured.autor?.nome}</p><h2>{featured.titulo}</h2><p className="library-feature-summary">{featured.sinopse}</p><div className="library-feature-meta"><span>{featured.paginas} páginas</span><span>•</span><span>{featured.acesso_label}</span></div><button type="button" className="library-primary-action" onClick={() => onNavigate(`/biblioteca/${featured.slug}`)}>Abrir o livro <ChevronRight size={18} /></button></div>
    </section>}

    <section className="library-explorer" id="estante">
      <label className="library-search"><Search size={19} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Pesquisar por título, tema ou autor" /></label>
      <div className="library-filter-row" aria-label="Filtrar livros">{["Todos", ...(data?.categorias || [])].map((category) => <button type="button" key={category} onClick={() => setActiveCategory(category)} className={activeCategory === category ? "active" : ""}>{category}</button>)}</div>
      {(query || activeCategory !== "Todos") && <div className="library-search-results"><span>{filteredBooks.length} livro{filteredBooks.length === 1 ? "" : "s"} encontrado{filteredBooks.length === 1 ? "" : "s"}</span><div className="library-shelf">{filteredBooks.map((book) => <BookObject key={book.slug} book={book} onNavigate={onNavigate} />)}</div></div>}
    </section>

    {!query && activeCategory === "Todos" && <>
      <Shelf eyebrow="Na estante esta semana" title="Escolhidos para começar agora" books={data?.estante_semana} onNavigate={onNavigate} emptyCopy="A estante está a ser preparada." />
      <section className="library-audio-promise"><div className="library-audio-symbol"><Headphones size={31} /></div><div><span className="library-eyebrow">A escuta chega a seguir</span><h2>Audiolivros com voz autorizada.</h2><p>Estamos a preparar obras narradas e enviadas por autores e editoras. Quando estiverem disponíveis, poderá continuar a aprendizagem enquanto se desloca.</p></div><button type="button" onClick={() => onNavigate("/aluno")}>A minha biblioteca <ArrowRight size={17} /></button></section>
      <Shelf eyebrow="Leituras que abrem caminhos" title="Conhecimento para a sua próxima competência" books={data?.por_carreira} onNavigate={onNavigate} emptyCopy="Novas leituras profissionais em breve." />
    </>}
  </main>;
}
