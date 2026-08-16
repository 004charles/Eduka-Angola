# Auditoria do dashboard do aluno

## Estado atual observado

A área do aluno funciona e mostra a conta “Aluno Demo Eduka-Angola” com um curso inscrito. A navegação lateral contém Visão Geral, Concluídos, Favoritos, Certificados, Competências, Meus Cursos, Meu Perfil e Configurações.

## Problemas principais

A primeira impressão é a de um dashboard administrativo genérico, não a de uma área de aprendizagem. O topo usa uma fotografia grande e um banner alto, ocupando demasiado espaço antes de o aluno chegar aos cursos. O conteúdo principal começa com três cartões de contagem, mas não existe uma hierarquia clara para a ação mais importante: continuar o curso.

O cartão do curso não apresenta progresso real para cursos presenciais; o backend envia progresso zero e a página mostra apenas o cartão genérico do curso. Também não há uma secção dedicada a “Continuar a aprender”, próximas aulas, próxima turma, estado da inscrição, pagamentos ou recomendações.

A navegação lateral usa tabs e hashes para várias secções, o que torna a experiência menos previsível do que páginas dedicadas. As secções Concluídos, Certificados e Competências aparecem sobretudo como estados vazios e ocupam pouca utilidade na primeira visita.

## Direção recomendada

O novo dashboard deve começar por uma saudação compacta e uma ação principal “Continuar a aprender”. Em seguida deve mostrar o curso atual em destaque, com estado da inscrição, turma, próxima aula/turma, progresso e botão principal. Abaixo devem aparecer atalhos para Meus Cursos, Certificados, Favoritos e Perfil, além de uma secção de descoberta com cursos recomendados.

A experiência deve usar uma composição clara, com fundo neutro, cartões brancos, uma cor primária consistente, tipografia forte e responsividade mobile. O banner fotográfico alto pode ser substituído por um cabeçalho compacto para dar prioridade ao conteúdo de aprendizagem.


## Resultado após o redesenho

O dashboard foi validado com a conta `Aluno Demo Eduka-Angola`. A área agora começa com um cabeçalho compacto e uma saudação contextual, seguida da secção “Continue a aprender”. O curso “Informática Básica Demo” aparece como cartão principal com imagem, tipo de formação, estado “Inscrição ativa”, turma atual, centro, estado da inscrição e ações para ver o curso e descarregar o comprovativo.

A barra lateral foi simplificada para Visão geral, Meus cursos, Concluídos, Favoritos, Certificados e Competências, separando claramente a área de aprendizagem da área de conta. Foram adicionados cartões de estatísticas, biblioteca, descoberta de novos cursos, certificados, favoritos e competências.

A verificação Django passou sem erros, não existem migrações pendentes e o login da conta demo continua a funcionar com acesso HTTP 200 ao dashboard. O layout inclui regras responsivas para ecrãs pequenos e suporte para modo escuro.
