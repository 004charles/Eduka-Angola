import { LockKeyhole, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { authRequest } from "../lib/auth-api";
import "./admin-console-page.css";

export default function AdminAccessPage({ message, onAuthenticated }) {
  const [stage, setStage] = useState("login");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [codigo, setCodigo] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");
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

  const requestRecovery = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await authRequest("/auth/api/react/admin/recuperar-senha/", { email });
      setStage("reset");
    } catch (reason) {
      setError(reason.message || "Não foi possível pedir a recuperação.");
    } finally {
      setSubmitting(false);
    }
  };

  const resetPassword = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await authRequest("/auth/api/react/admin/redefinir-senha/", { codigo, senha: novaSenha, confirmar_senha: confirmarSenha });
      onAuthenticated();
    } catch (reason) {
      setError(reason.message || "Não foi possível redefinir a palavra-passe.");
    } finally {
      setSubmitting(false);
    }
  };

  const header = stage === "login" ? { title: "Acesso administrativo", copy: message || "Entre com a conta administrativa para abrir o centro de controlo." } : stage === "recover" ? { title: "Recuperar acesso", copy: "Enviaremos um código de confirmação para o e-mail administrativo." } : { title: "Definir nova palavra-passe", copy: "Introduza o código recebido e escolha uma nova palavra-passe segura." };
  return <main className="admin-console admin-access-page"><section className="admin-feedback admin-login-card"><ShieldCheck size={30}/><span className="admin-access-eyebrow"><LockKeyhole size={14}/> Área reservada</span><h1>{header.title}</h1><p>{header.copy}</p>{stage === "login" && <form onSubmit={submit}><label><span>E-mail</span><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="username" required /></label><label><span>Palavra-passe</span><input type="password" value={senha} onChange={(event) => setSenha(event.target.value)} autoComplete="current-password" required /></label>{error && <p className="admin-login-error" role="alert">{error}</p>}<button type="submit" disabled={submitting}>{submitting ? "A entrar…" : "Entrar"}</button><button type="button" className="admin-access-link" onClick={() => { setError(""); setStage("recover"); }}>Esqueci a palavra-passe</button></form>}{stage === "recover" && <form onSubmit={requestRecovery}><label><span>E-mail administrativo</span><input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="username" required /></label>{error && <p className="admin-login-error" role="alert">{error}</p>}<button type="submit" disabled={submitting}>{submitting ? "A enviar…" : "Enviar código"}</button><button type="button" className="admin-access-link" onClick={() => { setError(""); setStage("login"); }}>Voltar para entrar</button></form>}{stage === "reset" && <form onSubmit={resetPassword}><p className="admin-recovery-note">Se existir uma conta administrativa com este e-mail, enviámos um código válido por 10 minutos.</p><label><span>Código recebido</span><input inputMode="numeric" value={codigo} onChange={(event) => setCodigo(event.target.value)} autoComplete="one-time-code" required /></label><label><span>Nova palavra-passe</span><input type="password" value={novaSenha} onChange={(event) => setNovaSenha(event.target.value)} autoComplete="new-password" required /></label><label><span>Confirmar palavra-passe</span><input type="password" value={confirmarSenha} onChange={(event) => setConfirmarSenha(event.target.value)} autoComplete="new-password" required /></label>{error && <p className="admin-login-error" role="alert">{error}</p>}<button type="submit" disabled={submitting}>{submitting ? "A guardar…" : "Guardar nova palavra-passe"}</button><button type="button" className="admin-access-link" onClick={() => { setError(""); setStage("login"); }}>Voltar para entrar</button></form>}</section></main>;
}
