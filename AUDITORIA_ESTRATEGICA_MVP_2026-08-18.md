# Auditoria estratégica e técnica da Edukangola

**Data:** 18 de Agosto de 2026  
**Âmbito:** preparação do produto para adopção real em Angola, lançamento controlado e monetização sustentável.  
**Decisão recomendada:** **pronto para beta fechado, ainda não pronto para lançamento público amplo.**

## 1. Resumo executivo

A Edukangola tem mais produto do que um MVP: existe catálogo de cursos presenciais e em vídeo, perfis de centros, candidatura, biblioteca, bolsas, eventos, pagamentos, certificados verificáveis, GestorEduka, área de aluno, notificações, IA pública e administração Django. O problema não é falta de funcionalidades. O problema é **excesso de superfície de produto antes de haver uma proposta de valor comercial estreita, dados institucionais verificados e operação de produção comprovada**.

> A versão 1.0 não deve tentar ser simultaneamente Udemy, Coursera, marketplace de bilhetes, biblioteca, bolsa, plataforma de emprego e ERP académico. Deve vencer primeiro uma necessidade concreta: **ajudar estudantes a descobrir cursos e centros confiáveis, comparar alternativas e iniciar uma candidatura com resposta rastreável.**

> O mercado justifica este foco. Angola tem uma população muito jovem; a fonte comercial dos EUA estima que 66% da população tem menos de 25 anos e descreve dificuldades de acesso, conclusão e qualidade. A mesma fonte identifica oportunidades em formação técnico-profissional, qualificação de professores e soluções EdTech de baixo custo. [1]

O código tem uma base séria. A suite Django actual executou **68 testes sem falhas**, `manage.py check` não reportou erros e há uma separação funcional razoável entre domínio Django e experiência React. Isto reduz risco de reescrita. Não prova, contudo, disponibilidade, segurança de operações, desempenho em dados reais, recuperação de desastre ou conversão comercial. A auditoria técnica anterior também identificou que a base de domínio é forte, mas que notificações distribuídas, cache partilhada, certificados, reputação e operação de produção ainda precisam de consolidação. [4]

| Diagnóstico | Leitura prática | Decisão |
|---|---|---|
| Problema de mercado | Real, amplo e alinhado com educação técnico-profissional | Manter o foco em descoberta e candidatura |
| Base funcional | Acima do nível MVP, porém dispersa | Congelar expansões não essenciais |
| Arquitectura | Django modular + React/Vite, com legados Django | Evoluir por contratos de API, não reescrever |
| Confiabilidade operacional | Não comprovada em produção | Condição obrigatória para abrir ao público |
| Monetização | Há oportunidades B2B claras | Começar por centros, não por cobrar aos alunos |

## 2. Estado actual do sistema

### Arquitectura e organização

O repositório contém **17 aplicações Django de negócio** activas, incluindo utilizadores, cursos, cursos em vídeo, centros, GestorEduka, pagamentos, biblioteca, bolsas, carreira, eventos e notificações. O frontend React contém 142 ficheiros de origem e uma aplicação de rota manual com cerca de 35 decisões de percurso público. O Django continua a ser a fonte operacional de modelos, autenticação por sessão, administração e APIs; React entrega a maior parte da experiência pública. [4] [5]

Esta arquitectura é viável para a próxima fase porque preserva regras de negócio maduras no backend. O risco é a duplicação gradual de experiências: há páginas React modernas, templates Django legados e endpoints históricos coexistentes. A prioridade não é migrar tudo por estética; é estabelecer um catálogo de APIs, contratos testados e um critério para descontinuar páginas legadas sem interromper links usados por centros ou alunos.

