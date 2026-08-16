import { useEffect, useState } from "react";
import { ArrowLeft, Bookmark, BookOpen, Check, Clock3, Headphones, Share2 } from "lucide-react";
import { authRequest } from "../lib/auth-api";
import "./book-detail-page.css";

export default function BookDetailPage({ slug, student, onNavigate, onAnnounce }) {
  const [book, setBook] = useState(null);
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let active = true;
    fetch(`/api/public/biblioteca/${encodeURIComponent(slug)}/`, { headers: { Accept: "application/json" } })
      .then((response) => { if (!response.ok) throw new Error(); return response.json(); })
      .then((data) => { if (active) { setBook(data.livro); setRelated(data.relacionados || []); } })
      .catch(() => active && setBook(null))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [slug]);

  const saveBook = async () => {
    if (!student) return onNavigate("/entrar");
    try { const data = await authRequest(`/api/react/biblioteca/${encodeURIComponent(slug)}/guardar/`); setSaved(data.guardado); onAnnounce(data.mensagem); } catch (error) { onAnnounce(error.message); }
  };

  if (loading) return <main className="book-detail-page page-width"><p className="book-detail-state">A abrir o livro…</p></main>;
  if (!book) return <main className="book-detail-page page-width"><p className="book-detail-state">Este livro não está disponível.</p><button onClick={() => onNavigate("/biblioteca")}>Voltar à Biblioteca</button></main>;
  return <main className="book-detail-page page-width">
    <button className="book-back" type="button" onClick={() => onNavigate("/biblioteca")}><ArrowLeft size={17} /> Biblioteca</button>
    <section className="book-hero">
      <div className="book-detail-cover"><span /><img src={book.capa_url} alt={`Capa de ${book.titulo}`} /></div>
      <div className="book-detail-copy"><span className="book-detail-category">{book.categoria}</span><p className="book-detail-author">Por {book.autor?.nome}</p><h1>{book.titulo}</h1>{book.subtitulo && <p className="book-detail-subtitle">{book.subtitulo}</p>}<p className="book-detail-summary">{book.sinopse}</p><dl className="book-detail-specs"><div><dt>Formato</dt><dd>{book.tem_leitura ? "Leitura digital" : "Digital"}</dd></div><div><dt>Extensão</dt><dd>{book.paginas} páginas</dd></div><div><dt>Acesso</dt><dd>{book.acesso_label}</dd></div></dl><div className="book-detail-actions"><button className="book-read-action" type="button" onClick={() => student ? onNavigate(`/ler/${book.slug}`) : onNavigate("/entrar")}><BookOpen size={18} /> {student ? "Ler agora" : "Entrar para ler"}</button><button className={saved ? "book-save-action saved" : "book-save-action"} type="button" onClick={saveBook}>{saved ? <Check size={18} /> : <Bookmark size={18} />}{saved ? "Na minha biblioteca" : "Guardar"}</button></div><p className="book-rights-note">Esta é uma obra própria, gratuita e autorizada para leitura na Edukangola.</p></div>
    </section>
    {book.excerto && <section className="book-excerpt"><span>Um excerto</span><blockquote>“{book.excerto}”</blockquote></section>}
    <section className="book-about-author"><div><span>Sobre o autor</span><h2>{book.autor?.nome}</h2><p>{book.autor?.biografia}</p></div><div className="book-micro-meta"><span><Clock3 size={17} /> Leitura ao seu ritmo</span><span><Headphones size={17} /> Áudio editorial em preparação</span><span><Share2 size={17} /> Guarde para continuar depois</span></div></section>
    {related.length > 0 && <section className="book-related"><span className="book-detail-category">Na mesma estante</span><h2>Continue por aqui</h2><div className="book-related-row">{related.map((item) => <button type="button" key={item.slug} onClick={() => onNavigate(`/biblioteca/${item.slug}`)}><img src={item.capa_url} alt="" /><span>{item.titulo}</span><small>{item.autor?.nome}</small></button>)}</div></section>}
  </main>;
}
