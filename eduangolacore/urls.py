from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name = 'index'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('auth/', include('usuarios.urls')), 
    path('curso_video/', include('cursovideoapp.urls')),
    path('sobre/', views.sobre, name = 'sobre'),
    path('cursos/', include('cursos_app.urls')),
    path('gestoreduka/', include('gestoreduka.urls')),
    path('blog/', include('blog.urls')),
    path('estagio/', include('estagio.urls')), 
    path('biblioteca/', include('biblioteca.urls')), 
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'core.views.erro_404_view'
