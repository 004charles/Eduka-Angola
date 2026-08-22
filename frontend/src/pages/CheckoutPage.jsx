import { useEffect, useState } from "react";
import { ArrowLeft, CalendarDays, CheckCircle2, ChevronRight, CreditCard, ExternalLink, LoaderCircle, LockKeyhole, MapPin, ShieldCheck, Smartphone, UsersRound, Video } from "lucide-react";
import { authRequest } from "../lib/auth-api";
import "./checkout-page.css";
import "./checkout-empty-plan.css";

const formatarKz = (valor) => new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 0 }).format(Number(valor || 0)).replace(/,/g, " ") + " Kz";

function DetalhesTurma({ turma }) {
  if (!turma) return null;
  return <div className="checkout-class-summary"><UsersRound size={18} /><div><b>{turma.nome || turma.turma_nome || "Turma selecionada"}</b><span><CalendarDays size={14} /> {turma.inicio || turma.inicio_formatado || "Início a confirmar"}</span><span><MapPin size={14} /> {[turma.local, turma.sala].filter(Boolean).join(" · ") || "Local a confirmar"}</span></div>{turma.vagas !== undefined && <small>{turma.vagas} vagas</small>}</div>;
}

function CheckoutSubscricaoVideo({ course, stage, response, error, submitting, selectedPlanId, onChoosePlan, onStart, onPay, onNavigate, slug }) {
  const planos = course.subscricao?.planos || [];
  const plano = response?.plano || planos.find((item) => String(item.id) === String(selectedPlanId)) || planos[0];
  const formatPlan = (item) => item ? `${formatarKz(item.preco || response?.valor_agora)} / ${item.periodo_dias || 30} dias` : "Valor a confirmar";
  return <main className="checkout-page"><div className="page-width checkout-shell"><button className="checkout-back" onClick={() => onNavigate(`/video-cursos/${slug}`)}><ArrowLeft size={17} /> Voltar ao curso</button><div className="checkout-layout"><section className="checkout-main"><span className="eyebrow"><Video size={15} /> Edukangola Vídeo</span><h1>{stage === "details" ? "Acesso completo com uma subscrição." : stage === "review" ? "Confirme a sua subscrição mensal." : "A preparar o pagamento seguro."}</h1><p className="checkout-intro">A subscrição activa todos os cursos em vídeo da Edukangola durante o período escolhido. O valor é sempre apresentado antes de avançar para o pagamento.</p>{stage === "details" && <div className="checkout-form"><fieldset><legend>Escolha o seu plano</legend>{planos.length ? planos.map((item) => <label key={item.id} className="checkout-plan-option"><input type="radio" name="plano_video" value={item.id} checked={String(plano?.id) === String(item.id)} onChange={() => onChoosePlan(item.id)} /><span><b>{item.nome}</b><small>{item.descricao || "Acesso a todo o catálogo de cursos em vídeo."}</small></span><em>{formatPlan(item)}</em></label>) : <div className="checkout-plan-empty"><b>As subscrições estão temporariamente indisponíveis.</b><p>Volte em breve para escolher o seu plano mensal. Enquanto isso, explore os cursos incluídos no catálogo Edukangola Vídeo.</p><button type="button" className="checkout-secondary" onClick={() => onNavigate("/cursos-em-video")}>Explorar cursos em vídeo</button></div>}</fieldset>{error && <p className="checkout-error">{error}</p>}<button className="primary-action checkout-submit" disabled={submitting || !plano} onClick={onStart}>{submitting ? "A preparar…" : "Ver resumo da subscrição"}<ChevronRight size={17} /></button></div>}{stage === "review" && <div className="checkout-review"><div className="checkout-payment-explainer"><CreditCard size={21} /><div><b>{response?.plano?.nome || plano?.nome}</b><p>{response?.message || "A subscrição será activada depois de o pagamento ser confirmado."}</p></div></div>{error && <p className="checkout-error">{error}</p>}<button className="primary-action checkout-submit" onClick={onPay} disabled={submitting}>{submitting ? "A preparar pagamento…" : `Ir para pagamento seguro · ${formatPlan(response?.plano || plano)}`}<ChevronRight size={17} /></button></div>}{stage === "processing" && <div className="checkout-processing"><div className="checkout-processing-mark"><LoaderCircle size={34} /></div><h2>A preparar o pagamento seguro</h2><p>Será redireccionado para a Prontu. Quando o pagamento for aceite, a subscrição mensal activa todo o catálogo.</p></div>}</section><aside className="checkout-summary"><span>Subscrição mensal</span><div className="checkout-course"><div className="checkout-cover">{course.imagem_url ? <img src={course.imagem_url} alt="" /> : <Video size={24} />}</div><div><b>{course.titulo}</b><small>Incluído no catálogo Edukangola Vídeo</small></div></div><dl><div><dt>Plano seleccionado</dt><dd>{plano?.nome || "A confirmar"}</dd></div><div><dt>Valor</dt><dd>{formatPlan(plano)}</dd></div><div><dt>Depois do pagamento</dt><dd>Acesso a todos os cursos em vídeo</dd></div></dl><p><LockKeyhole size={15} /> A subscrição não altera inscrições presenciais nem pedidos do Mercado.</p></aside></div></div></main>;
}

