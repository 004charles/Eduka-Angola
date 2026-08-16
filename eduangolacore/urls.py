from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from core import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf.urls.i18n import i18n_patterns
from rest_framework import routers
from cursos_app.api_views import CourseViewSet, CategoryViewSet
from cursovideoapp.api_views import CursoVideoViewSet, ExercicioViewSet, AulaViewSet
from usuarios.api_views import AlunoViewSet
from gestoreduka.api_views import (
    CentroViewSet, ParceriaViewSet, CandidaturaExternaViewSet,
    CentroPlanosView, CentroCandidaturaRequestView, CentroCandidaturaVerifyView, CentroCandidaturaConfirmView, CentroCandidaturaCompleteView,
)
from blog.api_views import PostViewSet
# from estagio.api_views import EstagioViewSet
from django.views.decorators.csrf import csrf_exempt
from usuarios import views as usuarios_views
from django.views.i18n import set_language
from django.views.generic import TemplateView

router = routers.DefaultRouter()
router.register(r'cursos', CourseViewSet)
router.register(r'categorias', CategoryViewSet)
router.register(r'video-cursos', CursoVideoViewSet)
router.register(r'exercicios', ExercicioViewSet)
router.register(r'alunos', AlunoViewSet, basename='alunos')
router.register(r'centros', CentroViewSet, basename='centros')
router.register(r'parcerias', ParceriaViewSet, basename='parcerias')
router.register(r'candidaturas', CandidaturaExternaViewSet, basename='candidaturas')
router.register(r'aulas', AulaViewSet, basename='aulas')
router.register(r'blog', PostViewSet, basename='blog')
# router.register(r'estagios', EstagioViewSet, basename='estagios')




urlpatterns = [
    # path('ckeditor/', include('ckeditor_uploader.urls')),
    path('admin/', admin.site.urls),

    path('', views.index, name = 'index'),
    path('api/public/home/', views.public_home_data, name='api_public_home_data'),
    path('api/public/faq/', views.public_faq, name='api_public_faq'),
    path('api/public/comunidade/depoimentos/', views.public_platform_testimonial_submit, name='api_public_platform_testimonial_submit'),
    path('api/public/eventos/', include('eventos_marketplace.urls')),
    path('api/public/centros/<int:centro_id>/', views.public_center_profile, name='api_public_center_profile'),
    path('api/public/centros/planos/', CentroPlanosView.as_view(), name='api_public_centro_planos'),
    path('api/public/video-cursos/<slug:slug>/', views.public_video_course_detail, name='api_public_video_course_detail'),
    path('api/public/biblioteca/', include('biblioteca.urls')),
    path('api/react/recomendacoes/', views.react_course_recommendations, name='api_react_course_recommendations'),
    path('api/react/aluno/dashboard/', views.react_student_dashboard, name='api_react_student_dashboard'),
    path('auth/api/react/aluno/favoritos/', views.react_student_favorites, name='react_student_favorites'),
    path('auth/api/react/aluno/favoritos/alternar/', views.react_student_favorite_toggle, name='react_student_favorite_toggle'),
    path('auth/api/react/aluno/preferencias/', views.react_student_preferences, name='react_student_preferences'),
    path('auth/api/react/aluno/preferencias/actualizar/', views.react_student_preferences_update, name='react_student_preferences_update'),
    path('api/react/video-cursos/<slug:slug>/sala/', views.react_video_learning, name='api_react_video_learning'),
    path('api/react/video-cursos/<slug:slug>/aulas/<int:aula_id>/nota/', views.react_video_note, name='api_react_video_note'),
    path('api/react/video-cursos/<slug:slug>/aulas/<int:aula_id>/duvida/', views.react_video_comment, name='api_react_video_comment'),
    path('api/react/video-cursos/<slug:slug>/aulas/<int:aula_id>/ajuda-ia/', views.react_video_ai_answer, name='api_react_video_ai_answer'),
    path('api/react/video-cursos/<slug:slug>/aulas/<int:aula_id>/exercicio/', views.react_video_exercise, name='api_react_video_exercise'),
    path('api/react/video-cursos/<slug:slug>/certificado/', views.react_video_certificate, name='api_react_video_certificate'),
    path('api/react/video-cursos/<slug:slug>/certificado/emitir/', views.react_video_issue_certificate, name='api_react_video_issue_certificate'),
    path('api/react/video-cursos/<slug:slug>/aulas/<int:aula_id>/progresso/', views.react_video_progress, name='api_react_video_progress'),
    path('api/public/centros/candidatura/solicitar/', CentroCandidaturaRequestView.as_view(), name='api_public_centro_candidatura_solicitar'),
    path('api/public/centros/candidatura/verificar/', CentroCandidaturaVerifyView.as_view(), name='api_public_centro_candidatura_verificar'),
    path('api/public/centros/candidatura/confirmar/', CentroCandidaturaConfirmView.as_view(), name='api_public_centro_candidatura_confirmar'),
    path('api/public/centros/candidatura/concluir/', CentroCandidaturaCompleteView.as_view(), name='api_public_centro_candidatura_concluir'),
    path('test-404/', views.erro_404_view, kwargs={'exception': Exception("Teste 404")}),
    path('test-500/', views.erro_500_view),
    path('i18n/setlang/', csrf_exempt(set_language), name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('auth/', include('usuarios.urls')), 
    # path('accounts/', include('allauth.urls')), 
    path('curso_video/', include('cursovideoapp.urls')),
    # path('orientador-ia/', include('cursovideoapp.urls_orientador')), # Desativado no MVP
    path('sobre/', views.sobre, name = 'sobre'),
    path('cursos/', include('cursos_app.urls')),
    path('escolas/', include('escolas.urls')),
    path('gestoreduka/', include('gestoreduka.urls')),
    path('blog/', include('blog.urls')),
    # path('estagio/', include('estagio.urls')), # Desativado no MVP
    path('instrutor/', include('instrutores_app.urls')),
    
    # SHARED API ENDPOINTS
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include(router.urls)),
    path('api/v1/pagamentos/', include('pagamentos.urls')),  # API de pagamentos
    path('centro/', include('centro_formacao.urls')),
    path('contato/', views.contato, name = 'contato'),
    path('api/notificacoes/nao-lidas/', usuarios_views.api_notificacoes_nao_lidas, name='api_notificacoes_nao_lidas_root'),

    path('api/react/pagamentos/resultado/', views.react_payment_result, name='api_react_payment_result'),
    path('api/react/biblioteca/', include('biblioteca.urls')),
    path('pagamento/sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('pagamento/cancelado/', views.pagamento_cancelado, name='pagamento_cancelado'),
    path('faq/', views.faq, name = 'faq'),
    path('fundo-bolsas/', views.fundo_bolsas, name='fundo_bolsas'),
    path('bolsas/', include('bolsas.urls')),
] 

# Adicionar padrões de MEDIA e STATIC
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# O CATCH-ALL explícito foi removido para não quebrar o APPEND_SLASH do Django.
# O Django já usa o handler404 definido abaixo automaticamente.


handler404 = 'core.views.erro_404_view'
handler500 = 'core.views.erro_500_view'
