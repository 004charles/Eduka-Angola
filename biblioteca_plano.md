# Biblioteca Edukangola — plano de produto

> **Objectivo:** criar uma biblioteca angolana de aprendizagem, leitura e escuta, onde cada título é apresentado como um livro físico ou digital — e não como um cartão de curso — permitindo acesso gratuito, venda digital e venda de exemplares físicos.

## 1. Direcção do produto

A Biblioteca Edukangola será uma área própria, acessível pelo menu principal em **Biblioteca**, com uma experiência editorial centrada em capas, estantes, autores e percurso de leitura. A plataforma não será uma simples grelha de produtos. A página deve dar a sensação de entrar numa livraria bem cuidada: uma obra em destaque sobre uma mesa de leitura, estantes horizontais de capas com proporção real de livro, recomendações contextuais e uma zona de escuta com um leitor de áudio discreto.

A referência local confirma que há espaço para combinar descoberta, categorias e acesso digital. A Biblioteca Digital da AGT apresenta conteúdos por categorias e acesso associado a conta; a página consultada reporta mais de 212 mil utilizadores registados e 113 conteúdos publicados.[1] A Livraria Barquinho organiza a venda online através de destaques, novidades e mais vendidos, com preço e descrição de cada obra.[2] A Onleihe do Goethe-Institut demonstra o valor de reunir e-books, audiolivros e materiais de aprendizagem num único ambiente digital.[3]

| Princípio | Decisão de produto |
|---|---|
| **Identidade Edukangola** | Fundo claro/escuro, tipografia e ritmo visual existentes; azul Edukangola usado para acções e estados, nunca como decoração excessiva. |
| **Livro, não cartão** | Capa vertical em proporção editorial, lombada simulada, sombra curta e textura de papel. Sem caixas rectangulares de curso nem grelhas repetitivas. |
| **Descoberta editorial** | Estantes por intenção de leitura, selecção semanal, autores angolanos, obras gratuitas, escuta e leituras para carreira. |
| **Acesso transparente** | Cada título mostra claramente: gratuito, compra digital, audiolivro, físico sob encomenda ou indisponível. |
| **Aprendizagem responsável** | Resumos, áudio e ficheiros só são disponibilizados quando o direito de distribuição ou transformação estiver registado. |

## 2. Experiência principal

### Página `/biblioteca`

A entrada terá uma **mesa de leitura** com um único livro em destaque. À esquerda, uma capa grande com espessura visual; à direita, título, autor, uma razão editorial curta, formato disponível e uma acção principal. O destaque muda de forma editorial, não como um carrossel publicitário automático.

Depois da entrada, a página apresenta três blocos com cadência visual diferente. A secção **Na estante esta semana** terá uma fila horizontal de livros, cada um como objecto físico com capa e lombada. A secção **Ouvir enquanto aprende** mostrará duas ou três obras áudio com um leitor fino, duração e botão de reprodução. A secção **Leituras que abrem caminhos** associa obras a temas da Edukangola, como gestão, tecnologia, idiomas, saúde, criatividade e desenvolvimento pessoal. Cada bloco terá uma única ligação de exploração, evitando a sensação de catálogo infinito.

O filtro não será uma coluna pesada de opções. A pesquisa aparece no topo como já acontece na plataforma; os filtros secundários são chips compactos para **Tema**, **Formato**, **Acesso**, **Idioma** e **Autor angolano**. A página de resultados usa prateleiras e uma lista editorial vertical apenas quando o utilizador pede pesquisa ou filtro específico.

### Página `/biblioteca/:slug`

A ficha do livro dá prioridade à capa, sinopse, autor, editora, idioma, páginas, ano, formatos e condições de acesso. A área comercial terá apenas uma acção clara conforme o título: **Ler gratuitamente**, **Comprar e-book**, **Ouvir agora**, **Comprar exemplar físico** ou **Pedir disponibilidade**.

O detalhe inclui um excerto autorizado, assuntos relacionados, outros títulos do autor e uma secção **Para estudar melhor**. Esta última pode apresentar resumo editorial, pontos-chave e perguntas de reflexão apenas quando aprovados pelo detentor dos direitos ou produzidos para domínio público. O leitor nunca deve afirmar que um resumo substitui a obra completa.

