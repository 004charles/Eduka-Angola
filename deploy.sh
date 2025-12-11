#!/bin/bash
echo "🚀 Iniciando deploy da aplicação Django Eduka-Angola..."

# Ativar virtualenv
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Migrar banco de dados
echo "🗂 Aplicando migrações..."
python manage.py migrate

# Coletar arquivos estáticos
echo "🎨 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Rodar com Gunicorn
echo "⚡ Iniciando aplicação com Gunicorn..."
gunicorn --workers 4 --bind 0.0.0.0:8000 eduangolacore.wsgi:application
