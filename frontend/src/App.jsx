import { useCallback, useEffect, useRef, useState } from "react";
import PublicLayout from "./components/PublicLayout";
import LoadingScreen from "./components/LoadingScreen";
import HomePage from "./pages/HomePage";
import CoursesPage from "./pages/CoursesPage";
import CourseDetailPage from "./pages/CourseDetailPage";
import VideoCourseDetailPage from "./pages/VideoCourseDetailPage";
import CentersPage from "./pages/CentersPage";
import HowItWorksPage from "./pages/HowItWorksPage";
import AboutPage from "./pages/AboutPage";
import AuthPage from "./pages/AuthPage";
import CheckoutPage from "./pages/CheckoutPage";
import StudentDashboardPage from "./pages/StudentDashboardPage";
import StudentPreferencesPage from "./pages/StudentPreferencesPage";
import CenterProfilePage from "./pages/CenterProfilePage";
import ForCentersPage from "./pages/ForCentersPage";
import BlogPage from "./pages/BlogPage";
import BlogPostPage from "./pages/BlogPostPage";
import VideoLearningPage from "./pages/VideoLearningPage";
import PaymentResultPage from "./pages/PaymentResultPage";
import EventsPage from "./pages/EventsPage";
import EventDetailPage from "./pages/EventDetailPage";
import EventTicketsPage from "./pages/EventTicketsPage";
import LibraryPage from "./pages/LibraryPage";
import BookDetailPage from "./pages/BookDetailPage";
import BookReaderPage from "./pages/BookReaderPage";
import NotFoundPage from "./pages/NotFoundPage";
import { getStudentSession } from "./lib/auth-api";
import { I18nProvider, LANGUAGES } from "./lib/i18n";

function getRoute() { return `${window.location.pathname}${window.location.search}`; }

