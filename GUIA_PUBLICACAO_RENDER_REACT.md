# Publicação React + Django no Render

## Diagnóstico da falha recebida

O log de publicação não aponta para um erro de React. O processo Django terminava antes de iniciar porque `core.views` importava `matplotlib` globalmente, mas a dependência não estava declarada no ambiente Render. A importação foi tornada segura e `matplotlib==3.10.8` foi acrescentado aos dois manifestos Python.

> A publicação anterior também continuaria a entregar a página HTML legada no endereço principal. A configuração actual passa a compilar a aplicação React e a servi-la pelo mesmo processo Django, preservando sessão, cookies, API e PWA no mesmo domínio.

## Configuração do serviço web existente

Depois de enviar a alteração para o GitHub, abra o serviço **Edukangola** no Render e confirme os comandos abaixo em **Settings**.

| Campo Render | Valor |
|---|---|
| Build Command | `./render-build.sh` |
| Pre-Deploy Command | `python manage.py migrate --noinput` |
| Start Command | `gunicorn eduangolacore.wsgi:application --bind 0.0.0.0:$PORT --log-file -` |
| Runtime | Python 3.13 e Node 22 |

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
| `NODE_VERSION` | `22.13.0` |
| `PYTHON_VERSION` | `3.13.0` |

As restantes variáveis já necessárias para pagamentos, e-mail, Cloudinary, notificações e VAPID devem ser preservadas sem alteração.

## O que a publicação faz

O `render-build.sh` instala as dependências React, compila `frontend/dist`, instala as dependências Python e executa `collectstatic`. O Django entrega a SPA compilada na raiz e em rotas React, enquanto `/api/...` permanece API Django. O prefixo `/backend/...`, usado pela interface para pedidos autenticados, é encaminhado internamente para as rotas Django reais; por isso não depende do proxy Vite em produção.

## Validação realizada

No ambiente local, o processo Gunicorn devolveu HTTP 200 para a raiz React, `/api/public/home/` e `/backend/api/public/home/`. A raiz continha o elemento de montagem React `#root`, confirmando que já não serve o template HTML legado.