### Páginas pessoais

O aluno terá **A minha biblioteca**, integrada na área do aluno. A página separa obras adquiridas, leituras gratuitas guardadas, progresso de leitura, progresso de escuta e favoritos. Para obras digitais adquiridas, o ficheiro não será exposto como URL pública: a entrega acontece por autorização da conta. A experiência de leitura abre em `/ler/:slug` e a de áudio em `/ouvir/:slug`, com posição guardada, capítulos, marcadores e velocidade de reprodução.

## 3. Formatos e regras de publicação

| Formato | O que o utilizador recebe | Regra de publicação | Venda e acesso |
|---|---|---|---|
| **Livro físico** | Reserva/compra do exemplar e informação de entrega ou levantamento | Stock, fornecedor, preço e áreas de entrega definidos no painel administrativo | Pedido confirmado após pagamento; entrega é gerida pela entidade vendedora. |
| **E-book protegido** | Leitura no navegador e, se autorizado, descarga controlada | EPUB/PDF e licença de distribuição obrigatórios | Compra única ou acesso gratuito; permissão fica ligada à conta. |
| **Audiolivro** | Faixas ou capítulos de áudio num leitor interno | Áudio próprio ou licença de narração e distribuição registada | Compra, acesso gratuito ou prévia limitada. |
| **Resumo de estudo** | Texto breve e estruturado, associado ao livro | Só para títulos autorizados, domínio público ou conteúdo fornecido pelo titular | Gratuito como complemento da obra, nunca como cópia do livro. |

No lançamento, a publicação deve ser controlada pelo **Django Admin**. Assim, a Edukangola valida capa, metadados, preço, licença, formato e disponibilidade antes de qualquer título aparecer. Uma área de auto-publicação para autores e editoras pode ser criada numa segunda fase, com formulário de candidatura, acordo de direitos, revisão editorial e aprovação humana.

## 4. Dados e arquitectura a acrescentar

O projecto ainda não contém uma aplicação Django funcional para biblioteca, embora existam comentários antigos que apontam para uma futura `biblioteca`. A implementação deve criar uma aplicação isolada, sem alterar a estrutura do GestorEduka.

| Entidade | Responsabilidade principal |
|---|---|
| `Livro` | Título, sinopse, capa, idioma, ISBN opcional, categoria, editora, autor, estado editorial e formato disponível. |
| `Autor` e `Editora` | Identidade, biografia, país, imagem e catálogo relacionado. |
| `EdicaoLivro` | Ano, páginas, ISBN, idioma, preço, moeda, stock e formato específico. |
| `ArquivoDigitalLivro` | EPUB/PDF protegido, permissões de download, amostra e marca de direitos. |
| `AudioLivro` e `CapituloAudio` | Faixas, duração, narrador, prévia e ordem de reprodução. |
| `AcessoLivro` | Direito individual do aluno a ler, ouvir ou descarregar uma edição. |
| `ResumoLivroIA` | Resumo estruturado, pontos-chave, estado de revisão e origem/autorização. |
| `PedidoLivroFisico` | Entrega/levantamento, contacto, endereço, estado e referência de pagamento. |

O modelo de pagamentos existente já centraliza valor, referência, gateway, estado e metadados. Para livros, será acrescentado um tipo explícito como `LIVRO` e cada pagamento será ligado ao pedido ou ao direito de acesso. A activação de e-book/audiolivro só acontece depois da confirmação do pagamento; nenhum acesso é concedido apenas porque o utilizador abriu a página de checkout.

## 5. Resumos e áudio assistidos por IA

A Groq pode ser usada para produzir resumos estruturados e, nas línguas actualmente indicadas pela documentação, converter texto em voz. A API de chat suporta respostas estruturadas por JSON Schema, o que permite guardar resumo, pontos-chave, perguntas de revisão e aviso de escopo de forma previsível.[4] A API de voz da Groq disponibiliza actualmente modelos de síntese para inglês e árabe; por isso, **não devemos prometer narração automática em português no lançamento**.[5]