function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem("eduka-theme") || "light");
  const [language, setLanguage] = useState(() => {
    const saved = localStorage.getItem("eduka-language");
    return LANGUAGES.some((item) => item.code === saved) ? saved : "pt";
  });
  const [route, setRoute] = useState(getRoute);
  const [notice, setNotice] = useState("");
  const [homeData, setHomeData] = useState(null);
  const [homeDataLoading, setHomeDataLoading] = useState(true);
  const [appLoading, setAppLoading] = useState(true);
  const [student, setStudent] = useState(null);
  const sessionRequestId = useRef(0);

  useEffect(() => { document.documentElement.dataset.theme = theme; localStorage.setItem("eduka-theme", theme); }, [theme]);
  useEffect(() => { localStorage.setItem("eduka-language", language); }, [language]);
  useEffect(() => { const syncRoute = () => setRoute(getRoute()); window.addEventListener("popstate", syncRoute); return () => window.removeEventListener("popstate", syncRoute); }, []);
  useEffect(() => {
    let active = true; let finishTimer; const startedAt = Date.now();
    fetch("/api/public/home/").then((response) => { if (!response.ok) throw new Error("Falha ao carregar os dados públicos."); return response.json(); }).then((data) => active && setHomeData({ ...data, cursos: [...(data.cursos || []), ...(data.video_cursos || [])] })).catch(() => active && setHomeData({ cursos: [], turmas_abertas: [], centros_destaque: [] })).finally(() => { finishTimer = window.setTimeout(() => { if (active) { setHomeDataLoading(false); setAppLoading(false); } }, Math.max(0, 700 - (Date.now() - startedAt))); });
    return () => { active = false; window.clearTimeout(finishTimer); };
  }, []);
  useEffect(() => { window.scrollTo({ top: 0, behavior: "auto" }); }, [route]);

  const refreshStudentSession = useCallback(async () => {
    const requestId = ++sessionRequestId.current;
    try {
      const currentStudent = await getStudentSession();
      if (requestId === sessionRequestId.current) setStudent(currentStudent);
    } catch {
      if (requestId === sessionRequestId.current) setStudent(null);
    }
  }, []);

  useEffect(() => { refreshStudentSession(); }, [refreshStudentSession, route]);

  useEffect(() => {
    let active = true;
    const sincronizarFavoritos = async () => {
      if (!student) {
        window.__edukaFavoriteIds = [];
        window.dispatchEvent(new CustomEvent("eduka:favorites-changed", { detail: { ids: [] } }));
        return;
      }
      try {
        const response = await fetch("/backend/auth/api/react/aluno/favoritos/", { credentials: "same-origin", headers: { Accept: "application/json" } });
        const data = await response.json().catch(() => ({}));
        if (!active || !response.ok) return;
        const ids = (data.cursos || []).map((curso) => String(curso.id));
        window.__edukaFavoriteIds = ids;
        window.dispatchEvent(new CustomEvent("eduka:favorites-changed", { detail: { ids } }));
      } catch {
        // A interface mantém o estado anterior se a sincronização de sessão falhar.
      }
    };
    sincronizarFavoritos();
    return () => { active = false; };
  }, [student]);

  useEffect(() => {
    const syncSessionOnReturn = () => refreshStudentSession();
    const syncVisibleSession = () => {
      if (document.visibilityState === "visible") refreshStudentSession();
    };
    window.addEventListener("focus", syncSessionOnReturn);
    document.addEventListener("visibilitychange", syncVisibleSession);
    return () => {
      window.removeEventListener("focus", syncSessionOnReturn);
      document.removeEventListener("visibilitychange", syncVisibleSession);
    };
  }, [refreshStudentSession]);

  const navigate = (destination, scroll = true) => { window.history.pushState({}, "", destination); setRoute(getRoute()); if (scroll) window.scrollTo({ top: 0, behavior: "smooth" }); };
  const announce = (message) => { setNotice(message); window.setTimeout(() => setNotice(""), 3200); };
  if (appLoading) return <LoadingScreen theme={theme} />;

  const [pathname, queryString = ""] = route.split("?");
  const searchParams = new URLSearchParams(queryString);
  const catalogFilters = Object.fromEntries(searchParams.entries());
  const centerInviteToken = searchParams.get("convite");
  const authModes = { "/entrar": "login", "/criar-conta": "register", "/verificar-email": "verify", "/recuperar-palavra-passe": "recover", "/redefinir-palavra-passe": "reset" };
  const courseRouteMatch = pathname.match(/^\/cursos\/(\d+)\/?$/);
  const videoCourseRouteMatch = pathname.match(/^\/video-cursos\/([^/]+)\/?$/);
  const learningVideoRouteMatch = pathname.match(/^\/aprender\/video\/([^/]+)\/?$/);
  const checkoutCourseRouteMatch = pathname.match(/^\/inscrever\/(\d+)\/?$/);
  const checkoutVideoRouteMatch = pathname.match(/^\/comprar\/([^/]+)\/?$/);
  const centerRouteMatch = pathname.match(/^\/centros\/(\d+)\/?$/);
  const blogPostRouteMatch = pathname.match(/^\/blog\/([^/]+)\/?$/);
  const eventRouteMatch = pathname.match(/^\/eventos\/([^/]+)\/?$/);
  const libraryBookRouteMatch = pathname.match(/^\/biblioteca\/([^/]+)\/?$/);
  const libraryReaderRouteMatch = pathname.match(/^\/ler\/([^/]+)\/?$/);
  const courseId = courseRouteMatch ? Number(courseRouteMatch[1]) : null;
  const checkoutCourseId = checkoutCourseRouteMatch ? Number(checkoutCourseRouteMatch[1]) : null;
  const selectedCourse = courseId ? homeData?.cursos?.find((course) => course.id === courseId) : null;
  const checkoutCourse = checkoutCourseId ? homeData?.cursos?.find((course) => course.id === checkoutCourseId) : null;
  let page;
  if (pathname === "/") page = <HomePage data={homeData} loading={homeDataLoading} onNavigate={navigate} onAnnounce={announce} />;
  else if (authModes[pathname]) page = <AuthPage key={pathname} mode={authModes[pathname]} courses={homeData?.cursos || []} onNavigate={navigate} onSessionReady={refreshStudentSession} />;
  else if (pathname === "/aluno") page = <StudentDashboardPage onNavigate={navigate} />;
  else if (pathname === "/aluno/preferencias") page = <StudentPreferencesPage onNavigate={navigate} />;
  else if (pathname === "/pagamento/sucesso" || pathname === "/pagamento/sucesso/") page = <PaymentResultPage onNavigate={navigate} />;
  else if (pathname === "/pagamento/cancelado" || pathname === "/pagamento/cancelado/") page = <PaymentResultPage onNavigate={navigate} />;
  else if (checkoutCourseRouteMatch) page = <CheckoutPage kind="presencial" course={checkoutCourse} turmas={homeData?.turmas_abertas || []} onNavigate={navigate} />;
  else if (checkoutVideoRouteMatch) page = <CheckoutPage kind="video" slug={decodeURIComponent(checkoutVideoRouteMatch[1])} onNavigate={navigate} />;
  else if (centerRouteMatch) page = <CenterProfilePage centerId={Number(centerRouteMatch[1])} onNavigate={navigate} />;
  else if (eventRouteMatch) page = <EventDetailPage slug={decodeURIComponent(eventRouteMatch[1])} student={student} onNavigate={navigate} onAnnounce={announce} />;
  else if (pathname === "/eventos" || pathname === "/eventos/" || pathname === "/eventosv" || pathname === "/eventosv/") page = <EventTicketsPage student={student} onNavigate={navigate} onAnnounce={announce} />;
  else if (libraryReaderRouteMatch) page = <BookReaderPage slug={decodeURIComponent(libraryReaderRouteMatch[1])} student={student} onNavigate={navigate} onAnnounce={announce} />;
  else if (libraryBookRouteMatch) page = <BookDetailPage slug={decodeURIComponent(libraryBookRouteMatch[1])} student={student} onNavigate={navigate} onAnnounce={announce} />;
  else if (pathname === "/biblioteca" || pathname === "/biblioteca/") page = <LibraryPage onNavigate={navigate} />;
  else if (pathname === "/cursos") page = <CoursesPage data={homeData} loading={homeDataLoading} initialFilters={catalogFilters} onNavigate={navigate} onAnnounce={announce} />;
  else if (courseRouteMatch) page = <CourseDetailPage course={selectedCourse} courses={homeData?.cursos} turmas={homeData?.turmas_abertas} loading={homeDataLoading} onNavigate={navigate} onAnnounce={announce} />;
  else if (videoCourseRouteMatch) page = <VideoCourseDetailPage slug={decodeURIComponent(videoCourseRouteMatch[1])} student={student} onNavigate={navigate} />;
  else if (learningVideoRouteMatch) page = <VideoLearningPage slug={decodeURIComponent(learningVideoRouteMatch[1])} onNavigate={navigate} />;
  else if (pathname === "/centros") page = <CentersPage data={homeData} loading={homeDataLoading} onNavigate={navigate} />;
  else if (pathname === "/para-centros") page = <ForCentersPage inviteToken={centerInviteToken} onNavigate={navigate} onAnnounce={announce} />;
  else if (blogPostRouteMatch) page = <BlogPostPage slug={decodeURIComponent(blogPostRouteMatch[1])} onNavigate={navigate} />;
  else if (pathname === "/blog" || pathname === "/blog/") page = <BlogPage language={language} onNavigate={navigate} />;
  else if (pathname === "/como-funciona") page = <HowItWorksPage onNavigate={navigate} />;
  else if (pathname === "/sobre" || pathname === "/sobre-a-edukangola") page = <AboutPage data={homeData} student={student} onNavigate={navigate} />;
  else page = <NotFoundPage onNavigate={navigate} />;

  return <I18nProvider language={language} onLanguageChange={setLanguage}><PublicLayout suggestions={homeData?.cursos || []} student={student} theme={theme} language={language} path={pathname} onThemeChange={() => setTheme(theme === "light" ? "dark" : "light")} onLanguageChange={setLanguage} onNavigate={navigate}>{page}{notice && <div className="notice" role="status">{notice}</div>}</PublicLayout></I18nProvider>;
}

export default App;
