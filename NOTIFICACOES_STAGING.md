# Activação das notificações em staging

O gateway de notificações e o worker são processos separados. Ambos devem ser configurados no mesmo provedor do Django, em rede privada sempre que possível.

## Processos necessários

| Processo | Comando | Finalidade |
|---|---|---|
| Gateway | `uvicorn notification_service.main:app --host 0.0.0.0 --port $PORT` | Recebe eventos assinados do Django e responde ao health check. |
| Worker | `python -m notification_service.worker` | Resolve destinatários e entrega notificações de plataforma/e-mail. |

## Variáveis de ambiente

Definir somente no painel de segredos do provedor:

```text
NOTIFICATION_SERVICE_SHARED_SECRET=<valor longo e aleatório>
NOTIFICATION_SERVICE_DJANGO_SECRET=<valor longo e aleatório>
NOTIFICATION_WORKER_SECRET=<valor longo e aleatório>
DJANGO_INTERNAL_API_URL=https://<dominio-interno-ou-privado-do-django>
NOTIFICATION_DATABASE_PATH=<armazenamento persistente no ambiente temporário>
BREVO_API_KEY=<chave do ambiente>
DEFAULT_FROM_EMAIL=<remetente verificado>
```

O Django deve receber a URL HTTPS/privada do gateway e o mesmo `NOTIFICATION_SERVICE_SHARED_SECRET` usado pelo gateway. Estes valores nunca devem entrar no repositório.

## Critérios de aceitação de staging

1. `GET /health` do gateway devolve HTTP 200.
2. A publicação de um curso cria evento na outbox Django.
3. O gateway aceita o evento assinado e rejeita assinatura inválida ou repetida.
4. O worker cria uma notificação na conta de um aluno elegível.
5. Com preferência de e-mail activa, o destinatário recebe uma mensagem Brevo de teste.
6. Com a preferência desactivada, não é criada entrega naquele canal.
7. Os logs dos dois processos estão acessíveis no provedor e há reinício automático configurado.

## Estado validado localmente

Os três testes unitários do serviço passaram. Um gateway iniciado temporariamente com segredos fictícios respondeu `HTTP 200` em `/health`, sem entregar e-mails ou contactar serviços externos.
