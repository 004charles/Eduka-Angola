import { useEffect, useState } from "react";
import ManagerEventsPanel from "../components/ManagerEventsPanel";
import "./gestao-eventos-page.css";

const csrfToken = () => document.cookie.split(";").map((p) => p.trim()).find((p) => p.startsWith("csrftoken="))?.split("=")[1] || "";

export default function GestaoEventosPage() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [codigo, setCodigo] = useState("");
  const [perfil, setPerfil] = useState(null);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState("");
  const [editingPerfil, setEditingPerfil] = useState(false);
  const [perfilForm, setPerfilForm] = useState({});

  useEffect(() => {
    const convite = sessionStorage.getItem("convite_eventos");
    if (convite) {
      const data = JSON.parse(convite);
      setPerfil(data);
      setLoggedIn(true);
    }
  }, []);

  const loadPerfil = async () => {
    try {
      const res = await fetch("/backend/gestoreduka/api/react/perfil-organizacao/", { credentials: "same-origin" });
      if (res.ok) {
        const data = await res.json();
        setPerfil(data);
        setPerfilForm(data);
      }
    } catch { /* ignore */ }
  };

  useEffect(() => { if (loggedIn) loadPerfil(); }, [loggedIn]);

  const handleLogin = async () => {
    if (!codigo.trim()) { setErro("Digite o código de acesso."); return; }
    setLoading(true); setErro("");
    try {
      const res = await fetch("/backend/gestoreduka/api/react/convites-eventos/validar/", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ codigo: codigo.trim() }),
      });
      const data = await res.json();
      if (!res.ok) { setErro(data.detail || "Código inválido."); setLoading(false); return; }
      sessionStorage.setItem("convite_eventos", JSON.stringify(data.convite));
      setPerfil(data.convite);
      setLoggedIn(true);
    } catch { setErro("Erro de conexão. Tente novamente."); }
    setLoading(false);
  };

  const handleLogout = async () => {
    try { await fetch("/backend/gestoreduka/api/react/convites-eventos/logout/", { method: "POST" }); } catch {}
    sessionStorage.removeItem("convite_eventos");
    setLoggedIn(false); setCodigo(""); setPerfil(null);
  };

  const savePerfil = async () => {
    try {
      const res = await fetch("/backend/gestoreduka/api/react/perfil-organizacao/", {
        method: "PATCH", credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify(perfilForm),
      });
      if (res.ok) { const data = await res.json(); setPerfil(data.perfil); setEditingPerfil(false); }
    } catch { /* ignore */ }
  };

  const uploadLogo = async (file) => {
    const fd = new FormData();
    fd.append("logo", file);
    try {
      const res = await fetch("/backend/gestoreduka/api/react/perfil-organizacao/", {
        method: "PATCH", credentials: "same-origin",
        headers: { "X-CSRFToken": csrfToken() }, body: fd,
      });
      if (res.ok) { const data = await res.json(); setPerfil(data.perfil); }
    } catch { /* ignore */ }
  };

  if (!loggedIn) {
    return (
      <main className="gestao-eventos-page">
        <div className="gestao-eventos-gate">
          <span className="eyebrow">Área independente</span>
          <h1>Gestão de Eventos</h1>
          <p>Insira o código de acesso fornecido pelo administrador para gerir os eventos da sua organização.</p>
          <input type="text" className="gestao-input" placeholder="Ex: A1B2C3D4" value={codigo}
            onChange={(e) => { setCodigo(e.target.value.toUpperCase()); setErro(""); }}
            onKeyDown={(e) => e.key === "Enter" && handleLogin()} maxLength={8} autoFocus />
          {erro && <p className="gestao-error">{erro}</p>}
          <button className="primary-action" onClick={handleLogin} disabled={loading}>
            {loading ? "A validar..." : "Entrar"}
          </button>
        </div>
      </main>
    );
  }

  return (
    <div>
      <div className="gestao-eventos-topbar">
        <div className="gestao-eventos-topbar-left">
          {perfil?.logo ? <img src={perfil.logo} alt="" className="gestao-eventos-logo" /> : <div className="gestao-eventos-logo-placeholder" />}
          <div>
            <span className="gestao-eventos-org">{perfil?.nome_organizacao || "Organização"}</span>
            {perfil?.codigo && <span className="gestao-eventos-codigo">{perfil.codigo}</span>}
          </div>
        </div>
        <div className="gestao-eventos-topbar-actions">
          <button className="text-action" onClick={() => { setEditingPerfil(!editingPerfil); setPerfilForm(perfil || {}); }}>Perfil</button>
          <button className="text-action" onClick={handleLogout}>Sair</button>
        </div>
      </div>

      {editingPerfil && (
        <div className="gestao-eventos-perfil-section">
          <div className="gestao-eventos-perfil-card">
            <h3>Perfil da Organização</h3>
            <div className="gestao-eventos-perfil-grid">
              <label><span>Nome da Organização</span>
                <input className="gestao-input" value={perfilForm.nome_organizacao || ""} onChange={(e) => setPerfilForm({ ...perfilForm, nome_organizacao: e.target.value })} />
              </label>
              <label><span>Código de Acesso</span>
                <input className="gestao-input" value={perfilForm.codigo || ""} disabled />
              </label>
              <label><span>E-mail</span>
                <input className="gestao-input" type="email" value={perfilForm.email_gestor || ""} onChange={(e) => setPerfilForm({ ...perfilForm, email_gestor: e.target.value })} />
              </label>
              <label><span>Telefone</span>
                <input className="gestao-input" value={perfilForm.telefone || ""} onChange={(e) => setPerfilForm({ ...perfilForm, telefone: e.target.value })} />
              </label>
              <label className="wide"><span>Endereço</span>
                <input className="gestao-input" value={perfilForm.endereco || ""} onChange={(e) => setPerfilForm({ ...perfilForm, endereco: e.target.value })} />
              </label>
              <label className="wide"><span>Descrição</span>
                <textarea className="gestao-input" rows="3" value={perfilForm.descricao || ""} onChange={(e) => setPerfilForm({ ...perfilForm, descricao: e.target.value })} />
              </label>
              <label className="wide"><span>Logo</span>
                <input type="file" accept="image/*" onChange={(e) => e.target.files[0] && uploadLogo(e.target.files[0])} />
              </label>
            </div>
            <div className="gestao-eventos-perfil-actions">
              <button className="text-action" onClick={() => setEditingPerfil(false)}>Cancelar</button>
              <button className="primary-action" onClick={savePerfil}>Guardar</button>
            </div>
          </div>
        </div>
      )}

      <ManagerEventsPanel independente />
    </div>
  );
}
