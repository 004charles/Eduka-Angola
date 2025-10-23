from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password
from usuarios.models import Aluno
from cursos_app.models import Instrutor

class Biblioteca(models.Model):
    nome = models.CharField(_('Nome da Biblioteca'), max_length=200)
    email = models.EmailField(_('E-mail'), unique=True)
    senha = models.CharField(_('Senha'), max_length=128)
    data_cadastro = models.DateTimeField(_('Data de Cadastro'), default=timezone.now)
    ativo = models.BooleanField(_('Ativo'), default=True)
    
    def __str__(self):
        return f"Biblioteca: {self.nome}"

    def set_password(self, raw_password):
        self.senha = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.senha)
    
    def save(self, *args, **kwargs):
        if not self.senha.startswith('pbkdf2_sha256$'):
            self.set_password(self.senha)
        super().save(*args, **kwargs)
    
    @property
    def total_livros(self):
        return self.livros.count()
    
    @property
    def total_emprestimos_ativos(self):
        return self.emprestimos.filter(status='ativo').count()
    
    @property
    def total_vendas(self):
        return self.vendas.filter(status='concluida').count()

    class Meta:
        verbose_name = 'Biblioteca'
        verbose_name_plural = 'Bibliotecas'
        ordering = ['nome']

class PerfilBiblioteca(models.Model):
    TIPO_BIBLIOTECA = [
        ('publica', 'Pública'),
        ('universitaria', 'Universitária'),
        ('escolar', 'Escolar'),
        ('comunitaria', 'Comunitária'),
        ('especializada', 'Especializada'),
        ('nacional', 'Nacional'),
        ('municipal', 'Municipal'),
    ]
    
    biblioteca = models.OneToOneField(Biblioteca, on_delete=models.CASCADE, related_name='perfil')
    
    telefone = models.CharField(_('Telefone'), max_length=15)
    telefone_secundario = models.CharField(_('Telefone Secundário'), max_length=15, blank=True, null=True)
    website = models.URLField(_('Website'), blank=True, null=True)
    
    cnpj = models.CharField(_('CNPJ'), max_length=18, unique=True, blank=True, null=True)
    inscricao_estadual = models.CharField(_('Inscrição Estadual'), max_length=20, blank=True, null=True)
    inscricao_municipal = models.CharField(_('Inscrição Municipal'), max_length=20, blank=True, null=True)
    
    endereco = models.TextField(_('Endereço Completo'))
    numero = models.CharField(_('Número'), max_length=10)
    complemento = models.CharField(_('Complemento'), max_length=100, blank=True, null=True)
    bairro = models.CharField(_('Bairro'), max_length=100)
    cidade = models.CharField(_('Cidade'), max_length=100)
    estado = models.CharField(_('Estado'), max_length=2)
    cep = models.CharField(_('CEP'), max_length=9)
    
    tipo = models.CharField(_('Tipo de Biblioteca'), max_length=15, choices=TIPO_BIBLIOTECA, default='publica')
    descricao = models.TextField(_('Descrição da Biblioteca'), blank=True, null=True)
    missao = models.TextField(_('Missão'), blank=True, null=True)
    visao = models.TextField(_('Visão'), blank=True, null=True)
    valores = models.TextField(_('Valores'), blank=True, null=True)
    
    data_fundacao = models.DateField(_('Data de Fundação'), blank=True, null=True)
    horario_funcionamento = models.TextField(_('Horário de Funcionamento'))
    capacidade_publico = models.PositiveIntegerField(_('Capacidade de Público'), default=0)
    area_total = models.DecimalField(_('Área Total (m²)'), max_digits=8, decimal_places=2, default=0)
    
    logo = models.ImageField(_('Logo'), upload_to='logos_bibliotecas/', blank=True, null=True)
    foto_fachada = models.ImageField(_('Foto da Fachada'), upload_to='fachadas_bibliotecas/', blank=True, null=True)
    foto_interna = models.ImageField(_('Foto Interna'), upload_to='internas_bibliotecas/', blank=True, null=True)
    documento_registro = models.FileField(_('Documento de Registro'), upload_to='documentos_bibliotecas/', blank=True, null=True)
    
    facebook = models.URLField(_('Facebook'), blank=True, null=True)
    instagram = models.URLField(_('Instagram'), blank=True, null=True)
    twitter = models.URLField(_('Twitter'), blank=True, null=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True, null=True)
    youtube = models.URLField(_('YouTube'), blank=True, null=True)
    
    aceita_doacoes = models.BooleanField(_('Aceita Doações'), default=False)
    possui_isencao_fiscal = models.BooleanField(_('Possui Isenção Fiscal'), default=False)
    numero_certificado_isencao = models.CharField(_('Número Certificado Isenção'), max_length=50, blank=True, null=True)
    
    banco = models.CharField(_('Banco'), max_length=100, blank=True, null=True)
    agencia = models.CharField(_('Agência'), max_length=10, blank=True, null=True)
    conta_corrente = models.CharField(_('Conta Corrente'), max_length=20, blank=True, null=True)
    pix = models.CharField(_('Chave PIX'), max_length=100, blank=True, null=True)
    
    total_visitantes_ano = models.PositiveIntegerField(_('Total Visitantes/Ano'), default=0)
    media_emprestimos_mes = models.PositiveIntegerField(_('Média Empréstimos/Mês'), default=0)
    orcamento_anual = models.DecimalField(_('Orçamento Anual'), max_digits=12, decimal_places=2, default=0)
    
    max_emprestimos_usuario = models.PositiveIntegerField(_('Máx. Empréstimos por Usuário'), default=5)
    prazo_emprestimo_dias = models.PositiveIntegerField(_('Prazo Empréstimo (dias)'), default=15)
    multa_dia_atraso = models.DecimalField(_('Multa por Dia de Atraso'), max_digits=5, decimal_places=2, default=2.00)
    
    data_criacao_perfil = models.DateTimeField(_('Data Criação Perfil'), auto_now_add=True)
    data_atualizacao_perfil = models.DateTimeField(_('Data Atualização Perfil'), auto_now=True)
    verificado = models.BooleanField(_('Verificado'), default=False)
    
    class Meta:
        verbose_name = 'Perfil da Biblioteca'
        verbose_name_plural = 'Perfis das Bibliotecas'
    
    def __str__(self):
        return f"Perfil - {self.biblioteca.nome}"
    
    @property
    def endereco_completo(self):
        endereco = f"{self.endereco}, {self.numero}"
        if self.complemento:
            endereco += f" - {self.complemento}"
        endereco += f" - {self.bairro}, {self.cidade}/{self.estado} - CEP: {self.cep}"
        return endereco
    
    @property
    def tempo_funcionamento(self):
        if self.data_fundacao:
            from datetime import date
            anos = date.today().year - self.data_fundacao.year
            return f"{anos} anos"
        return "Não informado"

