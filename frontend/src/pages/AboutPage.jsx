import { ArrowRight, BookOpenCheck, Building2, Camera, CheckCircle2, Globe2, HeartHandshake, Image as ImageIcon, Lightbulb, MapPinned, ShieldCheck, Sparkles, UsersRound } from "lucide-react";
import { useI18n } from "../lib/i18n";
import "./about-page.css";

const copy = {
  pt: {
    eyebrow: "Sobre a plataforma",
    title: "Educação que aproxima oportunidades de quem quer avançar.",
    intro: "A Edukangola é uma plataforma angolana para descobrir formações, conhecer centros e tomar decisões com informação clara antes de se inscrever ou comprar um curso.",
    browse: "Explorar cursos",
    centres: "Conhecer centros",
    proof: "Uma plataforma feita para o contexto local",
    proofCopy: "Organizamos cursos presenciais, turmas, vídeo-cursos e centros de formação num só espaço, com as condições publicadas por cada entidade.",
    mission: "A nossa missão",
    missionCopy: "Tornar a formação mais fácil de encontrar, comparar e acompanhar, ajudando estudantes e centros a criar relações de aprendizagem mais transparentes.",
    vision: "A nossa visão",
    visionCopy: "Contribuir para um ecossistema de formação angolano mais acessível, confiável e ligado às oportunidades reais do país.",
    values: "Os princípios que orientam a Edukangola",
    valuesCopy: "A plataforma deve simplificar a decisão sem substituir o papel dos centros. Por isso, cada experiência é construída à volta de clareza, confiança e utilidade.",
    value1: "Clareza primeiro", value1Copy: "Mostramos modalidade, local, turma, vagas e condições de pagamento antes da inscrição.",
    value2: "Confiança local", value2Copy: "Valorizamos centros de formação e informação pública que ajudam o aluno a escolher melhor.",
    value3: "Acesso com propósito", value3Copy: "A tecnologia serve para aproximar pessoas de competências e oportunidades concretas.",
    journey: "Como ligamos as duas pontas",
    journeyCopy: "Para estudantes, a Edukangola é uma vitrina de aprendizagem. Para os centros, é uma forma de apresentar a sua oferta e receber inscrições mais organizadas.",
    statCourses: "cursos publicados", statCentres: "centros apresentados", statFormats: "formas de aprender", impact: "O impacto que já conseguimos medir", impactCopy: "Indicadores agregados da plataforma, atualizados a partir dos registos públicos do Edukangola.", students: "alunos ativos", confirmed: "inscrições confirmadas", gallery: "A Edukangola em imagens", galleryCopy: "Este espaço está preparado para receber fotografias reais de atividades, centros e momentos de aprendizagem.", galleryEmpty: "As fotografias serão adicionadas aqui quando a galeria pública estiver disponível.",
    ctaTitle: "Encontre o próximo passo para a sua formação.",
    ctaCopy: "Explore o catálogo ou conheça os centros que já apresentam as suas formações na Edukangola.",
  },
  en: {
    eyebrow: "About the platform", title: "Education that brings opportunities closer to people ready to move forward.",
    intro: "Edukangola is an Angolan platform for discovering training, learning about centres and making informed decisions before enrolling or buying a course.", browse: "Explore courses", centres: "Meet the centres", proof: "A platform made for the local context", proofCopy: "We bring together in-person courses, classes, video courses and training centres in one place, with each provider’s published conditions.", mission: "Our mission", missionCopy: "Make training easier to find, compare and follow, helping students and centres build more transparent learning relationships.", vision: "Our vision", visionCopy: "Contribute to a more accessible, trusted training ecosystem in Angola, connected to real opportunities.", values: "The principles behind Edukangola", valuesCopy: "The platform should simplify decisions without replacing the role of training centres. Every experience is built around clarity, trust and usefulness.", value1: "Clarity first", value1Copy: "We show format, location, class, vacancies and payment conditions before enrolment.", value2: "Local trust", value2Copy: "We value training centres and public information that help students choose better.", value3: "Purposeful access", value3Copy: "Technology should connect people to practical skills and real opportunities.", journey: "Connecting both sides", journeyCopy: "For students, Edukangola is a learning showcase. For centres, it is a way to present their offer and receive more organised applications.", statCourses: "published courses", statCentres: "centres listed", statFormats: "ways to learn", impact: "The impact we can already measure", impactCopy: "Aggregated platform indicators, updated from Edukangola’s public records.", students: "active students", confirmed: "confirmed enrolments", gallery: "Edukangola in images", galleryCopy: "This space is ready for real photographs of activities, centres and learning moments.", galleryEmpty: "Photographs will be added here when the public gallery is available.", ctaTitle: "Find your next step in training.",
 ctaCopy: "Explore the catalogue or meet the centres already presenting their training on Edukangola.",
  },
  fr: {
    eyebrow: "À propos de la plateforme", title: "Une éducation qui rapproche les opportunités de ceux qui veulent avancer.",
    intro: "Edukangola est une plateforme angolaise pour découvrir des formations, connaître les centres et décider avec des informations claires avant de s’inscrire ou d’acheter un cours.", browse: "Explorer les cours", centres: "Découvrir les centres", proof: "Une plateforme pensée pour le contexte local", proofCopy: "Nous réunissons formations en présentiel, groupes, cours vidéo et centres de formation dans un seul espace, avec les conditions publiées par chaque entité.", mission: "Notre mission", missionCopy: "Rendre les formations plus faciles à trouver, comparer et suivre, afin d’aider les étudiants et les centres à créer des relations d’apprentissage plus transparentes.", vision: "Notre vision", visionCopy: "Contribuer à un écosystème de formation angolais plus accessible, fiable et lié aux opportunités réelles.", values: "Les principes d’Edukangola", valuesCopy: "La plateforme doit simplifier la décision sans remplacer le rôle des centres. Chaque expérience repose sur la clarté, la confiance et l’utilité.", value1: "La clarté d’abord", value1Copy: "Nous affichons le format, le lieu, le groupe, les places et les conditions de paiement avant l’inscription.", value2: "La confiance locale", value2Copy: "Nous valorisons les centres et les informations publiques qui aident à mieux choisir.", value3: "Un accès utile", value3Copy: "La technologie doit rapprocher les personnes des compétences et des opportunités concrètes.", journey: "Relier les deux côtés", journeyCopy: "Pour les étudiants, Edukangola est une vitrine de l’apprentissage. Pour les centres, c’est une manière de présenter leur offre et de recevoir des candidatures mieux organisées.", statCourses: "cours publiés", statCentres: "centres présentés", statFormats: "façons d’apprendre", impact: "L’impact que nous pouvons déjà mesurer", impactCopy: "Des indicateurs agrégés de la plateforme, actualisés à partir des données publiques d’Edukangola.", students: "étudiants actifs", confirmed: "inscriptions confirmées", gallery: "Edukangola en images", galleryCopy: "Cet espace est prêt à accueillir de vraies photos d’activités, de centres et de moments d’apprentissage.", galleryEmpty: "Les photos seront ajoutées ici lorsque la galerie publique sera disponible.", ctaTitle: "Trouvez votre prochaine étape de formation.",
 ctaCopy: "Explorez le catalogue ou découvrez les centres qui présentent déjà leurs formations sur Edukangola.",
  },
  zh: {
    eyebrow: "关于平台", title: "让教育机会更接近每一个想要进步的人。", intro: "Edukangola 是一个安哥拉培训平台，帮助用户发现课程、了解培训中心，并在报名或购买前根据清晰的信息作出决定。", browse: "探索课程", centres: "了解培训中心", proof: "为本地需求打造的平台", proofCopy: "我们在同一空间汇集线下课程、班级、视频课程和培训中心，并展示各机构发布的条件。", mission: "我们的使命", missionCopy: "让培训更容易被发现、比较和跟进，帮助学生与培训中心建立更透明的学习关系。", vision: "我们的愿景", visionCopy: "为安哥拉建设更易获得、更可信并连接真实机会的培训生态。", values: "Edukangola 的原则", valuesCopy: "平台应该简化选择，而不是取代培训中心的作用。因此，我们始终重视清晰、信任和实用性。", value1: "清晰优先", value1Copy: "报名之前，我们展示课程形式、地点、班级、名额和付款条件。", value2: "本地信任", value2Copy: "我们重视培训中心和帮助学生作出更好选择的公开信息。", value3: "有目标的连接", value3Copy: "科技应该把人们连接到实际技能和真实机会。", journey: "连接学习的两端", journeyCopy: "对学生来说，Edukangola 是学习机会的展示平台；对中心来说，它是展示课程并接收更有组织报名的渠道。", statCourses: "已发布课程", statCentres: "已展示中心", statFormats: "学习方式", impact: "我们已经可以衡量的影响", impactCopy: "根据 Edukangola 公共记录更新的平台汇总指标。", students: "活跃学生", confirmed: "已确认报名", gallery: "图片中的 Edukangola", galleryCopy: "这里将展示活动、培训中心和学习时刻的真实照片。", galleryEmpty: "公共图片库开放后，照片将会添加到这里。", ctaTitle: "找到培训的下一步。", ctaCopy: "探索课程目录，或了解已经在 Edukangola 展示培训的中心。",
  },
};

