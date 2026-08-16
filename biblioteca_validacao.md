# Validação da Biblioteca Edukangola

- A rota pública `/biblioteca` apresenta a mesa de leitura, a pesquisa, os filtros de categoria e estantes horizontais de livros com capas verticais e lombadas visuais.
- A ficha de `/biblioteca/o-proximo-passo` apresenta capa, autor, sinopse, formatos, acesso gratuito, excerto e acções de leitura e guardar.
- A leitura autenticada em `/ler/o-proximo-passo` abre num capítulo com conteúdo, mantém índice e permite registar progresso.
- A acção de guardar/remover livro foi validada numa sessão autenticada; o estado regressou a guardado ao terminar o teste.
- A área `/aluno` apresenta a obra guardada na secção “As suas leituras”.
- A compilação Vite e a verificação Django foram concluídas sem erros. O aviso de tamanho de pacote do Vite já existia como recomendação de divisão futura e não impede a execução.

## Continuidade e voz

A leitura agora grava o índice exacto da página/parte no modelo pessoal. Ao reabrir uma obra com progresso, o leitor apresenta as opções “Continuar onde parei” e “Começar novamente”. A opção de continuação foi validada e abriu a segunda página guardada. O leitor também apresenta a leitura em voz alta local, com iniciar, pausar, parar e velocidades de 0,8×, 1×, 1,2× e 1,5×. A disponibilidade depende das vozes instaladas no navegador e respeita o idioma da obra.

## Estante na página inicial

A homepage apresenta a estante “Livros para continuar a aprender.” depois da colecção “Aprenda ao seu ritmo, com compra única.” e antes da colecção “Cursos recomendados para explorar agora.”. A estante carrega as obras da API pública da Biblioteca, usa capas verticais com lombadas, permite deslocação horizontal e liga cada título ao detalhe editorial.
