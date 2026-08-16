# Proposta de fluxos públicos: acesso, inscrição e compra

## Decisão de produto recomendada

> **O aluno não deve precisar criar uma conta antes de se inscrever num curso presencial ou comprar um vídeo-curso.** A conta é criada ou associada pelo e-mail durante a operação e o aluno pode definir uma palavra-passe depois, para acompanhar o seu percurso.

Esta abordagem preserva o requisito de conversão simples da Edukangola. Ao mesmo tempo, evita que um aluno perca o acesso futuro à compra, porque cada operação fica associada a um e-mail confirmado e a uma área de aluno que pode ser ativada em seguida.

## O que o backend já suporta

| Área | O que já existe | Situação para o novo percurso |
|---|---|---|
| **Inscrição presencial** | Página de ficha, seleção de turma, nome, e-mail, telefone, valor a cobrar online e criação de inscrição pendente. | É uma boa base; deve ser exposta numa interface React mais curta e clara. |
| **Visitante sem conta** | Criação ou reutilização de aluno pelo e-mail durante a inscrição presencial. | Permite não exigir login; precisa de uma proteção adicional quando o e-mail já pertence a uma conta ativa. |
| **Pagamento** | Criação de pagamento Prontu, callback, histórico e ativação automática de inscrição após confirmação. | A regra é suficiente; devem melhorar-se os ecrãs anterior e posterior ao pagamento. |
| **Vídeo-curso gratuito** | Acesso imediato para aluno autenticado. | Deve aceitar visitante e criar/associar acesso sem login obrigatório. |
| **Vídeo-curso pago** | Criação de pagamento Prontu e libertação de acesso após o callback. | Deve deixar de depender de login prévio e receber uma página de compra própria. |
| **Login e cadastro** | Login por e-mail e palavra-passe; cadastro com verificação por código de e-mail; recuperação de palavra-passe. | Deve preservar o destino de retorno e eliminar ações visuais sem implementação. |

## Problemas que devem ser corrigidos antes do redesenho

| Ponto | Impacto no aluno | Correção proposta |
|---|---|---|
| O login diz “E-mail ou telemóvel”, mas o backend autentica apenas por e-mail. | Cria uma expectativa errada. | Mostrar apenas **E-mail**. |
| Google, SMS, seletor de idioma e “manter sessão” aparecem sem integração funcional. | Introduz falsas alternativas e dúvidas. | Remover até existirem integrações reais; implementar a sessão persistente apenas se for configurada no backend. |
| Cadastro não explica a verificação por e-mail. | O aluno pensa que a conta foi concluída antes da ativação. | Mostrar “Criar conta em 2 minutos” e indicar que será enviado um código de seis dígitos. |
| Cadastro e login não preservam o regresso ao curso escolhido. | O aluno pode perder a intenção de compra após autenticar. | Guardar `next`, curso e turma na sessão e voltar ao checkout correto. |
| Valores mostram casas decimais técnicas. | Reduz confiança no preço. | Mostrar sempre valores como `21 600 Kz` e separar “Paga agora” de “Paga depois”. |
| A ação “Confirmar e Avançar” é vaga. | O aluno não sabe se pagará ou só reservará uma vaga. | Usar texto que reflete a ação: `Reservar vaga e pagar 21 600 Kz` ou `Confirmar inscrição gratuita`. |
| A compra de vídeo-curso requer login antes de começar. | Aumenta abandono. | Criar uma iniciação de compra de visitante equivalente à inscrição presencial. |

## Percurso recomendado para cursos presenciais

