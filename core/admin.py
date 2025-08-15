from django.contrib import admin
from .models import Galeria

@admin.register(Galeria)
class GaleriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'link', 'criado_em')
    search_fields = ('titulo', 'usuario')
