import { LocateFixed, MapPin, RefreshCw, ShieldCheck, X } from "lucide-react";
import { useMemo, useState } from "react";
import { backendUrl } from "../lib/backend-url";
import { etiquetaProduto, rotaDetalheProduto, textoRodapeProduto, tipoProduto } from "../lib/product-type";
import CourseCard from "./CourseCard";
import CourseShelf from "./CourseShelf";
import "./home-location-course-sections.css";

const LOCATION_CHOICE_KEY = "eduka-location-consent-v1";

function centreName(name) {
  return name?.replace(/Eduka-Angola/gi, "Edukangola") || "Centro de formação";
}

function toCourseCard(course) {
  return {
    ...course,
    category: course.categoria,
    title: course.titulo,
    centre: centreName(course.centro),
    productType: tipoProduto(course),
    productLabel: etiquetaProduto(course),
    mode: course.modalidade,
    schedule: textoRodapeProduto(course, null),
    imageUrl: course.imagem_url,
    detailUrl: rotaDetalheProduto(course),
    inscricaoUrl: backendUrl(course.inscricao_url),
  };
}

function saveMessage(onAnnounce) {
  return (message) => onAnnounce?.(
    message === "AUTH_REQUIRED"
      ? "Os cursos guardados estarão disponíveis após o login."
      : message,
  );
}

export function InternationalCoursesSection({ data, onAnnounce }) {
  const internationalCourses = useMemo(
    () => (data?.cursos || []).filter((course) => course.is_internacional).map(toCourseCard),
    [data],
  );

  if (!internationalCourses.length) return null;

  return (
    <CourseShelf
      id="cursos-internacionais"
      eyebrow="Formação no exterior"
      title="Cursos de centros internacionais."
      description="Explore formações publicadas por centros fora de Angola. A candidatura académica é analisada directamente pela instituição."
      courses={internationalCourses}
      featured
      onAnnounce={onAnnounce}
      collectionHref="/centros"
    />
  );
}

