# Selecção de gateway europeu para a Edukangola

## Evidências iniciais

A Stripe indica suporte a empresas em Portugal e informa que, quando a plataforma está disponível no país/região da empresa, ela pode vender a clientes no mundo inteiro.[1] A Stripe Connect é a linha adequada quando uma plataforma cobra em nome de parceiros e precisa de gerir contas conectadas e repasses.

A Adyen apresenta uma oferta específica para plataformas com onboarding e verificação de utilizadores, pagamentos online/presenciais, divisão de fundos, transferência, repasses, reconciliação e gestão de risco.[2] Estas capacidades respondem ao modelo em que a Edukangola cobra de um aluno e depois liquida o valor devido a um centro.

| Fornecedor | Encaixe inicial | Observação |
|---|---|---|
| Stripe + Connect | Alto para começar em Portugal/EUR | É a opção técnica mais simples para a primeira integração, caso exista uma entidade elegível e conta empresarial portuguesa/europeia. |
| Adyen for Platforms | Alto para operação multi-centro madura | É forte para divisão/liquidação/KYC, mas tende a exigir uma operação comercial e de risco mais estruturada. |
| Mollie | Médio para cobrança simples em EUR | Está disponível para empresas sediadas no EEE, Reino Unido ou Suíça e requer IBAN/conta bancária do Reino Unido; deve ser analisada apenas se o modelo não exigir repasse integrado a vários centros.[3] |

## Referências

[1] [Stripe — disponibilidade global](https://stripe.com/global)

[2] [Adyen — Platforms](https://docs.adyen.com/platforms)

[3] [Mollie — elegibilidade por país](https://help.mollie.com/hc/en-us/articles/115002116105-Can-I-use-Mollie-s-services-in-my-country)

## Recomendação para a Edukangola

O melhor caminho para a primeira operação em Portugal é **Stripe + Stripe Connect**, desde que a Edukangola tenha uma entidade empresarial elegível e uma conta bancária europeia/portuguesa. A Stripe resolve a cobrança em EUR e o Connect é a peça desenhada para ligar contas de centros, reter a comissão da plataforma e preparar repasses sob regras verificáveis.

| Cenário Edukangola | Gateway recomendado | Motivo |
|---|---|---|
| Primeiro lançamento em Portugal, com poucos centros verificados | Stripe Payments; depois Stripe Connect | Menor complexidade inicial e caminho claro para evoluir para contas conectadas e repasses. |
| Marketplace europeu grande, com vários centros, divisão de fundos, KYC e reconciliação complexa | Adyen for Platforms | A documentação cobre directamente onboarding, verificação, divisão de pagamentos, repasses, risco e reconciliação.[2] |
| Centro único a vender uma formação própria em EUR, sem repasse integrado | Mollie | Boa alternativa europeia de cobrança simples, desde que a entidade esteja no EEE/Reino Unido/Suíça e tenha conta elegível.[3] |
| Cliente que insiste em carteira digital | PayPal como método complementar, não como núcleo | Pode ampliar a escolha do aluno, mas não deve ser a base de comissão e repasse a centros. |

Não é recomendado activar Stripe, Adyen ou Mollie apenas por adicionar uma chave técnica. Antes da integração, a Edukangola precisa definir a entidade que contrata o serviço, o país de registo, o IBAN de liquidação, a política de reembolso, a comissão, quem assume risco de fraude e se o centro será pago directamente ou através de uma conta conectada.

## Próximo passo recomendado

Começar por **Portugal/EUR** com uma oferta limitada de centros verificados. Primeiro, cobrar a taxa de candidatura ou o valor de um único parceiro; em seguida, depois de validar conciliação e reembolso, activar Stripe Connect para repasses a centros. A Adyen deve ser reavaliada quando a operação tiver volume, vários centros e necessidade efectiva de divisão de saldo e gestão de risco centralizada.
