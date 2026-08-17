# Google Maps — utilização segura na Edukangola

## Decisão de segurança

Uma chave usada para mostrar mapas no navegador ficará visível no pedido do Maps JavaScript/Embed API. A protecção correcta não é escondê-la no código: é limitar rigorosamente **quais websites** e **quais APIs** podem usá-la.

Para a Edukangola, a configuração recomendada é criar uma chave específica para a interface web, permitir apenas os referenciadores HTTPS dos domínios publicados da Edukangola e restringir a chave somente à API escolhida. Uma eventual API de geocodificação no backend deve usar uma chave diferente com restrição por IP/infraestrutura, nunca a mesma chave do navegador.

## Antes de activar

1. No Google Cloud, confirmar qual API será usada: **Maps Embed API** para um mapa simples no perfil de centro ou **Maps JavaScript API** para mapa interactivo e marcadores.
2. Activar facturação no projecto Google Maps, se a API escolhida o exigir.
3. Aplicar restrição de website aos domínios públicos exactos, por exemplo `https://edukangola.com/*` e `https://www.edukangola.com/*`.
4. Não permitir `*`, domínios de preview ou localhost na chave de produção.
5. Restringir a chave apenas a Maps Embed API ou Maps JavaScript API. Criar outra chave para qualquer utilização no servidor.
6. Monitorizar consumo e rodar a chave caso haja utilização inesperada.

## Fontes oficiais

- [Google Maps Platform security guidance](https://developers.google.com/maps/api-security-best-practices)
- [Set up the Maps JavaScript API](https://developers.google.com/maps/documentation/javascript/get-api-key)
- [Set up the Maps Embed API](https://developers.google.com/maps/documentation/embed/get-api-key)
