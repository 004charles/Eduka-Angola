import { Building2, Camera, CheckCircle2, Globe2, ImagePlus, MapPin, Save, Upload } from "lucide-react";
import { useEffect, useState } from "react";
import "./manager-profile-panel.css";

const countries = [["AO", "Angola"], ["PT", "Portugal"], ["BR", "Brasil"], ["CV", "Cabo Verde"], ["MZ", "Moçambique"], ["ST", "São Tomé e Príncipe"], ["GW", "Guiné-Bissau"], ["TL", "Timor-Leste"]];
const csrfToken = () => document.cookie.split(";").map((part) => part.trim()).find((part) => part.startsWith("csrftoken="))?.split("=").slice(1).join("=") || "";

function MediaUpload({ type, url, label, hint, uploading, onUpload, logo = false }) {
  return <label className={logo ? "manager-profile-upload is-logo" : "manager-profile-upload"}>
    <span className="manager-profile-upload-preview">{url ? <img src={url} alt={`${label} actual`} /> : logo ? <Building2 size={25} /> : <ImagePlus size={27} />}</span>
    <span className="manager-profile-upload-copy"><b>{label}</b><small>{uploading ? "A enviar imagem…" : hint}</small></span>
    <span className="manager-profile-upload-action">{logo ? <Upload size={15} /> : <Camera size={15} />} Alterar</span>
    <input type="file" accept="image/png,image/jpeg,image/webp" disabled={Boolean(uploading)} onChange={(event) => onUpload(type, event.target.files?.[0])} />
  </label>;
}

