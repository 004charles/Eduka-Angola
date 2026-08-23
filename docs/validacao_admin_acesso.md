# Validação visual do acesso administrativo

Em 23-08-2026, a verificação local de `/admin` confirmou que o bundle servido ainda correspondia à compilação anterior: a tela continuava desalinhada à esquerda. Os seletores de acesso foram reforçados para prevalecer sobre os estilos gerais do painel; é necessário recompilar o frontend antes da confirmação visual seguinte.

O redesenho utiliza exclusivamente os tokens globais `--bg`, `--surface`, `--surface-soft`, `--ink`, `--muted`, `--line` e `--brand`, de forma que os modos claro e escuro tenham superfícies e contraste coerentes.

Após a recompilação, a tela foi verificada localmente em tema claro: o cartão está centrado, os textos são legíveis e formulário, fundo e botão pertencem ao mesmo sistema visual. A primeira tentativa de alternar o tema escuro no navegador falhou por sintaxe no comando de validação; a interface não foi alterada por essa tentativa.

O modo escuro foi depois aplicado e verificado localmente. O fundo, cartão, rótulos, campos e botão mantêm contraste coerente sem a mistura anterior de página clara e cartão escuro.
