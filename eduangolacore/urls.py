from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf.urls.i18n import i18n_patterns
from rest_framework import routers
from cursos_app.api_views import CourseViewSet, CategoryViewSet

router = routers.DefaultRouter()
router.register(r'cursos', CourseViewSet)
router.register(r'categorias', CategoryViewSet)



urlpatterns = [
    # path('ckeditor/', include('ckeditor_uploader.urls')),
    path('admin/', admin.site.urls),

    path('', views.index, name = 'index'),
    path('test-404/', views.erro_404_view, kwargs={'exception': Exception("Teste 404")}),
    path('test-500/', views.erro_500_view),
    path('i18n/', include('django.conf.urls.i18n')),
    path('auth/', include('usuarios.urls')), 
    path('accounts/', include('allauth.urls')), 
    path('curso_video/', include('cursovideoapp.urls')),
    path('sobre/', views.sobre, name = 'sobre'),
    path('cursos/', include('cursos_app.urls')),
    path('gestoreduka/', include('gestoreduka.urls')),
    path('blog/', include('blog.urls')),
    path('estagio/', include('estagio.urls')), 
    
    # SHARED API ENDPOINTS
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include(router.urls)),
    path('centro/', include('centro_formacao.urls')),
    path('contato/', views.contato, name = 'contato'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'core.views.erro_404_view'
handler500 = 'core.views.erro_500_view'