| Abordagem | Como funciona | Benefícios | Limites e cuidados | Complexidade |
|---|---|---|---|---|
| **Biblioteca com áudio enviado por editor/narrador** | O administrador carrega ficheiros áudio já autorizados; a IA só cria resumos de títulos elegíveis. | Português e línguas locais podem ter narração humana; menor risco de direitos e maior qualidade editorial. | Exige que autor/editora forneça o áudio ou a licença. | Baixa no lançamento. |
| **Áudio assistido pela Groq para conteúdo elegível** | A IA gera áudio a partir de texto próprio, domínio público ou autorização expressa; o resultado é guardado como ficheiro e revisto. | Produção rápida de prévias e materiais de estudo em idiomas suportados. | A documentação actual só anuncia vozes em inglês e árabe; não usar para reproduzir livros pagos sem autorização. | Média, com fila de processamento e revisão. |

Para resumos, a abordagem segura é sempre **gerar uma vez no momento de publicação**, guardar o resultado, permitir revisão editorial e apresentar uma etiqueta como “Resumo de estudo assistido por IA”. Não é recomendável enviar o conteúdo integral de qualquer PDF adquirido automaticamente sempre que um aluno abrir a página. Para obras longas autorizadas, o processamento deve dividir o texto em partes, gerar sínteses por capítulo e produzir uma síntese final; isso evita limites de contexto, custos repetidos e respostas inconsistentes.

A chave da Groq será configurada exclusivamente como segredo do servidor quando chegarmos à fase de implementação. Não será incluída em React, ficheiros `.env` versionados, commits, pedidos do navegador ou URLs. A pesquisa da sessão não encontrou uma integração Groq activa; portanto, a configuração segura deverá ser feita apenas depois de escolhermos o escopo de IA.

## 6. Sequência recomendada de entrega

| Etapa | Entrega | Resultado visível |
|---|---|---|
| **1. Fundação editorial** | Modelos básicos, Django Admin, categorias, autores, capas, página `/biblioteca` e detalhe de livro. | Uma biblioteca bonita e navegável, com livros demonstrativos reais/autorizados. |
| **2. Acesso gratuito e biblioteca pessoal** | Leitura web de e-books autorizados, favoritos, progresso e “A minha biblioteca”. | O aluno guarda, lê e retoma obras gratuitas. |
| **3. Venda digital e física** | Checkout de livros, direito de acesso após confirmação e pedidos físicos. | Venda clara sem misturar inscrições de cursos com livros. |
| **4. Áudio** | Leitor por capítulos, progresso e audiolivros enviados por editora/narrador. | Escuta contínua e controlada na plataforma. |
| **5. IA editorial** | Resumos revistos, pontos-chave, perguntas e piloto de voz apenas para conteúdo e idioma elegíveis. | Apoio ao estudo sem comprometer direitos nem qualidade. |

## 7. Decisões a confirmar antes de construir

Para avançar com uma primeira versão bem focada, preciso que confirme três decisões. A primeira é se a etapa inicial deve vender **também livros físicos**, ou se começa por **obras digitais e gratuitas** enquanto a entrega física fica preparada para a etapa seguinte. A segunda é qual abordagem de áudio prefere: ficheiros narrados e enviados por autores/editoras desde o início, ou um piloto limitado de voz assistida por IA em conteúdos elegíveis. A terceira é se a primeira colecção deve começar com obras de **domínio público/licenciadas** e conteúdos próprios, que é a opção mais segura para demonstrar leitura, áudio e resumos.

## Referências

[1] [Biblioteca Digital da AGT](https://bibliotecadigital.minfin.gov.ao/)

[2] [Livraria Online Barquinho](https://livrariabarquinho.net/)

[3] [Onleihe — Goethe-Institut Angola](https://www.goethe.de/ins/ao/pt/kul/xp/onl.html)

[4] [Groq — Text Generation and Structured Outputs](https://console.groq.com/docs/text-chat)

[5] [Groq — Text to Speech](https://console.groq.com/docs/text-to-speech)
