from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from .models import CentroDeFormacao, ConviteCentro

@receiver(post_save, sender=CentroDeFormacao)
def criar_convite(sender, instance, created, **kwargs):
    if created:
        convite = ConviteCentro.objects.create(centro=instance)

        link = f"http://127.0.0.1:8000{reverse('confirmar_cadastro', args=[convite.token])}"

        send_mail(
            subject="Convite para completar cadastro no Edukangola",
            message=f"Olá {instance.nome},\n\nClique no link para completar seu cadastro:\n{link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
        )
