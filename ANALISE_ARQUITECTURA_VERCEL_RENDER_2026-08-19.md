# Avaliação: Vercel para React e Render para Django

## Recomendação

A separação é recomendada, desde que os dois serviços usem **subdomínios do mesmo domínio próprio**. A configuração preferida é `www.edukangola.com` no Vercel para o React e `api.edukangola.com` no Render para o Django. Assim, o frontend pode ser entregue pela CDN do Vercel e o Render concentra-se no Django, base de dados, ficheiros, sessões, administração e tarefas de servidor.

Usar os domínios temporários `*.vercel.app` e `*.onrender.com` como configuração definitiva não é aconselhável para a Edukangola. Eles são sites distintos para o navegador e tornam a partilha de sessão baseada em cookies consideravelmente mais frágil. O Django documenta que a partilha de cookies entre subdomínios controlados pode ser configurada com um domínio de cookie comum, como `.edukangola.com`, e que origens adicionais devem constar em `CSRF_TRUSTED_ORIGINS`.

## Configuração proposta

| Camada | Plataforma | Domínio | Responsabilidade |
|---|---|---|---|
| Interface | Vercel | `www.edukangola.com` | React/Vite, PWA, páginas públicas e área React. |
| API e servidor | Render | `api.edukangola.com` | Django, sessões, CSRF, pagamentos, ficheiros, administração e Web Push. |
| Dados | Serviço actual | Sem alteração | PostgreSQL e recursos já associados ao backend. |

## Registos DNS observados e mudança proposta

O painel DNS apresentado contém o domínio `edukangola.com`, um registo A no ápice `@` para `216.24.57.1`, o CNAME `www` para `eduka-angola.onrender.com` e registos Brevo de DKIM/TXT. Os registos Brevo não devem ser modificados.

| Host | Situação actual | Destino após a migração | Acção |
|---|---|---|---|
| `@` | A → `216.24.57.1` | Manter no Render temporariamente | Mantém `edukangola.com` disponível enquanto a migração de `www` é validada. |
| `www` | CNAME → `eduka-angola.onrender.com` | CNAME exacto indicado pelo Vercel | Substituir somente depois de adicionar `www.edukangola.com` no projecto Vercel. |
| `api` | Não existe | CNAME → `eduka-angola.onrender.com` | Criar depois de adicionar `api.edukangola.com` nos domínios do serviço Render. |
| `brevo1._domainkey`, `brevo2._domainkey`, TXT Brevo | Activos | Sem alteração | Preservar para não interromper autenticação de e-mail. |

O Vercel apresenta no painel um destino CNAME específico do projecto; este valor deve ser copiado exactamente, em vez de assumir um CNAME genérico. O Render recomenda CNAME para subdomínios, portanto `api` deve apontar para `eduka-angola.onrender.com` depois de `api.edukangola.com` ser acrescentado ao serviço Render. Antes da alteração de `www`, é recomendável reduzir o TTL para 60 segundos com antecedência e confirmar a propagação.

## Ajustes que serão necessários

O Vercel encaminhará os caminhos de API para `api.edukangola.com`, mantendo a origem visível `www.edukangola.com` para o browser. Assim, as chamadas existentes e os seus cookies continuam no mesmo contexto para o utilizador. O Django restringirá explicitamente CORS e CSRF aos domínios públicos, activará `CORS_ALLOW_CREDENTIALS`, e poderá definir `SESSION_COOKIE_DOMAIN=.edukangola.com` e `CSRF_COOKIE_DOMAIN=.edukangola.com` para a continuidade de sessão entre os dois subdomínios controlados.

O Vercel precisa de uma regra SPA para que endereços como `/aluno`, `/cursos/81` e `/aprender/video/...` devolvam `index.html` em recarregamentos. A documentação Vercel recomenda uma regra `rewrites` para este fim em aplicações Vite SPA.

## Decisão antes da implementação

Esta mudança é uma melhoria estrutural, mas requer ligar os dois domínios próprios no Vercel e Render e configurar variáveis de ambiente nos dois painéis. Por isso, a preparação de código deve avançar apenas após confirmar que `www.edukangola.com` e `api.edukangola.com` serão usados.

## Referências

- [1] [Vercel — Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite)
- [2] [Vercel — Environment variables](https://vercel.com/docs/environment-variables)
- [3] [Django — Cross Site Request Forgery protection](https://docs.djangoproject.com/en/6.0/ref/csrf/)
- [4] [Django REST framework — AJAX, CSRF & CORS](https://www.django-restframework.org/topics/ajax-csrf-cors/)
- [5] [Vercel — Adding & Configuring a Custom Domain](https://vercel.com/docs/domains/working-with-domains/add-a-domain)
- [6] [Vercel — Working with DNS](https://vercel.com/docs/domains/working-with-dns)
- [7] [Render — Custom Domains](https://render.com/docs/custom-domains)
- [8] [Render — Configuring DNS Providers](https://render.com/docs/configure-other-dns)
