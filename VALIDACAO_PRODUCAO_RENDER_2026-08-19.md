# Validação de produção: Render + Vercel

## Resultado confirmado

O deploy Render concluiu as migrações, recolheu 1 392 ficheiros estáticos e iniciou Gunicorn no porto atribuído pelo Render. A API está acessível no domínio oficial.

| Endereço | Resultado |
|---|---|
| `https://api.edukangola.com/api/public/home/` | HTTP 200 com resposta JSON da API Django. |
| `https://www.edukangola.com/` | HTTP 200 com a aplicação React do Vercel. |
| `https://api.edukangola.com/` | HTTP 404 esperado: a raiz do subdomínio é API, não uma página pública. |

## Observações

As mensagens de ficheiros estáticos duplicados durante `collectstatic` são avisos não bloqueantes; o deploy completou e o serviço está em funcionamento. As variáveis `DATABASE_URL`, `SECRET_KEY` e `DEBUG=False` permitiram ultrapassar os bloqueios de inicialização anteriores.