| Área | Evidência observada | Classificação | Recomendação |
|---|---|---:|---|
| Organização de domínio | Apps separadas por utilizador, curso, centro, pagamento, conteúdo e eventos | Importante | Manter a modularidade; documentar limites de cada domínio e donos de dados |
| Frontend | React/Vite funcional, mas roteamento manual concentrado em `App.jsx` | Importante | Introduzir router declarativo e carregamento por rota antes de o catálogo crescer muito |
| Backend | Django 5.2, DRF, sessões, administração Unfold e APIs React | Pode esperar | Não reescrever; reforçar contratos e permissões locais |
| Dados | SQLite no desenvolvimento; URL de base de dados gerida em ambiente configurado | Crítico | Produção só com PostgreSQL gerido, réplica/backup e testes de restauro |
| Armazenamento | Cloudinary opcional, sistema local como fallback | Crítico | Definir armazenamento objecto único em produção e política de retenção |
| Integrações | Brevo, Groq, mapas e Prontu configurados por variáveis de ambiente | Importante | Mapear proprietário, custo, limite e plano de falha por integração |

### Capacidades funcionais já existentes

O produto já cobre mais do que a pergunta essencial de descoberta. Há pesquisa e filtros, cursos, centros, inscrição, pagamentos, favoritos, perfil de aluno, preferências, notificações, conversas, certificados, biblioteca, bolsas, carreira, eventos e gestão institucional. O GestorEduka, em particular, é uma aposta B2B diferenciadora: centros podem gerir turmas, alunos, comunicações, operação académica e oferta pública. [4] [6]

O ponto crítico é distinguir **capacidade implementada** de **promessa de lançamento**. Uma funcionalidade pode estar no menu, ter dados de demonstração e passar em testes, mas ainda não ter responsáveis, política operacional, dados reais, apoio ao utilizador, métricas ou processo de excepção. A versão 1.0 deve publicar apenas experiências que a equipa consiga actualizar, moderar e suportar semanalmente.

### Qualidade observada

O `manage.py check` e os 68 testes executados nesta auditoria passaram. Há testes de pagamentos mockados, fluxo de planos, GestorEduka, recomendações, certificados públicos, Eduka AI, preferências, favoritos, cursos e candidatura integrada de formador. Esta é uma boa base de regressão funcional. Não existe evidência de CI no repositório, de testes de carga, de monitorização de erros, de métricas de conversão, de auditoria de acessibilidade ou de testes end-to-end num ambiente de staging.

| Dimensão | Estado | Classificação | Próxima acção mensurável |
|---|---|---:|---|
| Testes unitários e integração | 68 testes Django aprovados localmente | Importante | Executar automaticamente em cada pull request e deploy |
| Testes de browser | Validações manuais pontuais | Importante | Cobrir 5 jornadas críticas com Playwright ou equivalente |
| CI/CD | Nenhum workflow encontrado no repositório | Crítico | Criar pipeline: lint, build React, migrations check, testes e deploy de staging |
| Logs | Consola Django por categoria | Importante | Centralizar logs estruturados com correlação por pedido e alertas |
| Monitorização | Serviço de notificações tem healthcheck; plataforma não tem visão consolidada | Crítico | Uptime, erro, latência, fila e pagamento com alertas accionáveis |
| Acessibilidade | Sem auditoria documentada | Importante | Auditoria WCAG dos fluxos de descoberta, login, candidatura e pagamento |
| SEO | Uma descrição genérica no HTML base; sem evidência de metadados por curso/centro ou sitemap | Importante | URLs canónicas, metadados dinâmicos, sitemap, schema.org e páginas indexáveis |

## 3. Problemas críticos antes do lançamento público

### 3.1 Operação e recuperação de dados — crítico

Não há prova no repositório de backup automatizado, retenção, cópia geograficamente separada, teste de restauro ou procedimento de incidente para a base de dados e ficheiros enviados. Para uma plataforma que guarda candidaturas, documentos, inscrições e pagamentos, isto bloqueia lançamento público. A documentação Django recomenda explicitamente configurar backups da base de dados e da média enviada antes de produção. [2]

**Acção:** escolher PostgreSQL gerido com backups diários, retenção mínima de 30 dias, teste mensal de restauro num ambiente isolado, inventário de media e um RPO/RTO simples: perder no máximo 24 horas de dados e recuperar o serviço prioritário em menos de 4 horas.

### 3.2 Segurança de API, identificação e fluxos de dinheiro — crítico

