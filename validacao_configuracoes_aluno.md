# Validação — Configurações do aluno

Data: 17 de agosto de 2026.

## Implementação validada

A rota React `/aluno/configuracoes` apresenta a identidade da conta autenticada e permite activar ou desactivar notificações na plataforma, resumo por e-mail, cursos, turmas, livros, eventos, continuidade de aprendizagem, calendário e feriados e resumo semanal.

O formulário consome o contrato autenticado `GET /auth/api/react/aluno/configuracoes/` e guarda as opções com `POST /auth/api/react/aluno/configuracoes/actualizar/`, com credenciais de sessão e token CSRF. A página foi também ligada pelo novo atalho **Configurações** na área do aluno.

## Evidências

| Verificação | Resultado |
|---|---|
| Compilação do frontend (`pnpm --dir frontend run build`) | Concluída sem erros |
| Verificação Django (`manage.py check`) | Sem problemas identificados |
| Carregamento autenticado da página | Dados da conta e nove controlos apresentados |
| Interacção | Uma preferência de novos cursos foi alternada e submetida pela interface |

> A compilação assinala apenas o aviso informativo de tamanho do bundle inicial do Vite; não afecta a construção nem a funcionalidade desta página.
