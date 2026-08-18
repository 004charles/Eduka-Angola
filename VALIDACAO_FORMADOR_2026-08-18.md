# Validação visual — entrada do formador

## Primeiro ciclo de verificação

No modo claro, a página `/formador` passou a mostrar uma estrutura de formulário completa: campos com largura total, rótulos, botão de acesso e um cartão com hierarquia visual própria.

No modo escuro, a primeira verificação revelou contraste insuficiente no título e fundos demasiado claros nos campos. Foram aplicadas regras explícitas para a superfície escura, tipografia, rótulos, campos e foco.

## Resultado final

O modo claro mantém cartão branco, campos com hierarquia nítida e acção primária roxa. No modo escuro, o cartão passa a usar uma superfície escura distinta, o título e rótulos têm contraste claro e os campos acompanham o tema sem fundos brancos. A compilação Vite terminou sem erros.

## Ajuste de composição

Por solicitação do utilizador, a composição de ecrãs largos deixa de centrar o formulário e passa a alinhá-lo à esquerda dentro da área de conteúdo. Em telemóveis, o cartão continua centrado para preservar a leitura e a utilização com uma mão.

## Candidatura a formador

A entrada apresenta agora a chamada “Candidate-se para ensinar”. Ao activá-la, o visitante vê o formulário React com nome, e-mail profissional, palavra-passe, confirmação, área de especialização e experiência de ensino. A página comunica que a candidatura é analisada antes da activação do acesso; a vitrina de cursos mantém-se à direita durante o preenchimento.

## Conta de demonstração

Foi criada uma conta de formador aprovada e foi confirmado o preenchimento do acesso React com as credenciais de demonstração. O passo seguinte é validar o carregamento autenticado do painel, incluindo o curso, a aula e a dúvida pendente preparados no cenário.

Na primeira tentativa pelo navegador, o formulário permaneceu visível após a submissão. A autenticação será agora diagnosticada antes de declarar a validação do painel concluída.

As credenciais foram verificadas directamente no Django e a palavra-passe de demonstração foi simplificada para um valor alfanumérico. O formulário recebeu a nova credencial para nova validação.

A segunda submissão no navegador também manteve a página de acesso visível. Será verificado o pedido exacto registado pela API para corrigir a transição autenticada, se necessário.

Foi identificado e corrigido o formato dos pedidos enviados pelo cliente React. A validação final autenticou Amélia Ventura e abriu o painel com um curso, uma aula, um aluno inscrito e uma dúvida pendente visíveis. A conta está pronta para demonstrar criação de curso, adição de aula e resposta ao aluno.