function Stat({ value, label }) { return <div className="about-stat"><strong>{value}</strong><span>{label}</span></div>; }

export default function AboutPage({ data, onNavigate }) {
  const { language } = useI18n();
  const text = copy[language] || copy.pt;
  const courses = data?.cursos || [];
  const centres = data?.centros_destaque || [];
  const formats = new Set(courses.map((course) => course.modalidade_codigo || course.modalidade).filter(Boolean)).size || 2;
  const impact = data?.impacto || {};
  const impactItems = [
    { value: impact.alunos_ativos, label: text.students, icon: UsersRound },
    { value: impact.centros_ativos, label: text.statCentres, icon: Building2 },
    { value: impact.cursos_publicados, label: text.statCourses, icon: BookOpenCheck },
    { value: impact.inscricoes_confirmadas, label: text.confirmed, icon: CheckCircle2 },
  ];
  const gallery = data?.galeria || [];
  const galleryPlaceholders = [
    { icon: Camera, title: "Atividades de aprendizagem" },
    { icon: Building2, title: "Centros de formação" },
    { icon: MapPinned, title: "Comunidade Edukangola" },
  ];
  return <main className="about-page">
    <section className="about-hero"><div className="page-width about-hero-grid"><div><span className="eyebrow"><Sparkles size={15} /> {text.eyebrow}</span><h1>{text.title}</h1><p className="about-lead">{text.intro}</p><div className="about-actions"><button className="subpage-cta" onClick={() => onNavigate("/cursos")}>{text.browse} <ArrowRight size={16} /></button><button className="about-secondary-action" onClick={() => onNavigate("/centros")}>{text.centres}</button></div></div><div className="about-hero-card"><div className="about-orbit about-orbit-one" /><div className="about-orbit about-orbit-two" /><div className="about-hero-icon"><Globe2 size={34} /></div><span>AO</span><strong>Edukangola</strong><small>{text.proof}</small></div></div></section>
    <section className="page-width about-proof"><div className="about-proof-copy"><span className="eyebrow muted">{text.proof}</span><h2>{text.proofCopy}</h2></div><div className="about-stats"><Stat value={courses.length || "—"} label={text.statCourses} /><Stat value={centres.length || "—"} label={text.statCentres} /><Stat value={formats} label={text.statFormats} /></div></section>
    <section className="about-impact"><div className="page-width"><div className="about-impact-heading"><div><span className="eyebrow"><Sparkles size={15} /> Edukangola</span><h2>{text.impact}</h2><p>{text.impactCopy}</p></div></div><div className="about-impact-grid">{impactItems.map(({ value, label, icon: Icon }) => <article key={label}><Icon size={21} /><strong>{value == null ? "—" : value}</strong><span>{label}</span></article>)}</div></div></section>
    <section className="page-width about-principles"><div className="about-principles-intro"><span className="eyebrow muted"><HeartHandshake size={15} /> Edukangola</span><h2>{text.mission}</h2><p>{text.missionCopy}</p><div className="about-vision"><Lightbulb size={22} /><div><strong>{text.vision}</strong><p>{text.visionCopy}</p></div></div></div><div className="about-values"><span className="eyebrow muted">{text.values}</span><h2>{text.valuesCopy}</h2><div className="about-value-grid"><article><ShieldCheck size={22} /><h3>{text.value1}</h3><p>{text.value1Copy}</p></article><article><Building2 size={22} /><h3>{text.value2}</h3><p>{text.value2Copy}</p></article><article><BookOpenCheck size={22} /><h3>{text.value3}</h3><p>{text.value3Copy}</p></article></div></div></section>
    <section className="about-bridge"><div className="page-width about-bridge-grid"><div><span className="eyebrow"><UsersRound size={15} /> Edukangola</span><h2>{text.journey}</h2><p>{text.journeyCopy}</p></div><div className="about-bridge-visual"><div className="about-bridge-node"><BookOpenCheck size={20} /><span>Aluno</span></div><div className="about-bridge-line" /><div className="about-bridge-node"><Building2 size={20} /><span>Centro</span></div><div className="about-bridge-check"><CheckCircle2 size={18} /></div></div></div></section>
    <section className="page-width about-gallery"><div className="about-gallery-heading"><div><span className="eyebrow muted"><ImageIcon size={15} /> Edukangola</span><h2>{text.gallery}</h2><p>{text.galleryCopy}</p></div></div>{gallery.length > 0 ? <div className="about-gallery-grid">{gallery.map((item) => <figure key={item.id}><img src={item.url} alt={item.legenda} /><figcaption>{item.legenda}</figcaption></figure>)}</div> : <div className="about-gallery-grid">{galleryPlaceholders.map(({ icon: Icon, title }) => <article className="about-gallery-placeholder" key={title}><Icon size={25} /><strong>{title}</strong><span>{text.galleryEmpty}</span></article>)}</div>}</section>
    <section className="page-width about-final-cta"><div><span className="eyebrow muted">Edukangola</span><h2>{text.ctaTitle}</h2><p>{text.ctaCopy}</p></div><div className="about-actions"><button className="subpage-cta" onClick={() => onNavigate("/cursos")}>{text.browse} <ArrowRight size={16} /></button><button className="about-secondary-action" onClick={() => onNavigate("/para-centros")}>{text.centres}</button></div></section>
  </main>;
}
