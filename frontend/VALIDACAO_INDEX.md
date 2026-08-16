# Validação da Index Web

A index React foi aberta no domínio temporário e renderizou corretamente em desktop. A página apresenta uma navegação superior, pesquisa em destaque, categorias, cartões de cursos de pré-visualização, área para centros de formação, explicação do percurso de inscrição e rodapé.

A composição usa fundo branco, roxo da marca Eduka-Angola e contraste claro entre blocos. Os conteúdos de cursos estão identificados na interface como pré-visualização até que a integração com o backend Django seja implementada. A próxima validação cobre os controlos de tema e de pesquisa, seguidos de uma revisão em largura reduzida.

## Interações validadas

O controlo de tema alterna corretamente entre o modo claro de fundo branco e o modo escuro, mantendo contraste nos textos, cartões, pesquisa e navegação. A pesquisa aceita termos como “Informática” e apresenta uma confirmação explícita de que os resultados reais serão ligados ao catálogo Django na fase seguinte, evitando um botão sem resposta.

Também foi executada a compilação de produção com sucesso através de `pnpm build`. A verificação do código não encontrou referências a React Native ou Expo no novo frontend web.

## Atualização de experiência — carrossel e cartões

Foi introduzido o componente reutilizável `CourseCard`, que fixa a largura, a altura, a área visual, a hierarquia de texto e o rodapé de cada cartão de curso. A index passou a utilizar um carrossel horizontal que mostra mais formações por área visível, pode ser controlado por setas e indicadores, pausa ao passar o rato e respeita a preferência de redução de movimento.

A revisão visual confirmou, em modo escuro, os cartões mais compactos e consistentes, o movimento horizontal do carrossel, a nova secção de objetivos de aprendizagem e a secção que explica as informações disponíveis antes da inscrição. A atualização foi compilada com sucesso.

As setas do carrossel foram acionadas no navegador e o trilho avançou entre as formações apresentadas. O seletor de tema continua disponível na navegação superior, preservando a preferência do utilizador entre visitas.

Foi também realizada uma verificação técnica do estado de tema guardado no navegador durante a validação do seletor.

O estado foi alterado com sucesso para modo claro e voltou a ser refletido tanto no atributo visual da página como na preferência guardada no navegador. A revisão visual posterior confirmou o contraste da atualização no tema claro.

## Correção de navegação do carrossel

O mecanismo anterior usava uma instrução que podia reposicionar também o documento ao procurar tornar um cartão visível. A navegação foi alterada para atualizar apenas a posição horizontal do elemento que contém os cartões.

A validação automática definiu uma posição vertical de referência na página, acionou a seta de avanço e confirmou que a posição vertical permaneceu igual. Em paralelo, o trilho de cursos passou a ter deslocamento horizontal positivo, comprovando que apenas os cartões foram movidos.

## Coleções temáticas de cursos

Com base nas referências de descoberta analisadas, a index passou a apresentar cinco prateleiras de cursos: formações para explorar, tecnologia, novos cursos, gestão e negócios, e idiomas e comunicação. Cada prateleira utiliza o mesmo cartão, tem controlos próprios e mantém o seu trilho horizontal independente.

A compilação da aplicação com o novo componente `CourseShelf` terminou sem erros. A página passou a ter mais profundidade de catálogo sem alterar a navegação principal nem o GestorEduka.

Foram abertas no navegador as coleções de novos cursos e gestão e negócios, com os cartões uniformes e controlos próprios. A interação numa coleção não reposicionou a página e não alterou os outros carrosséis.

## Secções orientadas à decisão do aluno

Foi validado o endpoint público Django que fornece cursos, turmas abertas, localização, vagas, condições de pagamento e centros com cursos publicados. Na interface React, a secção de próximas turmas apresentou as três turmas reais abertas para Informática Básica Demo, com datas, horários, salas, vagas e indicação correta de inscrição gratuita.

O seletor de província foi testado com **Luanda** e apresentou apenas o curso efetivamente publicado nessa localização. O centro publicado foi apresentado sem selo de verificação, pois o respetivo perfil não se encontra verificado. A compilação do frontend concluiu sem erros após a integração.

## Simplificação solicitada

