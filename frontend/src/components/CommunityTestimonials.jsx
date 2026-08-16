import { useState } from "react";
import { MessageCircle, Star } from "lucide-react";

const content = {
  pt: { eyebrow: "Comunidade Edukangola", title: "Experiências que ajudam outras pessoas a avançar.", intro: "Partilhe como a Edukangola contribuiu para o seu percurso. Todas as experiências passam por revisão antes de serem publicadas.", share: "Partilhar a minha experiência", signIn: "Entrar para partilhar", rating: "A sua avaliação", consent: "Autorizo a análise e a possível publicação deste depoimento na página da Edukangola.", fullName: "Mostrar o meu nome completo", send: "Enviar para revisão", sending: "A enviar…", submitted: "A sua experiência foi enviada para revisão.", empty: "Os primeiros depoimentos aprovados da comunidade aparecerão aqui.", textLabel: "Conte a sua experiência", placeholder: "O que encontrou na Edukangola e como isso ajudou no seu próximo passo?", privacy: "Se não escolher mostrar o nome completo, publicaremos apenas o seu primeiro nome e inicial." },
  en: { eyebrow: "Edukangola community", title: "Experiences that help others move forward.", intro: "Share how Edukangola contributed to your journey. Every experience is reviewed before publication.", share: "Share my experience", signIn: "Sign in to share", rating: "Your rating", consent: "I authorise the review and possible publication of this testimonial on Edukangola.", fullName: "Show my full name", send: "Send for review", sending: "Sending…", submitted: "Your experience was sent for review.", empty: "The first approved community testimonials will appear here.", textLabel: "Tell us about your experience", placeholder: "What did you find on Edukangola and how did it help your next step?", privacy: "If you do not choose to show your full name, we will publish only your first name and initial." },
  fr: { eyebrow: "Communauté Edukangola", title: "Des expériences qui aident les autres à avancer.", intro: "Partagez la manière dont Edukangola a contribué à votre parcours. Chaque expérience est examinée avant publication.", share: "Partager mon expérience", signIn: "Se connecter pour partager", rating: "Votre évaluation", consent: "J’autorise l’examen et la publication éventuelle de ce témoignage sur Edukangola.", fullName: "Afficher mon nom complet", send: "Envoyer pour examen", sending: "Envoi…", submitted: "Votre expérience a été envoyée pour examen.", empty: "Les premiers témoignages approuvés de la communauté apparaîtront ici.", textLabel: "Racontez votre expérience", placeholder: "Qu’avez-vous trouvé sur Edukangola et comment cela a-t-il aidé votre prochaine étape ?", privacy: "Sans nom complet, nous publierons seulement votre prénom et initiale." },
  zh: { eyebrow: "Edukangola 社区", title: "帮助他人不断前进的真实体验。", intro: "分享 Edukangola 如何帮助您的学习历程。每条体验都会在发布前经过审核。", share: "分享我的体验", signIn: "登录后分享", rating: "您的评分", consent: "我授权 Edukangola 审核并可能公开发布这条体验。", fullName: "显示我的全名", send: "提交审核", sending: "正在提交…", submitted: "您的体验已提交审核。", empty: "首批获批准的社区体验将显示在这里。", textLabel: "分享您的体验", placeholder: "您在 Edukangola 找到了什么？它怎样帮助了您的下一步？", privacy: "如不选择显示全名，我们只会公开您的名字和姓氏首字母。" },
};

function csrfToken() {
  return document.cookie.split("; ").find((item) => item.startsWith("csrftoken="))?.split("=")[1] || "";
}

export default function CommunityTestimonials({ testimonials = [], student, language = "pt", onNavigate }) {
  const copy = content[language] || content.pt;
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ texto: "", nota: 5, consentimento_publico: false, publicar_nome: false });
  const [status, setStatus] = useState({ type: "", message: "" });
  const [sending, setSending] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setSending(true); setStatus({ type: "", message: "" });
    try {
      const response = await fetch("/api/public/comunidade/depoimentos/", { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", "X-CSRFToken": decodeURIComponent(csrfToken()) }, body: JSON.stringify(form) });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Não foi possível enviar o depoimento.");
      setStatus({ type: "success", message: data.detail || copy.submitted });
      setForm({ texto: "", nota: 5, consentimento_publico: false, publicar_nome: false });
      setOpen(false);
    } catch (error) { setStatus({ type: "error", message: error.message }); }
    finally { setSending(false); }
  }

  return <section className="about-community"><div className="page-width">
    <div className="about-community-heading"><div><span className="eyebrow muted"><MessageCircle size={15} /> {copy.eyebrow}</span><h2>{copy.title}</h2><p>{copy.intro}</p></div><button className="about-secondary-action" onClick={() => student ? setOpen((value) => !value) : onNavigate("/entrar")}>{student ? copy.share : copy.signIn}</button></div>
    {status.message && <p className={`community-status ${status.type}`}>{status.message}</p>}
    {open && <form className="community-form" onSubmit={submit}><label>{copy.textLabel}<textarea minLength="30" maxLength="1000" required value={form.texto} placeholder={copy.placeholder} onChange={(event) => setForm({ ...form, texto: event.target.value })} /></label><div className="community-form-footer"><fieldset><legend>{copy.rating}</legend><div className="community-stars">{[1,2,3,4,5].map((value) => <button key={value} type="button" aria-label={`${value} estrelas`} className={value <= form.nota ? "selected" : ""} onClick={() => setForm({ ...form, nota: value })}><Star size={18} fill="currentColor" /></button>)}</div></fieldset><div className="community-consents"><label><input type="checkbox" required checked={form.consentimento_publico} onChange={(event) => setForm({ ...form, consentimento_publico: event.target.checked })} />{copy.consent}</label><label><input type="checkbox" checked={form.publicar_nome} onChange={(event) => setForm({ ...form, publicar_nome: event.target.checked })} />{copy.fullName}</label><small>{copy.privacy}</small></div><button className="subpage-cta" disabled={sending}>{sending ? copy.sending : copy.send}</button></div></form>}
    {testimonials.length > 0 ? <div className="community-testimonial-grid">{testimonials.map((item) => <article key={item.id}><div className="community-testimonial-top">{item.foto ? <img src={item.foto} alt="" /> : <span>{item.nome?.slice(0, 1) || "E"}</span>}<div><strong>{item.nome}</strong><small>{item.contexto}</small></div><div className="community-rating">{"★".repeat(item.nota || 5)}</div></div><p>“{item.texto}”</p></article>)}</div> : <div className="community-empty"><MessageCircle size={22} /><span>{copy.empty}</span></div>}
  </div></section>;
}
