# Mercado Edukangola — proposta de experiência e operação

> **Estado:** proposta para discussão. Este documento não autoriza ainda a implementação de catálogo, pagamentos, entregas ou contas de lojas.

## 1. Decisão já aprovada

O **Mercado Edukangola** será uma área própria para descobrir, pagar e acompanhar produtos educacionais fornecidos por **lojas parceiras**. A Edukangola não terá stock próprio, mas será a única entidade que opera o catálogo, confirma disponibilidade, recebe o pagamento, recolhe o produto na loja e entrega ao comprador. As lojas não terão painel, conta administrativa nem acesso aos pedidos.

Na página inicial existirá apenas uma faixa curta de descoberta. O comércio completo ficará separado em `/mercado`, evitando confundir cursos, Biblioteca e produtos físicos.

| Elemento | Decisão aprovada |
|---|---|
| Nome da área | **Mercado Edukangola** |
| Origem dos produtos | Lojas parceiras verificadas; sem stock próprio da Edukangola |
| Pagamento | Checkout seguro dentro da Edukangola |
| Operação | Catálogo, pedidos, recolha e entrega geridos apenas pela Administração Edukangola |
| Entrega | Recolha pela equipa Edukangola na loja e entrega ao comprador |
| Página inicial | Uma única faixa compacta, de descoberta e com scroll automático controlado |
| Acesso à área completa | Botão **Explorar o Mercado** |
| Relação com cursos | Separada; produtos não aparecem no catálogo de cursos nem interferem com inscrições |
| Relação com a Biblioteca | Livros digitais permanecem na Biblioteca; livros físicos podem ser produtos de lojas parceiras |

## 2. Faixa compacta da página inicial

### Conteúdo e posição

A faixa terá o título **“Materiais para aprender melhor.”** e a descrição curta **“Tecnologia, livros e essenciais de estudo de lojas parceiras.”**. Deve ficar depois da estante da Biblioteca e antes das recomendações finais de cursos, funcionando como descoberta complementar à aprendizagem.

O botão principal será **“Explorar o Mercado”**. Não haverá botão de comprar, carrinho, desconto agressivo ou formulário nessa área. A faixa leva o visitante ao Mercado Edukangola, onde existe contexto suficiente para tomar uma decisão.

### Cartão de produto na página inicial

Cada produto será deliberadamente pequeno, nunca do tamanho de um cartão de curso. A composição deve fazer o objecto parecer um produto físico, com imagem frontal limpa e pouca informação.

| Área | Desktop | Telemóvel |
|---|---:|---:|
| Largura do item | 148–160 px | 132–140 px |
| Imagem | quadrado de 100 px | quadrado de 88 px |
| Texto | categoria, nome em duas linhas, preço e loja | igual, com tipografia mais compacta |
| Interacção | pausa no hover/foco; setas discretas | scroll com o dedo; pausa ao tocar |

O carril desloca-se devagar, sem chamar mais atenção do que os cursos. Respeita `prefers-reduced-motion`, oferece controlo manual e nunca esconde produtos importantes atrás de animação. Os elementos podem incluir computador portátil, mochila, caderno, calculadora, livro físico, pen drive e auscultadores, desde que cada item esteja ligado ao estudo.

## 3. Estrutura da área completa

O Mercado Edukangola deve ter identidade própria dentro da plataforma, mas usar a tipografia, cores, espaçamento e componentes confiáveis já existentes na Edukangola.

| Rota | Objetivo | Conteúdo principal |
|---|---|---|
| `/mercado` | Descoberta completa | destaque editorial, categorias, lojas verificadas, produtos e filtros |
| `/mercado/produtos/:slug` | Decisão de compra | fotos, descrição, preço, disponibilidade, loja, garantia e opções de levantamento/entrega |
| `/mercado/lojas/:slug` | Confiança na loja | identidade, localização, contactos, políticas, produtos e avaliação operacional |
| `/mercado/pedidos` | Acompanhamento do aluno | pedidos, estados, referência, entrega/levantamento e pedido de apoio |

Na área completa, os produtos continuam compactos nas listas, mas ganham contexto no detalhe. O destaque inicial deve privilegiar percursos de aprendizagem — por exemplo, **“Essenciais para começar Informática”**, **“Materiais para o regresso às aulas”** e **“Leitura e organização”** — em vez de uma montra genérica de consumo.

