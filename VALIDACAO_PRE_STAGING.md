# Validação pré-staging — 17 de agosto de 2026

## Resultado da validação de código

| Verificação | Resultado |
|---|---|
| Suite Django | **40 testes aprovados** |
| Serviço de notificações | **3 testes aprovados** |
| Build React | **Aprovado** |
| Verificação de implantação Django com variáveis seguras de teste | **Sem avisos** |
| Gateway Prontu no runner de testes | **Simulado, sem autenticação externa** |
| Health check temporário do gateway de notificações | **HTTP 200** |

## O que foi fechado no código

1. A aplicação agora diferencia desenvolvimento, staging e produção por `DJANGO_ENV`.
2. Staging/produção recusam iniciar com `DEBUG=True`, `SECRET_KEY` insegura ou hosts/origens CSRF ausentes.
3. HTTPS, HSTS, cookies seguros e CORS restrito são configuráveis pelo ambiente.
4. A migration histórica deixou de criar um administrador com credencial embutida.
5. Os scripts manuais foram retirados da descoberta automática de testes.
6. A Prontu é simulada por defeito no runner de testes; testes de contrato continuam a usar mocks explícitos.
7. Há documentação de operação para o Django e para os dois processos de notificações.

## O que não pode ser concluído localmente

As tarefas abaixo exigem acesso ao provedor e segredos próprios de staging. Não devem ser simuladas como concluídas:

- Definir variáveis seguras e uma nova chave Django no provedor.
- Criar/rever o superutilizador no ambiente de destino e rodar credenciais antigas.
- Configurar Brevo e executar o teste de entrega de e-mail real.
- Configurar Prontu sandbox e executar compra, callback, acesso e reconciliação ponta a ponta.
- Criar os serviços gateway e worker de notificações no provedor e confirmar health checks/logs.
- Executar a checklist comercial completa com contas de teste em staging.
