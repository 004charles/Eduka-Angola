from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name = 'index'),
    path('auth/', include('usuarios.urls')), 
    path('cursos/', include('cursos_app.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'core.views.erro_404_view'