## 4. Perfis e responsabilidades

| Perfil | O que pode fazer | Responsabilidade |
|---|---|---|
| Aluno/comprador | Explorar, guardar, pedir, escolher entrega e acompanhar pedido | Confirmar dados de contacto e levantar/receber a encomenda |
| Loja parceira | Fornecer produtos e confirmar disponibilidade à equipa Edukangola por canal comercial acordado | Produto correcto, factura de compra e garantia do fabricante/loja |
| Administração Edukangola | Cadastrar lojas e produtos, actualizar preço e disponibilidade, confirmar o pedido, receber pagamento, recolher, entregar e acompanhar ocorrências | Qualidade do catálogo, operação do pedido, comunicação e resolução inicial de problemas |

Não existirá portal autónomo de vendedor. A Administração Edukangola usa uma área interna própria para registar cada loja, produto, custo de aquisição, preço apresentado ao aluno, disponibilidade, recolha e entrega. A disponibilidade não pode ser considerada automática: antes de o aluno pagar, a equipa confirma o stock com a loja.

## 5. Dados necessários antes de programar

O modelo deve manter produtos e pedidos isolados dos modelos de curso, inscrição e pagamento académico. Os objectos iniciais são os seguintes.

| Entidade | Informação essencial |
|---|---|
| `LojaParceira` | nome, logótipo, contacto operacional, localização, condições comerciais, garantia e estado de verificação; sem credenciais de acesso |
| `ProdutoMercado` | loja de origem, título, categoria, descrição, fotos, custo de aquisição, preço ao aluno, moeda, condição, garantia, activo e destaque |
| `VariacaoProduto` | cor, capacidade, tamanho ou outra característica que altera stock/preço |
| `DisponibilidadeProduto` | disponível após confirmação manual, indisponível ou sob consulta, com data e responsável pela última confirmação |
| `PedidoMercado` | comprador, loja, itens, subtotal, entrega, estado, referência e data |
| `RecolhaProduto` | loja de recolha, responsável Edukangola, custo confirmado, factura/comprovativo e data de recolha |
| `EntregaPedido` | endereço do comprador, contacto de recepção, responsável Edukangola, prazo, código de entrega, prova e estado |
| `OcorrenciaPedido` | cancelamento, indisponibilidade, atraso, devolução ou reclamação, com resposta da loja |

## 6. Pagamento, stock e entrega: modelo aprovado

O pagamento dos produtos será feito dentro da Edukangola, mas não deve reutilizar automaticamente o mesmo ciclo de cursos. Cursos desbloqueiam acesso académico; produtos físicos exigem confirmação manual de stock, recolha, entrega comprovada e eventual devolução. O checkout dos produtos será um domínio próprio, com referência de pedido, itens, endereço, pagamento e reembolso separados da inscrição académica.

| Elemento | Decisão operacional |
|---|---|
| Confirmação de stock | A Administração Edukangola confirma manualmente a disponibilidade e o preço final com a loja antes de abrir o pagamento ao aluno. |
| Pagamento | Depois da confirmação, o comprador paga na Edukangola através do gateway aprovado. |
| Recolha | A equipa Edukangola recolhe o produto na loja, guarda a factura/comprovativo e verifica o artigo antes de seguir para entrega. |
| Entrega | A Edukangola comunica o prazo e entrega ao comprador no endereço confirmado. |
| Liquidação à loja | A compra à loja, o custo de aquisição, a taxa de entrega e a margem da plataforma são registados pela Administração no pedido. |
| Reembolso | Se o produto não estiver disponível, for diferente ou a entrega não puder ocorrer, a Edukangola conduz o reembolso integral ou parcial conforme a ocorrência. |

### Ciclo operacional de um pedido

