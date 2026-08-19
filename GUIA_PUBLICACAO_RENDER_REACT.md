# Publicação React + Django no Render

> **Arquitectura actualizada:** o React será publicado no Vercel e o Django ficará no Render. Esta secção de serviço único permanece apenas como alternativa de recuperação; siga o guia Vercel/Render abaixo para a publicação definitiva.

## Diagnóstico da falha recebida

O log de publicação não aponta para um erro de React. O processo Django terminava antes de iniciar porque `core.views` importava `matplotlib` globalmente, mas a dependência não estava declarada no ambiente Render. A importação foi tornada segura e `matplotlib==3.10.8` foi acrescentado aos dois manifestos Python.

> A publicação anterior também continuaria a entregar a página HTML legada no endereço principal. A arquitectura definitiva mantém o Django no Render como API e entrega a aplicação React/PWA pelo Vercel, com pedidos de API reescritos para o Render.

## Configuração do serviço web existente

Depois de enviar a alteração para o GitHub, abra o serviço **Edukangola** no Render e confirme os comandos abaixo em **Settings**.

| Campo Render | Valor |
|---|---|
| Build Command | `./render-build.sh` |
| Pre-Deploy Command | `python manage.py migrate --noinput` |
| Start Command | `gunicorn eduangolacore.wsgi:application --bind 0.0.0.0:$PORT --log-file -` |
| Runtime | Python 3.13 |

O ficheiro `render.yaml` contém a mesma receita para serviços novos ou para uma futura migração a Blueprint. Num serviço já criado, a alteração manual destes três comandos continua a ser necessária caso ele não esteja ligado a um Blueprint.

## Variáveis de ambiente obrigatórias

| Variável | Orientação |
|---|---|
| `DJANGO_ENV` | `production` |
| `SECRET_KEY` | Definir um valor secreto forte no painel Render. Nunca incluir no Git. |
| `DATABASE_URL` | Ligação PostgreSQL de produção. |
| `ALLOWED_HOSTS` | Domínio Render e domínio próprio, separados por vírgula. |
| `CSRF_TRUSTED_ORIGINS` | URLs HTTPS completas desses domínios, separadas por vírgula. |
| `SITE_DOMAIN` | URL pública principal, por exemplo `https://www.edukangola.com`. |
| `PYTHON_VERSION` | `3.13.0` |

As restantes variáveis já necessárias para pagamentos, e-mail, Cloudinary, notificações e VAPID devem ser preservadas sem alteração.

## O que a publicação faz

O `render-build.sh` instala dependências Python e executa `collectstatic`. A compilação React deixa de ser responsabilidade do Render: o Vercel compila a pasta `frontend` e encaminha os pedidos de API ao Django. O prefixo `/backend/...`, usado pela interface para pedidos autenticados, é reescrito pelo Vercel para as rotas Django reais.

## Validação realizada

No ambiente local, o processo Gunicorn devolveu HTTP 200 para a raiz React, `/api/public/home/` e `/backend/api/public/home/`. A raiz continha o elemento de montagem React `#root`, confirmando que já não serve o template HTML legado.

## Publicação definitiva: Vercel + Render

| Serviço | Directório no mesmo repositório | Domínio |
|---|---|---|
| Vercel | `frontend` | `www.edukangola.com` |
| Render | raiz do repositório | `api.edukangola.com` |

No projecto Vercel, definir **Root Directory** como `frontend`. O `frontend/vercel.json` compila a aplicação Vite, encaminha `/api`, `/backend`, `/auth`, `/static` e `/media` para `api.edukangola.com`, e preserva o fallback SPA para recarregamentos de páginas React.

No serviço Render, adicionar `api.edukangola.com` como domínio personalizado e manter o build/start do Django. Definir as variáveis abaixo no Render:

| Variável | Valor de produção |
|---|---|
| `SITE_DOMAIN` | `https://www.edukangola.com` |
| `ALLOWED_HOSTS` | `api.edukangola.com,eduka-angola.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | `https://www.edukangola.com,https://edukangola.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://www.edukangola.com,https://edukangola.com,https://api.edukangola.com` |
| `SESSION_COOKIE_DOMAIN` | `.edukangola.com` |
| `CSRF_COOKIE_DOMAIN` | `.edukangola.com` |
| `SESSION_COOKIE_SAMESITE` | `Lax` |
| `CSRF_COOKIE_SAMESITE` | `Lax` |
| `CORS_ALLOW_CREDENTIALS` | `True` |

Não definir `VITE_API_BASE_URL` no Vercel enquanto as reescritas estiverem activas. As chamadas permanecem no domínio `www`, o que preserva os fluxos de sessão existentes e evita expor o endereço técnico do Render no browser.

### Ordem de configuração

1. No **Vercel**, importar o mesmo repositório GitHub, definir `frontend` como **Root Directory** e confirmar que o preview compila.
2. Em **Vercel → Settings → Domains**, adicionar `www.edukangola.com`. Copiar o CNAME exacto apresentado pelo Vercel.
3. Em **Render → serviço Edukangola → Settings → Custom Domains**, adicionar `api.edukangola.com` e guardar. Criar um CNAME `api` no fornecedor DNS a apontar para `eduka-angola.onrender.com`, depois usar **Verify** no Render.
4. Confirmado `api`, substituir somente o CNAME `www` actual pelo CNAME indicado no Vercel e aguardar a verificação SSL. Não apagar os dois CNAMEs DKIM nem o TXT do Brevo.
5. Quando `www` estiver verificado, aplicar as variáveis de produção no Render e publicar o commit mais recente. Só então testar login, inscrição, mensagens, preferências e notificações no domínio público.

O registo A do ápice `@` pode permanecer temporariamente no Render durante a migração. Depois de validar `www`, pode adicionar `edukangola.com` ao Vercel e configurar um redireccionamento para `www.edukangola.com`, usando exactamente o valor de A record que o painel Vercel apresentar.
