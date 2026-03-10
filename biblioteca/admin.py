from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import *
from usuarios.widgets import ColorPickerWidget

@admin.register(Biblioteca)
class BibliotecaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'get_email', 'data_cadastro', 'ativo', 'total_livros', 'total_emprestimos_ativos', 'total_vendas']
    list_filter = ['ativo', 'data_cadastro']
    search_fields = ['nome', 'usuario__email']
    readonly_fields = ['total_livros', 'total_emprestimos_ativos', 'total_vendas']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'nome', 'ativo')
        }),
        ('Estatísticas', {
            'fields': ('total_livros', 'total_emprestimos_ativos', 'total_vendas'),
            'classes': ('collapse',)
        }),
    )

    def get_email(self, obj):
        return obj.usuario.email if obj.usuario else "N/A"
    get_email.short_description = 'E-mail'

@admin.register(PerfilBiblioteca)
class PerfilBibliotecaAdmin(admin.ModelAdmin):
    list_display = ['biblioteca', 'tipo', 'cidade', 'estado', 'verificado', 'data_criacao_perfil']
    list_filter = ['tipo', 'estado', 'verificado', 'data_criacao_perfil']
    search_fields = ['biblioteca__nome', 'cidade', 'cnpj']
    readonly_fields = ['endereco_completo', 'tempo_funcionamento']
    fieldsets = (
        ('Biblioteca', {
            'fields': ('biblioteca', 'verificado')
        }),
        ('Informações de Contato', {
            'fields': ('telefone', 'telefone_secundario', 'website')
        }),
        ('Documentos', {
            'fields': ('cnpj', 'inscricao_estadual', 'inscricao_municipal')
        }),
        ('Endereço', {
            'fields': ('endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep')
        }),
        ('Informações Institucionais', {
            'fields': ('tipo', 'descricao', 'missao', 'visao', 'valores')
        }),
        ('Logística', {
            'fields': ('data_fundacao', 'horario_funcionamento', 'capacidade_publico', 'area_total')
        }),
        ('Mídias', {
            'fields': ('logo', 'foto_fachada', 'foto_interna', 'documento_registro')
        }),
        ('Redes Sociais', {
            'fields': ('facebook', 'instagram', 'twitter', 'linkedin', 'youtube')
        }),
        ('Configurações Financeiras', {
            'fields': ('aceita_doacoes', 'possui_isencao_fiscal', 'numero_certificado_isencao')
        }),
        ('Dados Bancários', {
            'fields': ('banco', 'agencia', 'conta_corrente', 'pix')
        }),
        ('Estatísticas', {
            'fields': ('total_visitantes_ano', 'media_emprestimos_mes', 'orcamento_anual')
        }),
        ('Configurações do Sistema', {
            'fields': ('max_emprestimos_usuario', 'prazo_emprestimo_dias', 'multa_dia_atraso')
        }),
        ('Informações Calculadas', {
            'fields': ('endereco_completo', 'tempo_funcionamento'),
            'classes': ('collapse',)
        }),
    )

