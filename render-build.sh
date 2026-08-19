#!/usr/bin/env sh
set -eu

corepack enable
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend run build
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py collectstatic --noinput
