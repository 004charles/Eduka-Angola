import { useEffect, useState } from "react";
import { ArrowLeft, Award, ExternalLink, ShieldCheck } from "lucide-react";
import "./student-certificates-page.css";

const backendUrl = (path) => path;

function formatDate(value) {
  try {
    return new Intl.DateTimeFormat("pt-PT", { day: "2-digit", month: "long", year: "numeric" }).format(new Date(value));
  } catch {
    return "Data não disponível";
  }
}

export default function StudentCertificatesPage({ onNavigate }) {
  const [state, setState] = useState({ loading: true, error: "", certificates: [] });

  useEffect(() => {
    let active = true;
    fetch("/api/react/aluno/certificados/", { credentials: "same-origin", headers: { Accept: "application/json" }, cache: "no-store" })
      .then(async (response) => {
        const data = await response.json().catch(() => ({}));
        if (response.status === 401) throw new Error("login");
        if (!response.ok) throw new Error(data.detail || "Não foi possível carregar os certificados.");
        return data;
      })
      .then((data) => active && setState({ loading: false, error: "", certificates: data.certificados || [] }))
      .catch((error) => active && setState({ loading: false, error: error.message, certificates: [] }));
    return () => { active = false; };
  }, []);

  if (state.loading) return <main className="certificates-page"><div className="page-width certificates-loading">A carregar o seu histórico académico…</div></main>;
  if (state.error === "login") return <main className="certificates-page"><section className="page-width certificates-gate"><h1>Entre para consultar os seus certificados.</h1><button className="primary-action" onClick={() => onNavigate("/entrar?next=/aluno/certificados")}>Entrar</button></section></main>;
  if (state.error) return <main className="certificates-page"><section className="page-width certificates-gate"><h1>Não foi possível abrir o histórico.</h1><p>{state.error}</p><button className="primary-action" onClick={() => window.location.reload()}>Tentar novamente</button></section></main>;

  return <main className="certificates-page">
    <section className="certificates-hero"><div className="page-width"><button className="certificates-back" type="button" onClick={() => onNavigate("/aluno")}><ArrowLeft size={17} /> Voltar à área do aluno</button><span className="eyebrow"><Award size={15} /> Prova do seu percurso</span><h1>Os seus certificados.</h1><p>Consulte as formações concluídas e partilhe o código de verificação com quem precisa de confirmar a sua aprendizagem.</p></div></section>
    <section className="page-width certificates-content">
      <div className="certificates-heading"><div><span className="eyebrow muted">Histórico académico</span><h2>{state.certificates.length ? `${state.certificates.length} certificado${state.certificates.length === 1 ? "" : "s"} emitido${state.certificates.length === 1 ? "" : "s"}` : "Ainda não tem certificados"}</h2><p>{state.certificates.length ? "Cada registo tem um código público de verificação." : "Conclua uma formação elegível para emitir o seu primeiro certificado."}</p></div><ShieldCheck size={28} /></div>
      {state.certificates.length ? <div className="certificate-list">{state.certificates.map((certificate) => <article className="certificate-item" key={`${certificate.tipo}-${certificate.id}`}><div className="certificate-seal"><Award size={28} /></div><div className="certificate-copy"><span>{certificate.tipo}</span><h3>{certificate.curso_titulo}</h3><p>Emitido em {formatDate(certificate.data_emissao)}{certificate.nota_final && ` · Nota final ${certificate.nota_final}%`}</p><code>{certificate.codigo_verificacao}</code></div><a className="certificate-verify" href={backendUrl(certificate.verificacao_url)} target="_blank" rel="noreferrer">Verificar <ExternalLink size={15} /></a></article>)}</div> : <div className="certificates-empty"><Award size={34} /><h3>O seu histórico começa aqui.</h3><p>Explore os cursos e continue a sua aprendizagem para construir um percurso verificável.</p><button className="primary-action" onClick={() => onNavigate("/cursos")}>Explorar cursos</button></div>}
    </section>
  </main>;
}
