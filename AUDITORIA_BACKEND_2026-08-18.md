# Auditoria do Backend Edukangola

**Data:** 18 de Agosto de 2026  
**Âmbito:** inventário funcional e técnico do backend Django antes de iniciar novas expansões de produto.

## Síntese executiva

> O backend da Edukangola já é substancialmente mais completo do que um MVP básico. A estrutura suporta aprendizagem presencial e em vídeo, centros de formação, inscrições, matrículas, pagamentos, biblioteca, eventos, comunicação, notificações, IA e operação administrativa. A prioridade não é reconstruir estes fundamentos, mas **unificar as experiências já existentes, fechar lacunas de produção e expor em React as capacidades que ainda vivem em templates Django**.

A suite Django completa passou com **57 testes** e a verificação do projecto não identificou erros de configuração. As migrações locais estão aplicadas. Foram, contudo, encontradas lacunas importantes em códigos promocionais, certificação verificável presencial, área React de formador e operação distribuída de notificações.[1] [2] [3]

| Diagnóstico | Estado |
|---|---|
| Base de domínio educacional | **Forte** |
| Gestão de centros e operação presencial | **Forte** |
| Aprendizagem por vídeo | **Forte, com partes legadas** |
| Área independente do formador | **Existe no backend, mas não em React** |
| Avaliações e reputação | **Base implementada; descoberta e confiança precisam de evolução** |
| Certificados verificáveis | **Vídeo operacional; presencial incompleto** |
| Promoções comerciais | **Preço promocional existe; cupões de curso ainda não** |
| Produção distribuída e automação | **Requer reforço** |

## Arquitectura e domínios já disponíveis

O projecto usa Django com autenticação própria por e-mail, sessões, Django REST Framework, API React e administração Unfold. Existem 18 módulos de modelos no repositório e 17 aplicações de negócio activas na configuração principal. O utilizador central já distingue administrador, aluno, gestor de centro, gestor de filial e instrutor.[1]

| Domínio | Capacidades já existentes | Estado de produto |
|---|---|---|
| **Centros e GestorEduka** | Perfil público, candidaturas, filiais, equipa, planos, comissões, repasses, candidaturas externas, comunicação com aluno, anúncios, eventos e auditoria | Maduro |
| **Cursos presenciais** | Categorias, instrutores, cursos, módulos, turmas, vagas, inscrições, documentos, matrículas, presenças, notas e parcelamento | Maduro |
| **Cursos em vídeo** | Curso, aulas, progresso, notas, materiais, comentários por aula, avisos, exercícios, resultados, turmas de acompanhamento e certificados | Maduro |
| **Aluno** | Perfil, onboarding, interesses, preferências de aprendizagem, favoritos, certificados, notificações e conversas | Maduro |
| **Pagamentos** | Prontu, enumeração para Stripe/PayPal, webhooks, tentativas, histórico, reembolsos, valores finais, descontos e financeiro de centros | Estrutura forte |
| **Conteúdo e oportunidades** | Biblioteca, blog, bolsas, carreira, escolas, estágios e bilhetes de eventos | Disponível |
| **IA** | Ajuda por aula, recomendações, Eduka AI pública e contexto de catálogo | Disponível, com limites recentes |

## O que já temos em relação às prioridades propostas

### 1. Área do formador

**Já existe uma área de instrutor independente**, portanto não começa do zero. O perfil `Instrutor` está ligado a um utilizador, pode ser independente ou associado a centro, inclui biografia, capa, ligações sociais, métricas, nota média e contagens. Há ainda login, registo sujeito a activação, painel de métricas, CRUD de cursos em vídeo e aulas, gestão de materiais, avisos, alunos e dúvidas.[4] [5]

**Lacuna principal:** esta experiência está em vistas e templates Django legados (`/instrutor/`), enquanto a área pública e o GestorEduka evoluíram para React. Falta uma API React de instrutor, fluxo de publicação/revisão e um perfil público de formador bem integrado no catálogo.

### 2. Perguntas e respostas por aula

**Já está implementado.** `ComentarioAula` liga o aluno à aula, aceita respostas encadeadas de instrutor e a sala de aprendizagem React já tem endpoints para dúvidas por aula. O painel legado de instrutor também lista e responde questões pendentes.[5] [6]

**Lacuna principal:** transformar a conversa em conhecimento reutilizável: pesquisa, voto “foi útil”, marcação de resposta do formador, moderação, filtros por aula/curso e visibilidade clara no React do formador.

### 3. Avaliações e reputação

**A base está implementada.** Cursos presenciais e em vídeo têm estrelas, comentários, respostas, moderação, denúncias e distribuição de avaliações. Os centros também têm um score híbrido de confiança que combina média de alunos, conclusão e frequência.[6] [7]

**Lacuna principal:** falta apresentar esta informação como sinal de confiança de marketplace. Não há restrição visível no modelo para uma avaliação por aluno/curso, nem destaque de avaliações verificadas, ranking de formadores, votos de utilidade ou resumo público de reputação.

### 4. Certificados verificáveis

**Existe uma base real.** Tanto cursos em vídeo como formações presenciais geram código único de verificação. O módulo de vídeo já expõe uma rota pública de validação por código.[5] [8]

