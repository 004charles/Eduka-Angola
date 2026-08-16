import { ArrowRight, CheckCircle2, ClipboardCheck, CreditCard, SearchCheck, UsersRound } from "lucide-react";
import { useI18n } from "../lib/i18n";
import "./public-pages.css";

export default function HowItWorksPage({ onNavigate }) {
  const { t } = useI18n();
  const steps = [{ icon: SearchCheck, number: "01", title: t("how.step1"), copy: t("how.step1Copy") }, { icon: ClipboardCheck, number: "02", title: t("how.step2"), copy: t("how.step2Copy") }, { icon: CreditCard, number: "03", title: t("how.step3"), copy: t("how.step3Copy") }, { icon: CheckCircle2, number: "04", title: t("how.step4"), copy: t("how.step4Copy") }];
  return <main><section className="subpage-hero how-page-hero"><div className="page-width"><span className="eyebrow"><UsersRound size={15} /> {t("how.eyebrow")}</span><h1>{t("how.hero")}</h1><p>{t("how.heroCopy")}</p><button className="subpage-cta" onClick={() => onNavigate("/cursos")}>{t("how.cta")} <ArrowRight size={16} /></button></div></section><section className="page-width process-page"><div className="section-heading"><div><span className="eyebrow muted">{t("how.sectionEyebrow")}</span><h2>{t("how.title")}</h2><p>{t("how.copy")}</p></div></div><div className="process-grid">{steps.map(({ icon: Icon, number, title, copy }) => <article key={number}><span className="process-number">{number}</span><Icon size={25} /><h3>{title}</h3><p>{copy}</p></article>)}</div><div className="process-note"><strong>{t("how.noteTitle")}</strong><span>{t("how.noteCopy")}</span><button className="text-action" onClick={() => onNavigate("/cursos")}>{t("how.noteLink")} <ArrowRight size={16} /></button></div></section></main>;
}
