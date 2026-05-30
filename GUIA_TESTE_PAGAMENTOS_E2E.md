# GUIA DE TESTE E2E - SISTEMA DE PAGAMENTOS
## EdukAngola

---

## 📋 Visão Geral

Este guia fornece instruções completas para executar testes E2E que validam a integração completa do sistema de pagamentos com o gateway Prontu.

### Componentes Testados:
- ✅ Configuração de variáveis de ambiente
- ✅ Modelos de dados (Pagamento, HistoricoPagamento, TentativaPagamento)
- ✅ Serviço de pagamentos (PaymentService)
- ✅ Endpoints da API REST
- ✅ Webhooks do Prontu
- ✅ Fluxo completo E2E
- ✅ Segurança e isolamento de dados
- ✅ Validação de dados

---

## 🚀 Começando

### Pré-requisitos

```bash
# 1. Ambiente virtual ativo
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\Activate.ps1  # Windows PowerShell

# 2. Dependências instaladas
pip install -r requirements.txt

# 3. Banco de dados sincronizado
python manage.py migrate

# 4. Variáveis de ambiente configuradas
# Veja a seção de Configuração abaixo
```

### Configuração de Variáveis de Ambiente

Crie ou atualize o arquivo `.env` com as seguintes variáveis:

```env
# ATIVAÇÃO DO SISTEMA
PAGAMENTOS_ATIVADOS=True

# GATEWAY PADRÃO
GATEWAY_PADRAO=PRONTU

# MOEDA
MOEDA_PADRAO=AOA

# PRONTU GATEWAY
PRONTU_API_URL=https://api.prontu.io
PRONTU_API_KEY=pk_live_sua_chave_api_aqui
PRONTU_CALLBACK_URL=http://localhost:8000/api/v1/pagamentos/webhook/prontu/

# URLs DE RETORNO
FRONTEND_RETURN_URL=http://localhost:3000/pagamento/sucesso
FRONTEND_CANCEL_URL=http://localhost:3000/pagamento/cancelado

# CONFIGURAÇÕES
TEMPO_EXPIRACAO_LINK_MINUTOS=120
MAX_TENTATIVAS_PAGAMENTO=3
```

---

## 🧪 Executando os Testes

### Opção 1: Teste E2E Completo (Recomendado)

```bash
# Executar script E2E com verificações abrangentes
python test_pagamentos_e2e.py

# Ou via manage.py shell
python manage.py shell < test_pagamentos_e2e.py
```

**Resultado esperado:**
```
==================================
  TESTE E2E - SISTEMA DE PAGAMENTOS
==================================

✓ 1. Variáveis de Ambiente
✓ 2. Django Settings
✓ 3. Banco de Dados
✓ 4. Criar Pagamento
✓ 5. Listar Pagamentos
...

============================================================
RELATÓRIO FINAL
============================================================
Total de testes: 11
✓ Passou: 11
✗ Falhou: 0
```

### Opção 2: Testes Unitários

```bash
# Executar todos os testes do app pagamentos
python manage.py test pagamentos

# Com verbosidade
python manage.py test pagamentos -v 2

# Teste específico
python manage.py test pagamentos.tests.PagamentoModelTestCase

# Com coverage
coverage run --source='pagamentos' manage.py test pagamentos
coverage report
coverage html  # Gera relatório em htmlcov/index.html
```

### Opção 3: Testes por Categoria

```bash
# Apenas testes E2E
python manage.py test pagamentos.tests.PagamentoE2ETestCase -v 2

# Apenas testes de validação
python manage.py test pagamentos.tests.PagamentoValidacaoTestCase -v 2

# Apenas testes de segurança
python manage.py test pagamentos.tests.PagamentoSegurancaTestCase -v 2

# Apenas testes da API
python manage.py test pagamentos.tests.PagamentoAPITestCase -v 2
```

### Opção 4: Testes com API Client

```bash
# Executar servidor de desenvolvimento
python manage.py runserver

# Em outro terminal, executar testes de API
python manage.py test pagamentos.tests.PagamentoAPITestCase -v 2
```