export function NearbyCoursesSection({ data, onAnnounce }) {
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");
  const [nearbyCourses, setNearbyCourses] = useState([]);
  const [selectedRegion, setSelectedRegion] = useState("");
  const [locationPromptOpen, setLocationPromptOpen] = useState(() => {
    try { return !window.localStorage.getItem(LOCATION_CHOICE_KEY); } catch { return true; }
  });
  const regions = useMemo(
    () => [...new Set((data?.cursos || []).map((course) => course.provincia).filter(Boolean))].sort((first, second) => first.localeCompare(second, "pt-PT")),
    [data],
  );
  const regionalCourses = useMemo(
    () => selectedRegion ? (data?.cursos || []).filter((course) => course.provincia === selectedRegion).slice(0, 8).map(toCourseCard) : [],
    [data, selectedRegion],
  );

  const rememberLocationChoice = (choice) => {
    try { window.localStorage.setItem(LOCATION_CHOICE_KEY, choice); } catch { /* A decisão mantém-se apenas nesta visita. */ }
  };

  const dismissLocationPrompt = (choice = "dismissed") => {
    rememberLocationChoice(choice);
    setLocationPromptOpen(false);
  };

  const locateUser = () => {
    rememberLocationChoice("approved");
    if (!navigator.geolocation) {
      setStatus("error");
      setMessage("Este navegador não disponibiliza localização. Escolha uma província para ver formações nessa região.");
      setLocationPromptOpen(false);
      return;
    }

    setStatus("loading");
    setMessage("A ligar ao GPS do seu dispositivo. Confirme a permissão do navegador para continuar.");
    navigator.geolocation.getCurrentPosition(async ({ coords }) => {
      try {
        const response = await fetch(
          backendUrl(`/api/public/cursos/proximos/?lat=${encodeURIComponent(coords.latitude)}&lng=${encodeURIComponent(coords.longitude)}&raio_km=75&limite=8`),
          { credentials: "same-origin" },
        );
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(payload.detail || "Não foi possível procurar centros próximos.");
        const results = (payload.cursos || []).map(toCourseCard);
        setNearbyCourses(results);
        setStatus("ready");
        setMessage(results.length ? `Encontrámos ${results.length} ${results.length === 1 ? "curso" : "cursos"} até ${payload.raio_km} km de si.` : "Ainda não existem cursos com localização confirmada num raio de 75 km. Escolha uma província para continuar a explorar.");
        setLocationPromptOpen(false);
      } catch (error) {
        setStatus("error");
        setMessage(error.message || "Não foi possível procurar centros próximos.");
        setLocationPromptOpen(false);
      }
    }, (error) => {
      setStatus("error");
      if (error.code === error.PERMISSION_DENIED) setMessage("A localização foi recusada no navegador. Pode autorizar novamente ou explorar por província, sem partilhar a sua posição.");
      else if (error.code === error.POSITION_UNAVAILABLE) setMessage("O GPS não conseguiu determinar a sua posição. Verifique se a localização do dispositivo está activa e tente novamente.");
      else if (error.code === error.TIMEOUT) setMessage("O GPS demorou mais do que o esperado. Tente novamente num local com melhor sinal ou explore por província.");
      else setMessage("Não foi possível obter a localização actual. Escolha uma província para continuar a explorar.");
      setLocationPromptOpen(false);
    }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 });
  };

  const requestLocation = () => setLocationPromptOpen(true);
  const announceSave = saveMessage(onAnnounce);

  return <>
    <section className={`page-width nearby-course-intro${nearbyCourses.length ? " has-results" : ""}`} aria-live="polite">
      <div className="nearby-course-copy">
        <span className="eyebrow muted"><LocateFixed size={14} /> Perto de si</span>
        <h2>Encontre cursos mais perto de si.</h2>
        <p>{message || "Autorize a localização apenas nesta pesquisa ou escolha uma província. A sua posição não é guardada."}</p>
        {(status !== "ready" || !nearbyCourses.length) && <div className="nearby-region-picker">
          <MapPin size={16} />
          <span>Explorar por província:</span>
          <div>{regions.map((region) => <button key={region} type="button" className={selectedRegion === region ? "is-selected" : ""} onClick={() => setSelectedRegion(region)}>{region}</button>)}</div>
        </div>}
      </div>
      <button type="button" className="nearby-location-button" onClick={requestLocation} disabled={status === "loading"}>
        {status === "loading" ? <RefreshCw size={17} className="is-spinning" /> : <LocateFixed size={17} />}
        {status === "loading" ? "A procurar" : "Usar a minha localização"}
      </button>
    </section>

    {nearbyCourses.length > 0 && <section id="cursos-proximos" className="page-width nearby-results" aria-labelledby="nearby-results-title">
      <div className="nearby-results-heading">
        <div>
          <span className="eyebrow muted"><MapPin size={14} /> Resultados por proximidade</span>
          <h3 id="nearby-results-title">Formações encontradas perto de si.</h3>
        </div>
        <a href="/cursos" className="nearby-results-link">Ver catálogo completo</a>
      </div>
      <div className="nearby-results-grid">
        {nearbyCourses.map((course) => <div className="nearby-result-card" key={`proximo-${course.id}`}><CourseCard course={course} onSave={announceSave} /></div>)}
      </div>
    </section>}

    {regionalCourses.length > 0 && <CourseShelf
      id="cursos-na-provincia"
      eyebrow={`Formações em ${selectedRegion}`}
      title={`Cursos disponíveis em ${selectedRegion}.`}
      description="Alternativa por região, sem partilha de localização."
      courses={regionalCourses}
      onAnnounce={onAnnounce}
      collectionHref={`/cursos?provincia=${encodeURIComponent(selectedRegion)}`}
    />}

    {locationPromptOpen && <div className="location-consent-overlay" role="presentation">
      <section className="location-consent-dialog" role="dialog" aria-modal="true" aria-labelledby="location-consent-title">
        <button type="button" className="location-consent-close" onClick={() => dismissLocationPrompt()} aria-label="Fechar pedido de localização"><X size={18} /></button>
        <span className="location-consent-icon"><LocateFixed size={23} /></span>
        <span className="location-consent-eyebrow"><ShieldCheck size={14} /> Privacidade primeiro</span>
        <h3 id="location-consent-title">Encontrar centros perto de si?</h3>
        <p>{status === "loading" ? "A ligar ao GPS do seu dispositivo. Confirme agora o aviso do navegador para continuar." : "Com a sua autorização, usaremos o GPS do navegador apenas nesta pesquisa para procurar cursos e centros próximos. A Edukangola não guarda a sua localização."}</p>
        <div className="location-consent-actions">
          <button type="button" className="location-consent-secondary" onClick={() => dismissLocationPrompt("declined")}>Agora não</button>
          <button type="button" className="location-consent-primary" onClick={locateUser} disabled={status === "loading"}>
            {status === "loading" ? <RefreshCw size={16} className="is-spinning" /> : <LocateFixed size={16} />}
            {status === "loading" ? "A pedir ao navegador" : "Permitir localização"}
          </button>
        </div>
      </section>
    </div>}
  </>;
}
