# Activação de administrador em produção

Em 23-08-2026, o painel do Render foi aberto para preparar a implantação, mas a sessão do navegador não está autenticada. Nenhuma variável, configuração ou implantação de produção foi alterada.

O repositório passa a suportar o comando idempotente `python manage.py provision_admin`, executado pelo `preDeployCommand` apenas quando `ADMIN_BOOTSTRAP_EMAIL` e `ADMIN_BOOTSTRAP_PASSWORD` existem no ambiente do Render. A palavra-passe não é guardada no repositório e o comando não substitui a palavra-passe se a mesma conta já existir.
