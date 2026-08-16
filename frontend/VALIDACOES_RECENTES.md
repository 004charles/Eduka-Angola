# Validações recentes

- Em 15/08/2026, uma sessão autenticada de aluno foi reconhecida no cabeçalho React. Os botões **Entrar** e **Criar conta** foram substituídos por **Conta ativa — Aluno**.
- A ação de conta abriu corretamente a rota React `/aluno`, que apresentou os dados reais do aluno autenticado.
- Após recarregamento completo em 15/08/2026, a página inicial voltou a consultar a sessão sem cache e manteve apenas **Conta ativa — Aluno** no cabeçalho.
- O cabeçalho público foi recarregado em 15/08/2026 sem qualquer link ou botão para o GestorEduka; o acesso ao painel deixa de ser divulgado na Edukangola.
- A nova rota React `/centros/2` foi validada com um centro que possui cinco formações reais. A página mostrou capa institucional de fallback, identidade, contactos e cartões de formação com dados provenientes do Django.
- A listagem React `/centros` foi validada em 15/08/2026 e cada cartão encaminha para o novo perfil React correspondente, sem regressar à página Django antiga.
- A rota pública antiga `/cursos/centro/2/cursos/` passou a devolver um redirecionamento para `/centros/2/` e foi validada pelo navegador no perfil React do Centro Atlas Digital.
- O perfil expandido do Centro Atlas Digital foi validado em 15/08/2026: apresenta a ação **Seguir centro**, cinco formações presenciais e um vídeo-curso reais. Os blocos de galeria, eventos, equipa e novidades ficaram ocultos porque este centro ainda não publicou dados nesses registos, evitando conteúdo artificial.
- A API expandida devolve os blocos públicos institucionais, de multimédia e oportunidades definidos para o perfil. O endpoint de seguir centro foi confirmado como protegido: sem sessão autenticada devolve `401` e não altera os dados.
- O catálogo React foi validado com 22 produtos reais: mostra nove produtos na primeira página, o intervalo `1–9 de 22` e os controlos para as páginas 1, 2 e 3.
- A URL `/cursos?pagina=2` apresentou corretamente os produtos 10–18. Ao filtrar por vídeo-cursos nessa página, a URL passou para `/cursos?tipo=video`, sem o parâmetro de página, e apresentou os dois resultados correspondentes.
- O seletor de idiomas foi validado em 15/08/2026: ao escolher `EN`, o cabeçalho, ações globais, faixa de confiança, áreas de descoberta e rodapé da página inicial passaram para inglês sem alterar nomes e conteúdos publicados pelos centros.
- A opção `中文` foi validada na página inicial: navegação, carrossel institucional, faixa de confiança e áreas de descoberta foram apresentados em chinês simplificado, com uma pilha de fontes CJK aplicada à interface.
- O catálogo foi validado nos idiomas chinês e francês. Cabeçalho, filtros, mensagem de intervalo, controlos de paginação e rodapé atualizaram sem modificar títulos, preços, categorias e demais dados publicados pelos centros.
- A página “Como funciona” foi validada integralmente em francês. Após recarregamento, o idioma francês permaneceu ativo, confirmando a persistência da preferência no navegador.
