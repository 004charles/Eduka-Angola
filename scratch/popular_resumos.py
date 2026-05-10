import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from cursovideoapp.models import Aula
from inteligencia.ai_utils import gerar_resumo_ia

def popular_resumos():
    aulas = Aula.objects.filter(resumo_ia__isnull=True) | Aula.objects.filter(resumo_ia='')
    print(f"Encontradas {aulas.count()} aulas sem resumo. Iniciando geração...")
    
    for aula in aulas:
        if aula.descricao and len(aula.descricao) > 10:
            print(f"Gerando resumo para: {aula.titulo}...")
            resumo = gerar_resumo_ia(aula.titulo, aula.descricao)
            if resumo and not resumo.startswith("Erro:"):
                aula.resumo_ia = resumo
                aula.save()
                print(f"✅ Sucesso!")
            else:
                print(f"❌ Falha na IA para esta aula.")
        else:
            print(f"⚠️ Pulando '{aula.titulo}': descrição muito curta ou vazia.")

if __name__ == "__main__":
    popular_resumos()
