import { BookOpen, GraduationCap, MapPin } from "lucide-react";
import CampaignCarousel from "../components/CampaignCarousel";
import CourseEditorialShowcase from "../components/CourseEditorialShowcase";
import HomeCentresShowcase from "../components/HomeCentresShowcase";
import { useI18n } from "../lib/i18n";
import "./public-pages.css";

export default function HomePage({ data, loading, onNavigate, onAnnounce }) {
  const { t } = useI18n();
  return <main id="top"><CampaignCarousel onNavigate={onNavigate} /><section className="trust-strip"><div className="page-width trust-inner"><span><GraduationCap size={20} /> {t("home.trustCentres")}</span><span><MapPin size={20} /> {t("home.trustVideos")}</span><span><BookOpen size={20} /> {t("home.trustClarity")}</span></div></section><CourseEditorialShowcase data={data} onNavigate={onNavigate} onAnnounce={onAnnounce} /><HomeCentresShowcase data={data} onNavigate={onNavigate} /></main>;
}
