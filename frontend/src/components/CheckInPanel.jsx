import { CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import { useState } from "react";
import "./check-in-panel.css";

const csrfToken = () => document.cookie.split(";").map((part) => part.trim()).find((part) => part.startsWith("csrftoken="))?.split("=")[1] || "";

export default function CheckInPanel() {
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const validar = async () => {
    if (!code.trim()) return;
    setLoading(true); setResult(null);
    try {
      const res = await fetch("/api/public/eventos/validar-bilhete/", {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify({ codigo: code.trim() }),
      });
      const data = await res.json();
      setResult(data);
    } catch { setResult({ status: "invalido", erro: "Erro de conexão." }); }
    setLoading(false);
  };

  const statusColor = result?.status === "validado" ? "valid" : result?.status === "ja_utilizado" ? "used" : "invalid";

  return (
    <div className="check-in-panel">
      <div className="check-in-input">
        <input type="text" value={code} onChange={(e) => setCode(e.target.value)}
          placeholder="Código do bilhete (UUID)" disabled={loading}
          onKeyDown={(e) => e.key === "Enter" && validar()} autoFocus />
        <button onClick={validar} disabled={loading || !code.trim()} className="primary-action">
          {loading ? "A validar..." : "Validar"}
        </button>
      </div>

      {result && (
        <div className={`check-in-result ${statusColor}`}>
          {statusColor === "valid" && <><CheckCircle2 size={48} /><h3>Entrada Autorizada</h3><p><strong>{result.participante}</strong></p><p>{result.bilhete?.lote} · {result.bilhete?.evento}</p></>}
          {statusColor === "used" && <><XCircle size={48} /><h3>Bilhete Já Utilizado</h3><p>{result.erro}</p>{result.data_validacao && <small>Utilizado em: {new Date(result.data_validacao).toLocaleString("pt-AO")}</small>}</>}
          {statusColor === "invalid" && <><AlertCircle size={48} /><h3>Bilhete Inválido</h3><p>{result.erro || "Código não encontrado"}</p></>}
          <button onClick={() => { setCode(""); setResult(null); }} className="text-action">Outro bilhete</button>
        </div>
      )}

      {!result && !loading && <p className="check-in-hint">Informe o código UUID do bilhete ou escaneie o QR Code</p>}
    </div>
  );
}
