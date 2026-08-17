from django.urls import path, include
from gestoreduka import views
from gestoreduka import views_video
from django.views.generic import RedirectView


urlpatterns = [
    path('api/react/dashboard/', views.react_gestor_dashboard, name='react_gestor_dashboard'),
    path('api/react/cursos/', views.react_gestor_courses, name='react_gestor_courses'),
    path('api/react/cursos/<int:curso_id>/', views.react_gestor_course_detail, name='react_gestor_course_detail'),
    path('api/react/cursos/<int:curso_id>/publicacao/', views.react_gestor_course_publish, name='react_gestor_course_publish'),
    path('api/react/cursos/<int:curso_id>/remover/', views.react_gestor_course_delete, name='react_gestor_course_delete'),
    path('api/react/turmas/', views.react_gestor_classes, name='react_gestor_classes'),
    path('api/react/turmas/<int:turma_id>/', views.react_gestor_class_detail, name='react_gestor_class_detail'),
    path('api/react/turmas/<int:turma_id>/presencas/', views.react_gestor_class_attendance, name='react_gestor_class_attendance'),
    path('api/react/turmas/<int:turma_id>/notas/', views.react_gestor_class_grades, name='react_gestor_class_grades'),
    path('api/react/inscricoes/', views.react_gestor_enrollments, name='react_gestor_enrollments'),
    path('api/react/inscricoes/manual/', views.react_gestor_manual_enrollment, name='react_gestor_manual_enrollment'),
    path('api/react/inscricoes/<int:inscricao_id>/', views.react_gestor_enrollment_detail, name='react_gestor_enrollment_detail'),
    path('api/react/inscricoes/<int:inscricao_id>/certificado/', views.react_gestor_enrollment_certificate, name='react_gestor_enrollment_certificate'),
    path('api/react/formadores/', views.react_gestor_instructors, name='react_gestor_instructors'),
    path('api/react/formadores/<int:instrutor_id>/', views.react_gestor_instructor_detail, name='react_gestor_instructor_detail'),
    path('api/react/filiais/', views.react_gestor_branches, name='react_gestor_branches'),
    path('api/react/filiais/<int:filial_id>/', views.react_gestor_branch_detail, name='react_gestor_branch_detail'),
    path('api/react/perfil/', views.react_gestor_profile, name='react_gestor_profile'),
    path('api/react/perfil/media/', views.react_gestor_profile_media, name='react_gestor_profile_media'),
    path('api/react/perfil/galeria/', views.react_gestor_profile_gallery, name='react_gestor_profile_gallery'),
    path('api/react/perfil/galeria/<int:imagem_id>/', views.react_gestor_profile_gallery_detail, name='react_gestor_profile_gallery_detail'),
    path('api/react/cursos-video/', views_video.react_gestor_video_courses, name='react_gestor_video_courses'),
    path('api/react/cursos-video/<int:curso_id>/', views_video.react_gestor_video_course_detail, name='react_gestor_video_course_detail'),
    path('api/react/cursos-video/<int:curso_id>/aulas/', views_video.react_gestor_video_lessons, name='react_gestor_video_lessons'),
    path('api/react/aulas-video/<int:aula_id>/', views_video.react_gestor_video_lesson_detail, name='react_gestor_video_lesson_detail'),
    path('api/react/certificados-video/', views_video.react_gestor_video_certificates, name='react_gestor_video_certificates'),
    path('api/react/certificados-video/<uuid:certificado_id>/', views_video.react_gestor_video_certificate_detail, name='react_gestor_video_certificate_detail'),
    path('api/react/eventos/', views.react_gestor_events, name='react_gestor_events'),
    path('api/react/eventos/<int:evento_id>/', views.react_gestor_event_detail, name='react_gestor_event_detail'),
    path('api/react/financeiro/', views.react_gestor_finance, name='react_gestor_finance'),
    path('api/react/conversas/', views.react_gestor_conversations, name='react_gestor_conversations'),
    path('api/react/conversas/<int:conversa_id>/', views.react_gestor_conversation_detail, name='react_gestor_conversation_detail'),
    path('api/react/conversas/<int:conversa_id>/mensagens/', views.react_gestor_conversation_message, name='react_gestor_conversation_message'),
    path('api/react/anuncios/', views.react_gestor_announcements, name='react_gestor_announcements'),
    path('api/react/anuncios/<int:anuncio_id>/', views.react_gestor_announcement_detail, name='react_gestor_announcement_detail'),
    path('api/react/comentarios/', views.react_gestor_comments, name='react_gestor_comments'),
    path('api/react/comentarios/<int:comentario_id>/', views.react_gestor_comment_detail, name='react_gestor_comment_detail'),
    path('api/react/estagios/', views.react_gestor_internships, name='react_gestor_internships'),
    path('api/react/estagios/<int:estagio_id>/', views.react_gestor_internship_detail, name='react_gestor_internship_detail'),
    path('api/react/analytics/', views.react_gestor_analytics, name='react_gestor_analytics'),
    path('api/react/assinatura/', views.react_gestor_subscription, name='react_gestor_subscription'),
    path('api/react/alunos/', views.react_gestor_students, name='react_gestor_students'),
    path('api/react/alunos/<int:aluno_id>/', views.react_gestor_student_detail, name='react_gestor_student_detail'),
    path('api/react/filiais/<int:filial_id>/cursos/', views.react_gestor_branch_courses, name='react_gestor_branch_courses'),
    path('', RedirectView.as_view(pattern_name='login_gestor', permanent=False), name='gestoreduka_home'),
    path('dashboard/centro/', views.centro_dashboard, name='centro_dashboard'),
    path('dashboard/seguidores/', views.listar_seguidores, name='listar_seguidores'),
    path('perfil/', views.perfil_institucional_interno, name='perfil_institucional_interno'),
    path("cadastro/confirmar/<uuid:token>/", views.confirmar_cadastro, name="confirmar_cadastro"),
    path('login_gestor/', views.login_gestor, name='login_gestor'),
    path('home/', views.home_centros, name='home_centros'),
    path('api/load_more/', views.api_load_more_centros, name='api_load_more_centros'),
    path('centros/buscar/', views.buscar_centros, name='buscar_centros'),
    path('centros/seguir/<int:centro_id>/', views.seguir_centro, name='seguir_centro'),
    path('logout_gestor/', views.logout_gestor, name = 'logout_gestor'),
    path('configuracoes/', views.configuracao_gestor, name='configuracao_gestor'),
    path('configuracoes/dados/', views.atualizar_dados_pessoais, name='atualizar_dados_pessoais'),
    path('configuracoes/senha/', views.atualizar_senha, name='atualizar_senha'),
    path('configuracoes/redes-sociais/', views.atualizar_redes_sociais, name='atualizar_redes_sociais'),
    path('configuracoes/upload-imagem/', views.upload_imagem_perfil, name='upload_imagem_perfil'),
    path('configuracoes/upload-banner/', views.upload_banner, name='upload_banner'),
    path('cursos/', views.listar_cursos, name='listar_cursos'),
    path('cursos/criar/', views.criar_curso, name='criar_curso'),
    path('cursos/editar/<int:curso_id>/', views.editar_curso, name='editar_curso'),
    path('cursos/publicar/<int:curso_id>/', views.publicar_curso, name='publicar_curso'),
    path('cursos/despublicar/<int:curso_id>/', views.despublicar_curso, name='despublicar_curso'),
    path('cursos/excluir/<int:curso_id>/', views.excluir_curso, name='excluir_curso'),
    path('cursos/<int:curso_id>/overview/', views.curso_overview, name='curso_overview'),
    path('cursos/<int:curso_id>/publicar-final/', views.publicar_curso_final, name='publicar_curso_final'),
    
    # Cursos em Vídeo
    path('cursos-video/', views_video.listar_cursos_video, name='listar_cursos_video'),
    path('cursos-video/criar/', views_video.criar_curso_video, name='criar_curso_video'),
    path('cursos-video/editar/<int:curso_id>/', views_video.editar_curso_video, name='editar_curso_video'),
    path('cursos-video/excluir/<int:curso_id>/', views_video.excluir_curso_video, name='excluir_curso_video'),
    path('cursos-video/<int:curso_id>/aulas/', views_video.gerenciar_aulas_video, name='gerenciar_aulas_video'),
    path('cursos-video/aulas/excluir/<int:aula_id>/', views_video.excluir_aula_video, name='excluir_aula_video'),
    
    # Certificados em Vídeo
    path('certificados-video/', views_video.listar_certificados_video, name='listar_certificados_video'),
    path('certificados-video/status/<int:certificado_id>/', views_video.alterar_status_certificado, name='alterar_status_certificado'),
    path('inscricoes/', views.gerenciar_inscricoes, name='gerenciar_inscricoes'),
    path('inscricoes/validar/', views.validar_inscricao, name='validar_inscricao'),
    path('inscricoes/manual/', views.matricular_aluno_manual, name='matricular_aluno_manual'),
    path('api/integracao/inscricoes/', views.receber_integracao_eduka, name='receber_integracao_eduka'),
    path('inscricoes/<int:inscricao_id>/emitir-certificado/', views.emitir_certificado_manual, name='emitir_certificado_manual'),
    path('assinatura/', views.gerenciar_assinatura, name='gerenciar_assinatura'),
    path('assinatura/assinar-prontu/<int:plano_id>/', views.assinar_plano_prontu, name='assinar_plano_prontu'),
    
    # Analytics
    path('analytics/', views.analytics_centro, name='analytics_centro'),
    
    # Turmas
    path('turmas/', views.gerenciar_turmas, name='gerenciar_turmas'),
    path('turmas/criar/', views.criar_turma, name='criar_turma'),
    path('turmas/editar/<int:turma_id>/', views.editar_turma, name='editar_turma'),
    path('turmas/<int:turma_id>/presencas/', views.gerir_presencas_turma, name='gerir_presencas_turma'),
    path('turmas/<int:turma_id>/notas/', views.gerir_notas_turma, name='gerir_notas_turma'),

    # Filiais
    path('filiais/', views.gerenciar_filiais, name='gerenciar_filiais'),
    path('filiais/criar/', views.criar_filial, name='criar_filial'),
    path('filiais/editar/<int:filial_id>/', views.editar_filial, name='editar_filial'),
    path('filiais/excluir/<int:filial_id>/', views.excluir_filial, name='excluir_filial'),
    path('filiais/atribuir-cursos/<int:filial_id>/', views.atribuir_cursos_filial, name='atribuir_cursos_filial'),
    
    # Instrutores
    path('instrutores/', views.gerenciar_instrutores, name='gerenciar_instrutores'),
    path('instrutores/criar/', views.criar_instrutor, name='criar_instrutor'),
    path('instrutores/editar/<int:instrutor_id>/', views.editar_instrutor, name='editar_instrutor'),
    
    # Eventos
    path('eventos/', views.gerenciar_eventos, name='gerenciar_eventos'),
    path('eventos/criar/', views.criar_evento, name='criar_evento'),
    
    # Estágios
    path('estagios/', views.gerenciar_estagios, name='gerenciar_estagios'),
    path('estagios/criar/', views.criar_estagio, name='criar_estagio'),
    path('estagios/editar/<int:estagio_id>/', views.editar_estagio, name='editar_estagio'),
    
    #--------------------------------url chat-------------------------------
    path('chat/', views.chat_centro, name='chat_centro'),
    path('chat/enviar/', views.enviar_mensagem_centro, name='enviar_mensagem_centro'),
    path('chat/mensagens/<int:conversa_id>/', views.get_mensagens_ajax, name='get_mensagens_ajax'),
    path('chat/digitando/', views.atualizar_status_digitando, name='atualizar_status_digitando'),
    path('chat/eliminar/<int:conversa_id>/', views.eliminar_conversa, name='eliminar_conversa'),




    path('centro/<int:centro_id>/chat/modal/', views.centro_chat_modal, name='centro_chat_modal'),
    path('chat/modal/enviar-mensagem/', views.enviar_mensagem_centro_modal, name='enviar_mensagem_centro_modal'),
    path('chat/modal/atualizar-digitando/', views.atualizar_digitando_modal, name='atualizar_digitando_modal'),
    path('chat/modal/buscar-mensagens/<int:conversa_id>/', views.buscar_mensagens_modal, name='buscar_mensagens_modal'),
    
    # Filiais
    path('filiais/', views.gerenciar_filiais, name='gerenciar_filiais'),
    path('filiais/criar/', views.criar_filial, name='criar_filial'),
    path('filiais/editar/<int:filial_id>/', views.editar_filial, name='editar_filial'),
    
    # Alunos (Motor de Busca e Dossiê)
    path('alunos/', views.gerenciar_alunos, name='gerenciar_alunos'),
    path('alunos/<int:aluno_id>/dossie/', views.dossie_aluno, name='dossie_aluno'),
    path('matriculas/<int:matricula_id>/alterar/', views.alterar_matricula, name='alterar_matricula'),
    
    # Administrativo / Financeiro
    path('financeiro/', views.gerenciar_financeiro, name='gerenciar_financeiro'),
    path('financeiro/recibos/<int:recibo_id>/pdf/', views.descarregar_recibo_presencial, name='descarregar_recibo_presencial'),
    path('centros/seguir/<int:centro_id>/', views.seguir_centro_ajax, name='seguir_centro_ajax'),
    
    # Anúncios Institucionais
    path('dashboard/anuncios/', views.listar_anuncios, name='listar_anuncios'),
    path('dashboard/anuncios/criar/', views.criar_anuncio, name='criar_anuncio'),
    path('dashboard/anuncios/editar/<int:anuncio_id>/', views.editar_anuncio, name='editar_anuncio'),
    path('dashboard/anuncios/excluir/<int:anuncio_id>/', views.excluir_anuncio, name='excluir_anuncio'),
    
    # Comentários e Dúvidas
    path('comentarios/', views.gerenciar_comentarios, name='gerenciar_comentarios'),
    path('comentarios/responder/<int:comentario_id>/', views.responder_comentario, name='responder_comentario'),
]