A secção de cursos publicados por província foi removida integralmente da página inicial, incluindo seletor, resultados e estilos associados. A página foi recompilada com sucesso e validada no navegador: depois das turmas abertas, a navegação passa diretamente para os centros em destaque e para o resumo do processo de inscrição.

## Espaçamento entre secções

Após esclarecimento, a primeira prateleira voltou a ser uma secção independente. Foi preservada uma linha de separação e aplicado um espaço visual reforçado antes de “Formações para explorar agora”, sem fundir o seu conteúdo com o resumo do processo de inscrição. A compilação de produção voltou a concluir sem erros.

## Ecrã de carregamento

Foi adicionado um ecrã de carregamento em página inteira com o símbolo e o nome Eduka-Angola centralizados, uma barra de progresso discreta e suporte a tema claro e escuro. A página mantém esse ecrã durante a preparação inicial e até os dados públicos responderem, com um intervalo mínimo breve para evitar uma transição brusca. A compilação terminou sem erros e não foram observados erros no navegador depois da transição para a index.

## Grafia da marca

A grafia visível da marca foi corrigida para **Edukangola** na navegação, no rodapé, no ecrã de carregamento, nos textos institucionais, no título da página e na descrição de metadados. A interface também normaliza a grafia anterior quando ela é recebida nos nomes de centros pela API, sem modificar os dados de origem no Django. A validação no navegador confirmou o resultado.

## Catálogo público real

A primeira prateleira de cursos passou a receber apenas cursos publicados pelo endpoint público Django. Na validação atual, o catálogo apresentou Informática Básica Demo, com imagem, modalidade, centro, ligação ao detalhe e a próxima turma aberta. O campo de pesquisa recebeu o termo “Informática” para validar a filtragem sobre os dados publicados.

A pesquisa foi submetida e deslocou a página para o catálogo, onde apresentou “Resultados para “Informática”” com um curso encontrado: Informática Básica Demo. A informação apresentada correspondeu ao catálogo público e não a cartões de demonstração.

Para validar o estado vazio, foi inserido de forma determinística o termo “Francês”, que não possui cursos publicados no catálogo atual, e a pesquisa foi submetida.

O estado vazio foi apresentado corretamente com o título “Nenhum curso encontrado” e a indicação de que não existem cursos publicados para “Francês”. Assim, a pesquisa da index responde tanto a resultados reais como a consultas sem correspondência, sem preencher a interface com dados fictícios.

## Navegação por páginas públicas

Foram validadas as novas páginas próprias de cursos e centros. A rota `/cursos?q=Informática` apresentou o catálogo real, o resultado correspondente e o link do curso para o detalhe Django. A rota `/centros` apresentou o centro publicado e os destinos para o perfil e para o diretório completo da versão Django.

A rota `/como-funciona` passou a conter a explicação completa do percurso de descoberta, inscrição, pagamento e confirmação. A ação “Explorar cursos publicados” foi testada e encaminhou corretamente para a rota React `/cursos`.

A index foi revista depois da separação: mantém a pesquisa, as áreas de interesse, uma prévia curta do catálogo real e dois encaminhamentos para os centros e para o processo de inscrição. As explicações extensas e as listagens completas foram deslocadas para páginas próprias.

## Catálogo filtrável

O catálogo React foi validado com a sua nova estrutura de barra de refinamento, distinta da página Django anterior. A página apresentou opções reais de categoria, modalidade, província, pagamento, turma aberta e ordenação. O filtro “Com pagamento no ato” produziu zero resultados para o curso atual, que possui inscrição gratuita, e a página apresentou corretamente o estado vazio e a ação para ver todos os cursos.

A ação “Limpar filtros” foi testada e restaurou o curso publicado, a contagem de resultados e a rota limpa `/cursos`.

## Filtros laterais

O catálogo foi reorganizado com o painel de filtros no lado esquerdo e a grelha de resultados ao lado direito. O painel mantém a pesquisa, categorias, modalidade, província, pagamento, turma aberta e a limpeza de filtros. A opção “Com turma aberta” foi acionada no painel lateral e preservou o curso publicado, que possui turmas abertas.

## Opções de modalidade