**Lacuna principal:** o dashboard React devolve uma URL de verificação de vídeo também para certificados presenciais. A rota pública consultada valida o modelo de certificado de vídeo, não o certificado presencial. Falta uma página/verificador unificado, QR code, estado de revogação e apresentação adequada para partilha profissional.

### 5. Promoções e códigos de desconto

**Já existe preço promocional temporário por curso** e `Pagamento` regista valor de desconto, valor final e metadados da transacção.[3] [6]

**Lacuna principal:** não existe modelo de cupão ou campanha para cursos. Os `VoucherPlano` actuais servem apenas para activar planos de centros, não para dar desconto a alunos. Falta código, período de validade, limite de utilizações, elegibilidade por curso/centro, aplicação no checkout e auditoria de resgates.

## Operação, segurança e produção

| Aspecto | Estado observado | Recomendação |
|---|---|---|
| Segredos | Chaves externas são lidas por variáveis de ambiente; produção exige segredo Django, hosts e origens CSRF | Manter valores apenas no provedor e auditar regularmente |
| Sessões e HTTPS | Cookies seguros e HSTS são activados em ambiente de produção | Validar os valores efectivamente aplicados em staging/produção |
| API | A configuração DRF global permite acesso por defeito; as vistas sensíveis devem continuar a impor autenticação localmente | Rever permissões endpoint a endpoint antes de abrir novas APIs |
| Cache e canal de eventos | Cache local em memória e canal Channels em memória | Migrar para Redis em staging/produção, sobretudo para rate limiting, chat e notificações |
| Localização | Há fallback textual quando GeoDjango/PostGIS não está disponível | Usar PostGIS em produção para proximidade e pesquisa geográfica fiáveis |
| Notificações | Há outbox, preferências e comandos de gestão para notificações periódicas | Activar gateway e worker independentes no provedor |
| Pagamentos | Prontu está integrado e a suite cobre cenários mockados | Validar webhook, assinatura e retorno num ambiente de staging real |

## Pontos técnicos a corrigir antes de ampliar muito o produto

1. **Executar o worker de notificações em produção.** Há comandos e outbox, mas a entrega depende de um processo separado.
2. **Unificar certificados.** Criar uma única rota pública capaz de validar vídeo e presencial, com QR code e estado de validade.
3. **Migrar a área de instrutor para React.** O domínio e as regras já existem; falta a experiência moderna e o contrato de API.
4. **Criar cupões para cursos.** Reutilizar `Pagamento.valor_desconto` e a lógica de preço, mas construir uma entidade própria de promoção/resgate.
5. **Reforçar a reputação.** Uma avaliação por aluno/curso, apenas após inscrição confirmada, selo de compra verificada, resposta do formador e ordenação útil.
6. **Corrigir pequenas dívidas no modelo de vídeo.** `ComentarioAula` tem duas implementações de `__str__`; a última substitui a anterior e referencia um atributo que o modelo não possui. A gestão de exercícios do instrutor também contém referências legadas ao módulo de inteligência que merecem validação antes de serem activadas.[5]

## Roteiro recomendado

| Ciclo | Entrega | Reaproveitamento directo |
|---:|---|---|
| 1 | Certificado unificado verificável com QR | `Certificado`, `CertificadoCurso`, códigos existentes e rotas públicas |
| 2 | React para formador independente | `Instrutor`, cursos em vídeo, aulas, materiais, comentários e métricas existentes |
| 3 | Fórum de dúvidas por aula | `ComentarioAula` e respostas encadeadas existentes |
| 4 | Reputação de marketplace | `Comentario`, médias/distribuições de curso e `AvaliacaoHibridaCentro` |
| 5 | Cupões e campanhas | preço promocional, `Pagamento.valor_desconto`, histórico e checkout actuais |
| 6 | Redis + worker de notificações | outbox e comandos de gestão existentes |

## Resultado das validações

| Verificação | Resultado |
|---|---|
| `python manage.py test` | **57 testes aprovados** em 8,6 segundos |
| `python manage.py check` | **Sem erros identificados** |
| Migrações locais | **Aplicadas** |
| Testes de Eduka AI públicos | Incluídos na suite e aprovados |

## Referências de código

[1]: https://github.com/004charles/Eduka-Angola/blob/main/eduangolacore/settings.py "Configuração Django da Edukangola"
[2]: https://github.com/004charles/Eduka-Angola/blob/main/eduangolacore/urls.py "Rotas principais e APIs React"
[3]: https://github.com/004charles/Eduka-Angola/blob/main/pagamentos/models.py "Modelos de pagamentos"
[4]: https://github.com/004charles/Eduka-Angola/blob/main/cursos_app/models.py "Cursos presenciais, instrutores e certificados"
[5]: https://github.com/004charles/Eduka-Angola/blob/main/cursovideoapp/models.py "Cursos em vídeo e aprendizagem"
[6]: https://github.com/004charles/Eduka-Angola/blob/main/instrutores_app/views.py "Área legada de instrutores"
[7]: https://github.com/004charles/Eduka-Angola/blob/main/avaliacoes/models.py "Avaliações e reputação"
[8]: https://github.com/004charles/Eduka-Angola/blob/main/cursovideoapp/urls.py "Rotas de certificados de vídeo"