---

## 📊 Detalhes dos Testes

### 1. Variáveis de Ambiente ✅
Valida se todas as variáveis necessárias estão configuradas:
- `PAGAMENTOS_ATIVADOS`
- `GATEWAY_PADRAO`
- `PRONTU_API_KEY`
- `FRONTEND_RETURN_URL`
- `FRONTEND_CANCEL_URL`
- E outras...

### 2. Django Settings ✅
Verifica se o Django está configurado corretamente:
- App `pagamentos` instalado
- URLs do webhook registradas
- Configurações do Prontu presentes

### 3. Banco de Dados ✅
Valida sincronização do banco:
- Tabelas existem
- Modelos acessíveis
- Integridade referencial

### 4. Criar Pagamento ✅
Testa criação de novo pagamento:
- Usuário associado
- Status inicial PENDING
- URL de pagamento gerada
- Referência única criada

### 5. Listar Pagamentos ✅
Verifica recuperação de pagamentos:
- Listar todos os pagamentos do usuário
- Informações completas retornadas
- Paginação funciona

### 6. Atualizar Status ✅
Testa atualização de status:
- Status pode ser alterado
- Histórico registra mudanças
- Dados persistem no banco

### 7. Webhook ✅
Valida processamento de webhooks:
- Webhook recebido corretamente
- Status atualizado via webhook
- Histórico registrado

### 8. Fluxo Completo E2E ✅
Testa cenário realista:
1. Criar usuário
2. Criar pagamento
3. Processar webhook
4. Confirmar pagamento
5. Verificar persistência

### 9. Endpoints da API ✅
Valida endpoints REST:
- `GET /api/v1/pagamentos/` - Listar
- `POST /api/v1/pagamentos/criar/` - Criar
- `GET /api/v1/pagamentos/{id}/` - Detalhe
- Autenticação requerida

### 10. Serviço de Pagamento ✅
Verifica o PaymentService:
- Métodos necessários existem
- Comportamento correto
- Tratamento de erros

### 11. Segurança ✅
Testa aspectos de segurança:
- Acesso sem autenticação bloqueado
- Isolamento de dados entre usuários
- Permissões validadas

---

## 🔍 Analisando Resultados

### Teste Passou ✅
```
✓ Teste executado com sucesso
  Nenhuma ação necessária
  Componente validado
```

### Teste Falhou ❌
```
✗ Erro ao configurar X
  └─ Mensagem de erro específica
  └─ Ação corretiva necessária
```

### Interpretando Falhas

**Falha: "PAGAMENTOS_ATIVADOS não configurada"**
```bash
# Solução:
# Adicionar ao .env:
PAGAMENTOS_ATIVADOS=True
```

**Falha: "App 'pagamentos' não está em INSTALLED_APPS"**
```python
# Solução em eduangolacore/settings.py:
INSTALLED_APPS = [
    ...
    'pagamentos',  # Adicionar esta linha
    ...
]
```

**Falha: "Webhook retornou status 404"**
```python
# Solução em eduangolacore/urls.py:
urlpatterns = [
    ...
    path('api/v1/pagamentos/', include('pagamentos.urls')),  # Verificar
    ...
]
```

**Falha: "Conexão recusada ao gateway"**
```env
# Verificar:
# 1. PRONTU_API_URL correto
# 2. PRONTU_API_KEY válida
# 3. Conexão de internet
# 4. Firewall/Proxy bloqueando?
```

---

## 📈 Cobertura de Testes

Verify code coverage:

```bash
# Gerar relatório de cobertura
coverage run --source='pagamentos' manage.py test pagamentos
coverage report

# Esperado:
# Name                                Stmts   Miss  Cover
# ─────────────────────────────────────────────────────
# pagamentos/__init__.py                  0      0   100%
# pagamentos/models.py                  150     15    90%
# pagamentos/services.py                200     20    90%
# pagamentos/views.py                   100     10    90%
# pagamentos/serializers.py              50      5    90%
# ─────────────────────────────────────────────────────
# TOTAL                                 500     50    90%
```

