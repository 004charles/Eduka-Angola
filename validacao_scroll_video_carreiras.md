# Validação — Scroll de vídeo e Carreiras e competências

Data: 17 de agosto de 2026.

## Colecções de vídeo

As faixas de cursos em vídeo agora apresentam controlos explícitos **anterior** e **seguinte** ao lado do contador de cursos. Estes controlos deslizam a faixa horizontal de forma suave e mantêm o gesto de arrastar/scroll disponível para dispositivos tácteis.

## Página inicial

A secção **Carreiras e competências** foi verificada na página inicial. O módulo passou a ter uma margem superior e inferior mais generosa, sombra suave e composição única de gradiente azul/verde. A coluna editorial, as categorias e os três cartões formam agora um bloco contínuo e deixaram de parecer colados à linha ou à secção anterior.

| Verificação | Resultado |
|---|---|
| Build Vite | Concluído sem erros |
| Controlos nas faixas de vídeo | Visíveis e acessíveis por botões com rótulos claros |
| Composição de carreiras | Espaçamento corrigido e módulo contínuo confirmado no preview |
| Referência panorâmica | Estrutura interpretada como coluna editorial + categorias + cartões num único gradiente |

O botão **Ver próximos cursos** da primeira colecção foi accionado directamente no preview. A interacção manteve o utilizador na faixa horizontal, como previsto para um controlo de deslocamento, sem abrir qualquer rota nem produzir erro.

Os controlos receberam posteriormente botões circulares próprios, com contraste para os temas claro e escuro, estados de foco acessíveis e uma apresentação mais compacta em ecrãs pequenos.

Na inspeção visual final, os dois botões surgem alinhados ao contador da colecção, com formato circular e hierarquia discreta, sem competir com os cartões de curso.
