# Auditoria de prontidão do MVP Edukangola

**Data da auditoria:** 17 de agosto de 2026
**Ambiente avaliado:** desenvolvimento local com frontend React, Django e SQLite local.
**Conclusão executiva:** **não é correcto considerar o MVP 100% terminado nem afirmar que tudo está a funcionar.** A plataforma já tem uma base funcional relevante, mas há bloqueios técnicos e operacionais que precisam de ser resolvidos e testados antes de receber alunos, centros e pagamentos reais em produção.

## Actualização após a correção inicial

Os bloqueios de código mais urgentes identificados nesta auditoria foram tratados: a suite Django passou a executar **40 testes com sucesso**, a Prontu passou a ser simulada no runner de testes, a configuração de produção foi separada do desenvolvimento e o gateway de notificações foi validado localmente. A plataforma continua dependente de uma validação de staging para e-mail real, pagamento real/sandbox, processos persistentes de notificações e configuração de segredos no provedor.

> Esta auditoria distingue claramente entre funcionalidades que respondem no ambiente local, funcionalidades implementadas mas não validadas ponta a ponta e capacidades que ainda não estão prontas para produção.

## 1. Estado actual por área

| Área | Estado | Evidência observada | Conclusão |
|---|---|---|---|
| Interface React pública | **Funcional localmente** | O frontend compila com sucesso e as APIs de home, FAQ, centros e detalhe de curso em vídeo responderam com HTTP 200. | A base visual está utilizável, mas ainda não tem testes automáticos de interface. |
| Catálogo presencial e centros | **Funcional localmente** | Catálogo e perfil público de centro estão disponíveis; a área de centros responde no backend. | Requer uma ronda manual de filtros, paginação, inscrição e seguimento numa conta limpa. |
| Biblioteca de cursos em vídeo | **Funcional localmente** | Existem 22 programas publicados, filtros por área, detalhe em estilo streaming, acesso, aulas, progresso, continuidade e avaliações. | É uma das áreas mais evoluídas; falta validar compra/acesso real em produção. |
| Área do aluno | **Funcional localmente** | O painel carregou cursos activos, inscrições, favoritos, leituras, certificados e atalhos. | Necessita de testes manuais para alunos novos, sem dados e com pagamentos reais. |
| Avaliações e comentários | **Coberto localmente** | Testes confirmam bloqueio antes do início, criação e actualização de uma avaliação sem duplicação. | A moderação administrativa e a experiência com comentários reais ainda devem ser testadas por utilizadores. |
| Biblioteca editorial | **Parcialmente validada** | As rotas correctas existem e a leitura/progresso fazem parte do painel do aluno. | É preciso validar compra de livro, leitura no telemóvel, voz e retoma com uma conta real. |
| Centros e candidatura | **Implementado, não validado ponta a ponta** | Planos respondem; o fluxo usa candidatura, código/link e criação de gestor. | Falta testar e-mail, expiração, tentativas, criação de centro e acesso ao GestorEduka. |
| Pagamentos Prontu | **Não pronto para produção** | Existem criação de pagamentos e retorno, mas a suite de pagamentos não é isolada e contactou o gateway durante testes. | Não deve receber dinheiro real antes de mocks, callback e reconciliação serem verificados em staging. |
| Bilhetes de eventos | **Implementado, não validado ponta a ponta** | Modelos, compra e área do aluno existem. | Falta testar emissão, pagamento, QR/código e validação de entrada com dados reais. |
| Notificações | **Não operacional neste ambiente** | O gateway/worker separados existem, mas `localhost:8080/health` não respondeu e não há worker activo. | Preferências de interface não garantem entrega por e-mail ou na plataforma. |
| Internacionalização | **Parcial** | O menu tem PT, EN, FR e ZH. | Conteúdo administrativo e dados cadastrados não têm tradução automática garantida. |

## 2. Problemas que bloqueiam o lançamento

