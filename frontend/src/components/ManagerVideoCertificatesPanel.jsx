import { Award } from "lucide-react";
import { useEffect, useState } from "react";

const csrfToken = () => document.cookie.split(";").map((part) => part.trim()).find((part) => part.startsWith("csrftoken="))?.split("=")[1] || "";

export default function ManagerVideoCertificatesPanel() {
  const [data, setData] = useState(null); const [error, setError] = useState(""); const [updating, setUpdating] = useState(null);
  const load = async () => { try { const response = await fetch("/backend/gestoreduka/api/react/certificados-video/", { credentials: "same-origin" }); const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || "Não foi possível carregar os certificados."); setData(payload); } catch (reason) { setError(reason.message); } };
  useEffect(() => { load(); }, []);
  const update = async (item, status) => { setUpdating(item.id); setError(""); try { const response = await fetch(`/backend/gestoreduka/api/react/certificados-video/${item.id}/`, { method: "PATCH", credentials: "same-origin", headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() }, body: JSON.stringify({ status }) }); const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || "Não foi possível actualizar o certificado."); await load(); } catch (reason) { setError(reason.message); } finally { setUpdating(null); } };
  if (error && !data) return <section id="certificados-video" className="manager-courses"><h2>Certificados em vídeo</h2><p className="manager-form-error">{error}</p></section>;
  if (!data) return <section id="certificados-video" className="manager-courses"><p>A preparar certificados em vídeo…</p></section>;
  return <section id="certificados-video" className="manager-courses"><div><span className="manager-eyebrow">Conclusão online</span><h2>Certificados em vídeo</h2></div>{error && <p className="manager-form-error">{error}</p>}<div className="manager-enrollment-list">{data.certificados.length ? data.certificados.map((item) => <article key={item.id}><div><strong>{item.aluno}</strong><span>{item.curso} · Código {item.codigo_verificacao}</span></div><span className={item.status === "EMITIDO" ? "published" : item.status === "REJEITADO" ? "draft" : "pending"}>{item.status}</span><select disabled={updating === item.id} value={item.status} onChange={(event) => update(item, event.target.value)}>{data.status_opcoes.map((status) => <option key={status} value={status}>{status}</option>)}</select></article>) : <p className="manager-empty-state"><Award size={16}/> Ainda não existem certificados de cursos em vídeo.</p>}</div></section>;
}
