from django.contrib import admin
from .models import Autor, Livro, CapituloAudio, BibliotecaPessoal


class CapituloAudioInline(admin.TabularInline):
    model = CapituloAudio
    extra = 0
    fields = ("ordem", "titulo", "duracao_segundos", "audio")


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("nome", "pais", "em_destaque")
    list_filter = ("pais", "em_destaque")
    search_fields = ("nome", "biografia")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "categoria", "formato", "gratuito", "estado", "em_destaque", "selecao_semana")
    list_filter = ("estado", "formato", "gratuito", "em_destaque", "selecao_semana", "categoria")
    search_fields = ("titulo", "subtitulo", "autor__nome", "sinopse", "temas")
    prepopulated_fields = {"slug": ("titulo",)}
    list_select_related = ("autor",)
    inlines = (CapituloAudioInline,)
    fieldsets = (
        ("Ficha editorial", {"fields": ("titulo", "slug", "subtitulo", "autor", "editora", "capa", "capa_url", "sinopse", "descricao_curta", "categoria", "temas", "idioma", "paginas", "ano_publicacao")} ),
        ("Acesso digital", {"fields": ("formato", "conteudo_leitura", "excerto", "narrador", "gratuito")} ),
        ("Publicação", {"fields": ("direitos_confirmados", "estado", "publicado_em", "em_destaque", "selecao_semana")} ),
    )


@admin.register(BibliotecaPessoal)
class BibliotecaPessoalAdmin(admin.ModelAdmin):
    list_display = ("usuario", "livro", "guardado", "progresso_leitura", "progresso_audio_segundos", "ultima_atividade")
    list_select_related = ("usuario", "livro")
    search_fields = ("usuario__email", "usuario__nome", "livro__titulo")
    readonly_fields = ("criado_em", "ultima_atividade")
