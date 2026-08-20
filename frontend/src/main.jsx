import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { installProductionApiTransport } from "./lib/backend-url";
import "./styles.css";

installProductionApiTransport();

if ("serviceWorker" in navigator && window.isSecureContext) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js").catch(() => {
      // A aplicação mantém a navegação normal se o navegador recusar o service worker.
    });
  });
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
