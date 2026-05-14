import os
import urllib.request
from django.core.management.base import BaseCommand
from django.core.files import File
from gestoreduka.models import CentroDeFormacao
from cursos_app.models import Curso, Categoria
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings

class Command(BaseCommand):
    help = 'Popula a base de dados com 5 centros e 7 cursos cada.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando povoamento de dados...")

        # Criar Categorias se não existirem
        cats = ["Tecnologia", "Línguas", "Negócios", "Saúde", "Artes"]
        categoria_objs = []
        for cat_name in cats:
            cat, created = Categoria.objects.get_or_create(
                nome=cat_name,
                defaults={'descricao': f'Cursos de {cat_name}', 'slug': slugify(cat_name)}
            )
            categoria_objs.append(cat)
            if created:
                self.stdout.write(f"Categoria {cat_name} criada.")

        # Criar 5 Centros
        centros = [
            ("Centro de Formação Tecnológica de Luanda", "cftl@example.com", "Luanda"),
            ("Instituto de Línguas de Angola", "ila@example.com", "Luanda"),
            ("Academia de Negócios do Kilamba", "ank@example.com", "Luanda"),
            ("Escola de Saúde de Benguela", "esb@example.com", "Benguela"),
            ("Centro de Artes e Ofícios do Huambo", "caoh@example.com", "Huambo"),
        ]

        centro_objs = []
        for nome, email, cidade in centros:
            centro, created = CentroDeFormacao.objects.get_or_create(
                email=email,
                defaults={
                    'nome': nome,
                    'cidade': cidade,
                    'provincia': cidade,
                    'endereco': f'Rua principal de {cidade}',
                    'telefone': '+244900000000',
                    'ativo': True
                }
            )
            centro_objs.append(centro)
            if created:
                self.stdout.write(f"Centro {nome} criado.")
            else:
                self.stdout.write(f"Centro {nome} já existe.")

        # Criar 7 Cursos para cada centro
        cursos_data = [
            ("Introdução à Programação", "Aprenda o básico de programação.", "Tecnologia", 40, 50000),
            ("Inglês Avançado", "Domine o idioma inglês.", "Línguas", 60, 75000),
            ("Gestão de Pequenas Empresas", "Como gerir o seu negócio.", "Negócios", 30, 40000),
            ("Primeiros Socorros", "Técnicas básicas de saúde.", "Saúde", 20, 30000),
            ("Design Gráfico", "Criação de marcas e layouts.", "Artes", 45, 60000),
            ("Desenvolvimento Web com Python", "Crie sites dinâmicos.", "Tecnologia", 50, 80000),
            ("Francês para Negócios", "Fale francês no ambiente corporativo.", "Línguas", 40, 70000),
        ]

        for centro in centro_objs:
            self.stdout.write(f"Cadastrando cursos para {centro.nome}...")
            for i, (titulo, desc, cat_name, carga, preco) in enumerate(cursos_data):
                # Encontrar a categoria
                cat = next((c for c in categoria_objs if c.nome == cat_name), categoria_objs[0])
                
                slug = slugify(f"{titulo}-{centro.id}-{i}")
                
                curso, created = Curso.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'centro': centro,
                        'titulo': f"{titulo} ({centro.nome})",
                        'descricao': desc,
                        'descricao_curta': desc,
                        'carga_horaria': carga,
                        'preco': preco,
                        'categoria': cat,
                        'publicado': True,
                        'ativo': True,
                    }
                )
                
                if created:
                    self.stdout.write(f"  Curso {titulo} criado.")
                    
                    # Baixar imagem
                    try:
                        img_url = f"https://picsum.photos/400/300?random={centro.id}_{i}"
                        img_name = f"curso_{curso.id}.jpg"
                        
                        # Criar diretório media/cursos se não existir
                        media_path = os.path.join(settings.MEDIA_ROOT, 'cursos')
                        if not os.path.exists(media_path):
                            os.makedirs(media_path)
                            
                        file_path = os.path.join(media_path, img_name)
                        
                        # Baixar imagem usando urllib
                        req = urllib.request.Request(
                            img_url, 
                            headers={'User-Agent': 'Mozilla/5.0'}
                        )
                        with urllib.request.urlopen(req) as response, open(file_path, 'wb') as out_file:
                            out_file.write(response.read())
                        
                        # Salvar no modelo
                        with open(file_path, 'rb') as f:
                            curso.imagem.save(img_name, File(f), save=True)
                            
                        self.stdout.write(f"    Imagem de capa baixada para {titulo}.")
                    except Exception as e:
                        self.stdout.write(f"    Erro ao baixar imagem: {e}")
                else:
                    self.stdout.write(f"  Curso {titulo} já existe.")

        self.stdout.write("Povoamento concluído com sucesso!")
