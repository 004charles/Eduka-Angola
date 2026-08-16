# Design da nova página de perfil de centro

A página segue uma composição editorial de largura total, alinhada à identidade roxa da Edukangola. O topo é uma capa ampla fornecida pelo próprio centro; quando não houver capa, um fundo tipográfico em gradiente apresenta o nome sem inventar imagens. O logótipo sobrepõe a capa como assinatura institucional e o selo de verificação aparece apenas quando estiver registado no perfil.

O bloco de identidade reúne localização, modalidade, ano de fundação, número real de cursos publicados e contactos disponíveis. A ação principal é explorar os cursos do centro. Ligações externas, WhatsApp e website só aparecem quando existirem no GestorEduka.

O conteúdo abaixo usa uma navegação local por âncoras e quatro blocos: apresentação institucional, formações publicadas, formadores e galeria. O bloco “sobre” exibe missão, visão e valores somente quando os campos forem preenchidos. Formadores e imagens seguem a mesma regra, sem contagens nem cartões fictícios.

Em telas pequenas, a capa reduz de altura, a assinatura do centro passa para fluxo vertical e as ações de contacto ocupam toda a largura de forma acessível. Todas as interações conservam foco visível e evitam movimentos quando o utilizador reduz animações.

## Expansão pública

O cabeçalho passa a exibir a ação **Seguir centro** e o total real de seguidores. Para alunos autenticados, a ação usa o mecanismo de seguimento já existente; para visitantes, conduz ao login com retorno ao perfil. Não será criada uma função de mensagens públicas porque a conversa do GestorEduka é privada e ainda não tem um fluxo React equivalente.

Além das formações presenciais, o perfil incluirá blocos condicionais para cursos em vídeo, novidades, eventos, estágios abertos, vídeo de apresentação, reels públicos, certificações, diferenciais, áreas de formação, recursos/infraestruturas, equipa, depoimentos aprovados, parcerias ativas, filiais e galeria. Cada bloco só é mostrado quando o GestorEduka possui registos próprios e publicáveis; a ausência de conteúdo não será mascarada com elementos fictícios.
