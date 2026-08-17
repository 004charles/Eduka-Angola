# Migração do GestorEduka para React

## Objectivo

Substituir progressivamente a experiência HTML do GestorEduka por uma aplicação React integrada na Edukangola, mantendo o Django como fonte de verdade para autenticação, permissões, dados e operações críticas. A transição não expõe dados de outros centros: todas as APIs administrativas devem determinar o centro e, quando aplicável, a filial a partir da sessão autenticada.

## Inventário do Gestor legado

| Domínio | Fluxos actuais | Prioridade React |
|---|---|---|
| Acesso e contexto | Login, logout, centro, filial e assinatura | Crítica |
| Painel | Métricas, actividade e indicadores | Crítica |
| Cursos presenciais | Criar, editar, publicar, remover e visão geral | Crítica |
| Cursos em vídeo | Curso, aulas e certificados | Alta |
| Inscrições e alunos | Validação, matrícula, dossiê e certificados | Alta |
| Turmas | Turmas, presenças e notas | Alta |
| Perfil institucional | Dados, imagem, banner, galeria, equipa e depoimentos | Alta |
| Operação | Filiais, instrutores, eventos, estágios, anúncios e comentários | Média |
| Gestão avançada | Financeiro, assinatura, analytics e chat | Média |

## Arquitectura de transição

1. A rota React pública de gestão é `/gestoreduka/` e nunca usa o `PublicLayout` destinado aos alunos.
2. O backend é acedido somente sob `/backend/gestoreduka/api/react/`, preservando o proxy de desenvolvimento e evitando CORS.
3. As chamadas enviam o cookie de sessão existente e operações de escrita exigem token CSRF.
4. A API inicial de dashboard usa `get_gestor_context`, por isso uma conta só recebe cursos e métricas do seu próprio centro ou filial.
5. Rotas HTML legadas permanecem acessíveis temporariamente para fluxos ainda não migrados; serão retiradas do menu React à medida que cada módulo ganhar API e testes próprios.

## Estado da primeira fundação

O GestorEduka React já tem uma rota protegida, ecrã de acesso, identidade Edukangola, modo claro/escuro, métricas reais do centro, lista real de cursos e operação rápida de publicar ou retirar um curso. A validação sem sessão mostrou o ecrã de entrada React e a ligação ao login de gestor, sem expor dados administrativos.

## Próxima sequência de implementação

A fase seguinte cobre o CRUD React de cursos presenciais, turmas, inscrições e perfil do centro. Depois serão adicionados cursos em vídeo, alunos, financeiro, comunicação, equipa e conteúdos institucionais. Cada grupo deve ser validado com contas de centro e filial antes de a respectiva página HTML deixar de ser a alternativa operacional.
