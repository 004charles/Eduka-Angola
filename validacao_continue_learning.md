# Validação — Continue a aprender

A API pública React passou a devolver `continuar_video` apenas para o aluno autenticado. Cada item corresponde a um curso em vídeo no qual o aluno já guardou progresso e cuja totalidade das aulas ainda não foi concluída.

| Informação devolvida | Uso na interface |
|---|---|
| Progresso percentual | Barra e indicador de conclusão do curso |
| Aulas concluídas e total | Contexto de avanço do aluno |
| Próxima aula | Orientação para a retoma |
| URL de aprendizagem | Acção directa **Retomar** |

O teste `core.test_continue_learning` foi executado com sucesso. O cenário cria um curso iniciado, outro concluído e confirma que apenas o curso iniciado chega ao payload de continuidade. A secção é intencionalmente ocultada quando o aluno não tem nenhum curso iniciado pendente, evitando um espaço vazio na biblioteca.
