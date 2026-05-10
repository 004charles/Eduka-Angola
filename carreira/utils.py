from .models import Skill, AlunoSkill
from cursos_app.models import Curso
from cursovideoapp.models import Curso_video

def get_skill_gap(aluno, vaga):
    """
    Retorna as competências que a vaga exige mas o aluno ainda não possui (comprovadas).
    """
    skills_exigidas = vaga.competencias_exigidas.all()
    skills_aluno = AlunoSkill.objects.filter(aluno=aluno, comprovada=True).values_list('skill', flat=True)
    
    gap = skills_exigidas.exclude(id__in=skills_aluno)
    return gap

def sugerir_cursos_para_gap(aluno, gap_skills):
    """
    Sugere cursos que ensinam as competências que o aluno não possui.
    """
    sugestoes = {
        'cursos_presenciais': [],
        'cursos_video': []
    }
    
    if not gap_skills:
        return sugestoes
        
    # Buscar cursos presenciais que ensinam estas skills
    cursos_p = Curso.objects.filter(skills__in=gap_skills).distinct()[:3]
    sugestoes['cursos_presenciais'] = cursos_p
    
    # Buscar cursos em vídeo que ensinam estas skills
    cursos_v = Curso_video.objects.filter(skills__in=gap_skills).distinct()[:3]
    sugestoes['cursos_video'] = cursos_v
    
    return sugestoes
