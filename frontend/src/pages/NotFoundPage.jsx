import { ArrowLeft } from "lucide-react";
import "./public-pages.css";

export default function NotFoundPage({ onNavigate }) { return <main className="page-width not-found-page"><span className="eyebrow muted">Página não encontrada</span><h1>Esta página não existe ou já foi movida.</h1><p>Volte à página inicial para explorar cursos e centros de formação.</p><button className="primary-action" onClick={() => onNavigate("/")}><ArrowLeft size={17} /> Voltar ao início</button></main>; }
