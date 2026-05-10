import os
import django
import sys

# Configurar ambiente Django
sys.path.append('/home/carlos/Eduka-Angola')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from cursovideoapp.models import Aula
from cursovideoapp.utils import fetch_youtube_metadata

def fix_all_durations():
    print("Iniciando a reparação de durações estáticas (0min)...")
    aulas_sem_duracao = Aula.objects.filter(duracao_segundos=0)
    total = aulas_sem_duracao.count()
    print(f"Encontradas {total} aulas para processar.")
    
    sucesso = 0
    falha = 0
    
    for aula in aulas_sem_duracao:
        if aula.video_url:
            print(f"Processando: {aula.titulo} ({aula.video_url})")
            try:
                metadata = fetch_youtube_metadata(aula.video_url)
                if metadata and metadata.get('duracao_segundos'):
                    aula.duracao_segundos = metadata['duracao_segundos']
                    # Também atualizar título/descrição se estiverem vazios
                    if not aula.titulo:
                        aula.titulo = metadata.get('titulo', aula.titulo)
                    aula.save()
                    print(f"  [OK] Duração obtida: {aula.duracao_segundos}s")
                    sucesso += 1
                else:
                    print(f"  [AVISO] Não foi possível obter metadados para este vídeo.")
                    falha += 1
            except Exception as e:
                print(f"  [ERRO] Falha ao processar vídeo: {e}")
                falha += 1
        else:
            print(f"  [SKIP] Aula {aula.id} não tem URL de vídeo.")
            falha += 1

    print("\n--- Relatório Final ---")
    print(f"Total processado: {total}")
    print(f"Sucesso: {sucesso}")
    print(f"Falhas/Ignorados: {falha}")

if __name__ == "__main__":
    fix_all_durations()
