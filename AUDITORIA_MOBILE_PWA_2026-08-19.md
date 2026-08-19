# Auditoria móvel e PWA — Edukangola

**Data:** 19 de agosto de 2026
**Âmbito:** navegação pública, catálogo, acesso do aluno, pesquisa, cursos, mensagens e base de instalação PWA.

## Conclusão executiva

A Edukangola já tem uma **base responsiva relevante**, com páginas de autenticação, área do aluno, mensagens, detalhes de curso e biblioteca que incluem adaptações a ecrãs estreitos. No entanto, a experiência actual ainda se comporta como um **site responsivo** e não como uma aplicação instalada: falta a fundação PWA, a navegação móvel não dá acesso imediato à conta, e acções essenciais ficam demasiado longe no fim de listas extensas.

> **Decisão recomendada:** tratar a próxima etapa como um ciclo de “mobile-first PWA”, começando pela navegação persistente, acesso à área do aluno, instalação e descoberta de catálogo. Não é necessário construir uma aplicação nativa para entregar uma experiência de aplicação coerente.

| Avaliação global | Estado |
|---|---|
| Leitura e temas claro/escuro | Bom, com pontos de densidade a reduzir |
| Navegação móvel e área do aluno | Crítico |
| Catálogo, filtros e paginação | Crítico |
| Pesquisa rápida | Corrigido recentemente; requer confirmação no dispositivo físico |
| Base PWA instalável | Ausente |
| Continuidade dos fluxos aluno | Parcial |

## Evidência observada

A auditoria combinou a leitura do frontend React, as regras responsivas existentes e as capturas fornecidas no telemóvel. O catálogo usa **nove itens por página** e, abaixo de 480 px, passa para uma coluna; como cada cartão tem **354 px de altura**, o controlo de paginação só aparece depois de uma sequência muito longa de cartões. Isto explica por que parece inexistente no uso real.

A navegação móvel reduz o perfil do aluno a um botão de ícone e mantém o menu da conta como um menu suspenso de topo. Ao mesmo tempo, as acções de entrar/criar conta desaparecem no ponto móvel, sem uma alternativa permanente no menu. Isto torna a área do aluno difícil de descobrir e inconsistente para quem tem a PWA instalada.

Na camada de instalação, `index.html` só contém viewport, fontes e metadados básicos. Não existem `manifest`, ícones PWA dedicados, `theme-color`, metadados Apple, service worker nem registo de service worker. Um manifesto é a fonte de informação que o navegador usa para instalar a PWA, incluindo nome, ícones e modo de apresentação. [1] A instalação promovida pelos navegadores requer, entre outros critérios, HTTPS e um manifesto com nome, ícones, `start_url` e `display`. [2]

## Achados prioritários

| Prioridade | Área | Problema observado | Impacto móvel | Recomendação objectiva |
|---|---|---|---|---|
| P0 | Instalação PWA | Não há manifesto, ícones de instalação ou service worker. | Não há experiência realmente instalada, ecrã de abertura, cache de base ou convite de instalação. | Criar `app.webmanifest`, ícones 192/512, `display: standalone`, cores da marca, service worker e ecrã offline. |
| P0 | Navegação do aluno | Área do aluno depende de ícone pequeno e menu suspenso; entrar/criar conta são ocultados no móvel. | O aluno não encontra a conta, mensagens, certificados ou sessão. | Criar barra inferior móvel com **Início, Catálogo, Vídeo, Biblioteca e Perfil**; mostrar “Entrar” como quinta ação para visitante. |
| P0 | Catálogo | Paginação aparece depois de 9 cartões de uma coluna; os controlos perdem texto no móvel. | O utilizador chega ao rodapé sem perceber que há mais resultados. | Usar 6 cartões por página no móvel e um controlo visível “Ver mais cursos” após o sexto cartão; manter páginas numeradas numa folha de resultados. |
| P0 | Área segura | Barra fixa e Eduka AI usam margens fixas, sem `safe-area-inset`. | Em telemóveis instalados, botões podem competir com a barra de gestos ou sobrepor conteúdo. | Aplicar `viewport-fit=cover` e `env(safe-area-inset-*)` na navegação inferior, alertas e Eduka AI. [3] |
| P1 | Cabeçalho de centros | Etiquetas e botões de ação ficam encostados no perfil de centro. | Reduz a leitura e dá sensação de composição quebrada. | Separar etiquetas e ações em duas faixas, com espaçamento vertical e rolagem horizontal apenas quando necessário. |
| P1 | Cartões de curso | Um cartão ocupa grande parte do ecrã em catálogo de coluna única. | A descoberta fica lenta e o rodapé aparece antes da paginação ser percebida. | Usar uma variante móvel mais densa: imagem menor, título limitado a duas linhas e dados essenciais em duas linhas. |
| P1 | Filtros | O catálogo concentra pesquisa, filtros, comparação e ordenação antes da lista. | Ocupa a primeira dobra e aumenta o esforço de voltar aos resultados. | Transformar filtros em folha inferior (“Filtros”), com resumo de filtros activos e botão aplicar. |
| P1 | Eduka AI | Lançador fixo sobrepõe o rodapé e não respeita área segura. | Pode competir com a navegação inferior e com acções do catálogo. | Reposicionar acima da barra inferior e reduzir para ícone em páginas com formulário ou leitura. |
| P2 | Mensagens | O fluxo já colapsa para uma coluna, mas precisa teste em Android real com teclado. | Campo de envio pode perder contexto quando o teclado abre. | Usar viewport com `interactive-widget=resizes-content` e testar conversa longa, anexos futuros e retorno à lista. [3] |
| P2 | Curso, vídeo e leitura | As páginas têm regras móveis, mas precisam de critérios consistentes de toque. | Pode haver desalinhamento entre botões, barras de progresso e ações secundárias. | Normalizar alturas mínimas de toque, espaçamentos e estados de carregamento nos três fluxos. |

