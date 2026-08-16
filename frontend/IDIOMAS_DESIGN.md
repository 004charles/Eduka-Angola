# Suporte de idiomas da Edukangola

O frontend público disponibiliza quatro idiomas de interface: **Português (PT)**, **English (EN)**, **Français (FR)** e **中文 (简体, ZH)**. A escolha aparece no cabeçalho, é guardada no navegador e atualiza o atributo `lang` da página para favorecer acessibilidade e tecnologias de leitura.

A tradução é aplicada apenas aos textos de interface criados pela Edukangola — navegação, ações, filtros, páginas institucionais, mensagens e etiquetas. Títulos, descrições, preços, nomes de centros, imagens e conteúdos publicados pelos centros continuam no idioma em que foram efetivamente registados no GestorEduka. Esta distinção evita alterar ou inventar informação institucional.

O primeiro conjunto cobre o cabeçalho e rodapé, pesquisa rápida, página inicial, catálogo, filtros e página “Como funciona”. Os componentes usam um único contexto React e chaves de tradução, permitindo ampliar o vocabulário para as áreas autenticadas, checkout e detalhe de curso sem criar uma segunda arquitetura.
