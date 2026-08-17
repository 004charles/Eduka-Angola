# Arquitectura do Edukangola Learning Core

## Princípio

O **GestorEduka** continua a ser o backoffice operacional dos centros: administração do centro, publicação e revisão de conteúdos, gestão financeira, instrutores, turmas, presenças e configurações internas. O **React Learning Core** é a experiência de consumo e aprendizagem do aluno e uma camada pequena, orientada a tarefas, para o formador.

O React não deve copiar cada ecrã administrativo. Deve consumir contratos JSON do Django e apresentar uma experiência consistente, responsiva e centrada na aprendizagem.

## Fronteiras

| Domínio | Sistema principal | React deve fazer |
|---|---|---|
| Identidade do aluno | Django + sessão | Login, conta, preferências, segurança e estado da sessão |
| Catálogo público | Django + React | Descoberta, comparação, detalhe e compra/inscrição |
| Sala de aprendizagem | Django APIs + React | Aulas, progresso, materiais, notas, dúvidas, exercícios e continuidade |
| Avaliação | Django como fonte de verdade | Responder, submeter, ver resultados e feedback |
| Certificação | Django como fonte de verdade | Consultar, descarregar, partilhar e validar |
| Gestão completa do centro | GestorEduka | Não duplicar no React nesta fase |
| Acções rápidas do formador | APIs Django + React | Responder dúvidas, ver progresso e corrigir actividades atribuídas |
| Percursos e competências | Nova camada de domínio Django + React | Construir depois do núcleo de aprendizagem |
| Estágios e bolsas | Django + React | Descoberta, candidatura e acompanhamento do aluno |

## Primeiro marco: Learning Core do aluno

O primeiro marco deve consolidar a rota já existente `/aprender/video/:slug` e criar uma área académica coerente. O aluno deve conseguir abrir uma formação, seguir o programa, concluir aulas, guardar notas, enviar dúvidas, responder exercícios, ver materiais, acompanhar a percentagem e emitir o certificado elegível.

Não serão criados novos modelos para funções que já têm modelos equivalentes. Antes de cada novo endpoint, será verificado se os modelos `Aula`, `ProgressoAula`, `NotaAula`, `ComentarioAula`, `Exercicio`, `ResultadoExercicio`, `MaterialAula` e `Certificado` já cobrem o caso.

## Segundo marco: formador sem duplicar o gestor

A camada React do formador será deliberadamente pequena. O formador poderá consultar as suas turmas ou cursos, responder a dúvidas, rever exercícios e acompanhar alunos em risco. Criar cursos, gerir preços, publicar, gerir pagamentos e alterar a estrutura administrativa continuará no GestorEduka.

## Contratos e permissões

Cada API deve confirmar a sessão, o papel do utilizador e a relação com o curso ou turma. O aluno só pode ler e alterar o seu próprio progresso, notas e respostas. O formador só pode ver alunos de cursos ou turmas a que está associado. O centro só pode gerir os seus próprios recursos.

## Critério de conclusão do primeiro marco

O fluxo será considerado concluído quando um aluno de teste conseguir, sem voltar a um template legado, entrar numa formação, assistir a uma aula, guardar uma nota, enviar uma dúvida, submeter um exercício, ver o resultado, concluir o curso e abrir o certificado verificável.
