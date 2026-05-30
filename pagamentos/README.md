# Sistema de Pagamentos - EdukAngola

## Visão Geral

Sistema robusto e escalável de pagamentos integrado ao EdukAngola, suportando múltiplos gateways de pagamento (Prontu, Stripe, PayPal) com arquitetura modular e boas práticas de segurança.

## Arquitetura

### Padrões de Design Utilizados

1. **Strategy Pattern**: Interface `PaymentGateway` abstrata com implementações específicas (`ProntuPaymentGateway`, etc.)
2. **Factory Pattern**: `get_payment_service()` para obter instância singleton
3. **Observer Pattern**: Signals para notificações pós-pagamento
4. **Atomic Transactions**: Operações DB seguras com rollback automático

### Estrutura de Arquivos

```
pagamentos/
├── __init__.py              # Inicialização do app
├── apps.py                  # Configuração do Django app
├── models.py                # Modelos de dados com audit trail
├── admin.py                 # Interface de administração
├── services.py              # Lógica de negócio e gateways
├── serializers.py           # Serializers DRF
├── views.py                 # ViewSets e endpoints REST
├── urls.py                  # Roteamento de URLs
├── utils.py                 # Utilidades e helpers
├── tests.py                 # Testes unitários
├── migrations/              # Migrações de banco de dados
└── templates/
    └── pagamentos/
        ├── email_confirmacao.html           # Email ao usuário
        └── email_notificacao_admin.html     # Email ao admin
```

## Modelos de Dados

### Pagamento
- Transação principal com referência única
- Rastreamento de valores (original, desconto, final)
- Status completo (PENDING, REQUESTED, PROCESSING, ACCEPTED, REJECTED, etc.)
- Armazenamento de resposta do gateway em JSON

### HistoricoPagamento
- Auditoria de todas as mudanças de status
- Rastreamento de IP e User-Agent
- Motivo da mudança com source (SISTEMA, WEBHOOK, MANUAL, ADMIN)

### TentativaPagamento
- Registro de cada tentativa de pagamento
- Codes de erro e mensagens detalhadas
- Tempo de resposta do gateway

### ConfiguracaoPagamento
- Singleton para configurações globais
- Gateway padrão, moeda, taxas de desconto
- Flags de notificação e validação

## Endpoints da API

### Autenticação
Todos os endpoints requerem `Authorization: Bearer <token>`

### Endpoints Disponíveis

#### 1. Listar Pagamentos do Usuário
```
GET /api/v1/pagamentos/
```
Retorna lista de pagamentos do usuário autenticado.

#### 2. Detalhes de Pagamento
```
GET /api/v1/pagamentos/{id}/
```
Retorna detalhes completos do pagamento.

#### 3. Criar Pagamento
```
POST /api/v1/pagamentos/criar/
Content-Type: application/json

{
  "tipo_pagamento": "INSCRICAO",
  "valor": 9999.00,
  "moeda": "AOA",
  "curso_id": 1,
  "url_sucesso": "https://seu-frontend.com/sucesso",
  "url_cancelamento": "https://seu-frontend.com/cancelado"
}
```

Retorna:
```json
{
  "sucesso": true,
  "pagamento": {
    "referencia_pagamento": "PAG-20240115120000-ABC123",
    "url_pagamento": "https://prontu.io/pay/...",
    "status": "PENDING",
    ...
  }
}
```

#### 4. Fazer Retry de Pagamento
```
POST /api/v1/pagamentos/{id}/retry/
```
Regenera link para pagamentos expirados/rejeitados.

#### 5. Verificar Status
```
GET /api/v1/pagamentos/{id}/verificar-status/
```
Consulta status atual no gateway.

#### 6. Histórico do Pagamento
```
GET /api/v1/pagamentos/{id}/historico/
```
Retorna auditoria completa de mudanças.

#### 7. Webhook Prontu
```
POST /api/v1/pagamentos/webhook/prontu/
Content-Type: application/json

{
  "result": {
    "reference_id": "PAG-20240115120000-ABC123",
    "status": "accepted",
    "prontu_transaction_id": "txn_123456"
  }
}
```

## Configuração

### 1. Variáveis de Ambiente (.env)

```bash
# Ativação
PAGAMENTOS_ATIVADOS=True
GATEWAY_PADRAO=PRONTU
MOEDA_PADRAO=AOA

# Prontu
PRONTU_API_URL=https://api.prontu.io
PRONTU_API_KEY=sua_api_key_aqui
PRONTU_CALLBACK_URL=https://seu-dominio.com/api/v1/pagamentos/webhook/prontu/

# URLs do Frontend
FRONTEND_RETURN_URL=https://seu-frontend.com/pagamento/sucesso
FRONTEND_CANCEL_URL=https://seu-frontend.com/pagamento/cancelado

# Configurações
TEMPO_EXPIRACAO_LINK_MINUTOS=120
MAX_TENTATIVAS_PAGAMENTO=3
DESCONTO_INSCRICAO_PERCENTUAL=10

# Notificações
NOTIFICAR_ADMIN_PAGAMENTO_RECEBIDO=True
VALIDAR_WEBHOOK_SIGNATURE=True

# Email
DEFAULT_FROM_EMAIL=nao-responda@edukangola.ao
SITE_DOMAIN=https://seu-dominio.com
```

### 2. Instalação e Migração

```bash
# Instalar dependências
pip install requests

# Criar migrações
python manage.py makemigrations pagamentos

# Aplicar migrações
python manage.py migrate pagamentos

# Criar superuser se necessário
python manage.py createsuperuser
```

