import { useEffect, useState } from "react";
import { Menu, Moon, Search, Sun, UserRound, X } from "lucide-react";
import QuickSearch from "./QuickSearch";
import { LANGUAGES, useI18n } from "../lib/i18n";
import "./public-layout.css";

function Brand({ onNavigate, label }) {
  return (
    <a className="brand" href="/" onClick={(event) => { event.preventDefault(); onNavigate("/"); }} aria-label={label}>
      <img src="/eduka-mark.png" alt="" />
      <span>eduk<span>angola</span></span>
    </a>
  );
}

export default function PublicLayout({ children, student, theme, language, onThemeChange, onLanguageChange, onNavigate, path, suggestions }) {
  const { t } = useI18n();
  const [menuOpen, setMenuOpen] = useState(false);
  const [quickSearchOpen, setQuickSearchOpen] = useState(false);
  const isAuthPath = ["/entrar", "/criar-conta", "/verificar-email", "/recuperar-palavra-passe", "/redefinir-palavra-passe"].includes(path);
  const goTo = (event, destination) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey) return;
    event.preventDefault();
    setMenuOpen(false);
    onNavigate(destination);
  };

  const items = [
    { href: "/cursos", label: t("nav.explore") },
    { href: "/blog", label: t("nav.news") },
    { href: "/eventos", label: "Eventos" },
    { href: "/centros", label: t("nav.centres") },
    { href: "/como-funciona", label: t("nav.how") },
    { href: "/sobre", label: t("nav.about") },
  ];
  const studentFirstName = student?.nome?.trim().split(/\s+/)[0] || "Aluno";

  useEffect(() => {
    const handleShortcut = (event) => {
      const target = event.target;
      const isTyping = target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target?.isContentEditable;
      if (!isTyping && (event.key === "/" || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k"))) {
        event.preventDefault();
        setQuickSearchOpen(true);
      }
    };
    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, []);

  return (
    <div className={isAuthPath ? "site-shell auth-site-shell" : "site-shell"}>
      <header className="topbar">
        <div className="page-width topbar-inner">
          <Brand onNavigate={onNavigate} label="Edukangola" />
          <nav className={menuOpen ? "main-nav open" : "main-nav"} aria-label="Navegação principal">
            {items.map((item) => <a key={item.href} className={path === item.href ? "nav-active" : ""} href={item.href} onClick={(event) => goTo(event, item.href)}>{item.label}</a>)}
          </nav>
          <div className="topbar-actions">
            <button className="header-search-trigger" onClick={() => setQuickSearchOpen(true)} aria-label={t("nav.openSearch")}><Search size={18} /></button>
            <a className="header-centres-link" href="/para-centros" onClick={(event) => goTo(event, "/para-centros")}>{t("nav.forCentres")}</a>
            <label className="language-picker"><span className="sr-only">{t("nav.language")}</span><select value={language} onChange={(event) => onLanguageChange(event.target.value)} aria-label={t("nav.language")}>{LANGUAGES.map((item) => <option key={item.code} value={item.code}>{item.short}</option>)}</select></label>
            <button className="theme-button" onClick={onThemeChange} aria-label={t("nav.theme")}>{theme === "light" ? <Moon size={18} /> : <Sun size={18} />}</button>
            {student ? <a className="student-account-link" href="/aluno" onClick={(event) => goTo(event, "/aluno")} aria-label={t("nav.openStudent", { name: studentFirstName })}><span className="student-account-avatar" aria-hidden="true"><UserRound size={15} /></span><span className="student-account-copy"><small>{t("nav.activeAccount")}</small><strong>{studentFirstName}</strong></span></a> : <><a className="login-link" href="/entrar" onClick={(event) => goTo(event, "/entrar")}>{t("nav.login")}</a><a className="header-cta" href="/criar-conta" onClick={(event) => goTo(event, "/criar-conta")}>{t("nav.createAccount")}</a></>}
            <button className="menu-button" onClick={() => setMenuOpen((open) => !open)} aria-label={t("nav.openSearch")}>{menuOpen ? <X /> : <Menu />}</button>
          </div>
        </div>
      </header>
      {children}
      {!isAuthPath && <footer className="footer"><div className="page-width footer-inner"><Brand onNavigate={onNavigate} label="Edukangola" /><p>{t("footer.tagline")}</p><span>Feito por Carlos Muquissi e Nelson Muquissi</span><span>© 2026 Edukangola</span></div></footer>}
      {quickSearchOpen && <QuickSearch suggestions={suggestions} onClose={() => setQuickSearchOpen(false)} onNavigate={onNavigate} />}
    </div>
  );
}