O seletor de modalidade passou a apresentar as três modalidades válidas no Django: **Presencial**, **Online** e **Híbrido**, mesmo quando não há cursos publicados em todas elas. A validação no navegador confirmou as três opções visíveis.

## Pesquisa rápida na barra superior

O ícone de pesquisa foi validado na navegação principal. Ao ser selecionado, abriu um painel de pesquisa rápida sobreposto à página, com foco automático no campo de texto, sugestão baseada no catálogo real e indicação da tecla Esc para fechar.

A pesquisa rápida foi submetida com o termo “Informática” e encaminhou corretamente para `/cursos?q=Informática`, onde o catálogo apresentou o curso real correspondente. O painel também foi aberto com sucesso diretamente a partir da página de resultados.

A tecla Esc foi usada com o painel aberto e fechou corretamente a pesquisa rápida, mantendo os resultados do catálogo visíveis.

## Cabeçalho com pesquisa permanente

O cabeçalho foi validado em desktop com os links Explorar, Centros e Como funciona, uma pesquisa central sempre visível e ações para centros, GestorEduka, tema, acesso e criação de conta. A pesquisa do cabeçalho foi submetida com “Informática” e encaminhou corretamente para os resultados reais do catálogo em `/cursos?q=Informática`.

## Cabeçalho simplificado

Conforme solicitado, o campo de pesquisa permanente foi retirado do cabeçalho. O ícone de pesquisa permaneceu visível e foi testado: abre corretamente o painel de pesquisa rápida já validado, sem afetar os links e ações restantes do cabeçalho.

## Carrossel de campanhas

Foi validada no topo da index uma área de campanhas em carrossel com uma campanha Edukangola, uma campanha para centros e um espaço explicitamente identificado para parceiros futuros. A ação de avançar mudou corretamente para o cartão de parceria. O carrossel inclui indicadores, avanço automático pausável e pausa ao passar o rato, respeitando a preferência de redução de movimento.

## Topo simplificado

O hero de apresentação com texto e fotografia foi removido para evitar duplicação com as campanhas. Os cards promocionais no topo foram reduzidos em altura, tamanho de títulos, arte e controlos. A index passa do carrossel compacto diretamente para a faixa de confiança, áreas de formação e cursos publicados.

## Pré-visualização de cursos

Na index, a passagem do rato sobre o cartão de **Informática Básica Demo** abriu um painel lateral de pré-visualização. O painel mostrou apenas dados publicados pelo Django: descrição curta, 40 horas, nível Básico, idioma Português, próxima turma, horário, vagas, local, condição de inscrição e certificado. A prévia apresentou também uma ação para o detalhe e as turmas do curso.

O foco no link do título abriu a mesma prévia, assegurando o acesso por teclado. O componente limita a pré-visualização a dispositivos com rato ou trackpad; em ecrãs tácteis o cartão conserva o acesso direto ao detalhe completo, sem introduzir uma interação que dependa de passagem do rato.

O catálogo React reutiliza o mesmo componente de cartão; a verificação técnica confirmou o cartão publicado na grelha, com o mesmo destino de detalhe e os mesmos dados públicos de turma associados.

Com o cartão do catálogo visível em desktop, a passagem do rato abriu a mesma prévia lateral sem esconder os filtros nem alterar a grelha. A ação “Ver curso e turmas” continua a encaminhar para o detalhe Django existente.

## Descoberta por competências

A index recebeu uma secção de descoberta por competências, colocada depois das áreas de formação. A secção apresenta o título, uma explicação concisa, um acesso ao catálogo completo e separadores gerados pelas categorias efetivamente publicadas. Na validação atual, os separadores **Todos os cursos** e **Tecnologia** apresentam Informática Básica Demo, único curso publicado no catálogo.

O separador Tecnologia foi acionado e atualizou tanto o subtexto da prateleira como o destino do acesso ao catálogo para a categoria correspondente. A verificação de acessibilidade confirmou que o separador ativo comunica `aria-selected="true"`; todos os controlos são botões nativos e permanecem operáveis por teclado. Em largura reduzida, os separadores passam a ter deslocamento horizontal para não truncar temas futuros.

## Catálogo demonstrativo

