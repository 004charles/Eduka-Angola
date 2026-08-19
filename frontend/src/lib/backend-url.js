const configuredApiBase = (import.meta.env.VITE_API_BASE_URL || "").trim().replace(/\/$/, "");

export function backendUrl(path) {
  const normalizedPath = path ? (path.startsWith("/") ? path : `/${path}`) : "/";
  return configuredApiBase ? `${configuredApiBase}${normalizedPath}` : `/backend${normalizedPath}`;
}
