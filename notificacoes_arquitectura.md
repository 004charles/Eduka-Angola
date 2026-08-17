# Arquitectura do serviço separado de notificações

## Objectivo

A Edukangola terá um serviço independente para receber eventos do Django, decidir quais alunos devem ser notificados, aplicar as preferências opt-in, deduplicar mensagens e encaminhar cada entrega para a plataforma ou para o e-mail.

## Componentes

| Componente | Responsabilidade | Estado de dados |
|---|---|---|
| Django Edukangola | Publica eventos de negócio e continua a ser a fonte oficial de alunos, cursos, turmas, livros e eventos | Base de dados actual |
| Gateway de notificações | Recebe eventos autenticados, valida assinatura e coloca cada evento numa fila durável | Serviço separado |
| Processador | Resolve destinatários, verifica preferências, cria a chave idempotente e agenda entregas | Base de dados própria do serviço |
| Entrega na plataforma | Sincroniza uma notificação persistente no perfil do aluno | API interna autenticada do Django |
| Entrega por e-mail | Envia mensagens individuais ou agrupadas através do Brevo | Credencial apenas no ambiente do serviço |
| Tarefas periódicas | Processa reintentos, lembretes, calendário e resumo semanal | Scheduler do serviço |

## Contrato de evento

Cada evento terá `event_id`, `event_type`, `occurred_at`, `source`, `schema_version` e `payload`. O `event_id` é único no produtor e a combinação `event_type + recipient_id + dedupe_key + channel` é única no serviço. O corpo será assinado com HMAC-SHA256 através de um segredo que nunca será colocado no repositório.

Os tipos iniciais serão `course.published`, `class.opened`, `book.published`, `event.published`, `learning.reminder`, `calendar.notice` e `weekly.digest.requested`. Eventos de conversa e suporte continuarão a ser compatíveis com as notificações actuais, mas serão migrados progressivamente para o contrato comum.

## Segurança e fiabilidade

O gateway aceitará apenas HTTPS, verificará timestamp e assinatura para impedir replay, limitará o tamanho do pedido e rejeitará eventos fora da janela de tolerância. O produtor Django usará uma fila de saída transaccional para não perder eventos quando a rede estiver indisponível. O serviço responderá rapidamente com um identificador de aceitação; o processamento será assíncrono e terá reintentos com backoff.

Nenhum segredo, token ou credencial será guardado no GitHub. O serviço terá variáveis de ambiente separadas para a assinatura entre serviços, URL interna do Django, Brevo e base de dados própria.

## Activação por etapas

A primeira activação será em modo observação, registando eventos e decisões sem enviar e-mails. Em seguida serão activadas apenas notificações na plataforma para a conta de teste. Por fim, o e-mail e os resumos periódicos serão activados depois de confirmar o remetente Brevo, o domínio e os limites de envio.

## Decisões ainda necessárias para produção

O serviço precisa de um alojamento persistente independente do processo web Django. O código será preparado como serviço autónomo com processo web e worker, mas a activação de produção deve definir o provedor, a base de dados própria, o endereço HTTPS e os segredos do ambiente. Até essa configuração existir, a implementação local não enviará mensagens reais.