Foi carregado um catálogo idempotente de **20 cursos publicados**, cada um com uma turma futura aberta, informações de inscrição, descrição, duração, modalidade, nível, idioma, centro e capa local. As cinco categorias públicas são **Tecnologia e Dados**, **Gestão e Negócios**, **Idiomas e Comunicação**, **Design e Criatividade** e **Saúde e Bem-estar**. A resposta pública foi validada com 20 turmas e cinco categorias distintas.

As capas são servidas pelo Django em `/media/` e o frontend React passou a encaminhar essa rota, permitindo que os cartões sejam apresentados com imagens reais no carrossel de competências. A revisão visual confirmou os cinco separadores e os cursos exibidos com capas, centro, modalidade e data de início.

## Prateleiras de descoberta na index

Com base no padrão da Udemy de combinar tópicos populares e em tendência em coleções navegáveis [1], a index passou a ter prateleiras de cursos além da descoberta por competências: **Em destaque**, **Novas formações**, **Comece em breve**, as cinco coleções por categoria e **Inscrição gratuita**. Todas reutilizam o cartão canónico, os controlos horizontais independentes e as informações reais do catálogo Django.

A validação confirmou a presença das coleções de destaques, recência, turmas próximas e inscrição gratuita, bem como as cinco áreas de formação. Cada prateleira mostra apenas cursos que cumprem o seu critério real e mantém uma ligação ao catálogo completo.

## Densidade entre prateleiras

O espaçamento vertical de cada prateleira foi reduzido de 54 px para 34 px em desktop e de 48 px para 32 px em largura reduzida. A primeira coleção após a descoberta por competências também foi compactada, mantendo uma separação visual ligeiramente superior para sinalizar a transição de conteúdo.

## Indicador de vídeo

Os cartões de cursos **Online** e **Híbrido** passaram a mostrar um ícone de vídeo no canto inferior direito da respetiva capa. A validação visual confirmou o ícone nos cursos online e híbridos, incluindo *Bem-estar e Saúde Mental no Trabalho* e *Cuidados ao Idoso*, enquanto o cartão presencial de *Primeiros Socorros e Suporte Básico de Vida* mantém apenas a etiqueta de modalidade.

## Detalhe de curso React

Foi adicionada a rota `/cursos/:id`. A validação de **Fundamentos de Informática** confirmou a apresentação da descrição, carga horária, nível, idioma, modalidade, certificado, centro, localização, turma, vagas, dias, horário, sala, condição de inscrição e ação para a ficha Django existente. A validação de **Segurança Digital para Equipas** confirmou o indicador **Inclui vídeo**, a modalidade online e a condição de inscrição gratuita.

Os dois botões de inscrição encaminham para a ficha de inscrição Django do curso, mantendo o fluxo operacional já existente e deixando a seleção da turma explícita antes da candidatura.

## Recomendações no detalhe

No fim da página de detalhe foi adicionada a prateleira **Também pode gostar**. A seleção começa por cursos da mesma categoria, continua por formações do mesmo centro e só depois completa a coleção com outros cursos publicados, sempre excluindo o curso que o aluno está a consultar.

Na validação de *Segurança Digital para Equipas*, a prateleira apresentou primeiro **Excel e Power BI para Gestão**, **Python Aplicado a Dados** e **Fundamentos de Informática**, da área Tecnologia e Dados, antes de sugerir cursos adicionais do catálogo. A secção está posicionada entre os dados do centro e o rodapé, com navegação horizontal e rotas React para os cursos recomendados.

## Currículo de vídeo-cursos

O frontend passou a diferenciar um curso regular com modalidade online de um **vídeo-curso** do modelo `Curso_video`. Apenas vídeo-cursos reais recebem o ícone de vídeo e a rota `/video-cursos/:slug`; essa rota consulta `/api/public/video-cursos/<slug>/` e apresenta a lista real de aulas, respetiva ordem, duração, descrição e indicação de exercício.

A verificação do backend encontrou **zero vídeo-cursos publicados** no ambiente atual. Ainda assim, o endpoint público foi validado e já devolve a coleção `video_cursos`; quando o primeiro vídeo-curso com aulas for publicado no Gestor/Backend, ele aparecerá no catálogo e o respetivo detalhe exibirá o currículo automaticamente. Cursos online regulares continuam a apresentar turmas e não são apresentados como vídeo-cursos.

