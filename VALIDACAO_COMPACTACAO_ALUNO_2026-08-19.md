# Validação da compactação da área do aluno — 19 de Agosto de 2026

| Verificação | Resultado | Observação |
|---|---|---|
| Compilação React | Confirmada | O build Vite terminou sem erros. |
| Página `/aluno` no ambiente local | Confirmada | O painel voltou a carregar após corrigir a rota React dos cursos em vídeo. |
| Cartões de aprendizagem no desktop | Confirmados | Os cartões passaram a usar uma grelha de quatro colunas, imagem de 112 px, corpo compacto e acções de 33 px. |
| Vitrina de bolsas na página inicial | Removida | A página inicial deixou de renderizar o componente de patrocínio educativo. |

A inspecção do DOM confirmou `0` componentes `.educational-sponsor` e a ausência do texto “Bolsas e oportunidades para avançar”.

## Correcção adicional identificada na validação

O painel devolvia HTTP 500 quando um curso em vídeo tinha um slug Unicode, porque tentava resolver uma rota HTML legada cujo padrão só aceita caracteres ASCII. O contrato passou a devolver directamente a rota React canónica `/video-cursos/<slug>`, com teste de regressão para um slug com acento.
