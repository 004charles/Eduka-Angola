# Centros estrangeiros e candidaturas para estudo no exterior

## Princípio do produto

A Edukangola deve ser uma **ponte de descoberta e candidatura**, não uma agência de vistos. O centro estrangeiro é a entidade que analisa documentos, aprova ou recusa a candidatura e emite a confirmação académica. A plataforma organiza o processo, guarda o histórico, notifica o aluno e torna o estado transparente.

> Uma aprovação na Edukangola significa apenas que o centro aceitou a candidatura académica. Não constitui garantia de visto, residência, emprego, equivalência de diploma ou financiamento.

## O que já existe

O modelo actual de centro já contém país, cidade, região, fuso horário, contacto e site. Portugal e Moçambique já estão entre os países suportados. Os cursos presenciais já possuem modalidade, idioma, requisitos, datas e preços em AOA, EUR ou USD.

Isto permite começar sem criar uma segunda plataforma: um centro estrangeiro continua a ser um **Centro de Formação**; apenas recebe atributos e regras adicionais de oferta internacional.

## Experiência do aluno

| Etapa | Experiência proposta |
|---|---|
| Descoberta | Filtro **Estudar no exterior**, país, cidade, modalidade, idioma, nível e orçamento indicativo. Cartão identificado como **Centro internacional**. |
| Detalhe do curso | País/cidade, início, duração, idioma, preço e moeda, requisitos, documentos esperados, prazo de candidatura e contacto do centro. |
| Candidatura | Formulário separado da inscrição local: dados do aluno, motivação, formação anterior e documentos solicitados pelo centro. |
| Análise | Estado claro: rascunho, enviada, em análise, documentação adicional, aprovada condicionalmente, aprovada, recusada ou desistida. |
| Decisão | O centro aprova/recusa no GestorEduka, com nota opcional e prazo de resposta. A Edukangola envia confirmação ao aluno. |
| Pós-aprovação | Acesso à carta/confirmação, instruções do centro, datas, contacto e próximos passos. Não prometer visto ou pagamento concluído sem confirmação externa. |

## MVP recomendado

### 1. Limite geográfico inicial

Começar por **Portugal e Moçambique**, onde há maior afinidade linguística e procura provável. Cabo Verde e Brasil podem entrar em seguida. Para países fora da lista actual, substituir a lista fixa por uma tabela de países ISO administrável, mas não bloquear o MVP por isso.

### 2. Dados adicionais do centro internacional

- Tipo de operação: local ou internacional.
- Verificação da instituição e selo **Centro internacional verificado**.
- País, cidade, fuso horário, endereço e contacto de admissões.
- Idiomas de atendimento.
- Se aceita candidaturas de alunos residentes no exterior.
- Políticas publicadas de propina, reembolso, alojamento e apoio ao estudante, quando aplicável.

### 3. Dados adicionais do curso internacional

- Local de realização e formato: presencial, online ou híbrido.
- Moeda da oferta e indicação clara de que custos são informativos até confirmação do centro.
- Prazo de candidatura, data de início e vagas.
- Lista configurável de documentos exigidos.
- Requisitos académicos/linguísticos e idade mínima, se definidos pelo centro.
- Campo de observação para custos que não são propina, como material ou taxa de candidatura.

### 4. Nova candidatura internacional

Criar uma entidade própria, em vez de reutilizar directamente a inscrição local.

| Campo essencial | Finalidade |
|---|---|
| Curso e aluno | Mantém a candidatura ligada ao programa e à conta. |
| Estado e datas | Dá transparência, prazo de resposta e auditoria. |
| Documentos | Permite ao centro pedir e rever ficheiros exigidos. |
| Decisão e nota privada | Regista aprovação, recusa ou pedido de complemento. |
| Confirmação do centro | Guarda referência/carta enviada pelo centro. |
| Próximo passo | Indica se o aluno deve contactar o centro, pagar directamente ou enviar documentos adicionais. |

### 5. Pagamento no MVP

Para a primeira versão internacional, a Edukangola **não deve cobrar a propina estrangeira automaticamente**. A plataforma pode cobrar apenas uma taxa de candidatura, se houver contrato claro, ou encaminhar o aluno para as instruções oficiais do centro após a aprovação. O pagamento transfronteiriço e o repasse a instituições estrangeiras entram numa fase posterior, depois de validar regras cambiais, contratos, reembolsos e suporte.

### 6. Notificações e transparência

Reutilizar o serviço de notificações para avisar quando uma candidatura é recebida, quando faltam documentos, quando o centro toma uma decisão e quando a confirmação fica disponível. Cada estado deve ter e-mail e notificação na plataforma, respeitando as preferências do aluno.

## Segurança e responsabilidade

Documentos de candidatura podem incluir informação sensível. Antes de os aceitar, o MVP deve definir armazenamento privado, permissões só para aluno/centro/Edukangola autorizado, limites de retenção, registo de acesso e opção de apagar candidatura desistida conforme a política de privacidade. Documentos de viagem não devem ser obrigatórios na primeira etapa, salvo se um centro verificado justificar essa exigência.

## Ordem de implementação

1. Adicionar filtros e selo internacional ao catálogo usando os campos de país já existentes.
2. Criar dados de admissões internacionais no centro e no curso.
3. Criar candidatura internacional, estados, documentos e decisões no GestorEduka.
4. Mostrar histórico e confirmação na área do aluno.
5. Ligar notificações de estados.
6. Só depois avaliar cobrança transfronteiriça e integrações de pagamento específicas.
