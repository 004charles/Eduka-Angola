# Validação de descoberta e decisão de cursos

**Data:** 18 de agosto de 2026

## Pesquisa, filtros e comparação

A página pública `/cursos` apresentou os novos controlos de pesquisa unificada, modalidade, nível, preço, início e vagas. No ambiente actual, o catálogo presencial não devolveu cursos publicados, pelo que a interface mostrou correctamente o estado vazio sem cartões seleccionáveis.

A rota `/comparar-cursos?ids=1,2` apresentou o estado orientador para seleccionar dois ou três cursos. O estado é esperado porque os identificadores informados não correspondem ao catálogo actualmente devolvido pelo ambiente. A rota, a página e a navegação de retorno renderizaram sem erro.

Depois da correcção da rota legada dos cursos em vídeo, o catálogo público voltou a devolver 24 formações. Foram vistos no navegador os filtros avançados, as sugestões de pesquisa e a acção “Comparar”. A selecção de uma formação actualizou o estado para “Comparar 1 curso” e marcou o cartão como “Na comparação”, mantendo favoritos e pré-visualização activos.

## Comparação editorial

A comparação com os cursos 35, 32 e 34 foi revista após a recomposição visual. A página passou a apresentar uma matriz com cabeçalhos compactos de curso e linhas comuns para formato, investimento, próxima turma, vagas, local, confiança e acções. O resultado deixou de repetir cartões altos e mantém os dados comparáveis na mesma linha visual.

Depois do ajuste final, a matriz passou a ter uma separação vertical de 42px da introdução. A transição entre a nota de confiança e a comparação ficou visualmente distinta em ecrã largo, sem alterar a hierarquia de leitura.

Na revisão das faixas geográficas da página inicial, confirmou-se que não existiam centros nem cursos presenciais publicados fora de Angola. A secção internacional deixa, por isso, de ocupar espaço com um estado vazio e passa a surgir automaticamente quando houver dados publicados. A descoberta por proximidade mantém-se disponível, agora com os atalhos de província integrados junto do pedido de localização.

O pedido de localização foi revisto para ocorrer em duas etapas: primeiro, a página mostra uma janela central com finalidade, privacidade e as opções de aceitar ou recusar; só depois de “Permitir localização” é chamado o GPS do navegador. A recusa fecha a janela sem qualquer pedido de permissão ao navegador e mantém a descoberta por província disponível.

A janela central passa a abrir automaticamente logo ao carregar a página inicial. A acção “Permitir localização” mantém o encaminhamento para `navigator.geolocation`, que faz o navegador apresentar a respectiva autorização nativa ao aluno.

No navegador de validação, a API de permissões confirmou contexto seguro, geolocalização disponível e estado `prompt`. Depois de confirmar a janela da Edukangola, a interface passou para “A procurar”, o que confirma a chamada nativa. Este navegador de teste não devolveu coordenadas antes do limite, pelo que a mensagem de indisponibilidade foi apresentada; a chamada será reforçada com pedido de alta precisão e estados mais claros.

O pedido nativo passou a solicitar uma posição recente com alta precisão, limite de 15 segundos e sem reutilizar uma posição antiga. A interface agora distingue recusa de permissão, GPS indisponível e demora de sinal, orientando o aluno para activar a localização do dispositivo ou usar a alternativa por província.

Foi adicionada uma política explícita `Permissions-Policy: geolocation=(self)` tanto ao servidor React como ao Django, confirmada também na resposta pública HTTPS. Ao carregar a página, a plataforma pede a posição automaticamente e conserva a janela central com um botão “Pedir novamente”, para desencadear o pedido por interacção manual nos navegadores que silenciam pedidos automáticos.

O fluxo foi corrigido para que a geolocalização só seja chamada no clique directo de “Permitir localização”, preservando o gesto necessário para navegadores mais restritivos. Num teste isolado, a chamada foi interceptada sem recolher coordenadas e confirmou `enableHighAccuracy: true`, `timeout: 15000` e `maximumAge: 0`; o botão passou imediatamente para o estado “A pedir ao navegador”.

Com uma localização de teste próxima de Luanda, a API devolveu três cursos e a prateleira “Formações mais perto de si” foi renderizada correctamente, incluindo a distância de 7,1 km. Os cartões ficam abaixo da faixa introdutória, pelo que será aplicado deslocamento suave para os trazer imediatamente para a área visível após a pesquisa.

Depois de a resposta de proximidade trazer cursos, a página passa a deslocar-se suavemente até à prateleira “Formações mais perto de si”, evitando que o aluno fique apenas com a mensagem de contagem sem ver de imediato os cartões encontrados.
