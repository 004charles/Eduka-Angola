import os
import django
import sys

# Configurar Django
sys.path.append('/home/carlos/Eduka-Angola')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from inteligencia.ai_utils import gerar_exercicios_ia

def test_ia():
    print("Testando geração de exercícios com IA...")
    aula_titulo = "Introdução ao Python"
    aula_descricao = "Nesta aula vamos aprender os conceitos básicos da linguagem Python, incluindo variáveis, tipos de dados e operadores."
    
    resultado = gerar_exercicios_ia(aula_titulo, aula_descricao)
    
    if "error" in resultado:
        print(f"ERRO: {resultado['error']}")
        if "raw" in resultado:
            print(f"RESPOSTA BRUTA: {resultado['raw']}")
    else:
        print("SUCESSO!")
        import json
        print(json.dumps(resultado, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    test_ia()
