import { CheckCircle2, ClipboardCheck, X } from "lucide-react";
import { useEffect, useState } from "react";

function token() {
  return document.cookie.split(";").map((part) => part.trim()).find((part) => part.startsWith("csrftoken="))?.split("=")[1] || "";
}

export default function ManagerClassRecordsModal({ turma, mode, onClose }) {
  const attendance = mode === "attendance";
  const [data, setData] = useState(null);
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const endpoint = `/backend/gestoreduka/api/react/turmas/${turma.id}/${attendance ? "presencas" : "notas"}/`;
  const load = async () => { setData(null); setError(""); try { const url = attendance ? `${endpoint}?data=${date}` : endpoint; const response = await fetch(url, { credentials: "same-origin" }); const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || "Não foi possível carregar os registos."); setData(payload); } catch (reason) { setError(reason.message); } };
  useEffect(() => { load(); }, [date, mode, turma.id]);
  const change = (id, field, value) => setData((current) => ({ ...current, alunos: current.alunos.map((aluno) => aluno.inscricao_id === id ? { ...aluno, [field]: value } : aluno) }));
  const save = async () => { if (!data) return; setSaving(true); setError(""); try { const body = attendance ? { data: date, registos: data.alunos.map(({ inscricao_id, estado, observacao }) => ({ inscricao_id, estado, observacao })) } : { registos: data.alunos.filter((aluno) => aluno.nota !== "").map(({ inscricao_id, nota, observacao }) => ({ inscricao_id, nota, observacao })) }; const response = await fetch(endpoint, { method: "PUT", credentials: "same-origin", headers: { "Content-Type": "application/json", "X-CSRFToken": token() }, body: JSON.stringify(body) }); const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || "Não foi possível guardar os registos."); await load(); } catch (reason) { setError(reason.message); } finally { setSaving(false); } };
  return <div className="manager-modal"><section className="manager-records-modal"><header><div><span className="manager-eyebrow">{attendance ? "Assiduidade" : "Avaliação final"}</span><h2>{turma.nome}</h2><p>{turma.curso_titulo}</p></div><button type="button" onClick={onClose} aria-label="Fechar"><X size={18}/></button></header>{attendance && <label className="manager-record-date"><span>Data da aula</span><input type="date" value={date} onChange={(event) => setDate(event.target.value)} /></label>}{error && <p className="manager-form-error">{error}</p>}{!data ? <p>A preparar os alunos confirmados…</p> : <div className="manager-record-list">{data.alunos.length ? data.alunos.map((aluno) => <article key={aluno.inscricao_id}><strong>{aluno.nome}</strong>{attendance ? <select value={aluno.estado} onChange={(event) => change(aluno.inscricao_id, "estado", event.target.value)}>{data.estados.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select> : <input aria-label={`Nota de ${aluno.nome}`} type="number" min="0" max="20" step="0.01" placeholder="0–20" value={aluno.nota} onChange={(event) => change(aluno.inscricao_id, "nota", event.target.value)} />}<input aria-label={`Observação de ${aluno.nome}`} placeholder="Observação opcional" value={aluno.observacao} onChange={(event) => change(aluno.inscricao_id, "observacao", event.target.value)} /></article>) : <p className="manager-empty-state">Não existem alunos confirmados nesta turma.</p>}</div>}<footer><button type="button" onClick={onClose}>Fechar</button><button className="primary" disabled={!data || saving} onClick={save}>{attendance ? <ClipboardCheck size={16}/> : <CheckCircle2 size={16}/>} {saving ? "A guardar…" : attendance ? "Guardar presenças" : "Guardar notas"}</button></footer></section></div>;
}
