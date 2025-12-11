from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Inscricao

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
            instance.enviar_email_status()