| Prioridade | Problema | Porque bloqueia o MVP | Correcção necessária |
|---|---|---|---|
| **P0** | A bateria completa de testes falha: 3 erros de descoberta/importação e 1 falha de pagamentos. | Não há prova automática confiável de que inscrições, checkout e páginas públicas não regressaram. | Converter scripts soltos em testes Django reais, corrigir asserções e garantir base limpa por teste. |
| **P0** | Testes de pagamento autenticararam/tentaram criar transacções no gateway. | Um ambiente de teste não pode depender nem correr o risco de acções no fornecedor real. | Aplicar mock obrigatório a Prontu em testes, criar ambiente sandbox separado e bloquear credenciais reais no runner de testes. |
| **P0** | Configuração de implantação insegura: DEBUG activo, chave de desenvolvimento, HTTPS/HSTS e cookies seguros ausentes. | Expõe sessões, dados e comportamentos de desenvolvimento se for publicado assim. | Criar configuração de produção por variáveis de ambiente, exigir HTTPS e rodar a chave Django antes da publicação. |
| **P0** | Existe uma migration histórica com criação de administrador e credencial embutida. | Mesmo que a conta já tenha sido alterada, essa credencial faz parte do histórico do repositório. | Revogar/rodar credenciais, criar administrador via processo seguro de implantação e documentar a remoção do risco. |
| **P1** | Serviço de notificações e worker não estão em execução. | Avisos de cursos, turmas, livros, eventos e e-mails não são entregues. | Configurar os dois processos, segredos HMAC, acesso interno, Brevo e monitorização no provedor. |
| **P1** | Registo e candidatura de centro dependem de e-mail e códigos, mas o fluxo completo não foi executado em ambiente configurado. | Alunos/centros podem ficar bloqueados sem concluir acesso. | Teste ponta a ponta com caixas de e-mail de teste, expiração, tentativas e recuperação. |
| **P1** | Não existem testes frontend declarados. | Interacções React, redireccionamentos, filtros e botões podem quebrar sem alerta. | Adicionar testes de componentes e testes e2e aos fluxos críticos. |

## 3. Funcionalidades que ainda precisam de prova ponta a ponta

Estas capacidades podem ter código implementado, mas não devem ser dadas como concluídas sem o cenário completo em um ambiente semelhante ao de produção.

| Fluxo | Cenário mínimo de aceitação |
|---|---|
| Cadastro de aluno | Criar conta, receber código por e-mail, validar, entrar, terminar sessão e recuperar palavra-passe. |
| Curso gratuito em vídeo | Activar acesso, abrir primeira aula, guardar progresso, retomar, concluir e emitir certificado. |
| Curso pago em vídeo | Criar pagamento, concluir no Prontu sandbox, receber retorno, liberar acesso e registar pedido. |
| Curso presencial | Inscrever-se, escolher turma quando aplicável, confirmar estado da inscrição e pagamento. |
| Centro | Solicitar candidatura por e-mail/NIF, validar código/link, concluir cadastro, entrar no GestorEduka e publicar curso. |
| Bilhete de evento | Comprar, confirmar retorno de pagamento, mostrar bilhete, validar código na entrada e evitar reutilização. |
| Notificações | Publicar curso/evento, gravar outbox, processar worker, criar notificação e enviar e-mail conforme preferência. |
| Biblioteca | Guardar livro, iniciar leitura, fechar sessão, retomar página, testar leitura por voz e restrição de acesso pago. |

## 4. Plano pragmático para fechar o MVP

### Bloco A — Segurança e estabilidade de lançamento

Primeiro devem ser removidos os riscos de produção. Isso inclui uma configuração de produção sem DEBUG, nova chave Django, HTTPS obrigatório, cookies seguros, rotação da credencial administrativa histórica e remoção de segredos de todos os ambientes de código. Em paralelo, a suite de testes deve voltar a ficar verde e sem chamadas ao gateway real.

### Bloco B — Fluxos comerciais reais

Depois, o trabalho deve focar no que gera acesso e receita: e-mail de cadastro, recuperação de palavra-passe, compra de curso, retorno do Prontu, liberação de acesso, bilhete de evento e candidatura de centro. Cada fluxo precisa de uma conta/caso de teste, registo de evidência e tratamento de erro claro.

### Bloco C — Operação contínua

Por fim, activar o gateway e worker de notificações, configurar Brevo, logs, alertas e processos separados no provedor. Sem esta etapa, a plataforma pode abrir, mas não terá comunicação confiável com utilizadores.

### Bloco D — Qualidade pós-beta

Após os três blocos anteriores, podem entrar optimização do bundle React, cobertura de testes frontend, aperfeiçoamento de traduções de conteúdo, moderação de avaliações e métricas de produto.

## 5. Decisão recomendada

O produto está num bom ponto de **beta fechado local**, especialmente nas experiências de descoberta, catálogo, biblioteca em vídeo e área do aluno. Porém, ainda não está pronto para um lançamento público com pagamentos e dados reais.

O caminho correcto é fechar primeiro os itens P0 e P1, executar os oito fluxos ponta a ponta acima em um ambiente de staging e só então publicar. Depois da auditoria, a próxima etapa recomendada é criar uma lista executável de correções P0, começando pela segurança de produção e pelo isolamento dos testes de pagamentos.
