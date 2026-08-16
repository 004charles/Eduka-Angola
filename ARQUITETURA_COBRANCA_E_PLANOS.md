# Arquitetura de Cobrança e Planos — Eduka-Angola

## Objetivo

Este documento organiza a monetização do Eduka-Angola sem misturar o pagamento dos cursos pelos alunos com a subscrição do GestorEduka pelos centros. A definição oficial da plataforma prevê simultaneamente comissões sobre inscrições, mensalidade SaaS, gestão de bolsas, destaques premium e cursos EAD próprios. Portanto, a decisão não é eliminar um modelo em favor do outro, mas separar claramente cada fonte de receita e definir quando ela se aplica.

## Princípio central

> O aluno paga pela formação. O centro paga pelo software. A Eduka-Angola pode receber uma comissão apenas quando prestar o serviço de marketplace ou processamento financeiro acordado com o centro.

Os três fluxos devem possuir estados, documentos e regras próprias:

| Fluxo | Pagador | Beneficiário principal | Registo principal |
|---|---|---|---|
| Curso e inscrição | Aluno | Centro de formação | `Inscricao`, `Pagamento`, `Matricula`, `ParcelaMatricula` |
| Subscrição do GestorEduka | Centro | Eduka-Angola | `Plano`, `AssinaturaMembro`, `Pagamento` |
| Comissão/repasse | Centro ou marketplace | Eduka-Angola e centro | `ConfiguracaoPlataforma`, pagamento e relatório de repasse |

## 1. Subscrição SaaS do centro

A aplicação `planos` já representa este domínio. O modelo `Plano` deve continuar a ser o catálogo dos planos comerciais do GestorEduka, e `AssinaturaMembro` deve continuar a ligar cada centro ao seu plano.

Os planos devem vender principalmente capacidade operacional:

- número de alunos ativos;
- número de turmas;
- número de filiais;
- número de utilizadores do centro;
- gestão financeira e de parcelas;
- relatórios;
- emissão de certificados;
- integrações;
- cursos em vídeo, quando aplicável.

A visibilidade no marketplace — prioridade de pesquisa, destaque na página inicial e selo — deve ser tratada como benefício comercial separado dentro do plano ou como suplemento Premium claramente identificado.

### Estados mínimos da subscrição

```text
PENDENTE → ATIVO → EM_ATRASO → EXPIRADO
                 └→ CANCELADO
```

O código atual usa `ATIVO`, `EXPIRADO`, `CANCELADO` e `PENDENTE`. Esta nomenclatura deve ser preservada para evitar migrações desnecessárias; `EM_ATRASO` pode ser acrescentado numa melhoria posterior.

Cada pagamento mensal deve deixar histórico próprio, mesmo que continue ligado ao modelo geral `Pagamento`. No futuro, será necessário um registo de fatura ou período de cobrança com referência, vencimento, valor, desconto, estado e data de pagamento.

## 2. Pagamento do aluno pelo curso

O curso deve definir a sua própria política de cobrança, independente do plano do centro:

| Campo existente | Função |
|---|---|
| `preco` | Preço base ou preço total do curso. |
| `preco_inscricao` | Valor cobrado para reservar a inscrição, quando aplicável. |
| `mensalidade` | Valor de cada mensalidade, quando aplicável. |
| `tipo_cobranca_inscricao` | Define o que é cobrado no primeiro checkout. |
| `permite_parcelamento` | Indica se o curso aceita pagamento parcelado. |
| `max_parcelas` | Limita a quantidade de parcelas. |
| `ParcelaMatricula` | Controla vencimento, valor e estado de cada parcela. |

As opções atuais de cobrança online são adequadas como ponto de partida:

```text
APENAS_TAXA
TAXA_E_MENSALIDADE
CURSO_COMPLETO
```

Contudo, a descrição exibida ao aluno deve ser inequívoca. O checkout deve informar sempre o valor pago hoje, o saldo restante e as datas ou condições das cobranças futuras.

A inscrição do aluno sem conta deve criar uma candidatura ou inscrição provisória, iniciar o pagamento e criar/ativar a conta somente após a confirmação do email ou do pagamento. A matrícula apenas deve ficar ativa quando o pagamento exigido pelo centro estiver confirmado.

## 3. Comissão sobre inscrições e pagamentos

A definição oficial da plataforma prevê comissões sobre inscrições. Esta fonte de receita pode ser mantida, mas não deve ser confundida com a mensalidade SaaS.

A comissão deve aplicar-se apenas quando existir uma base comercial clara, por exemplo:

| Situação | Comissão recomendada |
|---|---|
| Aluno descobriu o curso no marketplace e pagou através da Eduka-Angola | Pode existir comissão acordada. |
| Centro usa o GestorEduka para registar uma inscrição presencial paga no balcão | Não aplicar automaticamente; depende do contrato. |
| Centro usa apenas o GestorEduka, sem marketplace nem gateway da plataforma | Cobrar apenas a subscrição SaaS. |
| Plataforma processa pagamento de mensalidade do aluno | Pode aplicar-se taxa transacional/comissão acordada. |
| Curso próprio EAD da Eduka-Angola | Possui regra comercial própria. |

