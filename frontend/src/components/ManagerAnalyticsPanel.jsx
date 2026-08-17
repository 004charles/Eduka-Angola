import { BarChart3, BookOpen, TrendingUp, UsersRound } from "lucide-react";
import { useEffect, useState } from "react";

const money = (value) => `${Number(value || 0).toLocaleString("pt-AO")} Kz`;

export default function ManagerAnalyticsPanel() {
  const [data, setData] = useState(null); const [error, setError] = useState("");
  useEffect(() => { fetch("/backend/gestoreduka/api/react/analytics/", { credentials: "same-origin" }).then(async (response) => { const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || "Não foi possível carregar os indicadores."); setData(payload); }).catch((reason) => setError(reason.message)); }, []);
  if (error && !data) return <section id="analytics" className="manager-courses manager-analytics"><h2>Analytics</h2><p className="manager-form-error">{error}</p></section>;
  if (!data) return <section id="analytics" className="manager-courses manager-analytics"><p>A preparar indicadores…</p></section>;
  const cards = [[TrendingUp, "Receita (30 dias)", money(data.metricas.receita_30_dias)], [UsersRound, "Inscrições (30 dias)", data.metricas.inscricoes_30_dias], [UsersRound, "Confirmadas", data.metricas.inscricoes_confirmadas], [BookOpen, "Cursos publicados", data.metricas.cursos_publicados]];
  return <section id="analytics" className="manager-courses manager-analytics"><div><span className="manager-eyebrow">Desempenho do centro</span><h2>Analytics</h2></div><div className="manager-enrollment-metrics">{cards.map(([Icon, label, value]) => <article key={label}><Icon size={15}/><small>{label}</small><strong>{value}</strong></article>)}</div><div className="manager-course-list">{data.top_cursos.length ? data.top_cursos.map((course) => <article key={course.id}><div><strong>{course.titulo}</strong><span>Curso com mais alunos confirmados</span></div><span className="published"><BarChart3 size={14}/>{course.alunos} alunos</span></article>) : <p className="manager-empty-state">Ainda não existem dados suficientes para ordenar os cursos.</p>}</div></section>;
}
