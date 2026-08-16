import { useEffect, useMemo, useState } from "react";
import { ArrowRight, CalendarDays, Hash, Play, Radio, Search, Video } from "lucide-react";
import { newsCover } from "../lib/news-covers";

const copy = {
  pt: { eyebrow: "Blog e notícias", title: "O que importa para o seu futuro.", intro: "Ideias, oportunidades e histórias que ajudam Angola a aprender, ensinar e avançar.", all: "Tudo", articles: "Artigos", videos: "Telejornal", search: "Pesquisar notícias", latest: "Todas as publicações", watch: "Ver notícia", empty: "Ainda não há publicações neste tema.", week: "Esta semana", weekCopy: "Leituras em destaque para acompanhar agora.", topics: "Explorar por tema", topicsCopy: "Encontre conteúdos por área de interesse.", allTopics: "Todos os temas", reading: "A ler" },
  en: { eyebrow: "Blog and news", title: "What matters for your future.", intro: "Ideas, opportunities and stories helping Angola learn, teach and move forward.", all: "All", articles: "Articles", videos: "Newsroom", search: "Search news", latest: "All stories", watch: "Read story", empty: "There are no publications in this topic yet.", week: "This week", weekCopy: "Featured reads to follow now.", topics: "Explore by topic", topicsCopy: "Find content by area of interest.", allTopics: "All topics", reading: "Reading" },
  fr: { eyebrow: "Blog et actualités", title: "Ce qui compte pour votre avenir.", intro: "Des idées et des histoires pour apprendre, enseigner et avancer en Angola.", all: "Tout", articles: "Articles", videos: "Journal", search: "Rechercher", latest: "Toutes les publications", watch: "Voir la nouvelle", empty: "Aucune publication dans ce thème.", week: "Cette semaine", weekCopy: "Lectures à suivre maintenant.", topics: "Explorer par thème", topicsCopy: "Trouvez du contenu par domaine d'intérêt.", allTopics: "Tous les thèmes", reading: "À lire" },
  zh: { eyebrow: "博客与新闻", title: "与您的未来息息相关。", intro: "分享帮助安哥拉学习、教学和前进的想法、机会与故事。", all: "全部", articles: "文章", videos: "新闻节目", search: "搜索新闻", latest: "所有发布", watch: "查看新闻", empty: "该主题暂无内容。", week: "本周精选", weekCopy: "值得现在关注的内容。", topics: "按主题探索", topicsCopy: "按兴趣领域查找内容。", allTopics: "全部主题", reading: "阅读" },
};

function formatDate(value, language) { if (!value) return ""; try { return new Intl.DateTimeFormat(language === "pt" ? "pt-AO" : language, { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value)); } catch { return value.slice(0, 10); } }
function uniqueBySlug(items) { return Array.from(new Map(items.filter(Boolean).map((item) => [item.slug, item])).values()); }