| Passo | Ecrã e informação essencial | Ação principal |
|---|---|---|
| **1. Escolher turma** | Curso, centro, local, dias, horário, vagas e preço. O aluno escolhe uma turma. | `Continuar` |
| **2. Dados de contacto** | Apenas nome, e-mail e WhatsApp. Texto: “Não precisa criar conta agora.” Ligação discreta: “Já tem conta? Entrar”. | `Ver resumo` |
| **3. Rever e confirmar** | Turma escolhida, “Paga agora”, “Paga depois”, política de reserva e aviso de pagamento seguro. | `Reservar vaga e pagar X Kz` ou `Confirmar inscrição` |
| **4. Pagamento externo** | Checkout Prontu já existente. | `Pagar com segurança` |
| **5. Confirmação** | Estado claro: “Pagamento confirmado” ou “Pagamento pendente”; turma, próximo passo, comprovativo e botão para a área do aluno. | `Ver a minha inscrição` |

Para cursos sem cobrança no ato, o quarto passo não é apresentado. O aluno vê uma confirmação de vaga e a explicação exata de qualquer valor que terá de tratar diretamente com o centro.

## Percurso recomendado para vídeo-cursos

| Passo | Ecrã e informação essencial | Ação principal |
|---|---|---|
| **1. Acesso ao vídeo-curso** | Capa, número de aulas, origem (Edukangola ou centro), preço e indicação se existe acompanhamento por turma. | `Continuar para acesso` |
| **2. Dados essenciais** | Nome e e-mail, ou opção de entrar numa conta existente. Não solicitar turma para vídeo original. | `Ver resumo` |
| **3. Confirmar acesso** | `Paga agora: X Kz`; acesso imediato após confirmação; aulas incluídas. Para gratuito: “Acesso gratuito”. | `Pagar e desbloquear aulas` ou `Criar acesso gratuito` |
| **4. Confirmação** | “Acesso desbloqueado”, botão `Começar a primeira aula` e opção `Definir palavra-passe para gerir a conta`. | `Começar o curso` |

Um vídeo-curso de centro pode mostrar separadamente uma turma de acompanhamento. Essa informação deve ser explicada como benefício adicional e nunca confundida com uma turma obrigatória para assistir às aulas gravadas.

## Login, cadastro e recuperação de palavra-passe

| Página | Conteúdo final | Regra de continuidade |
|---|---|---|
| **Entrar** | E-mail, palavra-passe, recuperação e ligação para criar conta. | Depois de entrar, regressa ao curso, turma ou checkout que iniciou o fluxo. |
| **Criar conta** | Nome, e-mail, palavra-passe e confirmação; aviso claro de verificação de e-mail. | Mantém o destino pendente para regressar ao checkout após verificar. |
| **Verificar e-mail** | E-mail parcialmente oculto, campo de código de seis dígitos, reenviar código e trocar e-mail. | Ativa a conta, inicia sessão e conduz o aluno ao destino pendente. |
| **Recuperar palavra-passe** | E-mail, código e nova palavra-passe numa sequência curta. | No fim, regressa à entrada ou diretamente ao destino pendente. |

Se o visitante introduzir um e-mail associado a uma conta ativa durante a compra, não se deve criar uma segunda sessão com essa identidade. O sistema deve pedir que entre ou confirme um código enviado para aquele e-mail, mantendo o curso e a turma selecionados.

## Ordem de implementação recomendada

1. Corrigir o texto e as ações falsas das páginas atuais de login e cadastro, preservando `next` em todos os passos.
2. Criar páginas React de **checkout simplificado** para curso presencial e vídeo-curso, mantendo o Django como fonte das regras e do pagamento.
3. Criar no backend a iniciação de compra de vídeo-curso para visitante, com proteção para e-mails de contas existentes.
4. Criar as páginas de confirmação específicas para inscrição e compra, ligadas ao estado real do pagamento.
5. Testar os quatro cenários: presencial pago, presencial sem pagamento no ato, vídeo pago e vídeo gratuito.

## Critério de sucesso

O aluno deve compreender, antes de confirmar, **o que está a adquirir ou reservar**, **qual turma foi escolhida quando aplicável**, **quanto paga agora**, **o que fica para depois** e **qual será o próximo passo**. Nenhum botão da experiência pública deve sugerir uma funcionalidade que ainda não esteja disponível.
