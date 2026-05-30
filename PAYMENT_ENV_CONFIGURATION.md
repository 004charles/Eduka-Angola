# CONFIGURAÇÃO DO SISTEMA DE PAGAMENTOS
# ========================================

## Variáveis de Ambiente Necessárias

Todas as variáveis abaixo devem ser adicionadas ao arquivo `.env` na raiz do projeto.

### 1. ATIVAÇÃO DO SISTEMA

```env
PAGAMENTOS_ATIVADOS=True
```
- **True**: Sistema de pagamentos ativo
- **False**: Desativa todos os pagamentos

### 2. GATEWAY PADRÃO

```env
GATEWAY_PADRAO=PRONTU
```
Opções disponíveis:
- `PRONTU`: Prontu (implementado)
- `STRIPE`: Stripe (planejado)
- `PAYPAL`: PayPal (planejado)

### 3. MOEDA PADRÃO

```env
MOEDA_PADRAO=AOA
```
Código ISO 4217 da moeda padrão.

---

## PRONTU GATEWAY (OBRIGATÓRIO)

### URL da API Prontu

```env
PRONTU_API_URL=https://api.prontu.io
```

### Chave de API

```env
PRONTU_API_KEY=pk_live_sua_chave_api_aqui
```

⚠️ **CRÍTICO**: Esta chave deve ser alterada em produção!
- Obtenha em: https://prontu.io/admin
- Nunca commite a chave real no git
- Use variáveis de ambiente em produção

### URL de Callback (Webhook)

```env
PRONTU_CALLBACK_URL=http://localhost:8000/api/v1/pagamentos/webhook/prontu/
```

**Local**: `http://localhost:8000/api/v1/pagamentos/webhook/prontu/`
**Produção**: `https://seu-dominio.com/api/v1/pagamentos/webhook/prontu/`

Configure esta URL exata no dashboard do Prontu.

---

## REDIRECIONAMENTO DO FRONTEND

### Sucesso

```env
FRONTEND_RETURN_URL=http://localhost:3000/pagamento/sucesso
```

Para onde redirecionar o usuário após pagamento bem-sucedido.

### Cancelamento

```env
FRONTEND_CANCEL_URL=http://localhost:3000/pagamento/cancelado
```

Para onde redirecionar o usuário após cancelamento.

---

## CONFIGURAÇÕES DE PAGAMENTO

### Expiração do Link

```env
TEMPO_EXPIRACAO_LINK_MINUTOS=120
```

- **120**: Link expira após 2 horas
- Recomendado: 60-240 minutos

### Máximo de Tentativas

```env
MAX_TENTATIVAS_PAGAMENTO=3
```

- Usuário pode fazer retry até N vezes
- Recomendado: 3-5 tentativas

### Desconto de Inscrição

```env
DESCONTO_INSCRICAO_PERCENTUAL=0
```

- **0**: Sem desconto
- **10**: 10% de desconto
- Intervalo: 0-100

---

## NOTIFICAÇÕES E SEGURANÇA

### Notificar Admin

```env
NOTIFICAR_ADMIN_PAGAMENTO_RECEBIDO=True
```

Enviar email para administradores quando pagamento é recebido.

### Validar Assinatura de Webhook

```env
VALIDAR_WEBHOOK_SIGNATURE=True
```

⚠️ Obrigatório em produção para evitar callbacks falsos.

---

## CONFIGURAÇÃO DE EMAIL

### Email de Origem

```env
DEFAULT_FROM_EMAIL=nao-responda@edukangola.ao
```

Será usado para enviar:
- Confirmação de pagamento ao usuário
- Notificação para admin

### Backend de Email

**Desenvolvimento**:
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Produção** (exemplo com Gmail):
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-app-password
```

---

## SITE DOMAIN

```env
SITE_DOMAIN=http://localhost:8000
```

Usado para construir URLs absolutas em emails e referências.

**Produção**: `https://www.edukangola.com/`

---

## CHECKLIST DE CONFIGURAÇÃO

### Desenvolvimento Local

- [ ] `PAGAMENTOS_ATIVADOS=True`
- [ ] `GATEWAY_PADRAO=PRONTU`
- [ ] `PRONTU_API_URL=https://api.prontu.io` (ou sandbox)
- [ ] `PRONTU_API_KEY=sua_chave_teste` (de um gateway teste)
- [ ] `FRONTEND_RETURN_URL` apontando para seu frontend local
- [ ] `FRONTEND_CANCEL_URL` apontando para seu frontend local
- [ ] Email backend em modo console (para desenvolvimento)

### Pré-Produção

- [ ] `DEBUG=False`
- [ ] `PRONTU_API_KEY` com credenciais reais (ambiente staging)
- [ ] `FRONTEND_RETURN_URL` aponta para domínio staging
- [ ] `FRONTEND_CANCEL_URL` aponta para domínio staging
- [ ] `SITE_DOMAIN` aponta para domínio staging
- [ ] `PRONTU_CALLBACK_URL` aponta para domínio staging
- [ ] Email backend configurado com SMTP real
- [ ] HTTPS em todas as URLs

### Produção

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` alterada e aleatória
- [ ] `PRONTU_API_KEY` com credenciais de PRODUÇÃO
- [ ] Todas as URLs com HTTPS
- [ ] `ALLOWED_HOSTS` configurado corretamente
- [ ] Email backend com serviço real (SendGrid, AWS SES, etc.)
- [ ] Backup automático de banco de dados
- [ ] Logs monitorados
- [ ] Alertas configurados para erros de pagamento
- [ ] Webhook signature validation ativado

---

## EXEMPLO .env COMPLETO

```env
# Django
DEBUG=True
SECRET_KEY=django-insecure-dev-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
USE_SQLITE=True
DB_NAME=eduka_db

# Pagamentos
PAGAMENTOS_ATIVADOS=True
GATEWAY_PADRAO=PRONTU
MOEDA_PADRAO=AOA

# Prontu
PRONTU_API_URL=https://api.prontu.io
PRONTU_API_KEY=pk_test_sua_chave_aqui
PRONTU_CALLBACK_URL=http://localhost:8000/api/v1/pagamentos/webhook/prontu/

# Frontend
FRONTEND_RETURN_URL=http://localhost:3000/pagamento/sucesso
FRONTEND_CANCEL_URL=http://localhost:3000/pagamento/cancelado

# Configuração
TEMPO_EXPIRACAO_LINK_MINUTOS=120
MAX_TENTATIVAS_PAGAMENTO=3
DESCONTO_INSCRICAO_PERCENTUAL=0

# Notificações
NOTIFICAR_ADMIN_PAGAMENTO_RECEBIDO=True
VALIDAR_WEBHOOK_SIGNATURE=True

# Email
DEFAULT_FROM_EMAIL=nao-responda@edukangola.ao

# Site
SITE_DOMAIN=http://localhost:8000
```

---

## VALIDAR CONFIGURAÇÃO

Execute o script de checklist para validar todas as configurações:

```bash
python PAYMENT_INTEGRATION_CHECKLIST.py
```

Este script verifica:
- ✓ Variáveis de ambiente
- ✓ Configurações Django
- ✓ URLs registradas
- ✓ Estrutura do app
- ✓ Banco de dados

---

## SUPORTE

Para problemas com configuração:

1. Verificar logs: `tail -f logs/pagamentos.log`
2. Testar webhook manualmente (veja README.md)
3. Acessar admin: `/admin/pagamentos/`
4. Verificar se `DEBUG=True` para mensagens de erro detalhadas

---

**Última atualização**: 2024-01-15
**Versão**: 1.0
