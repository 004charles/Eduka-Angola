import { useEffect, useState } from "react";
import { ArrowLeft, CalendarDays, ExternalLink, Play, Radio, Video } from "lucide-react";

function getVideoId(url = "") { const match = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|shorts\/))([^?&/]+)/i); return match?.[1] || ""; }
function formatDate(value) { try { return new Intl.DateTimeFormat("pt-AO", { day: "2-digit", month: "long", year: "numeric" }).format(new Date(value)); } catch { return value?.slice(0, 10) || ""; } }

export default function BlogPostPage({ slug, onNavigate }) {
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => { let active = true; fetch(`/api/v1/blog/${encodeURIComponent(slug)}/`).then((response) => response.ok ? response.json() : Promise.reject(new Error("not-found"))).then((payload) => active && setPost(payload)).catch(() => active && setPost(null)).finally(() => active && setLoading(false)); return () => { active = false; }; }, [slug]);
  if (loading) return <main className="page-width blog-detail-loading"><p className="page-empty">A carregar notícia.</p></main>;
  if (!post) return <main className="page-width"><div className="page-empty"><strong>Notícia não encontrada.</strong><button className="primary-action" onClick={() => onNavigate("/blog")}>Voltar ao blog</button></div></main>;
  const videoId = getVideoId(post.video_url);
  return <main className="blog-detail"><div className="page-width"><button className="back-link" onClick={() => onNavigate("/blog")}><ArrowLeft size={16} /> Voltar às notícias</button><article className="blog-article"><div className="blog-article-head"><span className="eyebrow"><Radio size={15} /> {post.tipo_conteudo === "video" ? "Edukangola Agora" : "Blog e notícias"}</span><h1>{post.titulo}</h1><div className="blog-meta"><CalendarDays size={14} /> {formatDate(post.publicado_em)} {post.categoria?.nome && <><span>·</span>{post.categoria.nome}</>} {post.tipo_conteudo === "video" && <><Video size={14} /> {post.duracao_video || "Vídeo"}</>}</div></div>{post.tipo_conteudo === "video" && videoId ? <div className="blog-video-frame"><iframe title={post.titulo} src={`https://www.youtube.com/embed/${videoId}`} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen /></div> : post.tipo_conteudo === "video" && post.video_url ? <a className="blog-external-video" href={post.video_url} target="_blank" rel="noreferrer"><Play size={18} /> Abrir vídeo da notícia <ExternalLink size={15} /></a> : post.imagem_capa && <img className="blog-article-cover" src={post.imagem_capa} alt="" />}<div className="blog-article-content">{post.resumo && <p className="blog-article-summary">{post.resumo}</p>}<div className="blog-article-text">{post.conteudo}</div></div></article></div></main>;
}
