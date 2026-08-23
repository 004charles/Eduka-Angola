# Auditoria internacional — centros, moedas e pagamentos

## Referências externas confirmadas

Moçambique opera com o **metical** e o Banco de Moçambique apresenta o sistema de pagamentos instantâneos **METIX** como parte da infra-estrutura de pagamento nacional. A instituição também mantém avisos específicos sobre limites de pagamentos ao exterior com cartões, o que reforça a necessidade de validar o fornecedor de cobrança, liquidação e conversão antes de vender em MZN ou cobrar de alunos moçambicanos.[1]

A Guiné-Bissau integra a União Monetária da África Ocidental. A BCEAO é a instituição comum de emissão monetária e supervisiona operações bancárias nos oito Estados-membros, incluindo a Guiné-Bissau. A configuração de moeda para esse mercado deve, portanto, começar por **XOF**, não por AOA, EUR ou USD.[2]

| Mercado | Moeda operacional inicial | Implicação para a Edukangola |
|---|---|---|
| Angola | AOA | Pode usar a configuração e o gateway Prontu já existentes, depois de validar produção. |
| Moçambique | MZN | Exige moeda, fornecedor local/internacional compatível, liquidação e regras de reembolso próprias. |
| Guiné-Bissau | XOF | Exige suporte a XOF e um parceiro autorizado para a zona BCEAO/UEMOA. |
| Portugal | EUR | Exige gateway e liquidação em EUR; o enum actual possui EUR, mas não há gateway operativo nem repasse internacional. |

## Referências

