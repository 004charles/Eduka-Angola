# Design — Index Web Eduka-Angola

A primeira entrega é a index pública em React. A página inspira-se na clareza de descoberta da Udemy, mas usa a identidade própria da Eduka-Angola: roxo `#651CF2`, superfícies brancas, tipografia editorial e foco em cursos de centros de formação em Angola. A index apresenta pesquisa, áreas, cursos, centros e o percurso simples de descoberta até à inscrição. O modo escuro preserva os mesmos contrastes e hierarquia.

## Fluxo da primeira fase

| Ação | Comportamento atual |
|---|---|
| Pesquisar | Mostra retorno de interface e será ligado ao catálogo Django na próxima fase. |
| Abrir categoria | Comunica a futura abertura de resultados reais. |
| Entrar ou criar conta | Comunica a futura integração de autenticação Django. |
| Explorar GestorEduka | Comunica que o onboarding de centros será ligado sem modificar o módulo existente. |

## Próximas páginas

Depois da index, serão implementadas a lista de cursos, detalhe do curso, perfil do centro, login e área do aluno. As regras de inscrição, pagamentos, turmas e matrículas permanecem no backend atual.
