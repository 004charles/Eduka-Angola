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
| Capas de cursos | O catálogo de cursos presenciais e a secção de cursos recentes apresentam miniaturas, categoria, preço, estado e acções administrativas em cada formação. |
| Auditoria visual | A biblioteca de cursos em vídeo e o bloco de certificados exigiam capas, hierarquia e cartões próprios; a lista de eventos necessitava de uma composição temporal e acções menos técnicas. |
| Áreas adicionais | Estágios mantêm uma leitura demasiado técnica em lista; comentários exigem cartões de feedback, leitura de avaliação, contexto do curso e acções de moderação bem agrupadas. |
| Cursos em vídeo | A biblioteca apresenta cartões com capa, categoria, descrição, aulas, alunos, preço e acesso às aulas; os certificados usam uma lista de conclusão com aluno, estado e controlo. |
| Comentários | A moderação apresenta cartões de feedback com aluno, curso, avaliação, data, visibilidade, resposta do centro e acções operacionais. |
| Eventos e estágios | Eventos usam uma agenda com data, local, tipo, destaque e acções; estágios apresentam cartões com modalidade, cidade, vagas, estado e edição. |
| Conversas | O atendimento apresenta um resumo de conversas activas, contactos recentes, histórico com autoria identificada e compositor de resposta do centro. |
| Validação visual do atendimento | A interface foi confirmada no domínio de desenvolvimento com selecção de conversa, bolhas de aluno e centro, contactos recentes e campo de resposta visíveis. |
| Envio de mensagem | Foi enviada uma resposta de teste à conversa de Carla Domingos; a mensagem foi persistida no histórico e tornou-se a prévia da conversa recente. |
| Logout do gestor | O botão Terminar sessão foi confirmado no cabeçalho; ao accioná-lo, a sessão foi encerrada e a rota retornou à tela React de acesso do GestorEduka. |
| Navegação com ícones | A sessão de demonstração foi preparada novamente para validar os ícones do menu lateral no painel autenticado. |
| Validação do menu | Todos os módulos exibem ícones à esquerda dos rótulos; a visão geral e os cursos presenciais foram abertos para confirmar o indicador activo por rota. |
| Comunicação aluno-centro | A área Mensagens do GestorEduka mostra contagem de não lidas no menu, lista de conversas e histórico de Bruno Miguel após a correcção do detalhe de conversa. |
| Mensagens React do aluno | As APIs cobertas por teste criam ou recuperam uma conversa por centro, enviam a mensagem do aluno, notificam o gestor, notificam o aluno na resposta e marcam ambas as notificações como lidas ao abrir o histórico. |