O DRF tem `AllowAny` como permissão global; as vistas sensíveis compensam com verificações locais, mas isto cria um risco estrutural: qualquer endpoint novo pode nascer público por engano. A plataforma também expõe fluxos de candidatura, autenticação, e-mail, IA, pagamento e upload, todos alvos de abuso e custos não lineares. A OWASP destaca autorização por objecto, autenticação, consumo ilimitado de recursos e fluxos de negócio automatizáveis como riscos principais de APIs. [3]

**Acção:** inverter a política para autenticação por defeito, mantendo explicitamente públicos apenas os endpoints necessários; inventariar endpoints; validar propriedade de objectos; rate-limit de login, recuperação, código de e-mail, IA e candidatura; e criar alertas de custo/volume para Brevo, Groq, mapas e Prontu.

### 3.3 Produção distribuída — crítico

Cache e Channels usam memória local do processo. Isto funciona no desenvolvimento e num único processo, mas não é uma base para múltiplas instâncias, mensagens, rate limiting ou notificações consistentes. O serviço de notificações documenta um worker separado, armazenamento local de desenvolvimento e segredos próprios; não há prova de que o worker esteja activo em produção. [4] [7]

**Acção:** Redis gerido para cache, sessões quando necessário, rate limiting e canal; worker de notificações como processo separado monitorizado; fila idempotente; e dashboard operacional com eventos pendentes e falhos.

### 3.4 Dados reais e confiança de marketplace — crítico

O maior risco de produto não é técnico: é mostrar cursos, centros, bolsas ou eventos desactualizados. Se o estudante não recebe resposta depois de candidatar-se, a Edukangola perde o seu diferencial perante Google, Facebook ou WhatsApp. Um catálogo só é defensável se cada instituição tiver dono, data de verificação, SLA de resposta e mecanismo simples de denúncia.

**Acção:** começar com 15–30 centros parceiros verificados, cada um com responsável, contactos confirmados, cursos actualizados e compromisso de responder em 48 horas. Mostrar data de actualização e selo “perfil verificado”, não inventar classificações.

### 3.5 Observabilidade, incidentes e apoio — crítico

Há logs de consola, mas não há evidência de agregação de erros, alertas, métricas de funil, runbooks ou suporte operacional. Sem estes instrumentos a equipa só descobre falhas por mensagens de utilizadores. A própria checklist de deployment do Django recomenda rever logs, monitorizar erros e usar um sistema de agregação à medida que o tráfego cresce. [2]

**Acção:** configurar tracking de erro, uptime, alertas de pagamento/webhook, métricas de pesquisa, candidatura e resposta de centro; publicar canal de suporte; e criar um runbook de indisponibilidade, rollback e incidente de dados.

## 4. O que remover do foco ou adiar

Não é necessário apagar o que já existe. Deve-se **retirar do esforço de lançamento, ocultar de navegação principal quando confunde e congelar novas expansões** até que descoberta e candidatura provem procura. Tecnologia não é uma solução automática para aprendizagem; conectividade, competências, desenho pedagógico, privacidade e professor continuam determinantes. [1] [8]

| Capacidade | Decisão | Porquê agora seria erro | Condição para retomar |
|---|---|---|---|
| Chat interno completo | Adiar | Exige moderação, presença, notificações, custo de suporte e SLA | Pelo menos 50 centros activos e suporte com SLAs definidos |
| Rede social / feed | Adiar | Baixo impacto na descoberta; alto custo de moderação e segurança | Comunidade com propósito pedagógico e equipa de moderação |
| Marketplace complexo com múltiplos vendedores | Adiar | Multiplica disputa, KYC, reembolso, fiscalidade e conciliação | Pagamentos e suporte estabilizados em cursos de parceiros |
| IA avançada e recomendação opaca | Adiar | Custo variável, risco de erro e pouca vantagem antes de haver dados confiáveis | Catálogo validado, consentimento e métricas de conversão |
| LMS completo e vídeo próprio | Adiar | Hospedagem, banda, direitos, moderação e suporte são caros | Receita recorrente e oferta de cursos que justifique a operação |
| Gamificação | Adiar | Pode optimizar métricas erradas e distrair do valor de candidatura | Retenção em cursos comprovada e hipótese clara a testar |
| Certificados próprios em massa | Adiar | Exigem governança, validação e reputação institucional | Parcerias e política de emissão/revogação estabelecidas |
| Bolsas, carreira e bilhetes como foco de aquisição | Manter como conteúdo secundário, não como produto de lançamento | Cada vertical tem operações, verificação e regulação próprias | Depois de dominar centros, cursos e candidatura |

