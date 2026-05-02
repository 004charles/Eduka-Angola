from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Curso_video, Aula
from django.contrib.auth.models import Group

class AulaInline(admin.TabularInline):
    model = Aula
    extra = 1

@admin.register(Curso_video)
class Curso_videoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'instrutor', 'categoria', 'data_publicacao', 'import_playlist_link')
    search_fields = ('titulo', 'descricao')
    list_filter = ('categoria', 'instrutor')
    inlines = [AulaInline]
    
    def import_playlist_link(self, obj):
        return format_html(
            '<a class="button" href="/curso_video/curso/{}/importar-playlist-admin/" style="background: #d9534f; color: white;">Importar Playlist</a>',
            obj.id
        )
    import_playlist_link.short_description = "Ação YouTube"

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'titulo', 'curso', 'duracao_formatada')
    list_filter = ('curso',)
    search_fields = ('titulo',)

admin.site.site_header = "Edukangola"
admin.site.site_title = "Edukangola Administração"
admin.site.index_title = "Administração do Site"
admin.site.unregister(Group)