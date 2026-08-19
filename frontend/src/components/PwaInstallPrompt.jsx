import { Download, X } from "lucide-react";
import { useEffect, useState } from "react";
import "./pwa-install-prompt.css";

const DISMISS_KEY = "edukangola-pwa-install-dismissed";

function isStandalone() {
  return window.matchMedia?.("(display-mode: standalone)").matches || window.navigator.standalone === true;
}

export default function PwaInstallPrompt() {
  const [installEvent, setInstallEvent] = useState(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (isStandalone() || sessionStorage.getItem(DISMISS_KEY)) return undefined;
    const onBeforeInstall = (event) => {
      event.preventDefault();
      setInstallEvent(event);
      setVisible(true);
    };
    const onInstalled = () => {
      setInstallEvent(null);
      setVisible(false);
    };
    window.addEventListener("beforeinstallprompt", onBeforeInstall);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", onBeforeInstall);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  const dismiss = () => {
    sessionStorage.setItem(DISMISS_KEY, "1");
    setVisible(false);
  };

  const install = async () => {
    if (!installEvent) return;
    installEvent.prompt();
    await installEvent.userChoice;
    setInstallEvent(null);
    setVisible(false);
  };

  if (!visible || !installEvent) return null;
  return <aside className="pwa-install-banner" aria-label="Instalar Edukangola">
    <div className="pwa-install-copy"><span><Download size={16} /></span><p><strong>Instale a Edukangola</strong><small>Abra como aplicação e continue a aprender mais depressa.</small></p></div>
    <button className="pwa-install-action" type="button" onClick={install}>Instalar</button>
    <button className="pwa-install-close" type="button" onClick={dismiss} aria-label="Agora não"><X size={17} /></button>
  </aside>;
}
