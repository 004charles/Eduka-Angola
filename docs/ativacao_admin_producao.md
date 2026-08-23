# Activação de administrador em produção

Em 23-08-2026, o painel do Render foi aberto para preparar a implantação, mas a sessão do navegador não está autenticada. Nenhuma variável, configuração ou implantação de produção foi alterada.

O repositório passa a suportar o comando idempotente `python manage.py provision_admin`, executado pelo `preDeployCommand` apenas quando `ADMIN_BOOTSTRAP_EMAIL` e `ADMIN_BOOTSTRAP_PASSWORD` existem no ambiente do Render. A palavra-passe não é guardada no repositório e o comando não substitui a palavra-passe se a mesma conta já existir.

Uma pré-visualização local do painel redesenhado foi preparada com uma conta administrativa efémera. A página de login carregou, mas o navegador ficou indisponível antes da autenticação e da captura da visão geral; a validação visual final deve ser repetida quando o navegador estiver disponível.

Após a nova conta administrativa ter sido criada e o acesso validado em produção, o percurso temporário de criação foi removido do código. A variável `ADMIN_BOOTSTRAP_TOKEN` deve ser apagada do Render depois da implantação desta remoção.