class Autor(models.Model):
    TIPO_AUTOR = [
        ('aluno', 'Aluno'),
        ('instrutor', 'Instrutor'),
        ('externo', 'Autor Externo'),
        ('biblioteca', 'Biblioteca'),
    ]
    
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=TIPO_AUTOR)
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, null=True, blank=True, related_name='biblioteca_autoria_aluno')
    instrutor = models.ForeignKey('cursos_app.Instrutor', on_delete=models.CASCADE, null=True, blank=True, related_name='biblioteca_autoria_instrutor')
    biblioteca = models.ForeignKey('Biblioteca', on_delete=models.CASCADE, null=True, blank=True, related_name='biblioteca_autoria_biblioteca')
    
    biografia = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='autores/', blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    nacionalidade = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    receber_royalties = models.BooleanField(default=True)
    percentual_royalty = models.DecimalField(max_digits=5, decimal_places=2, default=30.00)
    conta_bancaria = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Autor'
        verbose_name_plural = 'Autores'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if self.aluno and not self.nome:
            self.nome = self.aluno.nome
        elif self.instrutor and not self.nome:
            self.nome = self.instrutor.nome
        elif self.biblioteca and not self.nome:
            self.nome = self.biblioteca.nome
        super().save(*args, **kwargs)
    
    @property
    def total_livros(self):
        return self.livros.count()
    
    @property
    def total_vendas(self):
        """Total de vendas dos livros deste autor"""
        try:
            from .models import Venda, ItemVenda  # Import aqui para evitar circular imports
            
            # Correção: Acesse através do relacionamento correto
            return Venda.objects.filter(
                itens__livro__autor=self,  # Corrigido: 'itens' em vez de 'item'
                status='concluida'
            ).distinct().count()
        except Exception as e:
            print(f"Erro em total_vendas: {e}")
            return 0
    
    @property
    def total_royalties(self):
        """Total de royalties do autor"""
        try:
            from .models import Venda
            
            # Correção: Use o campo royalty_autor se existir, ou calcule
            vendas = Venda.objects.filter(
                itens__livro__autor=self,  # Corrigido: 'itens' em vez de 'item'
                status='concluida'
            ).distinct()
            
            total = 0
            for venda in vendas:
                # Se existir um campo royalty_autor na Venda
                if hasattr(venda, 'royalty_autor'):
                    total += venda.royalty_autor
                else:
                    # Calcule os royalties manualmente
                    itens_autor = venda.itens.filter(livro__autor=self)
                    for item in itens_autor:
                        royalty = (item.subtotal * self.percentual_royalty) / 100
                        total += royalty
            
            return total
        except Exception as e:
            print(f"Erro em total_royalties: {e}")
            return 0
    
    @property
    def usuario_associado(self):
        """Retorna o usuário associado ao autor"""
        if self.aluno:
            return self.aluno.usuario
        elif self.instrutor:
            return self.instrutor.usuario
        return None


