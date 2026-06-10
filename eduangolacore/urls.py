from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from core import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf.urls.i18n import i18n_patterns
from rest_framework import routers
from cursos_app.api_views import CourseViewSet, CategoryViewSet
from cursovideoapp.api_views import CursoVideoViewSet, ExercicioViewSet
from django.views.decorators.csrf import csrf_exempt
from django.views.i18n import set_language
from django.views.generic import TemplateView

router = routers.DefaultRouter()
router.register(r'cursos', CourseViewSet)
router.register(r'categorias', CategoryViewSet)
router.register(r'video-cursos', CursoVideoViewSet)
router.register(r'exercicios', ExercicioViewSet)



urlpatterns = [
    # path('ckeditor/', include('ckeditor_uploader.urls')),
    path('admin/', admin.site.urls),

    path('', views.index, name = 'index'),
    path('test-404/', views.erro_404_view, kwargs={'exception': Exception("Teste 404")}),
    path('test-500/', views.erro_500_view),
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript'), name='sw.js'),
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    path('i18n/setlang/', csrf_exempt(set_language), name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('auth/', include('usuarios.urls')), 
    # path('accounts/', include('allauth.urls')), 
    path('curso_video/', include('cursovideoapp.urls')),
    path('orientador-ia/', include('cursovideoapp.urls_orientador')), # Atalho limpo
    path('sobre/', views.sobre, name = 'sobre'),
    path('cursos/', include('cursos_app.urls')),
    path('escolas/', include('escolas.urls')),
    path('gestoreduka/', include('gestoreduka.urls')),
    path('blog/', include('blog.urls')),
    path('estagio/', include('estagio.urls')), 
    path('instrutor/', include('instrutores_app.urls')),
    
    # SHARED API ENDPOINTS
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include(router.urls)),
    path('api/v1/pagamentos/', include('pagamentos.urls')),  # API de pagamentos
    path('centro/', include('centro_formacao.urls')),
    path('contato/', views.contato, name = 'contato'),

    path('pagamento/sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('pagamento/cancelado/', views.pagamento_cancelado, name='pagamento_cancelado'),
    path('faq/', views.faq, name = 'faq'),
    path('carreira/', include('carreira.urls')),
    # path('fundo-bolsas/', views.fundo_bolsas, name='fundo_bolsas'),
    # path('bolsas/', include('bolsas.urls')),
] 

# Adicionar padrões de MEDIA e STATIC
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# O CATCH-ALL explícito foi removido para não quebrar o APPEND_SLASH do Django.
# O Django já usa o handler404 definido abaixo automaticamente.


handler404 = 'core.views.erro_404_view'
handler500 = 'core.views.erro_500_view'
