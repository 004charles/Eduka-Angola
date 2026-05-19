from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from .models import CentroDeFormacao, ConviteCentro, Evento, AnuncioCentro
from cursos_app.models import Curso
from cursos_app.utils import notificar_seguidores
import threading

def _send_mail_async(subject, message, from_email, recipient_list):
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(f"Erro ao enviar e-mail em background: {e}")

@receiver(post_save, sender=CentroDeFormacao)
def criar_convite(sender, instance, created, **kwargs):
    if created:
        convite = ConviteCentro.objects.create(centro=instance)
        try:
            site_domain = getattr(settings, 'SITE_DOMAIN', 'http://127.0.0.1:8000')
            link = f"{site_domain}{reverse('confirmar_cadastro', args=[convite.token])}"
            
            t = threading.Thread(
                target=_send_mail_async,
                args=(
                    "Convite para completar cadastro no Edukangola",
                    f"Olá {instance.nome},\n\nClique no link para completar seu cadastro:\n{link}",
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email]
                )
            )
            t.start()
        except Exception as e:
            print(f"Erro ao processar e-mail de convite para {instance.email}: {e}")

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

from django.db.models.signals import pre_save

@receiver(pre_save, sender=Curso)
def pre_salvar_curso(sender, instance, **kwargs):
    """Rastreia se o estado de publicação do curso mudou"""
    if instance.id:
        try:
            old_instance = Curso.objects.get(id=instance.id)
            instance._was_publicado = old_instance.publicado
        except Curso.DoesNotExist:
            instance._was_publicado = False
    else:
        instance._was_publicado = False

@receiver(post_save, sender=Curso)
def notificar_novo_curso(sender, instance, created, **kwargs):
    """Notifica seguidores quando um novo curso é publicado (e marcado como publicado)"""
    was_publicado = getattr(instance, '_was_publicado', False)
    if (created and instance.publicado) or (not created and instance.publicado and not was_publicado):
        notificar_seguidores(instance, tipo_conteudo='CURSO')
