# Auditoria inicial da homepage pública — observações

## Estado observado

A homepage pública abre corretamente no ambiente de desenvolvimento depois de reiniciar o servidor. O título é “EdukAngola | O mercado de cursos e centros de formação de Angola”. A página apresenta navegação superior, subnavegação por categorias, hero, categorias, cursos em destaque, banner para empresas, ranking, secções por categoria, cursos internacionais, centros de formação e rodapé.

## Conteúdo identificado

- Proposta principal: “Encontre as melhores formações em Angola”.
- CTA principal no hero: “Explorar Cursos”.
- Subnavegação com oito categorias, Internacional e Bolsas e descontos.
- Hero com publicidade dinâmica; quando não há publicidade suficiente, usa fallback genérico.
- Secção “Cursos em destaque” com filtros Todos, Presencial e Online.
- Banner “Formação para empresas”.
- Secção “Mais procurados esta semana”.
- Secções de Tecnologia e Informática, Idiomas, Novos na plataforma e Internacional.
- Secção “Centros de formação” com filtro Nacional/Internacional.
- Rodapé com links para catálogo, instituições, bolsas, área do aluno, instrutor e criação de conta.

## Observações visuais

- A composição tem aparência profissional e utiliza uma linguagem visual consistente: azul profundo, cartões brancos, sombras suaves e grelha editorial.
- O hero domina a primeira dobra e possui bom contraste, mas a primeira mensagem é genérica e não comunica imediatamente como o aluno encontra uma turma, vê preço ou se inscreve.
- A primeira dobra apresenta muitos elementos concorrentes: cabeçalho, dois níveis de navegação, hero, dois cartões laterais e oito categorias. A hierarquia pode ficar mais focada no objetivo “encontrar e inscrever-se”.
- Os cartões laterais fazem promessas fortes (“Pague o seu curso em 6 prestações sem juros” e “68 centros parceiros”) que parecem conteúdo estático/fallback e precisam de fonte dinâmica ou revisão para não criar expectativas incorretas.
- A homepage renderizada mostra dados de demonstração: “Centro Demo Eduka-Angola”, “1 cursos”, categorias com zero cursos e números de catálogo como 1 248, 312 e 164 que parecem valores fixos. Isto reduz confiança se for apresentado como dado real.
- O cabeçalho reconhece “Gestor Demo Eduka-Angola”, o que é inadequado para um visitante público e indica que a sessão de demonstração está exposta na homepage.

## Primeiras hipóteses de melhoria

1. Tornar a homepage orientada à tarefa: “Encontre um curso, escolha uma turma e inscreva-se”.
2. Colocar pesquisa de cursos e localização/modalidade mais visíveis na primeira dobra.
3. Substituir números fixos por contagens reais ou ocultar a informação quando não houver dados.
4. Remover o nome da conta demo do cabeçalho público.
5. Mostrar no cartão ou hero o preço de inscrição e a modalidade de cobrança, não apenas o preço total.
6. Dar prioridade a cursos reais publicados e com turmas abertas; evitar hero genérico quando o catálogo está vazio.
7. Rever a quantidade de secções na homepage para não criar uma página longa com conteúdo repetido.

## Observações abaixo da primeira dobra

A homepage tem uma grande quantidade de secções, mas várias aparecem visualmente quase vazias no ambiente atual: “Mais procurados esta semana”, “Tecnologia e Informática”, “Idiomas” e “Novos na plataforma” mostram títulos e filtros, mas não apresentam cartões de cursos. Isto cria uma sensação de catálogo incompleto, mesmo quando os subtítulos anunciam centenas de cursos.

A secção internacional é visualmente forte como bloco editorial, mas também não mostra ofertas concretas na captura observada. A secção de centros mostra apenas o Centro Demo Eduka-Angola. A combinação de números altos nos títulos com poucos ou nenhum resultado real é o principal problema de confiança da homepage atual.

A navegação mantém boa consistência e os filtros Presencial/Online são uma boa ideia, mas eles aparecem repetidos em muitas secções sem conteúdo suficiente para justificar a repetição. A página pode ser mais curta e mais eficaz se cada bloco só for apresentado quando tiver resultados reais.

O rodapé é completo e contém os caminhos importantes, mas o objetivo principal do aluno — pesquisar, comparar e inscrever-se num curso — fica diluído no volume de conteúdo secundário.

## Validação após as correções

A homepage voltou a renderizar corretamente no navegador. O cabeçalho deixou de mostrar “Bem-vindo, Gestor Demo Eduka-Angola”. O hero agora apresenta o curso real “Informática Básica Demo”, o catálogo mostra “1 curso publicado”, a categoria Tecnologia mostra “1 curso” e a secção de centros mostra “1 instituição ativa em Angola”.

As secções sem dados reais — cursos internacionais e várias categorias sem cursos — deixaram de aparecer. O banner de empresas também deixou de aparecer porque não existe publicidade ativa configurada nessa posição.

A homepage continua a mostrar o curso de demonstração, que é um dado real da base de desenvolvimento. Antes de produção, deverá ser substituído por cursos reais ou marcado claramente como conteúdo de demonstração num ambiente de teste.

O teste anónimo de renderização passou e confirmou a ausência dos números fictícios, das promessas de prestações sem juros, do centro British Language Centre e da saudação da conta demo.