class CategoriaLivro(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    icone = models.CharField(max_length=50, blank=True, null=True)
    imagem = models.ImageField(upload_to='categoria de Livros/')
    cor = models.CharField(max_length=7, default='#007bff')
    
    class Meta:
        verbose_name = 'Categoria de Livro'
        verbose_name_plural = 'Categorias de LIvros'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

from django.db import models
from django.utils import timezone
from django.db.models import Count
from decimal import Decimal

class LivroManager(models.Manager):
    def disponiveis(self):
        """Livros disponíveis para exibição"""
        return self.filter(status='disponivel', estoque__gt=0)
    
    def mais_populares(self, limite=8):
        """Livros mais populares baseado em engajamento"""
        return self.disponiveis().select_related(
            'autor', 'biblioteca_proprietaria'
        ).prefetch_related(
            'categorias'
        ).order_by('-visualizacoes', '-avaliacao_media', '-data_cadastro')[:limite]
    
    def em_promocao(self, limite=8):
        """Livros em promoção"""
        return self.disponiveis().filter(
            em_promocao=True, 
            desconto_percentual__gt=0
        ).select_related('autor').order_by('-desconto_percentual')[:limite]
    
    def mais_recentes(self, limite=8):
        """Livros mais recentes"""
        return self.disponiveis().select_related('autor').order_by('-data_cadastro')[:limite]
    
    def melhor_avaliados(self, limite=8):
        """Livros melhor avaliados"""
        return self.disponiveis().filter(
            avaliacao_media__gte=3.0,
            total_avaliacoes__gte=3
        ).select_related('autor').order_by('-avaliacao_media', '-total_avaliacoes')[:limite]
    
    def mais_vendidos(self, limite=8):
        """Livros mais vendidos"""
        return self.disponiveis().select_related('autor').order_by('-vendas_totais', '-visualizacoes')[:limite]
    
    def gratuitos(self, limite=8):
        """Livros gratuitos"""
        return self.disponiveis().filter(
            tipo_acesso='gratuito'
        ).select_related('autor').order_by('-visualizacoes', '-avaliacao_media')[:limite]

class Livro(models.Model):
    TIPO_LIVRO = [
        ('fisico', 'Físico'),
        ('digital', 'Digital'),
        ('ambos', 'Físico e Digital'),
    ]
    
    STATUS_LIVRO = [
        ('disponivel', 'Disponível'),
        ('emprestado', 'Emprestado'),
        ('reservado', 'Reservado'),
        ('manutencao', 'Em Manutenção'),
        ('vendido', 'Vendido'),
    ]
    
    TIPO_AUTORIA = [
        ('aluno', 'Aluno'),
        ('instrutor', 'Instrutor'),
        ('externo', 'Autor Externo'),
        ('biblioteca', 'Biblioteca'),
    ]
    
    TIPO_ACESSO = [
        ('gratuito', 'Gratuito'),
        ('pago', 'Pago'),
        ('assinatura', 'Assinatura'),
    ]
    
    titulo = models.CharField(max_length=200)
    subtitulo = models.CharField(max_length=200, blank=True, null=True)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='livros')
    biblioteca_proprietaria = models.ForeignKey(Biblioteca, on_delete=models.CASCADE, related_name='livros')
    tipo_autoria = models.CharField(max_length=10, choices=TIPO_AUTORIA)
    categorias = models.ManyToManyField(CategoriaLivro, related_name='livros')
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    descricao = models.TextField()
    capa = models.ImageField(upload_to='capas_livros/')
    editora = models.CharField(max_length=100)
    ano_publicacao = models.PositiveIntegerField()
    edicao = models.PositiveIntegerField(default=1)
    numero_paginas = models.PositiveIntegerField()
    idioma = models.CharField(max_length=50, default='Português')
    tipo = models.CharField(max_length=10, choices=TIPO_LIVRO, default='fisico')
    status = models.CharField(max_length=15, choices=STATUS_LIVRO, default='disponivel')
    
    tipo_acesso = models.CharField(max_length=15, choices=TIPO_ACESSO, default='gratuito')
    preco = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    preco_promocional = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    em_promocao = models.BooleanField(default=False)
    desconto_percentual = models.PositiveIntegerField(default=0)
    
    estoque = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=5)
    quantidade_total = models.PositiveIntegerField(default=1)
    data_aquisicao = models.DateField(default=timezone.now)
    valor_aquisicao = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    arquivo_digital = models.FileField(upload_to='livros_digitais/', blank=True, null=True)
    amostra_gratuita = models.FileField(upload_to='amostras/', blank=True, null=True)
    
    visualizacoes = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    vendas_totais = models.PositiveIntegerField(default=0)
    emprestimos_totais = models.PositiveIntegerField(default=0)
    avaliacao_media = models.FloatField(default=0)
    total_avaliacoes = models.PositiveIntegerField(default=0)
    
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    # Manager personalizado
    objects = LivroManager()
    
    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'
        ordering = ['-data_cadastro']
    
    def __str__(self):
        return f"{self.titulo} - {self.autor.nome} ({self.biblioteca_proprietaria.nome})"
    
    def save(self, *args, **kwargs):
        # Define tipo_autoria baseado no autor
        if self.autor:
            self.tipo_autoria = self.autor.tipo
        
        # Calcula preço promocional se estiver em promoção
        if self.em_promocao and self.desconto_percentual > 0:
            try:
                from decimal import Decimal
                # Garante que todos os valores são Decimal
                preco = Decimal(str(self.preco)) if not isinstance(self.preco, Decimal) else self.preco
                desconto_percentual = Decimal(str(self.desconto_percentual))
                
                # Calcula o desconto
                desconto = preco * (desconto_percentual / Decimal('100'))
                self.preco_promocional = preco - desconto
                
                # Arredonda para 2 casas decimais
                self.preco_promocional = self.preco_promocional.quantize(Decimal('0.01'))
                
            except (TypeError, ValueError, AttributeError) as e:
                # Em caso de erro, não define preço promocional
                self.preco_promocional = None
                print(f"Erro ao calcular preço promocional: {e}")
        else:
            # Se não está em promoção, limpa o preço promocional
            self.preco_promocional = None
        
        # Garante que campos numéricos têm valores padrão
        if not self.estoque:
            self.estoque = 0
        if not self.quantidade_total:
            self.quantidade_total = 1
        
        super().save(*args, **kwargs)
    
    @property
    def preco_atual(self):
        if self.em_promocao and self.preco_promocional:
            return self.preco_promocional
        return self.preco
    
    @property
    def e_gratuito(self):
        return self.tipo_acesso == 'gratuito'
    
    @property
    def tem_amostra(self):
        return bool(self.amostra_gratuita)
    
    @property
    def estoque_baixo(self):
        return self.estoque <= self.estoque_minimo
    
    @property
    def disponivel_emprestimo(self):
        return self.status == 'disponivel' and self.estoque > 0
    
    @property
    def disponivel_venda(self):
        return self.status == 'disponivel' and self.estoque > 0 and self.tipo_acesso == 'pago'
    
    def atualizar_avaliacao(self):
        avaliacoes = self.avaliacoes.all()
        if avaliacoes.exists():
            self.avaliacao_media = sum([av.rating for av in avaliacoes]) / avaliacoes.count()
            self.total_avaliacoes = avaliacoes.count()
            self.save()