export default function BlogPage({ onNavigate, language = "pt" }) {
  const text = copy[language] || copy.pt;
  const [posts, setPosts] = useState([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [topic, setTopic] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { let active = true; const params = query.trim() ? `?search=${encodeURIComponent(query.trim())}` : ""; fetch(`/api/v1/blog/${params}`).then((response) => response.ok ? response.json() : Promise.reject(new Error("blog"))).then((payload) => { if (active) setPosts(Array.isArray(payload) ? payload : payload.results || []); }).catch(() => active && setPosts([])).finally(() => active && setLoading(false)); return () => { active = false; }; }, [query]);

  const videos = useMemo(() => posts.filter((post) => post.tipo_conteudo === "video" && post.video_url), [posts]);
  const lead = videos[0] || posts[0];
  const weekly = useMemo(() => posts.filter((post) => post.id !== lead?.id).slice(0, 3), [posts, lead]);
  const topics = useMemo(() => {
    const tags = uniqueBySlug(posts.flatMap((post) => post.tags || [])).map((item) => ({ ...item, kind: "tag" }));
    if (tags.length) return tags.slice(0, 8);
    return uniqueBySlug(posts.map((post) => post.categoria)).map((item) => ({ ...item, kind: "category" })).slice(0, 8);
  }, [posts]);
  const visible = useMemo(() => posts.filter((post) => {
    const contentMatch = filter === "all" || (filter === "video" ? post.tipo_conteudo === "video" : post.tipo_conteudo !== "video");
    if (!topic) return contentMatch;
    const topicMatch = topic.kind === "tag" ? (post.tags || []).some((tag) => tag.slug === topic.slug) : post.categoria?.slug === topic.slug;
    return contentMatch && topicMatch;
  }), [filter, posts, topic]);

  return <main className="blog-page">
    <section className="blog-hero"><div className="page-width blog-hero-grid"><div><span className="eyebrow"><Radio size={15} /> {text.eyebrow}</span><h1>{text.title}</h1><p>{text.intro}</p><div className="blog-search"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={text.search} aria-label={text.search} /></div></div></div></section>
    {lead && <section className="page-width blog-lead"><div className="blog-lead-media"><img className="blog-lead-cover" src={newsCover(lead)} alt="" />{lead.tipo_conteudo === "video" && <span className="blog-play"><Play size={22} fill="currentColor" /></span>}<span className="blog-lead-label">{lead.tipo_conteudo === "video" ? "Edukangola Agora" : text.week}</span></div><div className="blog-lead-copy"><span className="eyebrow muted">{lead.categoria?.nome || text.eyebrow}</span><h2>{lead.titulo}</h2><p>{lead.resumo || lead.conteudo?.slice(0, 220)}</p><div className="blog-meta"><CalendarDays size={14} /> {formatDate(lead.publicado_em, language)} {lead.tipo_conteudo === "video" && <><Video size={14} /> {lead.duracao_video || "Vídeo"}</>}</div><button className="primary-action" onClick={() => onNavigate(`/blog/${lead.slug}`)}>{text.watch} <ArrowRight size={16} /></button></div></section>}
    {!!weekly.length && <section className="page-width news-weekly-section"><div className="news-section-heading"><div><span className="eyebrow muted">{text.week}</span><h2>{text.weekCopy}</h2></div></div><div className="weekly-grid">{weekly.map((post) => <button className="weekly-card" key={post.id} onClick={() => onNavigate(`/blog/${post.slug}`)}><img className="weekly-image" src={newsCover(post)} alt="" /> <span className="weekly-copy"><small>{post.categoria?.nome || text.reading}</small><strong>{post.titulo}</strong><em><CalendarDays size={12} /> {formatDate(post.publicado_em, language)}</em></span><ArrowRight size={16} /></button>)}</div></section>}
    <section className="page-width news-topics-section"><div className="news-section-heading"><div><span className="eyebrow muted"><Hash size={14} /> {text.topics}</span><h2>{text.topicsCopy}</h2></div></div><div className="topic-chips"><button className={!topic ? "active" : ""} onClick={() => setTopic(null)}>{text.allTopics}</button>{topics.map((item) => <button key={`${item.kind}-${item.slug}`} className={topic?.slug === item.slug && topic?.kind === item.kind ? "active" : ""} onClick={() => setTopic(item)}>{item.nome}</button>)}</div></section>
    <section className="page-width blog-list-section"><div className="blog-section-head"><div><span className="eyebrow muted">{topic?.nome || text.latest}</span><h2>{topic ? `Conteúdos sobre ${topic.nome}.` : text.latest}</h2></div><div className="blog-tabs"><button className={filter === "all" ? "active" : ""} onClick={() => setFilter("all")}>{text.all}</button>{videos.length > 0 && <button className={filter === "video" ? "active" : ""} onClick={() => setFilter("video")}>{text.videos}</button>}<button className={filter === "article" ? "active" : ""} onClick={() => setFilter("article")}>{text.articles}</button></div></div>{loading ? <p className="page-empty">A carregar publicações.</p> : !visible.length ? <p className="page-empty">{text.empty}</p> : <div className="blog-grid compact-news-grid">{visible.map((post) => <article className={`blog-card compact-news-card ${post.tipo_conteudo === "video" ? "is-video" : ""}`} key={post.id} onClick={() => onNavigate(`/blog/${post.slug}`)}><div className="blog-card-image"><img className="blog-card-cover" src={newsCover(post)} alt="" />{post.tipo_conteudo === "video" && <span className="blog-card-play"><Play size={14} fill="currentColor" /></span>}<span>{post.categoria?.nome || "Notícia"}</span></div><div className="blog-card-body"><div className="blog-meta"><CalendarDays size={12} /> {formatDate(post.publicado_em, language)}</div><h3>{post.titulo}</h3><span className="blog-read">{text.watch} <ArrowRight size={14} /></span></div></article>)}</div>}</section>
  </main>;
}
