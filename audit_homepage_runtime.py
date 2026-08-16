import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()

from django.db.models import Count, Q
from cursos_app.models import Curso, Categoria, Instrutor
from gestoreduka.models import CentroDeFormacao
from cursovideoapp.models import Curso_video
from blog.models import Post
from estagio.models import Estagio

print('RESUMO_REAL')
print({'cursos_publicados_ativos': Curso.objects.filter(publicado=True, ativo=True).count()})
print({'cursos_destaque': Curso.objects.filter(destaque=True, publicado=True, ativo=True).count()})
print({'cursos_presenciais': Curso.objects.filter(publicado=True, ativo=True, modalidade='PRESENCIAL').count()})
print({'cursos_online': Curso.objects.filter(publicado=True, ativo=True, modalidade='ONLINE').count()})
print({'cursos_hibridos': Curso.objects.filter(publicado=True, ativo=True, modalidade='HIBRIDO').count()})
print({'centros_ativos': CentroDeFormacao.objects.filter(ativo=True).count()})
print({'instrutores_ativos': Instrutor.objects.filter(ativo=True).count()})
print({'video_originais': Curso_video.objects.filter(centro__isnull=True, destaque=True).count()})
print({'video_parceiros': Curso_video.objects.filter(centro__isnull=False, destaque=True).count()})
print({'posts_publicados': Post.objects.filter(status='publicado').count()})
print({'estagios_ativos': Estagio.objects.filter(ativo=True).count()})
print('CATEGORIAS')
for categoria in Categoria.objects.annotate(num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True))).order_by('-num_cursos')[:10]:
    print({'nome': categoria.nome, 'slug': categoria.slug, 'cursos': categoria.num_cursos})