## Turmas por origem de vídeo-curso

A regra de negócio foi separada explicitamente. Um vídeo-curso com `is_original_edukangola=true` não aceita turmas: o detalhe comunica que é estudado ao ritmo do aluno, sem horários ou vagas. Um vídeo-curso publicado por um centro pode usar a nova estrutura `TurmaVideo`, com início, turno, dias, horários, vagas e estado de abertura.

O endpoint público devolve `is_original_edukangola`, `tem_turmas`, `origem_label` e, para cursos de centros, as turmas abertas. O detalhe React mostra uma secção de acompanhamento por turmas apenas nessa segunda situação. A migração `cursovideoapp.0019_turmavideo` foi aplicada, a compilação React terminou sem erros e a verificação Django reportou zero problemas.

## Compra e currículo de vídeo-cursos

Foram carregados dois vídeo-cursos demonstrativos reais no backend, ambos com quatro aulas: *Excel para o Dia a Dia* como original Edukangola e *Marketing Digital com Mentoria* como vídeo-curso de centro. A pré-visualização dos cartões usa agora **Comprar vídeo-curso** para conteúdos pagos e **Aceder gratuitamente** quando `is_gratuito=true`, em vez de referir inscrição ou turmas.

A validação do original confirmou a compra de **15 000 Kz**, quatro aulas com duração e descrição, e a ausência de turma. A validação do curso do centro confirmou a compra de **22 000 Kz**, quatro aulas reais e a turma de acompanhamento aberta, com 24 vagas. O botão comercial encaminha para a rota de compra já existente do backend (`/curso_video/<slug>/inscrever/`).

## Produtos separados no catálogo

A navegação passou a distinguir explicitamente dois grupos. **Formações com turma** compreendem cursos presenciais, online e híbridos, com início, horários, vagas e inscrição. **Vídeo-cursos** usam compra ou acesso gratuito, aulas gravadas e estudo ao ritmo do aluno; apenas os publicados por centros podem adicionar uma turma de acompanhamento.

O catálogo recebeu o filtro de produto. Ao selecionar Vídeo-cursos, ficam visíveis apenas os filtros de área e pagamento; modalidade, província e disponibilidade de turma deixam de aparecer. Ao selecionar Formações com turma, os filtros de modalidade, província e turma aberta permanecem disponíveis. A validação confirmou dois vídeo-cursos de dois e oito formações online de vinte, sem mistura entre os resultados. Os cartões mostram `Vídeo-curso` e o ícone de vídeo apenas para esse produto; as outras formações mostram `Presencial com turma`, `Online com turma` ou `Híbrido com turma`.

## Oferta final: cursos presenciais e vídeo-cursos

A taxonomia pública foi consolidada em dois produtos. As formações dos centros expostas na React são exclusivamente **presenciais**, utilizam turmas, horários, vagas e condições de inscrição; os **vídeo-cursos** permanecem num produto próprio, podendo ser originais da Edukangola ou publicados por centros com acompanhamento quando aplicável. As modalidades `ONLINE` e `HIBRIDO` continuam disponíveis exclusivamente na gestão interna do GestorEduka, mas são excluídas do endpoint público React. Os dados demonstrativos foram normalizados para `PRESENCIAL` pela migração `cursos_app.0031_simplificar_modalidade_presencial`; a migração `cursos_app.0032_restaurar_modalidades_internas` repõe as opções internas sem voltar a expô-las ao aluno.

O carregamento do catálogo demonstrativo foi repetido após a migração e confirmou 20 cursos presenciais, 23 turmas abertas, cinco categorias e dois vídeo-cursos. A compilação final com `pnpm build` e a verificação Django com `manage.py check` concluíram sem erros. No navegador, `/cursos?tipo=formacao` apresentou apenas cursos com a etiqueta **Presencial com turma**, enquanto `/cursos?tipo=video` apresentou apenas os dois vídeo-cursos, com compra e origem bem identificadas. O filtro de modalidade foi removido, pois deixou de ter utilidade na oferta pública.

## Referências

[1] [Udemy — Popular and trending topics](https://www.udemy.com/featured-topics/)
