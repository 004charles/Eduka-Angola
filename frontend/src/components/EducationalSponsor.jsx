import { ArrowUpRight, BadgeCheck } from "lucide-react";
import "./educational-sponsor.css";

export default function EducationalSponsor({ data, onNavigate }) {
  const sponsor = data?.patrocinios_educativos?.[0];
  if (!sponsor) return null;
  const navigate = () => onNavigate(sponsor.url || "/cursos");
  return <section className="page-width educational-sponsor-wrap" aria-label="Conteúdo patrocinado"><article className={`educational-sponsor${sponsor.imagem_url ? " has-image" : ""}`} style={sponsor.imagem_url ? { "--sponsor-image": `url(${sponsor.imagem_url})` } : undefined}><div className="educational-sponsor-overlay" /><div className="educational-sponsor-copy"><span className="sponsor-label"><BadgeCheck size={14} /> Patrocinado</span><small>{sponsor.etiqueta}</small><h2>{sponsor.titulo}</h2><p>{sponsor.subtitulo}</p><button type="button" onClick={navigate}>{sponsor.texto_botao} <ArrowUpRight size={16} /></button></div><div className="educational-sponsor-disclosure"><span>Conteúdo educativo seleccionado e identificado pela Edukangola.</span><button type="button" onClick={() => onNavigate("/politica-privacidade")}>Como funciona</button></div></article></section>;
}