## 5. MVP recomendado

### Problema e proposta de valor

O verdadeiro problema não é “falta de cursos na internet”. É a ausência de uma fonte confiável e actualizada que responda, em linguagem simples: **que formação existe perto de mim ou na área que quero, em que instituição, quanto custa, como me candidato e quando recebo resposta?**

O utilizador principal é o estudante angolano de ensino médio, técnico, superior ou requalificação profissional; o comprador inicial é o centro de formação privado que precisa de procura qualificada e de uma presença digital organizada. Empresas e patrocinadores são clientes futuros, não o primeiro motor de receita.

| Camada | Essencial para o lançamento | Definição de “feito” |
|---|---|---|
| Catálogo público | Pesquisa, filtros por província, área, modalidade, preço e nível | Resultado rápido, sem duplicados, com dados actualizados |
| Página de centro | Contactos verificados, localização, cursos, data de actualização e responsável | Centro confirma os dados mensalmente |
| Página de curso | Objectivo, requisitos, preço/forma de pagamento, datas, vagas, centro e CTA | Informação suficiente para decidir sem WhatsApp adicional |
| Candidatura | Formulário curto, consentimento, documentos apenas quando necessários, confirmação e estado | Centro recebe lead e aluno vê “recebida/em análise/respondida” |
| Área de centro | Publicar e actualizar cursos, gerir candidaturas e responder | Centro consegue operar sem apoio técnico diário |
| Confiança | Selo de centro verificado, denúncia e moderação | Fraude/erro tem um canal e proprietário definido |
| Operação | Backups, monitorização, logs, segurança e suporte | Incidente detectado e recuperável |

### Importante após o lançamento

Depois de medir procura e resposta de centros, devem entrar favoritos com alertas úteis, comparação de cursos, métricas básicas para centros, perfis premium, melhores filtros, páginas SEO por província/área e reputação baseada em inscrições verificadas. A sequência correcta é adicionar capacidade que melhora **descoberta, conversão e confiança**, não capacidade que aumenta apenas o menu.

### Futuras

Formação em vídeo, biblioteca comercial, bolsas patrocinadas, eventos, empregabilidade, integração profunda de pagamentos, funcionalidades de formador e GestorEduka financeiro podem evoluir, mas como linhas de negócio separadas com responsáveis e metas próprias. O GestorEduka pode ser a maior aposta B2B, mas não deve ser requisito para validar o marketplace de descoberta.

## 6. Modelo de negócio recomendado

O modelo inicial deve ser **B2B2C**. O estudante não deve pagar para descobrir onde estudar; o centro paga por aquisição, visibilidade e eficiência operacional. Isto cria alinhamento: a Edukangola ganha quando o centro tem dados melhores, responde aos candidatos e recebe procura qualificada.

| Receita | Cliente pagador | Valor entregue | Complexidade | Potencial | Momento ideal |
|---|---|---|---:|---:|---|
| Perfil institucional premium | Centro | Página verificada, contacto, analytics e maior confiança | Baixa | Média, recorrente | Lançamento controlado |
| Destaque de curso/centro | Centro | Mais visibilidade segmentada por província e área | Baixa | Média | Quando houver procura orgânica e regras de transparência |
| Assinatura GestorEduka básica | Centro | Gestão de cursos, candidaturas, comunicação e relatórios | Média | Alta, recorrente | Após 5–10 centros usarem operação real |
| Lead qualificado com consentimento | Centro | Candidatura completa, rastreável e com intenção | Média | Média/alta | Após medir resposta e qualidade dos leads |
| Bolsas patrocinadas | Empresa/ONG | Distribuição, verificação e relatório de impacto | Alta | Alta por contrato | Fase 2, com governação e compliance |
| Publicidade educativa contextual | Instituições e marcas | Alcance segmentado sem vender dados pessoais | Média | Média | Depois de tráfego e política editorial |
| Comissão de pagamento | Centro | Cobrança e reconciliação simplificadas | Alta | Alta | Só com parceiro, webhook, suporte e conciliação reais |
| Relatórios agregados | Centros, empresas, Estado | Tendências de procura sem dados pessoais identificáveis | Média | Média | Depois de escala e consentimento claros |
| Serviços pagos para alunos | Aluno | Opcional: revisão de candidatura, orientação ou documentos | Média | Baixa/média | Apenas quando existe valor humano verificável |

