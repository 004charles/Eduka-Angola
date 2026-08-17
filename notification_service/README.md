# Serviço de notificações Edukangola

Este processo recebe eventos assinados do Django e garante a aceitação idempotente antes do processamento de destinatários e canais.

## Execução local

A partir da raiz do repositório:

```bash
python3 -m venv .venv-notifications
. .venv-notifications/bin/activate
pip install -r notification_service/requirements.txt
export NOTIFICATION_SERVICE_SHARED_SECRET='defina-apenas-no-ambiente'
uvicorn notification_service.main:app --reload --port 8080
```

O endpoint de saúde é `GET /health` e a ingestão é `POST /v1/events`. O processo `python -m notification_service.worker` deve correr como worker separado; ele resolve destinatários e cria as notificações na plataforma. A rota `POST /v1/process-pending` existe para execução controlada por um scheduler, protegida por `NOTIFICATION_WORKER_SECRET`.

## Variáveis de ambiente

| Variável | Obrigatória | Finalidade |
|---|---:|---|
| `NOTIFICATION_SERVICE_SHARED_SECRET` | Sim | Assinatura HMAC entre Django e o serviço |
| `NOTIFICATION_DATABASE_PATH` | Não em desenvolvimento | Caminho do armazenamento local; em produção será substituído por uma base de dados gerida |
| `DJANGO_INTERNAL_API_URL` | Sim na entrega | URL privada para sincronizar notificações na conta do aluno |
| `BREVO_API_KEY` | Sim para e-mail | Credencial do fornecedor de e-mail, apenas no serviço |
| `NOTIFICATION_SERVICE_DJANGO_SECRET` | Sim | Chave para as APIs internas de destinatários e criação de notificações |
| `NOTIFICATION_WORKER_SECRET` | Sim para a rota manual | Protege o disparo de processamento por scheduler |
| `NOTIFICATION_WORKER_INTERVAL_SECONDS` | Não | Intervalo do worker, com mínimo de 5 segundos |

Nenhuma destas variáveis deve ser adicionada ao GitHub. O primeiro marco disponibiliza somente ingestão autenticada e deduplicação; o processador de entregas será ligado depois de o contrato de destinatários e a API interna do Django estarem prontos.