---

## 🐛 Debugging

### Modo Verbose

```bash
# Ver todos os detalhes dos testes
python manage.py test pagamentos -v 3

# Com print statements
python manage.py test pagamentos -v 2 --keepdb
```

### Django Shell Interactive

```bash
python manage.py shell

# Dentro do shell:
from pagamentos.services import get_payment_service
from pagamentos.models import Pagamento

# Verificar serviço
servico = get_payment_service()
print(servico)

# Listar pagamentos
print(Pagamento.objects.all().count())

# Criar teste manual
usuario = User.objects.first()
pag = servico.criar_pagamento(...)
```

### Logs

```bash
# Ver logs detalhados
python manage.py test pagamentos 2>&1 | tee test_output.log

# Filtrar erros
grep "ERROR\|FAIL" test_output.log

# Ver apenas erros críticos
python manage.py test pagamentos 2>&1 | grep -A 5 "FAIL"
```

---

## ✅ Checklist de Validação

Antes de considerar os testes completos:

- [ ] Todas as 11 categorias de testes passaram
- [ ] Não há avisos de configuração
- [ ] Banco de dados está sincronizado
- [ ] Variáveis de ambiente estão corretas
- [ ] Gateway Prontu está configurado
- [ ] API endpoints respondendo corretamente
- [ ] Webhooks podem ser processados
- [ ] Segurança validada (autenticação, autorização)
- [ ] Histórico de pagamentos sendo registrado
- [ ] Fluxo completo E2E funciona

---

## 📞 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'pagamentos'"

**Solução:**
```bash
# Verificar se app está instalado
ls pagamentos/__init__.py

# Validar INSTALLED_APPS em settings.py
grep "pagamentos" eduangolacore/settings.py

# Se não encontrado, adicionar manualmente
```

### Problema: "Migração pendente"

**Solução:**
```bash
# Executar migrações pendentes
python manage.py migrate

# Verificar status
python manage.py migrate --check

# Se erro, fazer rollback
python manage.py migrate pagamentos zero
python manage.py migrate pagamentos
```

### Problema: "Gateway indisponível"

**Solução:**
```bash
# 1. Verificar conectividade
curl https://api.prontu.io -I

# 2. Validar chave API
echo $PRONTU_API_KEY

# 3. Verificar logs do Django
tail -f /var/log/django.log

# 4. Executar sem gateway (modo teste)
GATEWAY_MOCK=True python manage.py test pagamentos
```

### Problema: "Banco de dados bloqueado"

**Solução:**
```bash
# Remover banco de teste anterior
rm db.sqlite3

# Recriar
python manage.py migrate

# Ou usar banco em memória
python manage.py test pagamentos --keepdb
```

---

## 🎯 Próximos Passos

### Após testes passarem:

1. **Deploy em Staging:**
   ```bash
   git add .
   git commit -m "Add comprehensive E2E payment tests"
   git push origin main
   # Deploy via CI/CD
   ```

2. **Monitoramento:**
   - Configurar alertas de pagamentos falhados
   - Monitorar taxa de sucesso
   - Registrar métricas

3. **Testes em Produção:**
   - Testar com valores reais (começar com pequenos)
   - Monitorar webhooks
   - Validar integrações com cursos

4. **Documentação:**
   - Manter este guia atualizado
   - Documentar mudanças no sistema de pagamentos
   - Treinamento da equipe

---

## 📚 Referências

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Prontu Payment Gateway Docs](https://prontu.io/api/docs)
- [Python Coverage Documentation](https://coverage.readthedocs.io/)

---

## 📝 Notas Importantes

- **Segurança:** Nunca commitar chaves API reais no git
- **Teste Regular:** Executar testes E2E após cada mudança
- **Isolamento:** Usar dados de teste separados
- **Limpeza:** Limpar dados de teste após testes
- **Documentação:** Manter atualizada com mudanças

---

**Última atualização:** 2024-01-28
**Versão:** 1.0
**Status:** ✅ Pronto para uso
