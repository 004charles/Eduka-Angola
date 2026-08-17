import { Banknote, CreditCard, ReceiptText, WalletCards } from "lucide-react";
import { useEffect, useState } from "react";

const money = (value) => `${Number(value || 0).toLocaleString("pt-AO")} Kz`;

export default function ManagerFinancePanel() {
  const [data, setData] = useState(null); const [error, setError] = useState("");
  const load = async () => { try { const response = await fetch("/backend/gestoreduka/api/react/financeiro/", { credentials: "same-origin" }); const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || "Não foi possível carregar os dados financeiros."); setData(payload); } catch (reason) { setError(reason.message); } };
  useEffect(() => { load(); }, []);
  if (error && !data) return <section id="financeiro" className="manager-courses manager-finance"><h2>Financeiro</h2><p className="manager-form-error">{error}</p></section>;
  if (!data) return <section id="financeiro" className="manager-courses manager-finance"><p>A preparar movimentos financeiros…</p></section>;
  const cards = [[WalletCards, "Receita total", data.metricas.total], [CreditCard, "Plataforma", data.metricas.plataforma], [Banknote, "Presencial", data.metricas.presencial], [ReceiptText, "Movimentos", data.metricas.quantidade_movimentos]];
  return <section id="financeiro" className="manager-courses manager-finance"><div><span className="manager-eyebrow">Acompanhamento financeiro</span><h2>Receitas e movimentos</h2></div><div className="manager-enrollment-metrics">{cards.map(([Icon, label, value]) => <article key={label}><Icon size={15}/><small>{label}</small><strong>{label === "Movimentos" ? value : money(value)}</strong></article>)}</div>{error && <p className="manager-form-error">{error}</p>}<div className="manager-enrollment-list">{data.movimentos.length ? data.movimentos.map((item, index) => <article key={`${item.referencia}-${index}`}><div><strong>{item.aluno}</strong><span>{item.curso} · {item.referencia}</span></div><span className={item.tipo === "PRESENCIAL" ? "published" : "draft"}>{item.tipo}</span><span className="manager-enrollment-payment">{money(item.valor)}</span><span>{new Date(item.data).toLocaleDateString("pt-AO")}</span></article>) : <p className="manager-empty-state">Ainda não existem movimentos financeiros confirmados.</p>}</div>{data.por_filial.length > 0 && <div className="manager-finance-branches"><strong>Receita por filial</strong>{data.por_filial.map((item) => <span key={item.id}>{item.nome}: {money(item.valor)}</span>)}</div>}</section>;
}
