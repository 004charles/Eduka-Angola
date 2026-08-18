# Validação de descoberta e decisão de cursos

**Data:** 18 de agosto de 2026

## Pesquisa, filtros e comparação

A página pública `/cursos` apresentou os novos controlos de pesquisa unificada, modalidade, nível, preço, início e vagas. No ambiente actual, o catálogo presencial não devolveu cursos publicados, pelo que a interface mostrou correctamente o estado vazio sem cartões seleccionáveis.

A rota `/comparar-cursos?ids=1,2` apresentou o estado orientador para seleccionar dois ou três cursos. O estado é esperado porque os identificadores informados não correspondem ao catálogo actualmente devolvido pelo ambiente. A rota, a página e a navegação de retorno renderizaram sem erro.

Depois da correcção da rota legada dos cursos em vídeo, o catálogo público voltou a devolver 24 formações. Foram vistos no navegador os filtros avançados, as sugestões de pesquisa e a acção “Comparar”. A selecção de uma formação actualizou o estado para “Comparar 1 curso” e marcou o cartão como “Na comparação”, mantendo favoritos e pré-visualização activos.

## Comparação editorial

A comparação com os cursos 35, 32 e 34 foi revista após a recomposição visual. A página passou a apresentar uma matriz com cabeçalhos compactos de curso e linhas comuns para formato, investimento, próxima turma, vagas, local, confiança e acções. O resultado deixou de repetir cartões altos e mantém os dados comparáveis na mesma linha visual.

Depois do ajuste final, a matriz passou a ter uma separação vertical de 42px da introdução. A transição entre a nota de confiança e a comparação ficou visualmente distinta em ecrã largo, sem alterar a hierarquia de leitura.
