import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
import django

django.setup()

from estagio.models import AreaEstagio, Estagio
from gestoreduka.models import CentroDeFormacao

print("CENTROS")
for centro in CentroDeFormacao.objects.filter(ativo=True).values("id", "nome", "cidade", "provincia").order_by("id"):
    print(centro["id"], centro["nome"], centro["cidade"], centro["provincia"])
print("AREAS")
for area in AreaEstagio.objects.filter(ativa=True).order_by("id"):
    print(area.id, area.nome)
print("ESTAGIOS_EXISTENTES", Estagio.objects.count())
for estagio in Estagio.objects.order_by("id")[:20]:
    print(estagio.id, estagio.titulo, estagio.centro_formacao_id, estagio.ativo)
