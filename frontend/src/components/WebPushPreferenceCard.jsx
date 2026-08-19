import { BellRing, CheckCircle2, CircleAlert, LoaderCircle, Send, Smartphone } from "lucide-react";
import { useEffect, useState } from "react";
import { backendUrl } from "../lib/backend-url";

function csrfToken() {
  return document.cookie.split(";").map((item) => item.trim()).find((item) => item.startsWith("csrftoken="))?.split("=").slice(1).join("=") || "";
}

function base64UrlToUint8Array(value) {
  const padding = "=".repeat((4 - (value.length % 4)) % 4);
  const base64 = (value + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  return Uint8Array.from(rawData, (character) => character.charCodeAt(0));
}

async function postPush(path, body = {}) {
  const response = await fetch(backendUrl(path), { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json", Accept: "application/json", "X-CSRFToken": csrfToken() }, body: JSON.stringify(body) });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Não foi possível actualizar as notificações neste dispositivo.");
  return data;
}

const INITIAL = { loading: true, supported: false, configured: false, enabled: false, subscriptions: 0, publicKey: "", busy: false, testing: false, message: "", error: "" };

export default function WebPushPreferenceCard() {
  const [state, setState] = useState(INITIAL);
  const supported = typeof window !== "undefined" && window.isSecureContext && "Notification" in window && "serviceWorker" in navigator && "PushManager" in window;

  const refresh = async () => {
    if (!supported) {
      setState((current) => ({ ...current, loading: false, supported: false }));
      return;
    }
    try {
      const response = await fetch(backendUrl("/auth/api/react/aluno/push/estado/"), { credentials: "same-origin", headers: { Accept: "application/json" } });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Não foi possível verificar as notificações.");
      setState((current) => ({ ...current, loading: false, supported: true, configured: Boolean(data.configured), enabled: Boolean(data.enabled), subscriptions: data.subscription_count || 0, publicKey: data.public_key || "" }));
    } catch (error) {
      setState((current) => ({ ...current, loading: false, supported: true, error: error.message }));
    }
  };

  useEffect(() => { refresh(); }, []);

  const enable = async () => {
    setState((current) => ({ ...current, busy: true, message: "", error: "" }));
    try {
      if (Notification.permission === "denied") throw new Error("As notificações estão bloqueadas no navegador. Altere esta permissão nas definições do site e tente novamente.");
      const permission = Notification.permission === "granted" ? "granted" : await Notification.requestPermission();
      if (permission !== "granted") throw new Error("A autorização não foi concedida. Pode activar as notificações mais tarde nas preferências do navegador.");
      const registration = await navigator.serviceWorker.ready;
      const existing = await registration.pushManager.getSubscription();
      const subscription = existing || await registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: base64UrlToUint8Array(state.publicKey) });
      await postPush("/auth/api/react/aluno/push/subscrever/", subscription.toJSON());
      setState((current) => ({ ...current, busy: false, enabled: true, subscriptions: Math.max(1, current.subscriptions), message: "Notificações activadas neste dispositivo." }));
    } catch (error) {
      setState((current) => ({ ...current, busy: false, error: error.message }));
    }
  };

  const disable = async () => {
    setState((current) => ({ ...current, busy: true, message: "", error: "" }));
    try {
      const registration = await navigator.serviceWorker.getRegistration();
      const subscription = await registration?.pushManager.getSubscription();
      await postPush("/auth/api/react/aluno/push/cancelar/", subscription ? { endpoint: subscription.endpoint } : {});
      await subscription?.unsubscribe();
      setState((current) => ({ ...current, busy: false, enabled: false, subscriptions: 0, message: "Notificações desactivadas neste dispositivo." }));
    } catch (error) {
      setState((current) => ({ ...current, busy: false, error: error.message }));
    }
  };

  const test = async () => {
    setState((current) => ({ ...current, testing: true, message: "", error: "" }));
    try {
      const data = await postPush("/auth/api/react/aluno/push/testar/");
      setState((current) => ({ ...current, testing: false, message: data.message || "Teste enviado." }));
    } catch (error) {
      setState((current) => ({ ...current, testing: false, error: error.message }));
    }
  };

  if (state.loading) return <section className="preferences-card push-preference-card"><LoaderCircle className="push-spinner" size={20} /><p>A verificar notificações neste dispositivo…</p></section>;
  return <section className="preferences-card push-preference-card"><div className="push-preference-heading"><span><Smartphone size={20} /></span><div><h2>Notificações neste dispositivo</h2><p>Receba avisos úteis sobre a sua aprendizagem, novas turmas, cursos, livros e eventos. A escolha é sua e pode ser alterada a qualquer momento.</p></div></div>{!state.supported ? <p className="push-note"><CircleAlert size={17} /> Abra a Edukangola num navegador actualizado, por ligação segura, para usar notificações.</p> : !state.configured ? <p className="push-note"><CircleAlert size={17} /> As notificações neste dispositivo estarão disponíveis quando forem activadas no ambiente da plataforma.</p> : <div className="push-preference-actions">{state.enabled ? <><p className="push-active"><CheckCircle2 size={17} /> Activas em {state.subscriptions} dispositivo{state.subscriptions === 1 ? "" : "s"}.</p><button type="button" className="push-secondary-action" onClick={test} disabled={state.busy || state.testing}>{state.testing ? <LoaderCircle className="push-spinner" size={16} /> : <Send size={16} />} Testar</button><button type="button" className="push-disable-action" onClick={disable} disabled={state.busy}>{state.busy ? "A desactivar…" : "Desactivar"}</button></> : <button type="button" className="primary-action push-enable-action" onClick={enable} disabled={state.busy}>{state.busy ? <><LoaderCircle className="push-spinner" size={16} /> A activar…</> : <><BellRing size={16} /> Activar notificações</>}</button>}</div>}{state.error && <p className="push-feedback error" role="alert"><CircleAlert size={16} /> {state.error}</p>}{state.message && <p className="push-feedback success" role="status"><CheckCircle2 size={16} /> {state.message}</p>}</section>;
}
