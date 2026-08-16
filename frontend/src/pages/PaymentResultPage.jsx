import { useEffect, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, Clock3, Home, LoaderCircle, RefreshCw, ShieldCheck, Ticket, XCircle } from "lucide-react";
import "./payment-result-page.css";

const copy = {
  success: { eyebrow: "Pagamento confirmado", fallbackTitle: "Pagamento processado com sucesso", fallbackMessage: "A sua transação foi confirmada. O acesso será disponibilizado na sua conta." },
  pending: { eyebrow: "A confirmar pagamento", fallbackTitle: "Pagamento pendente", fallbackMessage: "A Prontu ainda está a confirmar a transação. Não faça um novo pagamento enquanto a confirmação estiver em curso." },
  failed: { eyebrow: "Pagamento não concluído", fallbackTitle: "Pagamento não processado", fallbackMessage: "A transação não foi concluída. Pode voltar ao curso e tentar novamente." },
  unknown: { eyebrow: "Resultado do pagamento", fallbackTitle: "Não foi possível confirmar o pagamento", fallbackMessage: "Não encontramos uma referência válida para esta transação. Contacte o suporte antes de tentar pagar novamente." },
};

export default function PaymentResultPage({ onNavigate }) {
  const params = useMemo(() => new URLSearchParams(window.location.search), []);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    const query = new URLSearchParams();
    ["reference", "reference_id", "transaction_id", "id", "pedido", "tipo"].forEach((key) => { const value = params.get(key); if (value) query.set(key, value); });
    if (!query.toString()) { setResult({ status: "UNKNOWN" }); return undefined; }
    fetch(`/api/react/pagamentos/resultado/?${query.toString()}`, { credentials: "same-origin", headers: { Accept: "application/json" }, cache: "no-store" })
      .then(async (response) => { const payload = await response.json().catch(() => ({})); if (!response.ok) throw new Error(payload.message || payload.detail || "Não foi possível confirmar o pagamento."); return payload; })
      .then((payload) => { if (active) { setResult(payload); setError(""); } })
      .catch((reason) => { if (active) setError(reason.message); });
    return () => { active = false; };
  }, [params, attempt]);

  useEffect(() => {
    if (result?.status !== "PENDING" || attempt >= 10) return undefined;
    const timer = window.setTimeout(() => setAttempt((value) => value + 1), 5000);
    return () => window.clearTimeout(timer);
  }, [result, attempt]);

  const kind = result?.status === "SUCCESS" ? "success" : result?.status === "FAILED" ? "failed" : result?.status === "PENDING" ? "pending" : "unknown";
  const text = copy[kind];
  const Icon = kind === "success" ? CheckCircle2 : kind === "failed" ? XCircle : kind === "pending" ? Clock3 : AlertCircle;

  return <main className="payment-result-page"><section className={`payment-result-card is-${kind}`}><div className="payment-result-icon"><Icon size={34} /></div><span className="eyebrow">{text.eyebrow}</span><h1>{result?.titulo || text.fallbackTitle}</h1><p>{error || result?.mensagem || text.fallbackMessage}</p>{result?.status === "PENDING" && <div className="payment-pending-note"><LoaderCircle size={16} /> A confirmar automaticamente ({Math.min(attempt + 1, 10)}/10)</div>}{result?.referencia_pagamento && <div className="payment-reference"><span>Referência</span><strong>{result.referencia_pagamento}</strong></div>}{result?.curso && <div className="payment-course"><ShieldCheck size={17} /><span>{result.curso}</span></div>}{result?.evento && <div className="payment-course"><Ticket size={17} /><span>{result.evento}{result.bilhetes ? ` · ${result.bilhetes} bilhete(s)` : ""}</span></div>}
<div className="payment-result-actions">{kind === "success" && result?.curso && <button className="subpage-cta" onClick={() => onNavigate("/aluno")}><ShieldCheck size={16} /> Ir para a área do aluno</button>}{kind === "failed" && <button className="subpage-cta" onClick={() => onNavigate("/cursos")}><RefreshCw size={16} /> Voltar aos cursos</button>}{kind === "pending" && <button className="payment-secondary" onClick={() => setAttempt((value) => value + 1)}><RefreshCw size={16} /> Verificar agora</button>}<button className="payment-secondary" onClick={() => onNavigate("/")}><Home size={16} /> Página inicial</button></div></section></main>;
}