# admin.py
@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'email', 'total_livros_display', 'total_vendas_display', 'receber_royalties']
    list_filter = ['tipo', 'receber_royalties', 'data_nascimento']
    search_fields = ['nome', 'email', 'nacionalidade']
    readonly_fields = ['total_livros_display', 'total_vendas_display', 'total_royalties_display']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'tipo', 'foto', 'biografia')
        }),
        ('Associações', {
            'fields': ('aluno', 'instrutor', 'biblioteca'),
            'description': 'Associe o autor a um aluno, instrutor ou biblioteca'
        }),
        ('Informações Pessoais', {
            'fields': ('data_nascimento', 'nacionalidade', 'email', 'website')
        }),
        ('Configurações de Royalties', {
            'fields': ('receber_royalties', 'percentual_royalty', 'conta_bancaria')
        }),
        ('Estatísticas', {
            'fields': ('total_livros_display', 'total_vendas_display', 'total_royalties_display'),
            'classes': ('collapse',)
        }),
    )
    
    def total_livros_display(self, obj):
        return obj.total_livros
    total_livros_display.short_description = 'Total de Livros'
    
    def total_vendas_display(self, obj):
        return obj.total_vendas
    total_vendas_display.short_description = 'Vendas Totais'
    
    def total_royalties_display(self, obj):
        return f"kz {obj.total_royalties:.2f}"
    total_royalties_display.short_description = 'Total de Royalties'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra as opções baseadas no tipo"""
        if db_field.name == "aluno":
            kwargs["queryset"] = Aluno.objects.filter(ativo=True)
        elif db_field.name == "instrutor":
            kwargs["queryset"] = Instrutor.objects.filter(ativo=True)
        elif db_field.name == "biblioteca":
            kwargs["queryset"] = Biblioteca.objects.filter(ativo=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(CategoriaLivro)
class CategoriaLivroAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cor', 'imagem_preview']
    search_fields = ['nome']
    fieldsets = (
        ('Informações da Categoria', {
            'fields': ('nome', 'descricao', 'icone', 'cor', 'imagem')
        }),
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'cor':
            kwargs['widget'] = ColorPickerWidget
        return super().formfield_for_dbfield(db_field, **kwargs)
    
    def imagem_preview(self, obj):
        if obj.imagem:
            return mark_safe(f'<img src="{obj.imagem.url}" style="width: 50px; height: 50px; object-fit: cover;" />')
        return "Sem imagem"
    imagem_preview.short_description = 'Preview'


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'biblioteca_proprietaria', 'tipo_acesso', 'preco_atual', 'estoque', 'status', 'vendas_totais']
    list_filter = ['tipo_acesso', 'tipo', 'status', 'em_promocao', 'biblioteca_proprietaria']
    search_fields = ['titulo', 'autor__nome', 'isbn']
    filter_horizontal = ['categorias']
    readonly_fields = ['vendas_totais', 'emprestimos_totais', 'avaliacao_media']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'subtitulo', 'autor', 'biblioteca_proprietaria', 'categorias', 'isbn', 'descricao', 'capa')
        }),
        ('Detalhes da Publicação', {
            'fields': ('editora', 'ano_publicacao', 'edicao', 'numero_paginas', 'idioma')
        }),
        ('Tipo e Status', {
            'fields': ('tipo', 'status', 'tipo_autoria')
        }),
        ('Sistema de Vendas e Acesso', {
            'fields': ('tipo_acesso', 'preco', 'em_promocao', 'desconto_percentual', 'preco_promocional')
        }),
        ('Estoque e Aquisição', {
            'fields': ('estoque', 'estoque_minimo', 'quantidade_total', 'data_aquisicao', 'valor_aquisicao')
        }),
        ('Arquivos', {
            'fields': ('arquivo_digital', 'amostra_gratuita')
        }),
        ('Estatísticas', {
            'fields': ('visualizacoes', 'downloads', 'vendas_totais', 'emprestimos_totais', 'avaliacao_media', 'total_avaliacoes'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'total_itens', 'total_carrinho', 'data_atualizacao']
    readonly_fields = ['total_itens', 'total_carrinho']
    fieldsets = (
        ('Informações do Carrinho', {
            'fields': ('aluno',)
        }),
        ('Estatísticas', {
            'fields': ('total_itens', 'total_carrinho'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ItemCarrinho)
class ItemCarrinhoAdmin(admin.ModelAdmin):
    list_display = ['carrinho', 'livro', 'quantidade', 'subtotal']
    list_filter = ['carrinho__aluno']
    readonly_fields = ['subtotal']
    fieldsets = (
        ('Item do Carrinho', {
            'fields': ('carrinho', 'livro', 'quantidade')
        }),
        ('Valores', {
            'fields': ('subtotal',)
        }),
    )

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['codigo_venda', 'aluno', 'biblioteca', 'status', 'total', 'data_venda']
    list_filter = ['status', 'metodo_pagamento', 'data_venda', 'biblioteca']
    search_fields = ['codigo_venda', 'aluno__nome', 'biblioteca__nome']
    readonly_fields = ['codigo_venda', 'subtotal', 'total', 'royalty_autor', 'lucro_biblioteca']
    fieldsets = (
        ('Informações da Venda', {
            'fields': ('codigo_venda', 'aluno', 'biblioteca', 'status', 'metodo_pagamento')
        }),
        ('Valores', {
            'fields': ('subtotal', 'desconto', 'total', 'royalty_autor', 'lucro_biblioteca')
        }),
        ('Dados da Transação', {
            'fields': ('dados_pagamento', 'data_pagamento', 'data_confirmacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    list_display = ['venda', 'livro', 'quantidade', 'preco_unitario', 'subtotal']
    list_filter = ['venda__status']
    readonly_fields = ['subtotal']
    fieldsets = (
        ('Item da Venda', {
            'fields': ('venda', 'livro', 'quantidade', 'preco_unitario')
        }),
        ('Valores', {
            'fields': ('subtotal',)
        }),
    )

@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'livro', 'biblioteca', 'data_emprestimo', 'data_devolucao_prevista', 'status']
    list_filter = ['status', 'data_emprestimo', 'biblioteca']
    readonly_fields = ['multa']
    fieldsets = (
        ('Informações do Empréstimo', {
            'fields': ('aluno', 'livro', 'biblioteca', 'status')
        }),
        ('Datas', {
            'fields': ('data_emprestimo', 'data_devolucao_prevista', 'data_devolucao_real')
        }),
        ('Detalhes', {
            'fields': ('renovacoes', 'multa'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'livro', 'biblioteca', 'data_reserva', 'status']
    list_filter = ['status', 'data_reserva']
    fieldsets = (
        ('Informações da Reserva', {
            'fields': ('aluno', 'livro', 'biblioteca', 'status')
        }),
        ('Datas', {
            'fields': ('data_reserva', 'data_expiracao')
        }),
    )

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'livro', 'rating', 'data_avaliacao']
    list_filter = ['rating', 'data_avaliacao']
    fieldsets = (
        ('Avaliação', {
            'fields': ('aluno', 'livro', 'rating', 'comentario')
        }),
    )

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'livro', 'data_adicao']
    fieldsets = (
        ('Favorito', {
            'fields': ('aluno', 'livro')
        }),
    )

@admin.register(HistoricoLeitura)
class HistoricoLeituraAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'livro', 'data_inicio', 'percentual_concluido']
    readonly_fields = ['percentual_concluido']
    fieldsets = (
        ('Histórico de Leitura', {
            'fields': ('aluno', 'livro')
        }),
        ('Progresso', {
            'fields': ('pagina_atual', 'percentual_concluido', 'data_fim')
        }),
    )

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'biblioteca', 'tipo', 'titulo', 'lida', 'data_criacao']
    list_filter = ['tipo', 'lida', 'data_criacao', 'biblioteca']
    fieldsets = (
        ('Notificação', {
            'fields': ('aluno', 'biblioteca', 'tipo', 'titulo', 'mensagem', 'lida', 'link')
        }),
    )

@admin.register(EstoqueBiblioteca)
class EstoqueBibliotecaAdmin(admin.ModelAdmin):
    list_display = ['biblioteca', 'livro', 'quantidade', 'estoque_baixo', 'data_atualizacao']
    list_filter = ['biblioteca', 'quantidade']
    readonly_fields = ['estoque_baixo']
    fieldsets = (
        ('Estoque', {
            'fields': ('biblioteca', 'livro', 'quantidade', 'quantidade_minima')
        }),
        ('Status', {
            'fields': ('estoque_baixo',),
            'classes': ('collapse',)
        }),
    )