# Auditoria de lacunas funcionais da Edukangola

**Data:** 17 de agosto de 2026
**Escopo:** experiência do aluno, aprendizagem, centros, operação pedagógica e capacidade de escala.

## Síntese executiva

A Edukangola já deixou de ser apenas um catálogo: tem cursos presenciais e cursos em vídeo, autenticação de alunos, favoritos, área pessoal, leitor de vídeo com progresso, biblioteca editorial, bilhetes de eventos, perfis de centros, notícias, FAQ, política de privacidade e preferências de notificações. O backend também contém modelos para exercícios, questões, materiais, notas, presenças, certificados, bolsas, estágios, instrutores, mensagens e avaliações operacionais.

A principal lacuna é que **muitos elementos existem no backend ou em templates Django legados, mas ainda não formam uma experiência pedagógica React completa e coerente para o aluno, centro e formador**. O próximo investimento não deve ser mais páginas editoriais; deve transformar o catálogo numa jornada de aprendizagem mensurável.

> A prioridade deve ser: **aprender → praticar → ser avaliado → receber prova de competência → avançar para uma oportunidade**.

## O que já existe

| Área | Situação actual | Observação |
|---|---|---|
| Descoberta | Página inicial editorial, catálogo, categorias, centros, notícias e Biblioteca | Boa base de aquisição e descoberta |
| Conta do aluno | Login, cadastro, preferências, configurações, favoritos, área do aluno, bilhetes e logout | A conta já tem estrutura funcional |
| Cursos em vídeo | Aulas, progresso, notas, comentários, avisos, materiais, exercícios e certificados no backend | Falta consolidar tudo numa experiência de aprendizagem React completa |
| Cursos presenciais | Turmas, inscrições, pagamentos, presenças, notas e certificados no backend | Falta um acompanhamento pedagógico claro para o aluno |
| Biblioteca | Livros digitais, progresso de leitura, áudio e retoma | Funcionalidade diferenciadora da plataforma |
| Centros | Perfis públicos, cursos, instrutores, galeria, eventos, estágios e gestão legada | Falta modernizar o painel de gestão e ligar melhor centros a resultados |
| Comércio | Pagamentos de cursos e bilhetes, pedidos e histórico financeiro no backend | Faltam autoatendimento financeiro e políticas visíveis |
| Conteúdo editorial | Notícias em texto e vídeo, FAQ dinâmica, privacidade e depoimentos moderados | Apoia confiança, mas não substitui funções pedagógicas |
| Notificações | Preferências opt-in, outbox, eventos, worker e canais preparados | Activação de produção ainda pendente |

## Lacunas prioritárias

### P0 — Essenciais antes de apresentar a Edukangola como uma plataforma educativa completa

| Prioridade | Funcionalidade | O que o aluno precisa conseguir fazer | Dependências |
|---|---|---|---|
| P0 | **Área de aprendizagem React completa** | Ver módulos e aulas, materiais, notas, dúvidas, avisos, exercícios, conclusão e estado geral do curso numa única área | APIs existentes do leitor, progresso e materiais; migração de telas legadas |
| P0 | **Avaliação e feedback** | Responder quizzes, entregar exercícios, ver nota, receber feedback e repetir quando permitido | Modelos de questões, alternativas, exercícios e resultados já existentes |
| P0 | **Certificados e histórico académico** | Ver, descarregar, partilhar e validar certificados; consultar cursos concluídos, notas e carga horária | Certificados existentes, página pública de validação e área `/aluno/certificados` |
| P0 | **Painel do formador e do centro em React** | Criar ou editar curso, módulos, aulas, materiais, exercícios, turmas, vagas, preços e datas; acompanhar alunos | Fluxos Django legados, permissões de centro e instrutor |
| P0 | **Livro de notas e acompanhamento de turmas** | Ver presenças, progresso, notas, estado da inscrição, pagamentos e mensagens do centro | Modelos de presenças, notas, matrículas e inscrições |
| P0 | **Suporte e resolução de problemas** | Abrir pedido, acompanhar resposta, reportar erro de pagamento, pedir ajuda sobre curso e consultar histórico | Mensagens/conversas existentes no backend; falta uma caixa de entrada unificada |
| P0 | **Segurança e operação de produção** | Recuperar conta, alterar palavra-passe, gerir sessões, receber confirmação de operações e ter dados protegidos | Auditoria de permissões, backups, logs, rate limiting, domínio de e-mail e segredos de ambiente |

