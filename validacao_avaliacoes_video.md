# Validação visual — Avaliações em cursos em vídeo

No detalhe de um programa gratuito, o botão **Aceder gratuitamente** passou a usar o botão roxo, a altura, tipografia e o espaçamento da Edukangola, substituindo o estilo nativo do navegador observado anteriormente.

A nova área **Avaliações e comentários** aparece no conteúdo do curso com média, estrelas, contagem, distribuição por estrela, formulário condicionado ao progresso e mensagem de orientação quando o aluno ainda não iniciou o programa. A vista foi inspecionada no preview com um curso sem avaliações; por isso, a área mostrou correctamente a média vazia e o estado de acesso antes de aprendizagem.

O teste automatizado `core.test_video_reviews` confirmou dois cenários essenciais: um aluno com acesso mas sem progresso recebe bloqueio de avaliação; depois de iniciar uma aula, o aluno cria uma avaliação e pode actualizá-la sem gerar duplicados. O payload público passa a mostrar a nova média, a avaliação pessoal e a permissão de avaliação.
