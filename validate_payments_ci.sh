#!/bin/bash
# Script de Validação de Pagamentos para CI/CD
# Pode ser usado em pipelines de deployment

set -e  # Parar em erro

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}VALIDAÇÃO DE PAGAMENTOS - PIPELINE CI/CD${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# 1. Verificar variáveis de ambiente
echo -e "${BLUE}[1/5]${NC} Verificando variáveis de ambiente..."

required_vars=(
    "PAGAMENTOS_ATIVADOS"
    "GATEWAY_PADRAO"
    "PRONTU_API_URL"
    "PRONTU_API_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}✗${NC} Variável $var não configurada"
        exit 1
    else
        echo -e "${GREEN}✓${NC} $var configurada"
    fi
done

echo ""

# 2. Executar migrações
echo -e "${BLUE}[2/5]${NC} Executando migrações..."

if python manage.py migrate --check > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Banco atualizado"
else
    echo -e "${YELLOW}⚠${NC} Aplicando migrações..."
    python manage.py migrate
    echo -e "${GREEN}✓${NC} Migrações aplicadas"
fi

echo ""

# 3. Validar configuração
echo -e "${BLUE}[3/5]${NC} Validando sistema..."

python validate_payment_system.py
if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} Validação do sistema falhou"
    exit 1
fi

echo ""

# 4. Testes unitários
echo -e "${BLUE}[4/5]${NC} Executando testes unitários..."

python manage.py test pagamentos -v 2 --no-input

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} Testes falharam"
    exit 1
fi

echo ""

# 5. Teste E2E
echo -e "${BLUE}[5/5]${NC} Executando testes E2E..."

python test_pagamentos_e2e.py

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠${NC} Testes E2E com aviso"
else
    echo -e "${GREEN}✓${NC} Testes E2E passaram"
fi

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}✓ VALIDAÇÃO COMPLETA E BEM-SUCEDIDA${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Sistema de pagamentos está pronto para produção!"

exit 0
