# Operação segura para staging e produção

## Variáveis obrigatórias em staging/produção

Defina `DJANGO_ENV=staging` ou `DJANGO_ENV=production`. Nesses ambientes, o Django recusa iniciar com `DEBUG=True`, chave insegura, CORS vazio ou origens CSRF ausentes.

| Variável | Exigência |
|---|---|
| `SECRET_KEY` | Valor novo, aleatório e com pelo menos 50 caracteres. Nunca reutilizar valores de desenvolvimento. |
| `DEBUG` | `False`. |
| `ALLOWED_HOSTS` | Lista separada por vírgulas com os domínios exactos do ambiente. |
| `CSRF_TRUSTED_ORIGINS` | Origens HTTPS completas do frontend e backend. |
| `CORS_ALLOWED_ORIGINS` | Apenas origens que realmente consomem a API. Pode ficar vazio quando o frontend é servido no mesmo domínio e CORS não é necessário. |
| `SECURE_SSL_REDIRECT` | `True` quando o proxy já termina TLS. |
| `SESSION_COOKIE_SECURE` e `CSRF_COOKIE_SECURE` | `True`. |
| `SECURE_HSTS_PRELOAD` | Activar como `True` apenas depois de confirmar que todos os subdomínios usam HTTPS permanentemente. |
| `SITE_DOMAIN` | URL HTTPS pública, sem caminho adicional. |
| `PRONTU_CALLBACK_URL`, `FRONTEND_RETURN_URL`, `FRONTEND_CANCEL_URL` | URLs HTTPS do ambiente, nunca localhost. |

## Administradores

A migration histórica deixou de criar automaticamente uma conta administrativa. Antes de publicar, um operador deve:

1. Rever contas administrativas existentes e desactivar qualquer conta de bootstrap que não seja necessária.
2. Alterar imediatamente a palavra-passe de contas existentes e activar MFA no provedor/administrador quando disponível.
3. Criar um novo superutilizador directamente no ambiente com `python manage.py createsuperuser`; nunca guardar a palavra-passe em ficheiros ou commits.

## Processos de produção

O processo principal inicia o Django via Gunicorn. O serviço de notificações exige **dois processos adicionais**: o gateway FastAPI e o worker. Ambos devem receber variáveis de ambiente próprias, health check e reinício automático no provedor.

## Antes de activar pagamentos reais

1. Executar a suite de testes com a Prontu obrigatoriamente simulada.
2. Validar criação, callback assinado, retorno ao frontend, idempotência e reconciliação num ambiente sandbox.
3. Só então colocar `PRONTU_ENV=1` e credenciais de produção no provedor.
