# Auditoria das páginas públicas — Centros e Detalhe do Curso

## Página de Centros de Formação

A rota pública é `/cursos/instituicoes/`. A página possui título, descrição, pesquisa por nome, select de província, sidebar de filtros, ordenação, grelha de centros, paginação e CTA para registar uma instituição.

No ambiente atual, a base contém um centro ativo. A página mostra “1 centros, escolas técnicas e institutos certificados” — deve ser corrigido para singular “1 centro” — e apresenta o Centro Demo Eduka-Angola com 1 curso e uma nota fixa de 4.8. A descrição do centro usa um fallback genérico de instituição certificada.

Os filtros “Tipo de instituição” e “Garantias & Benefícios” aparecem como checkboxes sem nomes no formulário e sem lógica correspondente na view. Na prática, parecem filtros visuais não funcionais. A ordenação “Mais relevantes” e “Melhor avaliados” também aparece como links, mas a view ainda não aplica `sort`.

O CTA “Registar o meu centro” aponta para `registro_instrutor`, que é provavelmente o fluxo de criação de instrutor, não necessariamente o registo de centro. Isto precisa de ser confirmado e corrigido.

## Página de detalhe do curso

A rota pública observada é `/cursos/curso/1/`. A página tem hero visual, breadcrumb, categoria, título, descrição, avaliação, número de alunos, centro, carga horária, idioma, certificado, conteúdo, instrutor/centro, avaliações e CTA de inscrição.

O problema central é que o aluno não vê no hero a informação operacional mais importante: próxima turma, data de início, horário, dias da semana, local, sala e vagas disponíveis. Esses dados existem no modelo `Turma`, mas não estão ligados ao contexto da view nem apresentados no template.

O sidebar mostra correctamente “Gratuito”, “Inscrição gratuita” e “0 Kz” para o curso demo, mas a página ainda não mostra a regra de cobrança dos cursos pagos com a mesma clareza que foi implementada nos formulários do GestorEduka. Também existe um CTA “Inscrever-se Agora”, mas o fluxo atual passa por `ficha_inscricao`, que ainda exige autenticação.

A página apresenta “Centro de Formação Verificado” como texto genérico e, no bloco do instrutor/centro, reutiliza métricas do curso para confiança institucional. O curso demo mostra 0 avaliações, o que é honesto; contudo, outros fallbacks do template precisam de ser revistos.

## Prioridades iniciais

1. Ligar a view do detalhe às turmas ativas e mostrar a próxima turma junto do CTA.
2. Mostrar data, horário, localização, vagas e condição de inscrição no primeiro ecrã.
3. Corrigir os filtros da lista de centros para serem funcionais ou removê-los até existirem campos/lógica reais.
4. Aplicar ordenação real por relevância e avaliações.
5. Remover notas e garantias fixas, usando apenas dados reais.
6. Corrigir o CTA de registo de centro para apontar ao fluxo correto.
7. Separar claramente reputação do centro de avaliação do curso.
8. Preparar a inscrição sem login obrigatório, mantendo a informação mínima do aluno.


## Validação visual após as correções — 14/08/2026

A página de Centros de Formação passou a apresentar 1 centro real, sem a nota fixa 4.8, sem a etiqueta genérica de parceiro oficial e com o CTA corrigido para “Falar com a equipa”. Os filtros de modalidade, verificação e parcelamento aparecem como controlos reais.

O detalhe do curso passou a mostrar honestamente que a turma demo está em andamento e que não existe, neste momento, uma turma aberta com vagas. O CTA apresenta “Sem Turmas Abertas” em vez de permitir uma inscrição impossível. A regra “Inscrição gratuita” e “A pagar agora: 0 Kz” está visível.

Ainda há um pequeno problema de apresentação no detalhe: alguns valores aparecem como códigos internos — “PRESENCIAL”, “PT” e “B” — em vez dos rótulos humanos “Presencial”, “Português” e o nome do nível. Estes valores devem ser trocados pelos métodos `get_*_display` do modelo na próxima correção.


## Validação das três turmas abertas — 14/08/2026

Foram abertas três novas turmas para “Informática Básica Demo”, mantendo a turma original em andamento:

| Turma | Início | Horário | Dias | Vagas | Sala |
|---|---|---|---|---:|---|
| Turma Demo — Tarde | 24/08/2026 | 14:00–16:00 | Segunda, Quarta e Sexta | 20 | Sala 2 |
| Turma Demo — Noite | 07/09/2026 | 18:00–20:00 | Terça e Quinta | 20 | Sala 3 |
| Turma Demo — Sábado | 05/09/2026 | 09:00–13:00 | Sábado | 18 | Sala 4 |

A página de detalhe mostra a próxima turma, que é a turma da tarde de 24/08/2026. A ficha pública mostra as três turmas abertas para seleção, sem exigir login, e pede apenas nome completo, email e telefone/WhatsApp. O botão mostra corretamente “Confirmar Inscrição Gratuita” porque o curso demo está configurado como gratuito.

Durante a validação no navegador, a sessão anterior de gestor inicialmente redirecionava para login; depois de terminar essa sessão, a ficha funcionou corretamente como visitante anónimo. O detalhe público também foi corrigido para exibir “20 vagas disponíveis” e o nome da sala sem duplicação.
