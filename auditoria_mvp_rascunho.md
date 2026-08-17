# Auditoria de prontidão do MVP — Evidências iniciais

## Linha de base automatizada

A execução global de `env -u DATABASE_URL python3 manage.py test --verbosity 1` encontrou **43 testes**, mas terminou com falha: **3 erros de importação** e **1 falha de asserção**.

| Área | Evidência | Impacto inicial |
|---|---|---|
| Scripts de checkout de visitante | `test_guest_enrollment.py` e `test_guest_paid_checkout.py` executam asserções no momento da importação e falham a descoberta de testes. | A suite não é fiável para validar inscrições e checkout. |
| Páginas públicas | `test_public_pages.py` falha uma asserção de estado HTTP ao importar. | Não existe garantia automatizada de que as páginas públicas críticas continuam acessíveis. |
| Pagamentos | `PagamentoAPITestCase.test_listar_pagamentos_usuario_autenticado` esperava lista vazia e recebeu quatro pagamentos. | O isolamento/limpeza de dados do teste de pagamentos está incompleto. |
| Integração Prontu durante testes | A saída mostra autenticação e tentativa de criação de transacções durante a bateria. | Testes de pagamentos não estão completamente isolados; antes de produção, devem usar mock obrigatório e nunca contactar o gateway real. |

Esta evidência é apenas a primeira fase da auditoria. A compilação React, os fluxos públicos e os serviços externos serão verificados separadamente para evitar que a falha de testes interrompa o restante diagnóstico.

## Correcção aplicada durante a auditoria

A suite Django foi estabilizada durante este trabalho. Os três scripts manuais que tinham asserções no momento de importação foram movidos para `arquivos_scripts/`, fora da descoberta automática. A Prontu deixou de autenticar externamente no runner de testes e passa a devolver transacções simuladas por defeito; testes que verificam payload ou validação usam simulação explícita.

Após a correcção, `env -u DATABASE_URL python3 manage.py test --verbosity 1` executou **40 testes** e terminou com **OK**, sem autenticação ou criação de transacção externa no gateway.

## Catálogo, área do aluno e aprendizagem

| Verificação | Resultado | Leitura de prontidão |
|---|---|---|
| Compilação do frontend React | `pnpm --dir frontend run build` concluiu com sucesso. | A aplicação compila, mas o bundle JavaScript final tem cerca de 885 kB e ultrapassa o limite de aviso do Vite. Não bloqueia o MVP, mas deve ser optimizado após estabilização. |
| Verificação Django | `manage.py check` sem problemas e migrations aplicadas no ambiente local. | A estrutura de dados local está consistente. Isto não confirma o estado da base de dados de produção. |
| APIs públicas | Home, FAQ, detalhe de curso em vídeo e perfil público de centro responderam com HTTP 200 no servidor local. | Os dados públicos essenciais respondem no ambiente de desenvolvimento. |
| Área do aluno | Aberta com a sessão activa; apresentou cursos activos, inscrições, favoritos, leituras e atalhos. | O painel base está operacional para a conta de teste usada na auditoria. |
| Continuidade e avaliações de vídeo | Testes específicos passaram; a página apresenta as áreas condicionadas ao acesso/progresso. | Fluxo técnico coberto localmente, mas ainda requer teste manual de pagamento, acesso, primeira aula, retoma e avaliação com uma conta real. |
| Testes frontend | O `package.json` do frontend apenas declara desenvolvimento, build e preview; não declara testes unitários/e2e. | Regressões de interface, rotas e interacções React não são apanhadas automaticamente. |

> A rota `/api/react/biblioteca/catalogo/` devolveu 404 durante a sondagem inicial, mas não foi classificada como falha: a rota pública correcta é `/api/react/biblioteca/`, confirmada na configuração da aplicação.

## Centros, pagamentos, notificações e operação

| Prioridade | Evidência | Consequência antes do lançamento |
|---|---|---|
| P0 | `manage.py check --deploy` encontrou seis avisos: DEBUG activo, chave Django de desenvolvimento, ausência de redireccionamento HTTPS, HSTS e cookies de sessão/CSRF seguros. | A configuração actual não é aceitável para produção pública. |
| P0 | Uma migration histórica cria uma conta administrativa inicial com uma credencial embutida. | A credencial deve ser removida do histórico operacional, rodada e substituída por criação segura fora do repositório. |
| P0 | A suite de pagamentos contactou/autenticou no gateway durante os testes. | É necessário obrigar mocks no ambiente de teste e separar claramente credenciais/testes do gateway real. |
| P1 | O serviço separado de notificações não responde em `localhost:8080`; não há worker activo. | As preferências já existem, mas entrega de notificações e e-mail não está operacional neste ambiente. |
| P1 | O serviço de notificações requer pelo menos segredos HMAC, URL interna, chave de e-mail e worker/scheduler; a documentação indica que a base local deve ser substituída por armazenamento gerido em produção. | A arquitectura está preparada, mas a activação operacional ainda não foi comprovada. |
| P1 | O Procfile principal inicia apenas o Django. O gateway e o worker de notificações têm Procfiles próprios. | O provedor precisa de processos separados, variáveis de ambiente e monitorização; sem isto, notificações ficam inactivas. |
| P1 | O ambiente local tem processos de desenvolvimento duplicados do Django em 8000 e Vite em 5173. | Não é uma topologia de produção nem prova que a supervisão/reinício de serviços esteja pronta. |
| P1 | Não foram encontrados ficheiros `.env`, chaves PEM ou ficheiros de credenciais versionados pelo inventário simples. | É positivo, mas não substitui a rotação de credenciais antigas e a revisão da migration administrativa. |

Os endpoints de planos de centros respondem localmente. As rotas de candidatura que recebem dados por POST responderam 405 em GET, como esperado. A rota de confirmação usa um link de convite por GET e, sem token, devolve 404; isto é coerente com a implementação, mas o fluxo completo de e-mail, código e conclusão ainda precisa de um teste manual em ambiente com e-mail configurado.
