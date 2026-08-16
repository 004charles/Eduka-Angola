# GestorEduka Operacional

## Objetivo

O GestorEduka funciona como a secretaria digital diária do centro de formação. O aluno pode chegar através da Eduka-Angola ou ser atendido presencialmente; ambos os caminhos convergem para a mesma matrícula, turma, pagamento, presença, avaliação e certificação.

## Fluxo presencial

1. Abrir **Inscrições > Matricular Aluno**.
2. Introduzir nome, email e telefone. O sistema reutiliza a conta existente quando o email já estiver registado.
3. Selecionar o curso e uma turma aberta.
4. Definir o valor acordado, desconto, forma de pagamento e origem `Atendimento presencial`.
5. Marcar **Pagamento confirmado pelo centro** quando o valor for recebido.
6. O sistema cria a inscrição presencial, a matrícula, atualiza as vagas e cria um recibo com referência única.
7. A matrícula aparece na pesquisa de alunos e no dossiê do aluno.
8. O centro regista presenças e notas na turma e, depois de cumprir os critérios, emite o certificado.

Se o pagamento não estiver confirmado, é criada uma pré-matrícula pendente. Esta deve ser confirmada posteriormente pelo centro.

## Fluxo online integrado

A Eduka-Angola envia um JSON para:

`POST /gestoreduka/api/integracao/inscricoes/`

O pedido deve conter o cabeçalho `X-Eduka-Integration-Key` e dados como `external_id`, `centro_id`, `aluno`, `curso_id`, `turma_id`, `pagamento_confirmado` e `valor_pago`.

O endpoint utiliza o identificador externo para evitar duplicações. Eventos processados novamente devolvem sucesso com `duplicado: true` e não criam uma segunda matrícula.

A chave deve ser configurada no ambiente através de `EDUKA_INTEGRATION_KEY`. Em desenvolvimento, quando `DEBUG=True` e a variável estiver vazia, a chave temporária é `eduka-dev-key`. Em produção, a variável deve ser obrigatória e o fallback deve ser removido.

## Estrutura operacional criada

| Componente | Função |
|---|---|
| `Matricula` | Participação confirmada do aluno numa turma, independente da origem. |
| `RecebimentoCentro` | Pagamento presencial, responsável, forma, valor e referência de recibo. |
| `EventoIntegracao` | Idempotência, payload, estado e erro da sincronização externa. |
| `MembroCentro` | Base para funções de gestor, secretaria, caixa, coordenação e consulta. |
| Dossiê do aluno | Pesquisa e histórico de inscrições e matrículas do centro. |
| Recibo PDF | Documento imprimível disponível no dashboard financeiro. |

## Critérios académicos atuais

A folha de presenças permite lançamento diário por turma e aluno. A folha de notas permite nota final de 0 a 20 valores. A emissão de certificado verifica, no mínimo, 75% de assiduidade e nota final igual ou superior a 10 valores.

## Verificações realizadas

Foram aplicadas as migrações `0028_matricula_operacional`, `0009_recebimentos_centro`, `0019_eventos_integracao` e `0020_membros_operacionais`. O comando `python3 manage.py check` passou sem erros. Também foram validados os fluxos de matrícula presencial, criação de recibo, dossiê do aluno, dashboard financeiro, PDF do recibo e integração idempotente.

## Próximas tarefas para produção

A base operacional está implementada, mas antes de produção devem ser concluídos o ecrã administrativo para gerir `MembroCentro`, a aplicação efetiva das permissões por função, o fecho diário de caixa, pagamentos parciais e mensalidades, a configuração da chave de produção, testes end-to-end com a plataforma Eduka-Angola real, fila de sincronização e monitorização de eventos com erro.