export default function ManagerProfilePanel() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState("");
  const load = async () => { try { const response = await fetch("/backend/gestoreduka/api/react/perfil/", { credentials: "same-origin" }); const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || "Não foi possível carregar o perfil institucional."); setData(payload); } catch (reason) { setError(reason.message); } };
  useEffect(() => { load(); }, []);
  const update = (group, field, value) => setData((current) => ({ ...current, [group]: { ...current[group], [field]: value } }));
  const save = async (event) => { event.preventDefault(); setSaving(true); setError(""); try { const response = await fetch("/backend/gestoreduka/api/react/perfil/", { method: "PATCH", credentials: "same-origin", headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() }, body: JSON.stringify({ centro: data.centro, perfil: data.perfil }) }); const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || "Não foi possível guardar o perfil institucional."); setData(payload); } catch (reason) { setError(reason.message); } finally { setSaving(false); } };
  const upload = async (field, file) => { if (!file) return; setUploading(field); setError(""); const body = new FormData(); body.append("campo", field); body.append("ficheiro", file); try { const response = await fetch("/backend/gestoreduka/api/react/perfil/media/", { method: "POST", credentials: "same-origin", headers: { "X-CSRFToken": csrfToken() }, body }); const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || "Não foi possível enviar a imagem."); setData((current) => ({ ...current, perfil: { ...current.perfil, [`${field}_url`]: payload.url } })); } catch (reason) { setError(reason.message); } finally { setUploading(""); } };
  if (error && !data) return <section className="manager-profile-panel manager-profile-feedback"><h2>Perfil institucional</h2><p className="manager-form-error">{error}</p><button onClick={() => { setError(""); load(); }}>Tentar novamente</button></section>;
  if (!data) return <section className="manager-profile-panel manager-profile-feedback"><p>A preparar o perfil institucional…</p></section>;
  const field = (group, name, label, type = "text", wide = false) => <label className={wide ? "wide" : ""}><span>{label}</span><input type={type} value={data[group][name] || ""} onChange={(event) => update(group, name, event.target.value)} /></label>;
  const countryName = countries.find(([code]) => code === data.centro.pais)?.[1] || "Localização a definir";
  const location = [data.centro.cidade, data.centro.provincia, countryName].filter(Boolean).join(", ");
  return <section className="manager-profile-panel">
    <form onSubmit={save}>
      <header className="manager-profile-hero">
        <div className="manager-profile-cover">{data.perfil.banner_url ? <img src={data.perfil.banner_url} alt="Capa actual do centro" /> : <div className="manager-profile-cover-fallback"><span /><span /><span /></div>}<div className="manager-profile-cover-shade" /></div>
        <div className="manager-profile-identity"><label className="manager-profile-logo-control"><span>{data.perfil.imagem_url ? <img src={data.perfil.imagem_url} alt={`Logótipo de ${data.centro.nome}`} /> : <Building2 size={28} />}</span><input type="file" accept="image/png,image/jpeg,image/webp" disabled={Boolean(uploading)} onChange={(event) => upload("imagem", event.target.files?.[0])} /><i><Camera size={14} /></i></label><div><span className="manager-eyebrow">Presença pública</span><h2>{data.centro.nome || "O seu centro"}</h2><p><MapPin size={14} /> {location || "Localização a definir"} <b>·</b> {data.perfil.modalidade || "Modalidade a definir"}</p></div></div>
        <MediaUpload type="banner" url={data.perfil.banner_url} label="Imagem de capa" hint="PNG, JPG ou WebP · até 5 MB" uploading={uploading === "banner"} onUpload={upload} />
      </header>
      <div className="manager-profile-editor">
        <main className="manager-profile-main">
          <section className="manager-profile-section"><div className="manager-profile-section-heading"><span><Building2 size={17} /></span><div><h3>Dados institucionais</h3><p>Estes dados identificam o seu centro na plataforma.</p></div></div><div className="manager-profile-grid">{field("centro", "nome", "Nome do centro")}{field("centro", "email", "E-mail institucional", "email")}{field("centro", "telefone", "Telefone")}{field("centro", "site", "Website", "url")}</div></section>
          <section className="manager-profile-section"><div className="manager-profile-section-heading"><span><MapPin size={17} /></span><div><h3>Localização</h3><p>Ajude os alunos a encontrar o centro e a modalidade certa.</p></div></div><div className="manager-profile-grid">{<label><span>País</span><select value={data.centro.pais || "AO"} onChange={(event) => update("centro", "pais", event.target.value)}>{countries.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>}{field("centro", "provincia", "Província / região")}{field("centro", "cidade", "Cidade")}{field("centro", "endereco", "Endereço", "text", true)}</div></section>
          <section className="manager-profile-section"><div className="manager-profile-section-heading"><span><Globe2 size={17} /></span><div><h3>Como o centro se apresenta</h3><p>Uma descrição clara ajuda os alunos a confiar antes de se inscreverem.</p></div></div><div className="manager-profile-grid"><label className="wide"><span>Apresentação</span><textarea rows="5" placeholder="Apresente o centro, as áreas de ensino e o que os alunos podem esperar." value={data.perfil.descricao || ""} onChange={(event) => update("perfil", "descricao", event.target.value)} /></label>{field("perfil", "tipo", "Tipo de centro")}<label><span>Modalidade</span><select value={data.perfil.modalidade || "Presencial"} onChange={(event) => update("perfil", "modalidade", event.target.value)}>{["Presencial", "Online", "Híbrido"].map((item) => <option key={item}>{item}</option>)}</select></label><label className="wide"><span>Missão</span><textarea rows="3" value={data.perfil.missao || ""} onChange={(event) => update("perfil", "missao", event.target.value)} /></label><label className="wide"><span>Visão</span><textarea rows="3" value={data.perfil.visao || ""} onChange={(event) => update("perfil", "visao", event.target.value)} /></label></div></section>
        </main>
        <aside className="manager-profile-sidebar"><section className="manager-profile-visibility"><span><CheckCircle2 size={18} /></span><div><strong>Perfil público do centro</strong><p>Os dados guardados aparecem na vitrina Edukangola para alunos e parceiros.</p></div></section><section className="manager-profile-assets"><h3>Identidade visual</h3><MediaUpload type="imagem" url={data.perfil.imagem_url} label="Logótipo" hint="PNG, JPG ou WebP · até 5 MB" uploading={uploading === "imagem"} onUpload={upload} logo /><div className="manager-profile-gallery-note"><ImagePlus size={16} /><div><strong>{data.galeria.length} imagens na galeria</strong><span>Use a área Galeria para mostrar espaços e actividades.</span></div></div></section></aside>
      </div>
      {error && <p className="manager-form-error manager-profile-error">{error}</p>}
      <footer className="manager-profile-footer"><p>As alterações são guardadas apenas quando confirmar esta edição.</p><button className="primary" disabled={saving}><Save size={16}/> {saving ? "A guardar…" : "Guardar perfil"}</button></footer>
    </form>
  </section>;
}
