# Especificação do MVP de Cursos Presenciais

## 1. Objetivo

O MVP deve permitir que cada centro de formação publique e administre cursos presenciais através do GestorEduka. O centro será responsável por cadastrar formadores, atribuí-los aos cursos, abrir turmas, definir horários, gerir inscrições, confirmar matrículas, controlar o percurso académico e emitir certificados.

Os formadores serão registados como responsáveis pedagógicos, mas não terão um painel operacional próprio nesta primeira versão.

## 2. Regras principais

| Elemento | Regra |
|---|---|
| Centro de formação | É o responsável por todo o processo administrativo e académico. |
| Formador | É cadastrado pelo gestor do centro e pode ser atribuído a vários cursos. |
| Curso | Deve ter pelo menos um formador atribuído antes de ser publicado. |
| Turma | É uma edição concreta de um curso, com datas, horário geral, sala e capacidade. |
| Formador principal da turma | É opcional e serve apenas como referência geral. |
| Aluno | Escolhe um curso ou uma turma e submete a inscrição. |
| Gestor | Aprova inscrições, confirma pagamentos, gere alunos, presenças, notas e certificados. |
| Professor | Leciona no centro; não processa inscrições, pagamentos ou certificados no sistema. |

## 3. Relação entre as entidades

A relação entre formadores e cursos é de muitos-para-muitos. Um curso pode ter vários formadores e um formador pode lecionar vários cursos.

Um curso pode ter várias turmas. Cada turma pertence a um único curso e possui um horário geral. O formador principal da turma é opcional porque os formadores já estão associados ao curso.

```text
Centro
  ├── Formadores
  ├── Cursos
  │     ├── Formadores responsáveis
  │     └── Turmas
  │            ├── Alunos matriculados
  │            ├── Horário geral
  │            └── Formador principal opcional
  └── GestorEduka: inscrições, pagamentos, presenças, notas e certificados
```

## 4. Cadastro de formador

O gestor deve conseguir criar e editar formadores no GestorEduka. Os dados mínimos são:

- Nome completo.
- Email ou telefone.
- Área de especialização.
- Biografia ou descrição profissional.
- Estado ativo ou inativo.
- Centro e filial associada, quando aplicável.

Um formador inativo não deve aparecer para novas atribuições, mas deve continuar associado aos cursos históricos para preservar o registo académico.

## 5. Cadastro e publicação de curso

Ao criar ou editar um curso, o gestor deve selecionar um ou mais formadores responsáveis. A seleção deve ser feita exclusivamente dentro do GestorEduka.

O curso não pode ser publicado quando não possui formador atribuído. O sistema deve apresentar uma mensagem clara: “Atribua pelo menos um formador antes de publicar o curso.”

O curso deve conter, no mínimo, título, descrição, categoria, modalidade, duração, carga horária, preço ou indicação de gratuidade, regras de inscrição e informação sobre certificado.

## 6. Criação de turma

A turma deve ser criada pelo gestor a partir de um curso existente. Os dados mínimos são:

| Campo | Obrigatório |
|---|---|
| Curso | Sim |
| Nome da turma | Sim |
| Código interno | Sim ou gerado automaticamente |
| Data de início | Sim |
| Data de término | Sim |
| Turno | Sim |
| Horário de início | Sim |
| Horário de término | Sim |
| Dias da semana | Sim |
| Sala ou local | Recomendado |
| Número de vagas | Sim |
| Formador principal | Não |
| Observações | Não |

Na primeira versão, a turma terá um horário geral. Não será necessário criar uma entidade de sessão individual para cada aula.

## 7. Fluxo operacional

```text
Gestor cadastra formador
        ↓
Gestor cria curso
        ↓
Gestor atribui um ou vários formadores
        ↓
Gestor publica curso
        ↓
Gestor cria turma e define horário geral
        ↓
Aluno faz inscrição
        ↓
Gestor analisa e aprova
        ↓
Gestor confirma pagamento ou bolsa
        ↓
Matrícula é ativada
        ↓
Gestor acompanha turma, presenças e notas
        ↓
Gestor conclui turma e emite certificado
```

## 8. Estados principais

### Curso

`Rascunho → Publicado → Suspenso ou Arquivado`

### Turma

`Aberta → Em andamento → Concluída`

Também pode ser `Cancelada` quando não atingir o número mínimo de alunos ou por decisão do centro.

### Inscrição

`Pendente → Aprovada → Aguarda pagamento → Matriculada`

Estados alternativos: `Rejeitada`, `Documentos pendentes` e `Cancelada`.

### Certificado

`Não elegível → Elegível → Emitido → Revogado`, quando necessário.

## 9. Perfis e permissões

| Perfil | Permissões no MVP |
|---|---|
| Gestor do centro | Acesso completo aos cursos, formadores, turmas, alunos, pagamentos, presenças, notas e certificados. |
| Funcionário da secretaria | Inscrições, matrículas, pagamentos, documentos e comunicação com alunos, conforme permissão atribuída. |
| Formador | Sem painel operacional próprio nesta fase. A instituição coordena o trabalho presencialmente. |
| Aluno | Consulta cursos, inscrição, matrícula, horário, progresso, pagamentos e certificados. |
| Administrador Eduka | Gestão global dos centros, planos, suporte e configurações da plataforma. |

## 10. Critérios de aceitação

O MVP será considerado correto quando:

1. O gestor conseguir cadastrar um formador.
2. O gestor conseguir atribuir o mesmo formador a vários cursos.
3. O gestor conseguir atribuir vários formadores ao mesmo curso.
4. O sistema impedir a publicação de um curso sem formador.
5. O gestor conseguir criar uma turma para um curso publicado.
6. A turma permitir definir horário geral, dias, sala e capacidade.
7. O formador principal da turma puder ficar vazio.
8. O aluno conseguir inscrever-se numa turma.
9. O gestor conseguir aprovar a inscrição e confirmar a matrícula.
10. O fluxo não exigir login ou painel operacional do formador.

## 11. Fora do âmbito desta versão

Não fazem parte do primeiro MVP a atribuição obrigatória de formador por cada aula, o calendário individual de sessões, a substituição automática de professores, o lançamento de notas pelo próprio formador, o chat entre aluno e professor e a gestão avançada de conflitos de salas e horários.

Essas funcionalidades podem ser adicionadas depois de o fluxo básico de cursos, turmas, matrículas e gestão pelo centro estar estável.
