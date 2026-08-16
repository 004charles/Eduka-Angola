# Diagnóstico de prontidão para lançamento da Edukangola

**Data da análise:** 16 de agosto de 2026
**Âmbito:** Frontend React, backend Django, área do aluno, centros, pagamentos, eventos, Biblioteca e operação editorial.

> **Conclusão executiva:** a Edukangola já tem uma base pública sólida e várias experiências diferenciadoras implementadas. Ainda não recomendaria um lançamento público com pagamentos reais sem concluir os fluxos financeiros de ponta a ponta, a administração dinâmica de FAQ, a área de bilhetes do aluno e as configurações de produção, segurança e operação.

## 1. O que já está funcional

| Área | Estado observado | Observação |
|---|---|---|
| Descoberta de cursos | Implementada | Catálogo React, filtros, preços, favoritos, prateleiras editoriais, categorias e detalhe de curso. |
| Cursos em vídeo | Implementada com validação adicional necessária | Compra, detalhe e área de aprendizagem existem; ainda precisa de teste completo desde pagamento até desbloqueio das aulas. |
| Área do aluno | Implementada | Inclui perfil, preferências, favoritos, inscrições presenciais e estante de leituras. |
| Centros de formação | Implementada | Vitrina pública, perfil de centro e fluxo de candidatura de centro estão disponíveis. |
| Notícias | Implementada | Página editorial, temas, notícias relacionadas, vídeos e capas já foram migrados. |
| Eventos e bilhetes | Implementada com validação financeira pendente | Catálogo, detalhe, lotes e pagamento estão presentes. Falta consolidar a área de bilhetes do aluno e testar retorno real do gateway. |
| Biblioteca | Implementada | Estante editorial, detalhe, leitura, progresso guardado, escolha de retoma e leitura em voz alta local do navegador. |
| Conteúdo institucional | Implementada | Sobre, FAQ, Política de privacidade, Como funciona e Para centros existem em React. |
| Idiomas e aparência | Implementada | Selecção PT, EN, FR e 中文 e modo claro/escuro estão presentes. |

## 2. Bloqueadores antes de aceitar pagamentos e tráfego público

| Prioridade | Trabalho em falta | Porque bloqueia o lançamento | Critério de conclusão |
|---|---|---|---|
| P0 | Validar Prontu em ambiente real | Um pagamento não confirmado, cancelado ou repetido não pode libertar acesso nem emitir bilhete de forma errada. | Testar sucesso, cancelamento, expiração, repetição de webhook, idempotência, recibo e retorno para cursos e eventos. |
| P0 | Configurar produção de Django | A configuração actual de desenvolvimento aceita todos os `ALLOWED_HOSTS` e deixa `DEBUG` com valor predefinido verdadeiro. | Variáveis de produção definidas, hosts explícitos, HTTPS obrigatório, cookies seguros, CSRF/CORS restritos e sem credenciais no repositório. |
| P0 | Criar “Os meus bilhetes” na área do aluno | O comprador precisa de consultar bilhetes confirmados, referência, estado e instruções do evento. | Rota React, endpoint autenticado, estado de pagamento e identificação/QR quando aplicável. |
| P0 | Administrar FAQ no Django Admin | A página foi criada, mas as perguntas ainda estão no frontend; isto impede actualização editorial sem deploy. | Modelo, Admin, API pública por idioma/estado e página React ligada apenas a dados publicados. |
| P1 | Validar todos os fluxos críticos com cenários reais | A compilação confirma o código, não a operação completa. | Roteiro formal de teste para cadastro e e-mail, inscrição, compra de curso em vídeo, bilhete, leitura, favoritos e centro. |
| P1 | Confirmar regras de acesso pós-pagamento | O acesso a curso, vídeo ou bilhete deve depender do estado transaccional definitivo. | Estados pendente, pago, falhado, reembolsado e expirado visíveis e coerentes na interface. |
| P1 | Rever juridicamente a política e os consentimentos | A página de privacidade está disponível, mas deve ser revista com dados empresariais, contactos e bases legais finais. | Política aprovada, versão datada, consentimento de cadastro registado e regras de retenção definidas. |

## 3. Trabalho importante antes ou logo após o lançamento

| Área | Recomendação prática |
|---|---|
| Conteúdo real | Substituir gradualmente cursos, livros, notícias, eventos e centros de demonstração por conteúdo autorizado, com proprietário, imagem, texto e estado de publicação definidos no Admin. |
| Moderação de comunidade | Testar a cadeia completa de submissão, consentimento, aprovação no Admin, publicação e remoção de depoimentos. |
| Emails transaccionais | Confirmar domínio remetente, entregabilidade, modelos de e-mail e mensagens de cadastro, pagamento, bilhete e recuperação de palavra-passe. |
| Acessibilidade e mobile | Testar teclado, foco, contraste, leitores de ecrã e os principais percursos em telemóveis de baixa largura e redes lentas. |
| Observabilidade | Adicionar registo de erros, alertas de falha de pagamento, monitorização de disponibilidade e rotina de backup/restauro de dados. |
| Performance | Reduzir o peso inicial do JavaScript com carregamento por rota e medir LCP, interacção e imagens em ligação móvel. |
| Administração | Criar um pequeno manual para quem publica curso, evento, livro, FAQ, notícia e centro, definindo quem aprova cada tipo de conteúdo. |

## 4. Roteiro recomendado para terminar

### Fase A — Fechar os requisitos de lançamento

Primeiro, migrar a FAQ para o banco de dados e criar “Os meus bilhetes”. Em seguida, executar uma bateria de testes de ponta a ponta para pagamentos, incluindo os retornos do Prontu e os webhooks. Esta fase deve terminar com acessos, estados e recibos coerentes para curso presencial, curso em vídeo e evento.

### Fase B — Preparar a operação segura

Depois, configurar o ambiente de produção com domínio, HTTPS, hosts permitidos, cookies seguros, e-mail remetente verificado, variáveis seguras, monitorização e backups. A política de privacidade e o consentimento do cadastro devem receber revisão final antes de abrir o serviço ao público.

### Fase C — Preparar catálogo e equipa editorial

Publicar o primeiro conjunto de conteúdo real, rever cada capa, preço, condições, datas e responsável editorial. Nesta fase, os centros e organizadores devem receber orientações curtas de publicação e suporte.

### Fase D — Lançamento controlado

Abrir inicialmente para um grupo pequeno de alunos, centros e organizadores. Acompanhar inscrições, pagamentos, e-mails, acessos, bilhetes e relatórios de erro durante alguns dias. Só depois ampliar divulgação e tráfego.

## 5. Itens que podem ficar para a próxima versão

A Biblioteca pode evoluir com audiolivros carregados por autores/editoras, resumos assistidos por IA apenas para obras autorizadas, anotações e marcadores pessoais. Recomendações mais avançadas, notificações push, cupões, avaliações de eventos e um painel analítico para centros também são bons candidatos para uma segunda fase, mas não devem atrasar a segurança e os fluxos financeiros do lançamento.

## 6. Decisão recomendada agora

A próxima tarefa recomendada é implementar a **FAQ administrada pelo Django Admin**, porque é uma pendência já identificada e remove conteúdo fixo do frontend. Depois disso, criar **Os meus bilhetes** e concluir a validação real do Prontu. Essas três entregas formam o caminho mais directo para deixar a plataforma preparada para uma abertura controlada.