**Não recomendo** vender dados pessoais de candidatos. O produto pode cobrar por candidatura elegível e consentida, com finalidade explícita, retenção limitada e possibilidade de o aluno retirar consentimento. A confiança é mais valiosa do que uma receita rápida de listas de contactos.

## 7. Fontes de receita por prioridade

| Prioridade | Receita | Hipótese a validar | Métrica de decisão |
|---:|---|---|---|
| 1 | Perfil premium + onboarding de centros | Centros pagam para aparecer confiáveis e gerar procura | Centros activos pagantes, renovação e tempo de publicação |
| 2 | Destaques transparentes | Promoção segmentada aumenta candidaturas qualificadas | CTR, candidatura iniciada e custo por candidatura |
| 3 | GestorEduka básico | O mesmo centro paga para operar candidaturas e catálogo | Utilizadores semanais por centro e retenção mensal |
| 4 | Lead qualificado opt-in | Centros valorizam candidato completo, não apenas contacto | Taxa de resposta e matrícula atribuída |
| 5 | Pagamentos e comissão | Centros aceitam pagar pela reconciliação e conveniência | Taxa de sucesso, reconciliação e volume líquido |
| 6 | Bolsas/analytics/patrocínios | Empresas pagam por impacto mensurável | Contratos, custo operacional e taxa de colocação |

## 8. Checklist de lançamento

| Área | Critério objectivo | Estado actual | Condição de saída |
|---|---|---:|---|
| Segurança | `check --deploy`, revisão de permissões, rate limits e gestão de segredos | Parcial | Concluir e registar evidência em staging |
| Dados | 15–30 centros verificados com cursos reais e proprietário de cada perfil | Não comprovado | Catálogo-piloto assinado e actualizado |
| Candidatura | Estado, notificação e SLA de resposta de centro | Parcial | 90% das candidaturas-piloto respondidas em 48h |
| Testes | CI com build, migration check e suite automatizada | Não | Pipeline obrigatório a cada alteração |
| Pagamentos | Webhook assinado e teste em staging real | Parcial/mockado | Pelo menos 20 transacções de homologação reconciliadas |
| Backups | Backup, retenção e restauro testado | Não comprovado | Restauro documentado e testado |
| Monitorização | Uptime, erros, API, worker e pagamentos com alertas | Não | Painel e canal de alerta activos |
| Conteúdo | Política editorial, data de actualização e denúncia | Parcial | Operador e SLA de moderação definidos |
| Privacidade e termos | Termos, privacidade, consentimento e retenção revistos | Parcial | Texto publicado e fluxo de consentimento testado |
| SEO | Sitemap, robots, canónicos, metadados por centro/curso e Search Console | Não comprovado | Primeiro conjunto de páginas indexável e medido |
| Suporte | E-mail/WhatsApp de apoio, FAQ e processo de incidente | Parcial | Responsável e tempos de resposta definidos |
| Acessibilidade e desempenho | Auditoria de jornadas móveis de baixa conectividade | Não comprovado | Lighthouse e teste manual com critérios mínimos |

## 9. Roadmap de 12 meses

### Fase 1 — Lançamento controlado (0–2 meses)

O objectivo é provar que a Edukangola consegue gerar candidaturas respondidas por centros reais. Seleccionar uma região inicial, 15–30 centros, quatro a seis áreas de formação e uma equipa interna responsável por qualidade de dados. Entregar pesquisa e filtros, páginas verificadas de centro e curso, candidatura rastreável, favoritar, painel mínimo do centro, termos/privacidade, suporte e analítica de funil. Em paralelo, fechar backups, monitorização, CI, segurança de APIs, cache/worker e staging.

