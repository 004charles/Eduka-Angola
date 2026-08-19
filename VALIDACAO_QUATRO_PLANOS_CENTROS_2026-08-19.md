# Validação: quatro planos para centros

## Resultado

A API pública passou a devolver exactamente quatro planos activos, ordenados por preço: **Essencial**, **Crescimento**, **Profissional** e **Rede**. O antigo plano de demonstração foi preservado para as assinaturas de teste existentes, mas passou a inactivo, portanto não aparece na vitrina pública.

| Plano | Preço mensal | Cursos | Cursos em vídeo |
|---|---:|---:|---:|
| Essencial | Gratuito | 5 | 0 |
| Crescimento | 15 000 AOA | 20 | 0 |
| Profissional | 30 000 AOA | 50 | 20 |
| Rede | 55 000 AOA | 150 | 50 |

## Validações efectuadas

Os testes do GestorEduka passaram com 11 testes, incluindo uma regressão que confirma a lista pública de quatro planos. O frontend compilou sem erros. No ambiente React local, os quatro cartões foram apresentados numa única linha no desktop, com o plano Crescimento realçado e a candidatura revista logo abaixo.