A área de aprendizagem e os certificados devem vir antes de novas campanhas de aquisição. Uma plataforma pode ter um catálogo visualmente forte, mas a confiança do aluno depende de conseguir concluir, ser avaliado e provar o que aprendeu.

### P1 — Diferenciação educativa e valor para o contexto angolano

| Prioridade | Funcionalidade | Valor para a Edukangola |
|---|---|---|
| P1 | **Percursos de carreira e planos de aprendizagem** | Transformar cursos isolados em caminhos como “Primeiro emprego em tecnologia”, “Gestão para PME” ou “Competências digitais básicas” |
| P1 | **Mapa de competências** | Mostrar quais competências cada curso desenvolve, quais o aluno já demonstrou e quais deve adquirir a seguir |
| P1 | **Portfólio do aluno** | Reunir certificados, projetos, exercícios, competências e links partilháveis para empregadores |
| P1 | **Estágios, bolsas e oportunidades** | Ligar aprendizagem a candidaturas, requisitos, documentos, prazos e estado do processo; o backend já possui bolsas e estágios |
| P1 | **Comunidade por curso** | Perguntas e respostas, discussões moderadas, respostas do formador, denúncias e marcação da melhor resposta |
| P1 | **Avaliações e reputação** | Avaliação estruturada de cursos, centros e formadores, com moderação contra abuso e transparência no catálogo |
| P1 | **Calendário de aprendizagem** | Datas de turmas, prazos, aulas, exames, feriados e lembretes num só lugar |
| P1 | **Modo de baixo consumo e offline** | Acesso com redes instáveis, compressão de vídeo, retoma confiável e, numa fase posterior, downloads protegidos |
| P1 | **Relatórios para centros** | Inscrições, conclusão, presença, notas, satisfação, receita, procura por curso e alunos em risco de abandono |
| P1 | **Pagamentos de autoatendimento** | Histórico, recibos, estado de pagamento, pedidos de suporte, política de reembolso e reconciliação clara |

Plataformas maduras tratam competências, planos de aprendizagem, atividades colaborativas, calendário, notificações, badges e relatórios como partes do LMS, não como funcionalidades periféricas.[^1] A documentação de competências do Moodle também descreve frameworks de competências, planos individuais, evidências e revisão pelo formador.[^2]

### P2 — Crescimento depois do núcleo pedagógico

| Funcionalidade | Quando faz sentido |
|---|---|
| Tutor de IA contextual por curso | Depois de existirem conteúdos bem estruturados, avaliações e regras de segurança; a IA deve responder com base no material do curso |
| Recomendação de cursos por competência | Depois de recolher eventos de aprendizagem reais, não apenas cliques ou favoritos |
| Badges e gamificação | Depois de definir critérios pedagógicos; não usar pontos apenas para aumentar cliques |
| Assinatura ou passes de aprendizagem | Quando houver catálogo e frequência de uso suficientes para justificar o modelo recorrente |
| Aulas ao vivo e videoconferência | Quando centros e formadores tiverem agenda, presença, gravação e suporte operacional definidos |
| Integração com LinkedIn e portfólio público | Depois de certificados verificáveis e consentimento de partilha estarem sólidos |
| API e integrações institucionais | Quando escolas, empresas e parceiros precisarem de sincronizar utilizadores, matrículas e resultados |

