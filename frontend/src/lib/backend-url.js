const configuredApiBase = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
const officialPublicHosts = new Set(["www.edukangola.com", "edukangola.com"]);
const directApiBase = configuredApiBase || (
  typeof window !== "undefined" && officialPublicHosts.has(window.location.hostname)
    ? "https://api.edukangola.com"
    : ""
);

const proxiedPrefixes = ["/backend/", "/api/", "/auth/", "/static/", "/media/"];

function normalizePath(path) {
  return path ? (path.startsWith("/") ? path : `/${path}`) : "/";
}

function directApiUrl(value) {
  const rawUrl = typeof value === "string" || value instanceof URL ? value.toString() : value?.url;
  if (!rawUrl || !directApiBase || typeof window === "undefined") return null;

  const parsed = new URL(rawUrl, window.location.origin);
  const isCurrentOrigin = parsed.origin === window.location.origin;
  const isApiOrigin = parsed.origin === directApiBase;
  if (!isCurrentOrigin && !isApiOrigin) return null;
  if (!proxiedPrefixes.some((prefix) => parsed.pathname.startsWith(prefix))) return null;

  const apiPath = parsed.pathname.startsWith("/backend/")
    ? parsed.pathname.slice("/backend".length)
    : parsed.pathname;
  return `${directApiBase}${apiPath}${parsed.search}${parsed.hash}`;
}

/**
 * Produção usa api.edukangola.com como origem da API. Este transporte evita
 * depender de um fallback SPA do Vercel para rotas autenticadas e mantém os
 * pedidos cross-origin credenciados dentro do mesmo domínio de site.
 */
export function installProductionApiTransport() {
  if (!directApiBase || typeof window === "undefined" || window.__edukaApiTransportInstalled) return;

  const nativeFetch = window.fetch.bind(window);
  window.fetch = (input, init = {}) => {
    const destination = directApiUrl(input);
    if (!destination) return nativeFetch(input, init);

    const originalCredentials = init.credentials || (input instanceof Request ? input.credentials : undefined);
    const requestInit = originalCredentials === "same-origin" || !originalCredentials
      ? { ...init, credentials: "include" }
      : init;

    if (input instanceof Request) {
      return nativeFetch(new Request(destination, input), requestInit);
    }
    return nativeFetch(destination, requestInit);
  };
  window.__edukaApiTransportInstalled = true;
}

export function backendUrl(path) {
  const normalizedPath = normalizePath(path);
  return directApiBase ? `${directApiBase}${normalizedPath}` : `/backend${normalizedPath}`;
}
