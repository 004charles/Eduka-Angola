# Experiência de mapas para centros Edukangola

## Decisão de interface

O mapa não deve substituir a lista de centros. A lista continua a ser a forma mais clara de comparar curso, país, cidade, modalidade e verificação. O mapa entra como contexto geográfico, sobretudo no perfil do centro e na descoberta de centros internacionais.

| Área | Comportamento previsto |
|---|---|
| Página de centros | Filtros por país, cidade/região, modalidade e selo de centro verificado. Um botão opcional **Ver no mapa** alterna entre lista e mapa quando existirem coordenadas suficientes. |
| Perfil do centro | Cartão **Localização** com mapa compacto, país/cidade/endereço e botão **Abrir no Google Maps**. |
| Curso presencial | Mostrar local de realização e ligar ao perfil do centro; não repetir um mapa pesado em cada cartão de curso. |
| Centro estrangeiro | Mostrar distintamente país, cidade, fuso horário e se aceita candidaturas internacionais. |
| Falta de coordenadas | Mostrar endereço/cidade em texto e ligação de pesquisa no Google Maps; nunca uma área vazia ou um marcador errado. |

## Dados necessários no GestorEduka

1. País, cidade/região e endereço normalizado do centro.
2. Latitude e longitude confirmadas pelo gestor do centro ou por um administrador.
3. Estado de verificação da localização.
4. Para centros estrangeiros: fuso horário e contacto de admissões.

## Implementação por etapas

### Etapa 1 — Sem dependência de mapa interactivo

Usar os campos actuais de país, cidade, região e endereço. Adicionar no perfil um link seguro de pesquisa/direcções para Google Maps, gerado a partir do endereço. Esta etapa funciona mesmo sem chave de API.

**Estado: concluída e validada localmente.** A vitrine pública permite filtrar centros por país e por província/região, os centros internacionais recebem identificação explícita e o perfil do centro disponibiliza a ligação `Google Maps Search` construída exclusivamente com os dados públicos de endereço. Não há carregamento de SDK, mapa incorporado ou chave de Google Maps no frontend.

### Etapa 2 — Mapa compacto no perfil

Depois de restringir a chave web, carregar Maps Embed API apenas no perfil de centro que tenha localização confirmada. O utilizador vê um mapa, mas o restante catálogo não fica mais lento.

### Etapa 3 — Descoberta global

Adicionar vista de mapa à página de centros, com clusters de marcadores e filtros por país. Esta etapa só entra quando houver centros suficientes com coordenadas verificadas para justificar a exploração geográfica.

## Protecção da chave

Antes da etapa 2, a chave de navegador deve estar limitada aos domínios HTTPS da Edukangola e à API de mapas escolhida. A chave entregue nesta conversa não será gravada em código, documentação ou GitHub.
