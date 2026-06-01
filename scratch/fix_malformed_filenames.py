import os
import glob

fonts_dir = r"c:\Users\Muquissi\Documents\Eduka-Angola\static\metronic\assets\vendors\keenicons\fonts"

if os.path.exists(fonts_dir):
    print("Diretorio de fontes encontrado!")
    for filename in os.listdir(fonts_dir):
        filepath = os.path.join(fonts_dir, filename)
        if os.path.isfile(filepath):
            # Procura por caracteres estranhos como  or ?
            if "" in filename or "?" in filename:
                new_filename = filename.split("")[0].split("?")[0]
                new_filepath = os.path.join(fonts_dir, new_filename)
                
                safe_old = filename.encode('ascii', errors='ignore').decode('ascii')
                safe_new = new_filename.encode('ascii', errors='ignore').decode('ascii')
                print(f"Renomeando: {safe_old} -> {safe_new}")
                try:
                    # Se o arquivo de destino ja existir, remova-o primeiro
                    if os.path.exists(new_filepath):
                        os.remove(new_filepath)
                    os.rename(filepath, new_filepath)
                    print("Renomeado com sucesso!")
                except Exception as e:
                    print(f"Erro ao renomear: {e}")
else:
    print("Diretorio de fontes nao encontrado.")
