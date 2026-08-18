import { BadgeCheck, Copy, QrCode, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import "./certificate-verify-page.css";

export default function CertificateVerifyPage({ code, onNavigate }) {
  const [state, setState] = useState({ loading: true, certificate: null, error: "" });
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let active = true;
    fetch(`/api/public/certificados/${encodeURIComponent(code)}/`, { headers: { Accept: "application/json" } })
      .then(async (response) => {
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(payload.detail || "Não foi possível validar o certificado.");
        return payload.certificado;
      })
      .then((certificate) => active && setState({ loading: false, certificate, error: "" }))
      .catch((error) => active && setState({ loading: false, certificate: null, error: error.message }));
    return () => { active = false; };
  }, [code]);

  const copyCode = async () => { await navigator.clipboard?.writeText(code); setCopied(true); window.setTimeout(() => setCopied(false), 1800); };
  if (state.loading) return <main className="certificate-verify"><p>A validar certificado…</p></main>;
  if (state.error) return <main className="certificate-verify"><section className="certificate-invalid"><ShieldCheck size={34}/><span>Verificação de certificado</span><h1>Certificado não encontrado</h1><p>{state.error}</p><button onClick={() => onNavigate("/")}>Voltar à Edukangola</button></section></main>;
  const certificate = state.certificate;
  return <main className="certificate-verify"><section className="certificate-card"><div className="certificate-seal"><BadgeCheck size={30}/><span>Certificado validado</span></div><div className="certificate-copy"><span className="certificate-eyebrow">Edukangola · {certificate.tipo}</span><h1>Este certificado é válido</h1><p>Confirmamos que <strong>{certificate.aluno}</strong> concluiu a formação abaixo.</p><dl><div><dt>Formação</dt><dd>{certificate.curso}</dd></div><div><dt>Emitido por</dt><dd>{certificate.centro}</dd></div><div><dt>Data de emissão</dt><dd>{new Date(certificate.emitido_em).toLocaleDateString("pt-AO")}</dd></div>{certificate.nota_final !== null && <div><dt>Nota final</dt><dd>{certificate.nota_final}</dd></div>}</dl><div className="certificate-code"><span>Código de verificação</span><strong>{certificate.codigo}</strong><button onClick={copyCode}><Copy size={15}/>{copied ? "Copiado" : "Copiar"}</button></div></div><aside><QrCode size={19}/><img src={`/api/public/certificados/${encodeURIComponent(certificate.codigo)}/qr/`} alt={`QR code do certificado ${certificate.codigo}`}/><small>Leia o QR para abrir esta validação.</small></aside></section></main>;
}