class Carrinho(models.Model):
    aluno = models.OneToOneField(Aluno, on_delete=models.CASCADE, related_name='biblioteca_carrinho')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'
    
    def __str__(self):
        return f"Carrinho - {self.aluno.nome}"
    
    @property
    def total_itens(self):
        return self.itens.count()
    
    @property
    def total_carrinho(self):
        return sum([item.subtotal for item in self.itens.all()])

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    data_adicao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'
        unique_together = ['carrinho', 'livro']
    
    def __str__(self):
        return f"{self.livro.titulo} - {self.quantidade}"
    
    @property
    def subtotal(self):
        return self.livro.preco_atual * self.quantidade

from decimal import Decimal
from django.utils import timezone
import random

class Venda(models.Model):
    STATUS_VENDA = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
        ('reembolsada', 'Reembolsada'),
    ]
    
    METODO_PAGAMENTO = [
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
        ('transferencia', 'Transferência Bancária'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='biblioteca_compras')
    biblioteca = models.ForeignKey(Biblioteca, on_delete=models.CASCADE, related_name='vendas')
    codigo_venda = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=15, choices=STATUS_VENDA, default='pendente')
    metodo_pagamento = models.CharField(max_length=20, choices=METODO_PAGAMENTO)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    royalty_autor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lucro_biblioteca = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    dados_pagamento = models.JSONField(blank=True, null=True)
    data_venda = models.DateTimeField(auto_now_add=True)
    data_pagamento = models.DateTimeField(blank=True, null=True)
    data_confirmacao = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-data_venda']
    
    def __str__(self):
        return f"Venda #{self.codigo_venda} - {self.aluno.nome}"
    
    def save(self, *args, **kwargs):
        # Gera código da venda se não existe
        if not self.codigo_venda:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_str = str(random.randint(1000, 9999))
            self.codigo_venda = f"V{timestamp}{random_str}"
        
        # Garante que subtotal e total não sejam nulos
        if self.subtotal is None:
            self.subtotal = Decimal('0.00')
        
        if self.total is None:
            self.total = Decimal('0.00')
        
        # Salva primeiro para obter o ID
        super().save(*args, **kwargs)
        
        # Agora calcula royalties (após ter ID)
        if self.status == 'concluida' and self.royalty_autor == 0:
            self.calcular_royalties_e_lucro()
    
    def calcular_royalties_e_lucro(self):
        """Calcula royalties para autores e lucro para biblioteca"""
        total_royalties = Decimal('0.00')
        total_lucro = Decimal('0.00')
        
        # Itera sobre os itens da venda
        for item in self.itens.all():
            livro = item.livro
            
            # Garante que os valores não são None
            custo_aquisicao = (livro.valor_aquisicao or Decimal('0.00')) * item.quantidade
            receita_venda = item.subtotal or Decimal('0.00')
            
            # Inicializa royalty
            royalty = Decimal('0.00')
            
            # Calcula royalties se o autor recebe
            if livro.autor and livro.autor.receber_royalties:
                percentual = livro.autor.percentual_royalty or Decimal('0.00')
                royalty = receita_venda * (percentual / Decimal('100'))
                total_royalties += royalty
            
            # Calcula lucro
            lucro_item = receita_venda - custo_aquisicao - royalty
            total_lucro += lucro_item
        
        # Atualiza os campos
        self.royalty_autor = total_royalties
        self.lucro_biblioteca = total_lucro
        
        # Salva apenas os campos atualizados
        super().save(update_fields=['royalty_autor', 'lucro_biblioteca'])
        
