from django.db.models.signals import pre_save
from django.dispatch import receiver
import logging
from .models import Inscricao

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Inscricao)
def enviar_email_ao_mudar_status(sender, instance, **kwargs):
    # Verifica se já existe no banco (update) e não é uma nova inscrição
    if instance.pk:
        try:
            inscricao_antiga = Inscricao.objects.get(pk=instance.pk)
        except Inscricao.DoesNotExist:
            return
        
        # Se o status mudou, envia o e-mail
        if inscricao_antiga.status != instance.status:
            try:
                instance.enviar_email_status()
            except Exception as exc:
                # O email é uma notificação secundária; nunca deve impedir
                # a gravação da inscrição ou a sincronização entre plataformas.
                logger.warning('Falha ao enviar email da inscrição %s: %s', instance.pk, exc)
