import { LockKeyhole, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { authRequest } from "../lib/auth-api";
import "./admin-console-page.css";

export default function AdminAccessPage({ message, onAuthenticated }) {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await authRequest("/auth/api/react/admin/login/", { email, senha });
      onAuthenticated();
    } catch (reason) {
      setError(reason.message || "Não foi possível iniciar a sessão administrativa.");
    } finally {
      setSubmitting(false);
    }
  };

  return <main className="admin-console admin-access-page"><section className="admin-feedback admin-login-card"><ShieldCheck size={30}/><span className="admin-access-eyebrow"><LockKeyhole size={14}/> Área reservada</span><h1>Acesso administrativo</h1><p>{message || "Entre com a conta administrativa para abrir o centro de controlo."}</p><form onSubmit={submit}><label><span>E-mail</span><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="username" required /></label><label><span>Palavra-passe</span><input type="password" value={senha} onChange={(event) => setSenha(event.target.value)} autoComplete="current-password" required /></label>{error && <p className="admin-login-error" role="alert">{error}</p>}<button type="submit" disabled={submitting}>{submitting ? "A entrar…" : "Entrar"}</button></form></section></main>;
}
