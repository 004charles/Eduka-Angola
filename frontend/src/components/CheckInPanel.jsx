import { Heart, CheckCircle2, XCircle2, AlertCircle, Loader2, User } from "lucide-react";
import { useEffect, useState } from "react";
import "./check-in-panel.css";

const csrfToken = () => document.cookie.split(";").map((part) => part.trim()).find((part) => part.startsWith("csrftoken="))?.split("=")[1] || "";

export default function CheckInPanel({ onTicketValidated }) {
  const [code, setCode] = useState("");
  const [status, setStatus] = useState(""); // "valid", "used", "invalid"
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const validarTicket = async () => {
    if (!code.trim()) {
      setError("Por favor, informe o código do bilhete");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/public/eventos/validar-bilhete/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken(),
        },
        body: JSON.stringify({ codigo: code.trim() }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Erro ao validar bilhete");
      
      setTicket(data.bilhete);
      setStatus(data.status);
      
      if (onTicketValidated) {
        onTicketValidated(data);
      }
    } catch (reason) {
      setStatus("invalid");
      setError(reason.message || "Bilhete inválido ou já utilizado");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="check-in-panel">
      <div className="check-in-header">
        <h2>Validação de Entrada</h2>
        <p>Escaneie ou informe o código do bilhete</p>
      </div>
      
      <div className="check-in-input">
        <input
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Código do bilhete ou QR Code"
          disabled={loading}
          aria-label="Código do bilhete"
        />
        <button onClick={validarTicket} disabled={loading || !code.trim()}>
          {loading ? "Validando..." : "Validar"}
        </button>
      </div>
      
      {status === "valid" && (
        <div className="check-in-result valid">
          <CheckCircle2 size={48} />
          <h3>Entrada Autorizada</h3>
          <p>{ticket.evento.titulo}</p>
          <p>Titular: {ticket.nome_comprador}</p>
          <p>Lote: {ticket.lote.nome}</p>
          <button onClick={() => setCode("")} className="btn-continue">Outro bilhete</button>
        </div>
      )}
      
      {status === "used" && (
        <div className="check-in-result used">
          <XCircle2 size={48} />
          <h3>Bilhete Já Utilizado</h3>
          <p>Este bilhete já foi validado anteriormente</p>
          <p>Data: {ticket ? ticket.data_validacao : "—"}</p>
          <button onClick={() => setCode("")} className="btn-continue">Outro bilhete</button>
        </div>
      )}
      
      {status === "invalid" && (
        <div className="check-in-result invalid">
          <AlertCircle size={48} />
          <h3>Bilhete Inválido</h3>
          <p>{error || "Código não encontrado ou expirado"}</p>
          <button onClick={() => setCode("")} className="btn-continue">Outro bilhete</button>
        </div>
      )}
      
      {!status && !error && !loading && (
        <div className="check-in-hint">
          <p>Informe o código de 8-16 dígitos ou escaneie o QR Code</p>
        </div>
      )}
    </div>
  );
}
