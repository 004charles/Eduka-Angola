import { ArrowRight, BookOpen, ChevronRight, GraduationCap, MapPin, SlidersHorizontal } from "lucide-react";
import CampaignCarousel from "../components/CampaignCarousel";
import DynamicCatalogShelves from "../components/DynamicCatalogShelves";
import SkillsDiscoverySection from "../components/SkillsDiscoverySection";
import RecommendedCoursesSection from "../components/RecommendedCoursesSection";
import { useI18n } from "../lib/i18n";
import "./public-pages.css";

const categories = [
  { key: "Technology", query: "Tecnologia", icon: "</>" },
  { key: "Business", query: "Gestão e Negócios", icon: "↗" },
  { key: "Languages", query: "Idiomas", icon: "Aa" },
  { key: "Design", query: "Design", icon: "✦" },
  { key: "Health", query: "Saúde", icon: "+" },
];

export default function HomePage({ data, loading, onNavigate, onAnnounce }) {
  const { t } = useI18n();
  const goToCatalogue = (query = "") => onNavigate(`/cursos${query ? `?q=${encodeURIComponent(query)}` : ""}`);

  return (
    <main id="top">
      <CampaignCarousel onNavigate={onNavigate} />
      <section className="trust-strip"><div className="page-width trust-inner"><span><GraduationCap size={20} /> {t("home.trustCentres")}</span><span><MapPin size={20} /> {t("home.trustVideos")}</span><span><BookOpen size={20} /> {t("home.trustClarity")}</span></div></section>
      <section className="page-width category-section">
        <div className="section-heading"><div><span className="eyebrow muted"><SlidersHorizontal size={14} /> {t("home.eyebrow")}</span><h2>{t("home.title")}</h2></div><button className="text-action" onClick={() => goToCatalogue()}>{t("home.allAreas")} <ArrowRight size={16} /></button></div>
        <div className="category-grid">{categories.map((category) => <button className="category-card" key={category.key} onClick={() => goToCatalogue(category.query)}><span className="category-icon">{category.icon}</span><span><strong>{t(`category.${category.key}`)}</strong><small>{t(`category.${category.key}Copy`)}</small></span><ChevronRight size={17} /></button>)}</div>
      </section>
      <SkillsDiscoverySection data={data} loading={loading} onAnnounce={onAnnounce} />
      <DynamicCatalogShelves data={data} loading={loading} onAnnounce={onAnnounce} collectionHref="/cursos" includeCatalog={false} />
      <RecommendedCoursesSection onNavigate={onNavigate} />
    </main>
  );
}
