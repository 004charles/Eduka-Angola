# Validação local — Conta de aluno e candidatura de centro

Foram executados testes isolados das aplicações `usuarios`, `centro_formacao` e `gestoreduka`.

| Fluxo validado | Resultado |
|---|---|
| Registo React com origem de pré-visualização e CSRF | Aprovado |
| Criação de conta pendente de verificação | Aprovado |
| Verificação de código e início de sessão | Aprovado |
| Login React e preservação de destino local | Aprovado |
| Resumo da área do aluno com sessão | Aprovado |
| Link único de candidatura de centro, conclusão e prevenção de reutilização | Aprovado |

Foram executados 10 testes e todos terminaram com sucesso. A validação por envio real de e-mail, expiração temporal e configuração do provedor continua pendente para staging.