Coursera combina cursos, especializações, certificados profissionais, projetos práticos e credenciais verificáveis; a credencial funciona como resultado visível da aprendizagem, não apenas como decoração do perfil.[^3] A Edukangola deve adoptar o princípio, mas começar com certificados e portfólio próprios, adaptados ao mercado angolano.

## O que não recomendo implementar agora

Não recomendo começar por marketplace de assinaturas, gamificação complexa, tutor de IA genérico, videoconferência própria ou mais blocos editoriais na página inicial. Essas funcionalidades aumentam custo e operação antes de resolver o ponto central: o aluno precisa de aprender, praticar, receber feedback e concluir com evidência.

## Roteiro recomendado

### Fase 1 — Núcleo de aprendizagem, 2 a 3 marcos

Primeiro, consolidar o leitor React: módulos, aulas, progresso, materiais, notas pessoais, perguntas, exercícios, resultados, avisos e estado de conclusão. Em paralelo, criar a página de certificados e histórico do aluno. O critério de aceitação é o aluno conseguir comprar ou inscrever-se, estudar, praticar, concluir e obter uma prova verificável sem voltar a uma tela Django legada.

### Fase 2 — Operação pedagógica dos centros

Depois, modernizar o painel do centro e do formador. O centro deve publicar em rascunho, submeter para revisão, corrigir, publicar, abrir turmas, gerir vagas e acompanhar resultados. O formador deve conseguir responder dúvidas, corrigir trabalhos e consultar o progresso da sua turma.

### Fase 3 — Carreira e confiança

Em seguida, lançar percursos de carreira, mapa de competências, portfólio do aluno, bolsas, estágios e oportunidades. Este é o ponto que diferencia a Edukangola de um simples catálogo de cursos e responde melhor à realidade de alunos que procuram emprego, progressão e mobilidade profissional.

### Fase 4 — Escala e retenção

Só depois devem entrar recomendações baseadas em dados, notificações de produção, relatórios avançados, modo de baixo consumo, badges e IA contextual. Relatórios de plataformas maduras acompanham actividade, progresso, competências, avaliações, adoção e utilizadores sem actividade; esse tipo de observabilidade deverá existir para centros e para a própria equipa Edukangola.[^4]

## As cinco funcionalidades que eu implementaria primeiro

Se for necessário escolher apenas cinco, a ordem seria: **(1) área de aprendizagem React completa; (2) quizzes, exercícios e livro de notas; (3) certificados e histórico académico; (4) painel React para centros e formadores; (5) percursos de carreira com competências, portfólio e estágios**.

Esta ordem aproveita o backend que já existe, reduz a dependência dos templates legados e faz a plataforma comunicar uma promessa concreta: a Edukangola não apenas mostra cursos; ajuda o aluno a construir competências e demonstrá-las.

## Decisão recomendada

O próximo grande projecto deve chamar-se **Edukangola Learning Core**, não “mais páginas”. Deve incluir a área de aprendizagem, avaliações, certificados, histórico e primeira versão de acompanhamento de turma. A partir daí, cada funcionalidade nova deverá responder a uma destas perguntas: melhora a aprendizagem, prova uma competência, ajuda o formador a ensinar ou aproxima o aluno de uma oportunidade.

## Referências

[^1]: [Moodle LMS Features — aprendizagem, gradebook, competências, planos, colaboração, calendário, notificações e relatórios](https://moodle.com/solutions/lms/features/)

[^2]: [Moodle Competencies — frameworks, planos de aprendizagem, evidências e revisão](https://docs.moodle.org/en/Competencies)

[^3]: [Coursera — cursos, especializações, certificados profissionais, projetos e credenciais verificáveis](https://www.coursera.org/articles/what-is-coursera)

[^4]: [Udemy Business — insights, progresso, competências, actividade, avaliações e relatórios](https://business-support.udemy.com/hc/en-us/articles/115005418728-What-insights-and-reporting-are-available-in-Udemy-Business)
