# Validação PWA — 19 de Agosto de 2026

## Evidência inicial no ambiente de desenvolvimento

| Verificação | Resultado | Observação |
|---|---|---|
| Registo do service worker | Confirmado | O âmbito activo é a origem pública do Vite. |
| Nome do manifesto | Confirmado | `Edukangola`. |
| Modo de apresentação | Confirmado | `standalone`. |
| Ícones do manifesto no navegador | Confirmado | Depois de invalidar a cache PWA com a versão `v2`, o navegador devolveu PNG 192 e 512 com `type: image/png`. |
| Página inicial pública | Confirmada | Carregou conteúdo de catálogo e a sessão de aluno sem erro visível. |
| Estado Web Push autenticado | Confirmado | O endpoint devolve `200` com configuração, preferência e número de dispositivos sem expor qualquer chave privada. |
| Interface de preferências | Confirmada | A secção “Notificações neste dispositivo” apresenta o estado de configuração sem erro depois do reinício da API. |
| Geolocalização no navegador de validação | Disponível, permissão negada | A origem é segura e expõe `navigator.geolocation`; o navegador de teste manteve a permissão anterior como negada. Este estado é específico da escolha local do navegador e não bloqueia o pedido de permissão a novos utilizadores. |
| Recarga da página inicial | Confirmada | A página pública recuperou a resposta actual da API após o reinício do Django, preservando a navegação autenticada do aluno. |

## Próxima validação

Será confirmada a instalação, o estado das permissões e o comportamento da navegação em modo autónomo.

## Verificação automatizada final

| Comando | Resultado |
|---|---|
| `python3 manage.py test --verbosity 1` | **73 testes aprovados**. |
| `pnpm --dir frontend run build` | **Compilação concluída**. O Vite assinalou apenas o aviso existente de bundle principal acima de 500 kB. |

## Limite da validação no ambiente actual

O navegador de validação tem a geolocalização previamente negada e a API não recebeu ainda chaves VAPID de ambiente. Por isso, a autorização GPS e a recepção física de uma notificação push devem ser confirmadas num dispositivo do aluno depois de configurar as três variáveis VAPID de produção. A interface, o contrato autenticado, a persistência de subscrições e a chamada de envio possuem cobertura automatizada.