## Avaliação por percurso

| Percurso | Estado actual | Diagnóstico | Próxima melhoria |
|---|---|---|---|
| Abrir e instalar | Insuficiente | A aplicação abre no navegador como site; não há elementos formais de instalação. | Fundação PWA e convite de instalação discreto após uso real. |
| Navegar como visitante | Parcial | Pesquisa e menu funcionam, mas login/criar conta não têm entrada móvel permanente. | Barra inferior e item de conta no menu. |
| Entrar na área do aluno | Crítico | O acesso depende de um controlo compacto no topo. | Separador “Perfil” persistente e estado autenticado inequívoco. |
| Explorar catálogo | Parcial | A lista funciona, mas paginação está escondida pela altura dos cartões. | Paginação móvel por “ver mais”, filtros em folha e cartões densos. |
| Pesquisar | Bom após ajuste | As sugestões passaram a ser empilhadas e legíveis. | Confirmar em Android e tornar o campo de pesquisa uma rota/tela própria na PWA. |
| Ver curso e inscrever-se | Parcial | Detalhe público já abre; cartões e navegação de retorno precisam ritmo móvel. | CTA de inscrição fixo no fundo apenas na página de detalhe. |
| Mensagens e notificações | Parcial | Há chat e contador, mas a entrada não é persistente no móvel. | Atalho na barra inferior e validação com teclado aberto. |
| Biblioteca e leitura | Parcial | Há telas dedicadas, mas não foram validadas num dispositivo físico nesta auditoria. | Testar continuidade de leitura, voz e controlo de brilho em Android. |

## Roteiro recomendado

### Bloco 1 — A aplicação instalada e navegável

Este bloco deve ser implementado primeiro porque desbloqueia o uso diário. Inclui manifesto, ícones, service worker prudente, modo `standalone`, cor da barra do sistema, área segura e barra inferior móvel. A barra deverá conter apenas cinco destinos: **Início**, **Catálogo**, **Vídeo**, **Biblioteca** e **Perfil**. Para visitante, o último item abre o login; para aluno autenticado, abre a área do aluno e mostra um ponto de mensagem não lida.

O service worker deve guardar apenas a estrutura estática e páginas públicas recentes. Dados de sessão, pagamentos, inscrições e mensagens devem continuar sempre a validar no servidor; a PWA não deve simular sucesso offline para operações que exigem confirmação.

### Bloco 2 — Descoberta sem cansaço

O catálogo deve mostrar seis itens antes da primeira continuação e terminar com um botão largo **“Ver mais cursos”**, mais fácil de descobrir por toque do que uma linha de números. A paginação numerada pode permanecer quando o utilizador abre a folha “Todos os resultados”. Os filtros devem passar para uma folha inferior, preservando no topo só a pesquisa, o total e filtros activos.

Os cartões móveis devem ser densos, sem retirar informação de decisão: imagem, categoria, título, centro, valor/condição e próxima turma. Comparar e favorito podem ficar numa ação contextual, evitando que cada cartão tenha demasiados ícones.

### Bloco 3 — Continuidade do aluno

Depois da navegação, devem ser priorizados: mensagens com teclado aberto, continuar aprendizagem de cursos em vídeo, biblioteca/leitura, certificados e preferências de notificação. Cada fluxo deve ter uma forma inequívoca de voltar à área anterior sem depender do gesto de recuo do navegador.

## Critérios de aceitação para a próxima entrega

| Tema | Critério verificável |
|---|---|
| Instalação | Chrome Android reconhece a Edukangola como instalável e abre em modo autónomo. |
| Navegação | Um aluno entra na área pessoal com um toque a partir de qualquer página. |
| Visitante | Um visitante encontra “Entrar” com um toque a partir de qualquer página. |
| Catálogo | A continuação de resultados aparece antes do rodapé, após no máximo seis cartões. |
| Área segura | Nenhum botão fixo fica encostado à barra de gestos ou ao recorte de ecrã. |
| Pesquisa | Sugestões mantêm título e metadados separados a 360 px de largura. |
| Mensagens | Campo de composição permanece acessível com teclado Android aberto. |

## Limites desta auditoria

Foram analisados o código React, as regras de responsividade e as capturas Android fornecidas. A confirmação final deve ser feita em pelo menos um Android instalado e um iPhone/Safari, sobretudo para instalação, áreas seguras, teclado e retorno de sessão.

## Referências

[1] [MDN — Web application manifest](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest)
[2] [web.dev — Critérios de instalação de PWA](https://web.dev/articles/install-criteria)
[3] [MDN — Meta viewport, `viewport-fit` e área segura](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name/viewport)
