# Matriz operacional da administração React

## Domínios prioritários

| Domínio | Entidades operacionais | Operações React necessárias |
|---|---|---|
| Centros e oferta | Centros, filiais, cursos presenciais, vídeo-cursos, turmas e inscrições | Pesquisa, leitura, activação/publicação, controlo de destaque e decisão de inscrições. |
| Pessoas e suporte | Utilizadores, alunos, gestores, instrutores, conversas, mensagens e contactos | Pesquisa, activação, leitura de contexto e encaminhamento de pendências. |
| Financeiro | Pagamentos, tentativas, histórico, configurações e planos | Filtros por estado/moeda, confirmação operacional controlada, reconciliação e configurações não secretas. |
| Mercado | Lojas parceiras, produtos, pedidos e entrega | Publicação/stock, validação de disponibilidade e avanço do estado de entrega. |
| Conteúdo público | Bolsas, escolas, estágios, biblioteca, carreira, eventos, blog e FAQs | Publicação, destaque, análise de candidaturas e moderação. |
| Plataforma | Módulos públicos, comissões, gateways, notificações e auditoria | Activação, parâmetros seguros, fila de alertas e histórico de mudanças. |

## Regras de segurança

Todas as APIs React administrativas exigem sessão administrativa isolada e `is_staff`. As alterações financeiras, de publicação, de estado de pedido e de conta devem guardar autor, data, recurso e valores anterior/novo num registo de auditoria. Segredos de gateway, correio, serviços externos e credenciais não devem ser expostos pela interface React.

## Ordem de entrega

1. Listagens e acções de centros, cursos, utilizadores, inscrições, pagamentos, produtos e pedidos.
2. Filtros, paginação, estados operacionais, detalhes e criação/edição de conteúdos permitidos.
3. Configurações não secretas, suporte, alertas e registo de auditoria.
4. Conteúdos editoriais e módulos especializados, mantendo a contingência interna apenas até a respectiva validação.