| Estado | Responsável | Resultado para o comprador |
|---|---|---|
| `A validar disponibilidade` | Administração Edukangola | O aluno manifestou interesse; a equipa confirma produto, preço e prazo na loja. |
| `A aguardar pagamento` | Comprador | A disponibilidade foi confirmada e o checkout seguro foi aberto. |
| `Pago — a recolher` | Administração Edukangola | O pagamento foi recebido e a equipa recolhe o produto na loja. |
| `Em preparação para entrega` | Administração Edukangola | O artigo foi conferido e é preparado para entrega. |
| `Em entrega` | Administração Edukangola | O comprador vê a previsão e o acompanhamento disponível. |
| `Entregue` | Comprador ou prova de entrega | O pedido é concluído com código ou prova de entrega. |
| `Ocorrência` | Administração Edukangola e comprador | Atraso, item errado, dano ou tentativa de entrega falhada fica documentada e é acompanhada. |
| `Reembolso pendente / reembolsado` | Edukangola | O comprador acompanha a decisão e a referência do reembolso. |

### Regras financeiras obrigatórias

A Edukangola deve manter um registo financeiro próprio por pedido: custo de aquisição na loja, preço apresentado ao aluno, custo de entrega, desconto, margem operacional, valor recebido, reembolso e referência do gateway. Não se deve assumir que o gateway actual suporta reembolsos automatizados; essa capacidade precisa ser confirmada formalmente com o fornecedor antes de a apresentar como automática.

O acordo comercial com cada loja deve definir preço de aquisição, prazo de reserva, factura, garantia, tratamento de devoluções e contacto operacional. Como a Edukangola recolhe e entrega, não haverá repasse automático de marketplace para uma conta de vendedor.

### Entrega e confirmação

No checkout, o aluno autenticado reutiliza nome, e-mail e telefone já verificados e apenas confirma o endereço de entrega. A loja não recebe dados pessoais do aluno; a comunicação de entrega é feita pela equipa Edukangola.

A entrega deve guardar uma janela prevista, contacto, método de entrega, custo, código de acompanhamento quando existir e prova de entrega. Para reduzir falsos encerramentos, o comprador confirma a recepção com um código de entrega ou a loja envia prova de entrega que fica sujeita a contestação por um prazo curto.

### Reembolso e problema de pedido

| Situação | Tratamento inicial |
|---|---|
| Produto sem stock depois de pago | Cancelamento e reembolso integral iniciado pela Edukangola. |
| Loja não aceita no prazo | Cancelamento e reembolso integral, salvo confirmação expressa do comprador para aguardar. |
| Produto errado, danificado ou diferente | Ocorrência aberta; retenção da liquidação à loja até decisão documentada. |
| Entrega falhada por endereço/contacto | Nova tentativa, entrega reagendada ou cancelamento conforme a política apresentada no checkout. |
| Devolução por arrependimento | Aplicável apenas quando a política da loja e a natureza do produto permitirem; a condição deve estar visível antes do pagamento. |

## 7. Regras de confiança no lançamento

Produtos de tecnologia devem mostrar explicitamente estado do equipamento, especificações essenciais, garantia, política de troca e identidade da loja. Produtos sem imagem real, preço, disponibilidade ou responsável verificável não são publicados.

O aluno deve saber em cada detalhe a loja de origem, como recebe, em que prazo, a garantia aplicável e como reporta um problema. A Edukangola é o ponto de contacto único para pagamento, acompanhamento, recolha, entrega e resolução inicial da ocorrência.

## 8. Pontos que exigem a sua decisão antes da implementação

1. A primeira fase será somente **Luanda** ou já aceitará lojas de outras províncias?
2. A entrega começa com equipa própria da Edukangola ou a plataforma contrata um estafeta/parceiro logístico sob gestão central?
3. Qual é o prazo máximo para a Administração confirmar a disponibilidade antes de abrir o pagamento: duas, quatro ou vinte e quatro horas?
4. A Edukangola aprova cada produto antes de publicar ou permite catálogo aprovado por categoria?
5. Como será definido o preço ao aluno: custo da loja mais margem fixa, margem percentual ou preço final acordado por produto?

## 9. Modelo anterior descartado

O modelo de pedido com pagamento directo à loja e o portal autónomo de vendedor foram descartados. O comprador paga dentro da Edukangola e recebe a encomenda através da operação centralizada da própria plataforma.

## Referências de contexto

- [Comércio electrónico em Angola — U.S. International Trade Administration](https://www.trade.gov/country-commercial-guides/angola-ecommerce)
- [Oportunidades de materiais e tecnologia educativa em Angola — U.S. International Trade Administration](https://www.trade.gov/market-intelligence/angola-education-market-opportunities)