O centro deve saber, antes de publicar o curso, qual é o método aplicado:

```text
Modelo SaaS apenas
SaaS + comissão sobre pagamentos online
SaaS + comissão sobre inscrições originadas no marketplace
Modelo personalizado Enterprise
```

O campo atual `metodo_precificacao` com `MARKUP` e `COMISSAO` pode ser preservado temporariamente, mas precisa de uma definição mais explícita. `MARKUP` altera o preço apresentado ao aluno; `COMISSAO` reduz o repasse ao centro. Essas duas opções não devem ser aplicadas silenciosamente.

## 4. Regra recomendada para a primeira versão comercial

Para lançar com segurança, a Eduka-Angola deve usar um modelo híbrido controlado:

1. **Mensalidade SaaS do centro** como receita recorrente principal.
2. **Comissão ou taxa de processamento** apenas nos pagamentos realmente intermediados pela Eduka-Angola, ou nos alunos efetivamente originados pelo marketplace, conforme contrato.
3. **Nenhuma comissão automática sobre pagamentos presenciais** apenas porque o centro utilizou o GestorEduka para lançar o recebimento.
4. **Preço do curso definido pelo centro**, com o valor líquido e a comissão apresentados antes da publicação.
5. **Planos de pagamento dos alunos separados dos planos do centro.**

Este modelo preserva a monetização prevista na definição oficial e evita penalizar os centros pelas inscrições que eles próprios captaram fora da plataforma.

## 5. Correções prioritárias antes de ampliar funcionalidades

A ordem técnica recomendada é:

### Fase A — Corrigir o fluxo atual

- usar `ATIVO` ao ativar uma assinatura paga;
- procurar o centro através de `centro__usuario`;
- corrigir o template para usar `data_fim`, `status` e `esta_ativa`;
- usar `timezone.now()` compatível com `DateTimeField`;
- impedir que uma filial altere a subscrição da sede;
- garantir idempotência no callback do gateway.

### Fase B — Criar planos reais e coerentes

- criar Inicial, Profissional e Enterprise;
- definir limites operacionais mensuráveis;
- separar benefícios de gestão dos benefícios de visibilidade;
- criar dados de demonstração apenas no ambiente de desenvolvimento;
- testar upgrade e downgrade sem apagar histórico.

### Fase C — Consolidar faturação

- manter `Pagamento` como registo transacional;
- adicionar histórico de períodos/faturas da subscrição;
- controlar vencimento e atraso;
- implementar renovação manual antes de renovação automática;
- gerar recibo ou comprovativo da subscrição;
- criar relatórios separados para SaaS, cursos, comissões e repasses.

### Fase D — Aplicar permissões por plano

Cada funcionalidade deve consultar o plano de forma centralizada. Não se deve usar apenas uma regra aproximada como “se o plano tiver preço maior que zero, permite 999 aulas”. A permissão deve ler diretamente os limites e flags configurados no plano.

Exemplo conceptual:

```text
pode_publicar_curso(centro)
pode_criar_inscricao_manual(centro)
pode_emitir_certificado(centro)
pode_publicar_video_curso(centro)
pode_adicionar_utilizador(centro)
pode_usar_relatorio_avancado(centro)
```

## Decisões que ficam pendentes

Antes de criar preços definitivos, a equipa deve decidir:

1. Quais funcionalidades entram no plano Inicial e no Profissional.
2. Se o destaque no marketplace está incluído ou é um suplemento.
3. Em que casos a comissão incide sobre inscrições presenciais.
4. Se a taxa de gateway é paga pelo centro, pelo aluno ou incorporada no preço.
5. Se a renovação será manual no primeiro lançamento.
6. Quais métodos de pagamento serão realmente suportados em Angola no lançamento.

## Conclusão

Os planos existentes não devem ser eliminados. Eles já representam a base do pilar SaaS do GestorEduka. O trabalho seguinte deve ser de organização e correção: separar os domínios financeiros, corrigir o callback de assinatura, configurar planos reais e tornar transparentes as regras de comissão e repasse.

A arquitetura final deve permitir que um centro tenha simultaneamente:

```text
Plano SaaS: Profissional
Pagamento do curso: 90.000 Kz em 3 parcelas
Comissão marketplace: aplicável apenas à origem Eduka-Angola
Recebimento presencial: registado no GestorEduka sem comissão automática
```

Dessa forma, o Eduka-Angola mantém as fontes de receita previstas oficialmente, mas o aluno, o centro e a própria plataforma passam a saber exatamente qual pagamento está a ser feito e porquê.