O indicador de sucesso não é número de páginas ou cursos criados. É **percentagem de candidaturas com resposta em 48 horas**, taxa de candidatura por visita qualificada, centros activos por semana e satisfação de estudante/centro.

### Fase 2 — Monetização e profundidade (2–6 meses)

Depois de o funil operar, activar perfis premium, destaques identificados como promoção, analytics simples para centros e primeiro plano GestorEduka. Melhorar SEO territorial, comparação de cursos, reputação somente com interacções verificadas, notificações transaccionais e expansão por província. Testar pagamentos em staging e só então abrir uma categoria limitada de cobrança real.

### Fase 3 — Escala selectiva (6–12 meses)

Escalar centros e províncias com qualidade, lançar parcerias de bolsas patrocinadas se existir operação de verificação, integrar relatórios agregados e expandir GestorEduka para gestão institucional paga. Cursos em vídeo, biblioteca, carreira e eventos devem ter metas próprias de receita/retenção e não competir com o funil principal. Só considerar app nativa quando dados mostrarem uma limitação clara da web móvel/PWA.

## 10. Análise de produto e decisão final

O diferencial competitivo possível não é “ter uma lista de cursos”. Google e redes sociais já fazem descoberta genérica. A Edukangola pode ser superior se oferecer **dados locais verificados, comparação estruturada, candidatura rastreável, resposta de centro e uma infraestrutura B2B que mantenha a informação viva**. A combinação de marketplace de descoberta e software para o centro é defensável; o catálogo alimenta o SaaS e o SaaS melhora o catálogo.

Os maiores riscos são dados desactualizados, baixa resposta dos centros, foco disperso, dependência de fluxos manuais invisíveis, falhas de pagamento/notificação e lançar sem recuperação/monitorização. A resposta não é adicionar IA, mais páginas ou mais verticais. É ter menos promessas e operar muito bem o percurso essencial.

> **Decisão:** a Edukangola está **pronta para beta fechado**, desde que o piloto use dados institucionais reais e sejam fechados backups, monitorização, CI, segurança de API e SLA de resposta. Está **ainda não pronta para lançamento público amplo** porque a evidência disponível não demonstra operação resiliente, dados verificados em escala, suporte, SEO, recuperação de incidente nem conciliação real de pagamento.

O próximo marco recomendado é um beta com 15–30 centros e uma métrica única de sucesso: **pelo menos 70% das candidaturas elegíveis devem receber uma resposta de centro dentro de 48 horas durante quatro semanas consecutivas.** Se esta métrica falhar, corrigir operação e proposta de valor antes de ampliar aquisição ou monetização.

## Referências

[1]: https://www.trade.gov/market-intelligence/angola-education-market-opportunities "Angola Education Market Opportunities — International Trade Administration"

[2]: https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/ "Django deployment checklist"

[3]: https://owasp.org/API-Security/editions/2023/en/0x11-t10/ "OWASP API Security Top 10 — 2023"

[4]: https://github.com/004charles/Eduka-Angola/blob/main/AUDITORIA_BACKEND_2026-08-18.md "Auditoria do Backend Edukangola"

[5]: https://github.com/004charles/Eduka-Angola/blob/main/eduangolacore/settings.py "Configuração Django: segurança, dados, cache e logs"

[6]: https://github.com/004charles/Eduka-Angola/blob/main/eduangolacore/urls.py "Rotas e módulos activos da Edukangola"

[7]: https://github.com/004charles/Eduka-Angola/blob/main/notification_service/README.md "Serviço de notificações Edukangola"

[8]: https://www.worldbank.org/ext/en/topic/education/digital-technologies-in-education "World Bank — Digital Technologies in Education"

[9]: https://www.worldbank.org/en/news/factsheet/2024/06/27/inclusive-digitalization-in-eastern-and-southern-africa-program-afe-angola "World Bank — Inclusive Digitalization in Angola"