export default function CheckoutPage({ kind, course: initialCourse, turmas = [], slug, onNavigate }) {
  const [course, setCourse] = useState(initialCourse || null);
  const [status, setStatus] = useState(kind === "video" && !initialCourse ? "loading" : "ready");
  const [stage, setStage] = useState("details");
  const [response, setResponse] = useState(null);
  const [paymentUrl, setPaymentUrl] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ nome: "", email: "", telefone: "", turma_id: "", plano_id: "" });
  const [coupon, setCoupon] = useState("");
  const [couponResult, setCouponResult] = useState(null);

  useEffect(() => {
    if (kind !== "video") return;
    let active = true;
    fetch(`/api/public/video-cursos/${encodeURIComponent(slug)}/`).then((res) => { if (!res.ok) throw new Error(); return res.json(); }).then((data) => { if (active) { setCourse(data); setStatus("ready"); } }).catch(() => active && setStatus("error"));
    return () => { active = false; };
  }, [kind, slug]);

  const isVideo = kind === "video";
  const courseId = course?.id;
  const availableClasses = turmas.filter((item) => item.id === courseId);
  const selectedClass = availableClasses.find((item) => String(item.turma_id || item.id) === String(form.turma_id));
  const setValue = (field) => (event) => setForm((current) => ({ ...current, [field]: event.target.value }));
  const back = () => onNavigate(isVideo ? `/video-cursos/${slug}` : `/cursos/${courseId}`);
  const initiate = async (event) => {
    event.preventDefault(); setError(""); setSubmitting(true);
    try {
      const data = isVideo
        ? await authRequest(`/curso_video/api/react/${encodeURIComponent(slug)}/acesso/`, { plano_id: Number(form.plano_id) || undefined })
        : await authRequest(`/cursos/api/react/checkout/${courseId}/`, { ...form, turma_id: Number(form.turma_id) });
      setResponse(data); setStage(data.requires_payment || data.status === "pendente" ? "review" : "complete");
    } catch (requestError) { setError(requestError?.data?.message || requestError?.data?.detail || requestError.message || "Não foi possível preparar a inscrição."); }
    finally { setSubmitting(false); }
  };
  useEffect(() => {
    if (stage !== "processing" || !paymentUrl) return undefined;
    const timer = window.setTimeout(() => window.location.assign(paymentUrl), 1400);
    return () => window.clearTimeout(timer);
  }, [stage, paymentUrl]);

  const pay = async () => {
    setError(""); setSubmitting(true);
    try {
      const path = isVideo
        ? `/curso_video/api/react/${encodeURIComponent(slug)}/pagamento/`
        : `/cursos/api/react/checkout/inscricao/${response.inscricao_id}/pagamento/`;
      const data = await authRequest(path, isVideo ? { plano_id: response?.plano?.id || Number(form.plano_id) } : { cupom: couponResult?.codigo || "" });
      if (data.payment_url) { setPaymentUrl(data.payment_url); setStage("processing"); }
      else setStage("complete");
    } catch (requestError) { setError(requestError?.data?.message || requestError.message || "Não foi possível preparar o pagamento."); }
    finally { setSubmitting(false); }
  };
  const validateCoupon = async () => {
    if (isVideo || !coupon.trim()) return;
    setError("");
    try {
      const data = await authRequest(`/cursos/api/react/checkout/${courseId}/cupom/`, { codigo: coupon });
      setCouponResult(data);
    } catch (requestError) { setCouponResult(null); setError(requestError?.data?.message || requestError.message || "Não foi possível validar o cupão."); }
  };

  if (status === "loading") return <main className="detail-state page-width"><span className="eyebrow muted">Checkout</span><h1>A preparar o seu resumo.</h1><p>Estamos a consultar as condições publicadas para este curso em vídeo.</p></main>;
  if (status === "error" || !course) return <main className="detail-state page-width"><span className="eyebrow muted">Checkout indisponível</span><h1>Não foi possível preparar este curso.</h1><button className="primary-action" onClick={() => onNavigate("/cursos")}>Voltar ao catálogo</button></main>;

  if (isVideo) return <CheckoutSubscricaoVideo course={course} stage={stage} response={response} error={error} submitting={submitting} selectedPlanId={form.plano_id} slug={slug} onNavigate={onNavigate} onChoosePlan={(plano_id) => setForm((current) => ({ ...current, plano_id }))} onStart={initiate} onPay={pay} />;

  const priceLabel = isVideo ? course.pagamento?.agora : course.pagamento?.agora;
  const needsClass = !isVideo;
  const activeClass = response?.turma || selectedClass;
  return <main className="checkout-page"><div className="page-width checkout-shell"><button className="checkout-back" onClick={back}><ArrowLeft size={17} /> Voltar ao curso</button><div className="checkout-progress" aria-label="Progresso do checkout"><span className={stage === "details" ? "active" : "done"}>1 <b>Dados</b></span><i /><span className={stage === "review" ? "active" : stage === "complete" ? "done" : ""}>2 <b>Resumo</b></span><i /><span className={stage === "complete" ? "active" : ""}>3 <b>{isVideo ? "Acesso" : "Confirmação"}</b></span></div><div className="checkout-layout"><section className="checkout-main"><span className="eyebrow"><ShieldCheck size={15} /> {isVideo ? "Acesso ao curso em vídeo" : "Inscrição presencial"}</span><h1>{stage === "details" ? "Só precisamos de alguns dados." : stage === "review" ? "Confirme antes de pagar." : "Está tudo preparado."}</h1><p className="checkout-intro">{stage === "details" ? "Não precisa iniciar sessão para continuar. Mostramos sempre o valor e o próximo passo antes de qualquer pagamento." : stage === "review" ? "A sua escolha foi registada. Reveja as informações abaixo antes de abrir o pagamento seguro." : response?.message || "Recebemos o seu pedido."}</p>{stage === "details" && <form className="checkout-form" onSubmit={initiate}>{needsClass && <fieldset><legend>Escolha a turma e a unidade</legend><p>Escolha a filial mais conveniente para si; cada opção mostra a localização exacta da unidade.</p><div className="checkout-class-options">{availableClasses.map((item) => <label key={item.turma_id} className={String(form.turma_id) === String(item.turma_id) ? "selected" : ""}><input type="radio" name="turma" required value={item.turma_id} checked={String(form.turma_id) === String(item.turma_id)} onChange={setValue("turma_id")} /><span><b>{item.turma_nome || "Turma aberta"}</b>{item.filial_nome && <small><MapPin size={14} /> Unidade: {item.filial_nome}</small>}<small><CalendarDays size={14} /> {item.dias || "Dias a confirmar"} · {item.turno || item.horario}</small><small><MapPin size={14} /> {item.filial_endereco || item.local || item.cidade || "Local a confirmar"}</small></span><em>{item.vagas_disponiveis} vagas</em></label>)}</div></fieldset>}<fieldset><legend>Os seus dados</legend><p>{isVideo ? "Usamos estes dados para associar o acesso ao curso e enviar a confirmação." : "Usamos estes dados para reservar a vaga e enviar a confirmação."}</p><label>Nome completo<input required value={form.nome} onChange={setValue("nome")} autoComplete="name" /></label><label>E-mail<input type="email" required value={form.email} onChange={setValue("email")} autoComplete="email" placeholder="nome@email.com" /></label>{needsClass && <label>Telefone / WhatsApp<input required value={form.telefone} onChange={setValue("telefone")} autoComplete="tel" placeholder="+244 923 000 000" /></label>}</fieldset>{error && <p className="checkout-error">{error}</p>}<button className="primary-action checkout-submit" disabled={submitting}>{submitting ? "A preparar…" : "Ver resumo"}<ChevronRight size={17} /></button></form>}{stage === "processing" && <div className="checkout-processing"><div className="checkout-processing-mark"><LoaderCircle size={34} /></div><span className="eyebrow"><ShieldCheck size={15} /> Edukangola</span><h2>A preparar o pagamento seguro</h2><p>Estamos a abrir o ambiente protegido da Prontu. Não feche esta página nem actualize o navegador.</p><div className="checkout-processing-track"><span /></div><small><ExternalLink size={14} /> Será redireccionado automaticamente para concluir o pagamento.</small><button className="checkout-secondary" onClick={() => window.location.assign(paymentUrl)}>Continuar agora para a Prontu <ExternalLink size={15} /></button></div>}{stage === "review" && <div className="checkout-review"><DetalhesTurma turma={activeClass} /><div className="checkout-payment-explainer"><CreditCard size={21} /><div><b>Pagamento seguro pela Prontu</b><p>Ao continuar, abre uma página segura para pagar o valor abaixo. A confirmação ativa a sua inscrição ou desbloqueia as aulas.</p></div></div>{!isVideo && <div className="checkout-coupon"><label>Código promocional<input value={coupon} onChange={(event) => { setCoupon(event.target.value); setCouponResult(null); }} placeholder="Ex.: BEMVINDO" /></label><button className="checkout-secondary" type="button" onClick={validateCoupon}>Aplicar código</button>{couponResult && <p>{couponResult.titulo}: menos {formatarKz(couponResult.desconto)}</p>}</div>}{error && <p className="checkout-error">{error}</p>}<button className="primary-action checkout-submit" onClick={pay} disabled={submitting}>{submitting ? "A preparar pagamento…" : `Ir para pagamento seguro · ${formatarKz(couponResult?.valor_final ?? response?.valor_agora)}`}<ChevronRight size={17} /></button><button className="checkout-secondary" onClick={() => setStage("details")}>Voltar e rever os dados</button></div>}{stage === "complete" && <div className="checkout-complete"><CheckCircle2 size={45} /><h2>{isVideo ? "O acesso está disponível." : "A sua inscrição foi confirmada."}</h2><p>{response?.message}</p>{isVideo ? <button className="primary-action" onClick={() => onNavigate(`/video-cursos/${slug}`)}>Ver o curso em vídeo <Video size={17} /></button> : <button className="primary-action" onClick={() => onNavigate(`/cursos/${courseId}`)}>Ver a formação <ChevronRight size={17} /></button>}<button className="checkout-secondary" onClick={() => onNavigate(`/criar-conta?email=${encodeURIComponent(form.email)}&next=${encodeURIComponent(isVideo ? `/video-cursos/${slug}` : `/cursos/${courseId}`)}`)}>Definir palavra-passe para gerir a conta</button></div>}</section><aside className="checkout-summary"><span>Resumo</span><div className="checkout-course"><div className="checkout-cover">{course.imagem_url ? <img src={course.imagem_url} alt="" /> : isVideo ? <Video size={24} /> : <UsersRound size={24} />}</div><div><b>{course.titulo}</b><small>{isVideo ? "Curso em vídeo" : course.centro}</small></div></div>{activeClass && <DetalhesTurma turma={activeClass} />}<dl><div><dt>{isVideo ? "Acesso ao curso" : "Valor a pagar agora"}</dt><dd>{couponResult?.valor_final !== undefined ? formatarKz(couponResult.valor_final) : response?.valor_agora !== undefined ? formatarKz(response.valor_agora) : priceLabel || "A confirmar"}</dd></div><div><dt>Depois do pagamento</dt><dd>{isVideo ? "Aulas desbloqueadas" : "Vaga confirmada"}</dd></div></dl><p><LockKeyhole size={15} /> O preço e as condições são confirmados antes do pagamento.</p>{!isVideo && <p><Smartphone size={15} /> Se houver valores posteriores, o centro explica-os nas condições da formação.</p>}</aside></div></div></main>;
}
