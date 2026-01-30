from .models import HistoricoNavegacao, VisualizacaoInteligente
from cursos_app.models import Curso
from django.utils import timezone

class InteligenciaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Só processar após a resposta e se o aluno estiver logado
        if request.path.startswith('/admin/') or request.path.startswith('/static/') or request.path.startswith('/media/'):
            return response

        if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
            try:
                from usuarios.models import Aluno
                aluno = request.user.aluno_profile
                aluno_id = aluno.id
                
                # 1. Registrar Histórico Básico
                # Evitar duplicatas rápidas (mesma URL em < 1 min)
                # HistoricoNavegacao.objects.create(...)
                
                # 2. Se for detalhe de curso, registrar VisualizacaoInteligente
                if '/cursos/detalhe/' in request.path:
                    # Tentar extrair ID da URL ou via context se disponível
                    # Ex: /cursos/detalhe/45/
                    parts = request.path.strip('/').split('/')
                    if len(parts) >= 3 and parts[2].isdigit():
                        curso_id = int(parts[2])
                        curso = Curso.objects.filter(id=curso_id).first()
                        if curso:
                            VisualizacaoInteligente.objects.create(
                                aluno_id=aluno_id,
                                item_id=curso_id,
                                tipo='CURSO_PRESENCIAL',
                                categoria=curso.categoria
                            )
                            
                elif '/curso_video/detalhe/' in request.path:
                    # Lógica similar para vídeos EdukaAngola
                    pass
                    
            except Exception:
                pass

        return response
