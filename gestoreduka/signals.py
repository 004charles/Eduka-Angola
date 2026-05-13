from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from .models import CentroDeFormacao, ConviteCentro, Evento, AnuncioCentro
from cursos_app.models import Curso
from cursos_app.utils import notificar_seguidores

@receiver(post_save, sender=CentroDeFormacao)
def criar_convite(sender, instance, created, **kwargs):
    if created:
        convite = ConviteCentro.objects.create(centro=instance)
        try:
            site_domain = getattr(settings, 'SITE_DOMAIN', 'http://127.0.0.1:8000')
            link = f"{site_domain}{reverse('confirmar_cadastro', args=[convite.token])}"
            send_mail(
                subject="Convite para completar cadastro no Edukangola",
                message=f"Olá {instance.nome},\n\nClique no link para completar seu cadastro:\n{link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
            )
        except Exception as e:
            print(f"Erro ao enviar e-mail de convite para {instance.email}: {e}")

@receiver(post_save, sender=Evento)
def notificar_novo_evento(sender, instance, created, **kwargs):
    """Notifica seguidores quando um novo evento é criado"""
    if created:
        notificar_seguidores(instance, tipo_conteudo='EVENTO')

@receiver(post_save, sender=AnuncioCentro)
def notificar_novo_anuncio(sender, instance, created, **kwargs):
    """Notifica seguidores quando um novo anúncio é publicado"""
    if created:
        notificar_seguidores(instance, tipo_conteudo='ANUNCIO')

@receiver(post_save, sender=Curso)
def notificar_novo_curso(sender, instance, created, **kwargs):
    """Notifica seguidores quando um novo curso é publicado (e marcado como publicado)"""
    if created and instance.publicado:
        notificar_seguidores(instance, tipo_conteudo='CURSO')
    elif not created and instance.publicado:
        # Aqui poderíamos checar se o estado 'publicado' mudou de False para True
        # mas para simplificar, vamos notificar seguidores.
        pass
