# Validação do Centro Demonstração GestorEduka

## Dados de demonstração

O comando `python3 manage.py popular_centro_demo_gestor` criou um cenário idempotente no centro **Centro Demonstração GestorEduka**. O cenário contém seis cursos presenciais, cinco turmas, dez alunos, dez inscrições, seis matrículas, dois cursos em vídeo, três eventos, três estágios, três comunicados e três conversas.

## Verificações realizadas

| Área | Resultado |
|---|---|
| Alunos | A lista do GestorEduka apresenta os dez alunos do centro. |
| Dossiê académico | O dossiê de Ana Luísa Vieira abre com uma inscrição aceite, uma matrícula activa e as acções administrativas disponíveis. |
| Interface | A área de alunos e o modal do dossiê usam a nova composição académica, incluindo resumo de métricas, histórico de admissões e registo de matrícula. |
| Financeiro | O módulo apresenta 11 movimentos, incluindo pagamentos de plataforma e recebimentos presenciais, com totais e repartição por filial. |
| Cursos presenciais | O catálogo do centro apresenta seis cursos publicados, com acções de edição, publicação e remoção disponíveis. |
| Cursos em vídeo | A biblioteca do centro mostra dois cursos em vídeo, quatro aulas por curso, alunos inscritos e um certificado emitido. |
| Eventos | A agenda apresenta três eventos futuros com tipos, datas e locais distintos, todos com acções de edição e remoção. |
| Inscrições | A área de admissões apresenta dez inscrições com estados aceite, pendente, negada e cancelada, permitindo testar acções de aprovação e recusa. |
| Comentários | A moderação apresenta três avaliações de alunos, incluindo respostas publicadas e um comentário pendente para testar aprovação e resposta. |
| Estágios | O módulo apresenta três vagas com modalidades presencial e híbrida, localizações e vagas restantes. |
| Mensagens | O atendimento apresenta três conversas com histórico de mensagem do aluno e resposta do centro, incluindo o campo de envio operacional. |