class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'
    
    def __str__(self):
        return f"{self.livro.titulo} - {self.quantidade}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.preco_unitario * self.quantidade
        super().save(*args, **kwargs)

class Emprestimo(models.Model):
    STATUS_EMPRESTIMO = [
        ('ativo', 'Ativo'),
        ('devolvido', 'Devolvido'),
        ('atrasado', 'Atrasado'),
        ('renovado', 'Renovado'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='biblioteca_emprestimos')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='emprestimos')
    biblioteca = models.ForeignKey(Biblioteca, on_delete=models.CASCADE, related_name='emprestimos')
    data_emprestimo = models.DateTimeField(auto_now_add=True)
    data_devolucao_prevista = models.DateTimeField()
    data_devolucao_real = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_EMPRESTIMO, default='ativo')
    renovacoes = models.PositiveIntegerField(default=0)
    multa = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = 'Empréstimos'
        ordering = ['-data_emprestimo']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.livro.titulo} ({self.biblioteca.nome})"
    
    def calcular_multa(self):
        if self.status == 'atrasado' and not self.data_devolucao_real:
            dias_atraso = (timezone.now() - self.data_devolucao_prevista).days
            if dias_atraso > 0:
                self.multa = dias_atraso * 2.00
                self.save()

class Reserva(models.Model):
    STATUS_RESERVA = [
        ('ativa', 'Ativa'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='biblioteca_reservas')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='reservas')
    biblioteca = models.ForeignKey(Biblioteca, on_delete=models.CASCADE, related_name='reservas')
    data_reserva = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_RESERVA, default='ativa')
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-data_reserva']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.livro.titulo}"