[1] [Banco de Moçambique — página institucional e sistema METIX](https://www.bancomoc.mz/en/)

[2] [BCEAO — apresentação da União Monetária da África Ocidental](https://www.bceao.int/en/content/presentation-bceao)

## Estado actual da Edukangola

### Cursos em vídeo

| Área | Estado | Evidência e limite actual |
|---|---|---|
| Catálogo e aprendizagem | **Pronto para Angola** | Catálogo, aulas, progresso, continuidade, comentários, subscrição mensal, acesso durante período activo e avisos de expiração estão implementados. |
| Modelo comercial | **Pronto em AOA, pendente fora de Angola** | Os planos têm `preco`, `moeda` e período de 30 dias, mas o padrão é AOA e a cobrança real depende unicamente do gateway Prontu. |
| Propriedade do catálogo | **Regra definida, aplicação parcial** | A decisão de produto é que os cursos em vídeo são originais Edukangola. O modelo ainda preserva `centro` opcional e o código da página inicial ainda prepara colecções de cursos de parceiros; isto deve ser removido/impedido antes de abrir a gestão a centros. |
| Distribuição internacional | **Não pronta para cobrança** | Não há preços localizados por país, selecção de moeda pelo aluno, imposto, parceiro de pagamento internacional ou processo de reembolso por mercado. |

### Centros nacionais

O GestorEduka está bem mais preparado para centros angolanos do que para o exterior. O modelo actual inclui país, província/cidade, fuso horário, geolocalização, dados bancários, filiais, cursos, turmas, mensagens, inscrições, certificados e um fluxo de candidatura de centro com confirmação de e-mail/NIF. A cobrança real está orientada para **AOA + Prontu**, e os relatórios de repasse estão explicitamente em Kz.

> **Conclusão:** é correcto lançar primeiro o GestorEduka para centros nacionais e tratá-lo como a operação principal no dia 25.

### Centros estrangeiros

| Aspecto | Estado actual | O que falta para ser operativo |
|---|---|---|
| País e localização | **Base pronta** | O centro suporta AO, PT, BR, CV, MZ, ST, GW e TL, mais cidade, região e fuso horário. |
| Descoberta pública | **Base parcial** | O catálogo já identifica centros internacionais pelo país, mas precisa de filtro explícito “Estudar no exterior”, selo de verificação e informação editorial própria. |
| Filiais internacionais | **Não pronta** | A filial só herda o centro principal; não tem país, fuso, moeda, NIF fiscal ou banco próprio. |
| Admissões | **Base parcial** | Existe `CandidaturaExterna`, mas tem apenas pendente/aprovada/rejeitada/cancelada, um documento genérico e comprovativo. Faltam estados de documentos adicionais, aprovação condicional, carta de aceitação, prazo, lista configurável de documentos e controlo de acesso/retensão. |
| Verificação | **Não pronta** | Não há um processo formal de verificação institucional, responsável de admissões ou política publicada de propina/reembolso/alojamento. |
| Cobrança e repasse | **Não pronta** | Não há fluxo de propina internacional, liquidação transfronteiriça, comissão por país, reconciliação ou repasse multimoeda. |

### Moedas e pagamentos internacionais

Há campos para **AOA, EUR e USD** em Curso e Pagamento, e o modelo também enumera Stripe e PayPal. Isto é **preparação de dados**, não uma integração internacional pronta. O serviço real de pagamentos inicializa somente **Prontu**; Stripe e PayPal não têm implementação de gateway, webhook, conciliação, reembolso ou configuração de credenciais.

Além disso, `FinanceiroCentro` e os planos SaaS do GestorEduka assumem Kz, a configuração global usa AOA e não existem regras por país ou moeda. Para Moçambique falta MZN. Para Guiné-Bissau falta XOF. Para uma futura Guiné-Conacri seria GNF, mas este é outro país e não deve ser misturado com a Guiné-Bissau.

> **Conclusão:** hoje a Edukangola pode **mostrar** preço em EUR/USD no catálogo, mas não deve prometer que consegue cobrar ou repassar em EUR/USD. O fluxo de pagamento internacional não está pronto para produção.

## Modelo operacional recomendado

### Fase 1 — Descoberta e candidatura internacional, sem cobrar propina

Começar por **Portugal e Moçambique**, não por todos os países ao mesmo tempo. O centro estrangeiro publica oferta, requisitos, datas, moeda de referência, contacto de admissões e prazo. O aluno envia candidatura; o centro toma a decisão no GestorEduka; a Edukangola envia histórico e notificações. Após aprovação, o pagamento da propina ocorre **directamente ao centro**, segundo as instruções oficiais dele.

Esta fase evita transformar a Edukangola numa intermediária financeira transfronteiriça antes de haver contratos, reconciliação, suporte de reembolso e validação regulatória. A plataforma pode cobrar uma taxa de candidatura apenas se o contrato, a política pública e o fornecedor de pagamento forem definidos para esse mercado.

### Fase 2 — Multimoeda por entidade jurídica e por país

Adicionar uma configuração `MercadoPais` e `ConfiguracaoFinanceiraCentro`, em vez de campos globais dispersos:

| Configuração | Finalidade |
|---|---|
| País de operação e entidade contratante | Define que termos, imposto e suporte se aplicam. |
| Moeda de apresentação e de cobrança | Separa “preço informativo” de “moeda efectivamente cobrada”. |
| Gateway autorizado por país | Impede que um curso MZN/XOF seja enviado para um gateway não suportado. |
| Conta de liquidação e titular verificado | Permite repasse auditável ao centro. |
| Comissão e periodicidade de repasse | Define a economia por parceiro, país e moeda. |
| Política de reembolso e prazo de estorno | Dá previsibilidade ao aluno e ao centro. |
| Fuso horário e calendário local | Mantém turmas, início e notificações correctos. |

### Fase 3 — Cobrança local por mercado

Implementar **um mercado de cada vez**, depois de contrato, gateway com cobertura local, testes de sandbox/produção e revisão jurídica/contabilística. A ordem recomendada é: Angola → Portugal (EUR) → Moçambique (MZN) → Guiné-Bissau (XOF). Não começar com USD só porque o modelo já aceita USD; a moeda deve corresponder ao país, ao contrato e ao gateway escolhido.

## Alterações prioritárias no GestorEduka

1. Separar “centro nacional” e “centro internacional” por um tipo de operação, com campos de admissões, idiomas, políticas, instituição verificada e responsável.
2. Criar uma tabela administrável de países e moedas ISO. Evitar uma lista fixa no código quando a expansão começar.
3. Dar a cada filial país, cidade/região, fuso horário, moeda/preço local e dados fiscais próprios, quando a operação tiver várias jurisdições.
4. Tornar planos SaaS multimoeda: preço, moeda, país/espaço de vendas, impostos e gateway. Remover a suposição `KZ` do modelo e da interface.
5. Tornar relatórios financeiros multimoeda: bruto, comissão, líquido, moeda, taxa de câmbio se existir, estado de liquidação, referência bancária e comprovativo.
6. Manter os cursos em vídeo exclusivos da Edukangola: remover permissões de publicar vídeo dos planos de centros, impedir `centro` em novos cursos de vídeo e corrigir colecções públicas antigas de “parceiros”.
7. Evoluir candidatura externa: estados detalhados, documentos configuráveis, autorização de acesso, data de expiração, carta de aceitação e notificações.

## Decisão para o lançamento de 25 de Agosto

No lançamento, comunicar apenas o que está operacional:

| Pode comunicar | Não deve comunicar ainda |
|---|---|
| Centros e cursos em Angola, em AOA, com pagamento local validado. | Pagamentos internacionais, conversão cambial ou repasses a centros estrangeiros. |
| Cursos em vídeo da Edukangola por subscrição mensal, depois de validar preço/plano e pagamento local. | Catálogo de vídeo aberto a centros parceiros ou cobrança de vídeo em EUR/USD/MZN/XOF. |
| Descoberta de centros estrangeiros e candidatura assistida, se os dados estiverem completos. | Garantia de visto, equivalência, alojamento, emprego ou aceitação académica. |
| GestorEduka para operação nacional. | Planos SaaS multimoeda e gestão financeira transfronteiriça. |
