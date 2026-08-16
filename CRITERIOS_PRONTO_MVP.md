# Critérios de pronto — GestorEduka MVP Operacional

O GestorEduka será considerado pronto para operação inicial de um centro quando os fluxos abaixo funcionarem de ponta a ponta, com dados persistidos, permissões, documentos e testes de aceitação.

## Fluxos obrigatórios

| Código | Fluxo | Critério de aceitação |
|---|---|---|
| F01 | Curso e turma | O gestor cria curso com formadores, abre turma, define horário, sala, datas, vagas e publica. |
| F02 | Aluno presencial | A secretaria pesquisa aluno por email, telefone ou BI; reutiliza o registo existente ou cria ficha nova. |
| F03 | Matrícula | O funcionário escolhe curso e turma, aplica preço, desconto e origem, e cria matrícula com código único. |
| F04 | Inscrição Eduka-Angola | Uma inscrição recebida por API é processada sem duplicar aluno, inscrição ou matrícula. |
| F05 | Pagamento único | O caixa regista recebimento, método, responsável e gera recibo PDF. |
| F06 | Pagamento parcelado | O sistema mantém parcelas, vencimentos, saldo, atrasos e recibos independentes. |
| F07 | Caixa | O caixa abre, regista movimentos, fecha o dia e identifica diferenças. |
| F08 | Operação de turma | A secretaria consulta alunos, transfere, suspende, cancela e conclui matrículas. |
| F09 | Presenças | O centro lança presença diária, justifica faltas, calcula assiduidade e fecha a folha. |
| F10 | Avaliação | O centro lança avaliações, calcula resultado final e fecha a pauta. |
| F11 | Certificação | O sistema só emite certificado quando os critérios da turma forem cumpridos. |
| F12 | Validação | O certificado possui código ou QR Code e página pública de validação. |
| F13 | Documentos | A ficha do aluno mantém BI, contratos, comprovativos e documentos académicos com histórico. |
| F14 | Permissões | Gestor, secretaria, caixa, coordenação e consulta têm acessos diferentes e verificáveis. |
| F15 | Auditoria | Alterações financeiras, académicas e administrativas registam utilizador, data e ação. |
| F16 | Relatórios | O centro exporta alunos, receitas, dívidas, presenças, notas, certificados e origens. |

## Fora do MVP de prontidão

A aplicação móvel do formador, gamificação, inteligência artificial, marketplace avançado, peer review, integração de emprego e automações sofisticadas de WhatsApp ficam fora do primeiro critério de pronto. Podem ser desenvolvidas depois de os fluxos administrativos e académicos estarem estáveis.

## Regra de aceitação

Nenhum módulo será marcado como concluído apenas porque a tela abre. Deve existir pelo menos um teste que crie ou altere dados, confirme a regra de negócio e verifique o resultado final através da interface ou da base de dados.