class Avaliacao(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='biblioteca_avaliacoes')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='avaliacoes')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True, null=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        unique_together = ['aluno', 'livro']
        ordering = ['-data_avaliacao']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.livro.titulo} - {self.rating}★"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.livro.atualizar_avaliacao()

class Favorito(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='biblioteca_favoritos')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='favoritado_por')
    data_adicao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        unique_together = ['aluno', 'livro']
        ordering = ['-data_adicao']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.livro.titulo}"

class HistoricoLeitura(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='biblioteca_historico_leitura')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='historico_leitura')
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_fim = models.DateTimeField(blank=True, null=True)
    pagina_atual = models.PositiveIntegerField(default=0)
    percentual_concluido = models.FloatField(default=0)
    
    class Meta:
        verbose_name = 'Histórico de Leitura'
        verbose_name_plural = 'Históricos de Leitura'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.livro.titulo}"

class Notificacao(models.Model):
    TIPO_NOTIFICACAO = [
        ('emprestimo', 'Empréstimo'),
        ('devolucao', 'Devolução'),
        ('reserva', 'Reserva'),
        ('atraso', 'Atraso'),
        ('novidade', 'Novidade'),
        ('venda', 'Venda'),
        ('promocao', 'Promoção'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='biblioteca_notificacoes')
    biblioteca = models.ForeignKey(Biblioteca, on_delete=models.CASCADE, related_name='notificacoes')
    tipo = models.CharField(max_length=15, choices=TIPO_NOTIFICACAO)
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.titulo}"

class EstoqueBiblioteca(models.Model):
    biblioteca = models.ForeignKey(Biblioteca, on_delete=models.CASCADE, related_name='estoque')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='estoque_bibliotecas')
    quantidade = models.PositiveIntegerField(default=0)
    quantidade_minima = models.PositiveIntegerField(default=5)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Estoque da Biblioteca'
        verbose_name_plural = 'Estoques das Bibliotecas'
        unique_together = ['biblioteca', 'livro']
    
    def __str__(self):
        return f"{self.biblioteca.nome} - {self.livro.titulo} ({self.quantidade})"
    
    @property
    def estoque_baixo(self):
        return self.quantidade <= self.quantidade_minima