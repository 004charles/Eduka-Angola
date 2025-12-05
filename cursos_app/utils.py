from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.urls import reverse
from usuarios.models import CentroSeguimento
from cursos_app.models import Curso

def notificar_seguidores(curso):
    seguidores = CentroSeguimento.objects.filter(centro=curso.centro)
    
    imagem_url = f"{settings.SITE_DOMAIN}{curso.imagem.url}" if curso.imagem else ""

    # Pegar até 3 outros cursos do mesmo centro
    outros_raw = Curso.objects.filter(
        centro=curso.centro, publicado=True, ativo=True
    ).exclude(id=curso.id)[:3]

    outros_cursos = []
    for outro in outros_raw:
        outros_cursos.append({
            'titulo': outro.titulo,
            'preco': outro.preco,
            'imagem_url': f"{settings.SITE_DOMAIN}{outro.imagem.url}" if outro.imagem else ""
        })

    for seguidor in seguidores:
        context = {
            'nome_aluno': seguidor.aluno.nome,
            'nome_centro': curso.centro.nome,
            'titulo_curso': curso.titulo,
            'preco': curso.preco,
            'data_inicio': curso.data_inicio,
            'carga_horaria': curso.carga_horaria,
            'nivel': curso.nivel,
            'idioma': curso.idioma,
            'descricao': curso.descricao,
            'imagem_url': imagem_url,
            'site_url': f"{settings.SITE_DOMAIN}{reverse('curso_detalhe', args=[curso.id])}",
            'outros_cursos': outros_cursos,
        }

        html_content = render_to_string('notificacao_novo_curso.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=f"Novo curso em {curso.centro.nome}: {curso.titulo}",
            body=text_content,
            from_email='muquissicarlos@gmail.com',
            to=[seguidor.aluno.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=True)
