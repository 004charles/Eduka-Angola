from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from cursovideoapp.models import Certificado
from usuarios.models import NotificacaoAluno, Aluno
from .models import AlunoSkill, Skill, Vaga

@receiver(post_save, sender=Certificado)
def atribuir_skills_por_certificado(sender, instance, created, **kwargs):
    """
    Atribui automaticamente as competências (skills) ao aluno quando um certificado é gerado.
    """
    if created:
        aluno = instance.aluno
        curso = instance.curso
        
        # Buscar todas as competências associadas a este curso de vídeo
        skills_do_curso = Skill.objects.filter(cursos_video_relacionados=curso)
        
        for skill in skills_do_curso:
            AlunoSkill.objects.get_or_create(
                aluno=aluno,
                skill=skill,
                defaults={'comprovada': True}
            )
            AlunoSkill.objects.filter(aluno=aluno, skill=skill).update(comprovada=True)

@receiver(m2m_changed, sender=Vaga.competencias_exigidas.through)
def notificar_vaga_compativel_m2m(sender, instance, action, **kwargs):
    """
    Notifica alunos compatíveis quando as competências da vaga são definidas/atualizadas.
    """
    if action == "post_add" and instance.status == 'ABERTA':
        skills_vaga = instance.competencias_exigidas.all()
        
        # Buscar alunos com skills compatíveis
        alunos_compativeis = AlunoSkill.objects.filter(
            skill__in=skills_vaga, 
            comprovada=True
        ).values_list('aluno', flat=True).distinct()
        
        for aluno_id in alunos_compativeis:
            try:
                aluno = Aluno.objects.get(id=aluno_id)
                # Evitar duplicatas de notificação para a mesma vaga
                if not NotificacaoAluno.objects.filter(aluno=aluno, link__contains=instance.slug).exists():
                    NotificacaoAluno.objects.create(
                        aluno=aluno,
                        titulo=f"Oportunidade: {instance.titulo}",
                        mensagem=f"Uma nova vaga compatível com o seu perfil foi publicada por {instance.empresa.nome}.",
                        link=f"/carreira/vagas/{instance.slug}/",
                        tipo='CARREIRA'
                    )
            except Aluno.DoesNotExist:
                continue
