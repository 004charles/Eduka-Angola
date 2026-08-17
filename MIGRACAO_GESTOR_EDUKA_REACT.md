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

## Estado actual da migração

O GestorEduka React dispõe de rota protegida, ecrã de acesso, identidade Edukangola, temas claro e escuro, painel com métricas reais e navegação para todos os módulos migrados. A gestão de cursos presenciais inclui criação, edição, publicação, remoção e auditoria. Também foram migrados turmas, presenças, notas, inscrições, matrícula manual, certificados presenciais, formadores, filiais, atribuição de cursos por filial, perfil institucional, logótipo, banner e galeria.

Na operação avançada, o painel React já cobre cursos em vídeo, aulas, certificados em vídeo, eventos, estágios, financeiro, analytics, conversas, comunicados, comentários, pesquisa de alunos, dossiê académico e transições controladas de matrículas. A assinatura apresenta plano, limites e permissões, e inicia o checkout Prontu apenas depois de uma acção explícita do gestor.

As APIs React usam sessão Django, CSRF em escritas, `get_gestor_context` e filtros por centro ou filial. Operações críticas, incluindo publicação, certificados, estado de matrícula, atribuição a filiais e comunicação, registam auditoria no Django.

## Validação e condição de remoção das rotas legadas

Foi executada validação técnica completa: `manage.py check`, a suite Django com 52 testes e a compilação de produção do frontend React. A validação com contas reais de gestor principal e de filial permanece pendente; só depois desse ensaio funcional as páginas HTML legadas devem deixar de ser a alternativa operacional ou ser removidas.