### 3. Registrar Webhook no Prontu

Configure no dashboard do Prontu:
```
URL: https://seu-dominio.com/api/v1/pagamentos/webhook/prontu/
Método: POST
Eventos: payment.accepted, payment.rejected, payment.pending
```

## Fluxo de Pagamento

```
1. Usuário solicita inscrição em curso
   ↓
2. Frontend chama POST /api/v1/pagamentos/criar/
   ↓
3. Sistema cria Pagamento (PENDING) e transação no Prontu
   ↓
4. Retorna URL de pagamento
   ↓
5. Usuário é redirecionado para Prontu
   ↓
6. Usuário completa pagamento no Prontu
   ↓
7. Prontu envia callback para webhook
   ↓
8. Sistema processa webhook:
   - Valida dados
   - Atualiza status para ACCEPTED
   - Envia email de confirmação
   - Notifica admin
   - Inscreve usuário no curso (integração futura)
   ↓
9. Frontend redireciona para URL de sucesso
```

## Integração com Cursos

Para integrar pagamentos com inscrição em cursos:

### Em cursos_app/views.py

```python
from pagamentos.services import get_payment_service

def inscrever_em_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    
    if curso.preco > 0:
        # Criar pagamento
        servico = get_payment_service()
        pagamento = servico.criar_pagamento(
            usuario=request.user,
            tipo_pagamento='INSCRICAO',
            valor=curso.preco,
            moeda=curso.moeda,
            curso=curso,
            url_sucesso=request.GET.get('return_url')
        )
        
        # Retornar URL de pagamento
        return redirect(pagamento.url_pagamento)
    else:
        # Curso gratuito - inscrever diretamente
        return inscrever_usuario_em_curso(request.user, curso)
```

### Signal pós-pagamento

```python
# Em cursos_app/signals.py
from django.dispatch import receiver
from pagamentos.models import Pagamento

@receiver(models.signals.post_save, sender=Pagamento)
def inscrever_apos_pagamento(sender, instance, **kwargs):
    if instance.eh_pago() and instance.tipo_pagamento == 'INSCRICAO':
        # Inscrever usuário no curso
        from cursos_app.models import Inscricao
        Inscricao.objects.get_or_create(
            usuario=instance.usuario,
            curso=instance.curso
        )
```

## Segurança

### Práticas Implementadas

1. **Validação CSRF**: Middleware Django padrão
2. **Autenticação JWT**: Bearer token nos headers
3. **Permissões**: Usuários só acessam seus próprios pagamentos
4. **Timeout**: Conexões ao gateway com timeout de 30s
5. **Logging**: Todas as operações são registradas
6. **Atomicidade**: Transações DB seguras
7. **Validação**: Dados validados em serializers
8. **HTTPS Obrigatório**: Em produção, usar HTTPS

### Checklist de Segurança em Produção

- [ ] `DEBUG = False` em settings.py
- [ ] `ALLOWED_HOSTS` configurado corretamente
- [ ] `SECRET_KEY` alterada
- [ ] SSL/TLS ativado
- [ ] CORS configurado adequadamente
- [ ] Rate limiting ativado
- [ ] Logs monitorados
- [ ] Backup automático do banco
- [ ] Webhook signature validado
- [ ] HTTPS obrigatório no webhook

## Testes

```bash
# Rodar testes
python manage.py test pagamentos

# Com cobertura
pip install coverage
coverage run --source='pagamentos' manage.py test pagamentos
coverage report
```

## Monitoramento e Debugging

### Logs
```python
import logging
logger = logging.getLogger('pagamentos')
logger.info("Mensagem informativa")
logger.error("Erro crítico")
```

### Admin Interface
- Acessar `http://localhost:8000/admin/`
- Menu "Pagamentos" com todas as transações
- Filtros por status, gateway, data
- Ações em massa
- Histórico visual com arrows

### Webhook Testing
```bash
# Simular callback Prontu
curl -X POST http://localhost:8000/api/v1/pagamentos/webhook/prontu/ \
  -H "Content-Type: application/json" \
  -d '{
    "result": {
      "reference_id": "PAG-20240115120000-ABC123",
      "status": "accepted",
      "prontu_transaction_id": "txn_123456"
    }
  }'
```

## Próximas Implementações

1. **Stripe Gateway**: Adicionar suporte para Stripe
2. **PayPal Gateway**: Adicionar suporte para PayPal
3. **Webhook Signature Validation**: Validar assinatura real do Prontu
4. **Reembolsos**: Implementar processamento de reembolsos
5. **Parcelamento**: Suporte para múltiplas parcelas
6. **Dashboard**: Painel de relatórios e analytics
7. **Reconciliação**: Verificação automática com banco
8. **Webhook Retry**: Reentrega automática de webhooks

## Troubleshooting

### "Gateway indisponível"
- Verificar URL e API key no .env
- Testar conexão com gateway
- Verificar logs em `pagamentos`

### "Webhook não processado"
- Verificar se callback URL está configurada
- Testar webhook manualmente
- Verificar logs do Django

### Email não enviado
- Verificar settings de EMAIL do Django
- Verificar SMTP em produção
- Verificar permissões de arquivo de templates

## Suporte e Documentação

- **Prontu Docs**: https://docs.prontu.io
- **Django DRF**: https://www.django-rest-framework.org
- **Django Signals**: https://docs.djangoproject.com/en/5.2/topics/signals

## Licença

Parte do projeto EdukAngola
