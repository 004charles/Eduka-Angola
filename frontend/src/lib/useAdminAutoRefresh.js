import { useCallback, useEffect, useRef, useState } from "react";

/** Mantém dados administrativos recentes sem efectuar pedidos enquanto a página está em segundo plano. */
export default function useAdminAutoRefresh(refresh, { interval = 15000, enabled = true } = {}) {
  const refreshRef = useRef(refresh);
  const inFlightRef = useRef(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => { refreshRef.current = refresh; }, [refresh]);

  const run = useCallback(async () => {
    if (!enabled || inFlightRef.current || document.visibilityState !== "visible" || !navigator.onLine) return false;
    inFlightRef.current = true;
    setSyncing(true);
    try {
      const success = await refreshRef.current();
      if (success !== false) setLastUpdated(new Date());
      return success;
    } finally {
      inFlightRef.current = false;
      setSyncing(false);
    }
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return undefined;
    run();
    const onVisible = () => { if (document.visibilityState === "visible") run(); };
    const onOnline = () => run();
    const timer = window.setInterval(run, interval);
    window.addEventListener("focus", run);
    window.addEventListener("online", onOnline);
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("focus", run);
      window.removeEventListener("online", onOnline);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [enabled, interval, run]);

  return { refreshNow: run, lastUpdated, syncing };
}
