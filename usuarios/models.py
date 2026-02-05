from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.contrib.gis.db import models as gis_models
from django.utils.safestring import mark_safe
# Note: CentroDeFormacao will be imported where used to avoid circular imports if needed
# or we can rely on string references.

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        if not password:
            raise ValueError("Superuser deve ter uma senha definida.")

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, nome, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('ALUNO', 'Aluno'),
        ('GESTOR', 'Gestor de Centro'),
        ('BIBLIOTECA', 'Bibliotecário'),
        ('ESCOLA', 'Escola'),
        ('EMPRESA', 'Empresa'),
    ]

    nome = models.CharField(_('Nome Completo'), max_length=100, blank=True, null=True)
    email = models.EmailField(_('E-mail'), unique=True)
    tipo_usuario = models.CharField(_('Tipo de Usuário'), max_length=20, choices=TIPO_USUARIO_CHOICES, default='ALUNO')
    is_active = models.BooleanField(_('Ativo'), default=True)
    is_staff = models.BooleanField(_('Equipe'), default=False)
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True)
    data_atualizacao = models.DateTimeField(_('Data de Atualização'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    objects = UsuarioManager()

    def get_full_name(self):
        return self.nome

    def get_short_name(self):
        return self.nome.split()[0] if self.nome else self.email

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'usuarios'



class Escola(models.Model):
    TIPO_ESCOLA_CHOICES = [
        ('PUBLICA', 'Pública'),
        ('PARTICULAR', 'Particular'),
        ('COMUNITARIA', 'Comunitária'),
    ]
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='escola_profile', null=True, blank=True)
    nome = models.CharField(_('Nome da Escola'), max_length=100)
    codigo_escola = models.CharField(_('Código INEP'), max_length=8, unique=True, blank=True, null=True)
    tipo = models.CharField(_('Tipo de Escola'), max_length=20, choices=TIPO_ESCOLA_CHOICES)
    endereco = models.CharField(_('Endereço'), max_length=255)
    telefone = models.CharField(_('Telefone'), max_length=20)
    # email is now in usuario
    site = models.URLField(_('Site'), blank=True, null=True)
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True)
    ativo = models.BooleanField(_('Ativo'), default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Escola'
        verbose_name_plural = 'Escolas'
        db_table = 'escolas'
        ordering = ['nome']


class Aluno(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='aluno_profile', null=True, blank=True)
    nome = models.CharField(_('Nome Completo'), max_length=100)
    # email and senha are now in usuario
    data_cadastro = models.DateTimeField(_('Data de Cadastro'), default=timezone.now)
    ativo = models.BooleanField(_('Ativo'), default=True)
    
    def __str__(self):
        return f"Aluno: {self.nome}"

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'


class CentroSeguimento(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='centros_seguidos', verbose_name=_('Aluno'))
    centro = models.ForeignKey('gestoreduka.CentroDeFormacao', on_delete=models.CASCADE, related_name='seguidores', verbose_name=_('Centro de Formação'))
    data_seguimento = models.DateTimeField(_('Data do Seguimento'), default=timezone.now)

    class Meta:
        unique_together = ('aluno', 'centro')  # evita duplicações
        verbose_name = _('Seguimento de Centro')
        verbose_name_plural = _('Seguimentos de Centros')

    def __str__(self):
        return f"{self.aluno.nome} segue {self.centro.nome}"


        

class PerfilAluno(models.Model):
    aluno = models.OneToOneField('Aluno', on_delete=models.CASCADE, related_name='perfil')
    imagem = models.ImageField(_('Imagem de Perfil'), upload_to='perfil_alunos/', null=True, blank=True)
    foto_de_perfil = models.ImageField(_('Foto de Perfil'), upload_to='fotos_perfil/', null=True, blank=True)
    biografia = models.TextField(_('Biografia'), blank=True)
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True, null=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True, null=True)
    github = models.URLField(_('GitHub'), blank=True, null=True)
    criado_em = models.DateTimeField(default=timezone.now)

    from django.conf import settings
    if 'django.contrib.gis' in settings.INSTALLED_APPS and not settings.DATABASES['default']['ENGINE'].endswith('sqlite3'):
        localizacao = gis_models.PointField(
            _('Localização Geográfica'),
            geography=True,
            blank=True,
            null=True,
            srid=4326
        )
    else:
        localizacao = models.CharField(
            _('Localização (Fallback)'),
            max_length=100,
            blank=True,
            null=True
        )

    def __str__(self):
        return f"Perfil de {self.aluno.nome}"

    def get_foto_perfil_url(self):
        """Retorna a URL da foto de perfil ou None se não existir"""
        if self.foto_de_perfil:
            return self.foto_de_perfil.url
        elif self.imagem:
            return self.imagem.url
        return None

    def get_foto_ou_inicial(self):
        """Retorna a foto de perfil ou a inicial do nome"""
        foto_url = self.get_foto_perfil_url()
        if foto_url:
            return f'<img src="{foto_url}" alt="{self.aluno.nome}" class="rounded-circle" style="width: 40px; height: 40px; object-fit: cover;">'
        else:
            inicial = self.aluno.nome[0].upper() if self.aluno.nome else 'A'
            return f'<div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">{inicial}</div>'

    def get_foto_ou_inicial_html(self, size=40):
        """Retorna HTML para exibir foto ou inicial com tamanho personalizado"""
        foto_url = self.get_foto_perfil_url()
        if foto_url:
            return f'<img src="{foto_url}" alt="{self.aluno.nome}" class="rounded-circle" style="width: {size}px; height: {size}px; object-fit: cover;">'
        else:
            inicial = self.aluno.nome[0].upper() if self.aluno.nome else 'A'
            return f'<div class="rounded-circle bg-main-600 text-white d-flex align-items-center justify-content-center fw-bold" style="width: {size}px; height: {size}px; font-size: {size*0.4}px;">{inicial}</div>'

    def get_inicial_nome(self):
        """Retorna apenas a inicial do nome"""
        return self.aluno.nome[0].upper() if self.aluno.nome else 'A'

    class Meta:
        verbose_name = 'Perfil do Aluno'
        verbose_name_plural = 'Perfis dos Alunos'
                
# models.py (adicione ou atualize esta classe)

# usuarios/models.py
class Comentario(models.Model):
    ALUNO_STATUS_CHOICES = [
        ('INS', 'Inscrito'),
        ('COM', 'Concluído'),
        ('AND', 'Em Andamento'),
    ]
    
    aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE, related_name='comentarios')
    curso = models.ForeignKey('cursos_app.Curso', on_delete=models.CASCADE, related_name='comentarios', null=True, blank=True)
    curso_video = models.ForeignKey('cursovideoapp.Curso_video', on_delete=models.CASCADE, related_name='comentarios', null=True, blank=True)
    
    comentario = models.TextField(_('Comentário'), max_length=1000)
    avaliacao = models.IntegerField(
        _('Avaliação'),
        choices=[(1, '1 Estrela'), (2, '2 Estrelas'), (3, '3 Estrelas'), 
                (4, '4 Estrelas'), (5, '5 Estrelas')],
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    status_aluno = models.CharField(
        _('Status do Aluno'),
        max_length=3,
        choices=ALUNO_STATUS_CHOICES,
        default='AND'
    )
    
    data_comentario = models.DateTimeField(_('Data de Comentário'), default=timezone.now)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)
    aprovado = models.BooleanField(_('Aprovado'), default=True)
    resposta = models.TextField(_('Resposta'), blank=True, null=True, max_length=1000)
    resposta_data = models.DateTimeField(_('Data da Resposta'), blank=True, null=True)
    
    # Campos para moderar o conteúdo
    denuncias = models.PositiveIntegerField(_('Denúncias'), default=0)
    editado = models.BooleanField(_('Editado'), default=False)
    
    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['-data_comentario']
        constraints = [
            models.UniqueConstraint(
                fields=['aluno', 'curso'], 
                name='unique_aluno_curso_comentario',
                condition=models.Q(curso__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['aluno', 'curso_video'], 
                name='unique_aluno_curso_video_comentario',
                condition=models.Q(curso_video__isnull=False)
            )
        ]
    
    def __str__(self):
        obj_titulo = self.curso.titulo if self.curso else self.curso_video.titulo if self.curso_video else "N/A"
        return f"Avaliação de {self.aluno.nome} para {obj_titulo}"
    
    def save(self, *args, **kwargs):
        # Verificar se é um update
        if self.pk:
            original = Comentario.objects.get(pk=self.pk)
            if original.comentario != self.comentario or original.avaliacao != self.avaliacao:
                self.editado = True
        
        # Definir status do aluno automaticamente
        if hasattr(self.aluno, 'inscricoes'):
            curso_obj = self.curso or self.curso_video
            if curso_obj:
                # Lógica simplificada: se estiver no banco de inscritos (ou ManyToMany)
                if self.curso:
                    inscricao = self.aluno.inscricoes.filter(curso=self.curso).first()
                else:
                    inscricao = self.curso_video.inscritos.filter(id=self.aluno.id).exists()
                
                if inscricao:
                    if self.curso and hasattr(inscricao, 'status'):
                        if inscricao.status == 'C':
                            self.status_aluno = 'COM'
                        elif inscricao.status == 'A':
                            self.status_aluno = 'AND'
                    else:
                        # Para curso video, por enquanto andamento se estiver inscrito
                        self.status_aluno = 'AND'
        
        super().save(*args, **kwargs)
    
    @property
    def get_estrelas(self):
        """Retorna HTML das estrelas"""
        estrelas = ''
        for i in range(1, 6):
            if i <= self.avaliacao:
                estrelas += '<i class="fa fa-star text-warning"></i>'
            else:
                estrelas += '<i class="fa fa-star-o text-muted"></i>'
        return mark_safe(estrelas)
    
    def denunciar(self):
        """Incrementa o contador de denúncias"""
        self.denuncias += 1
        if self.denuncias >= 3:
            self.aprovado = False
        self.save()
    
    def responder(self, resposta_texto):
        """Adiciona uma resposta ao comentário"""
        self.resposta = resposta_texto
        self.resposta_data = timezone.now()
        self.save()
        
class Biblioteca(models.Model):
    TIPO_BIBLIOTECA_CHOICES = [
        ('PUBLICA', 'Pública'),
        ('ESCOLAR', 'escolar'),
        ('UNVERSITARIA', 'universitaria'),
        ('ESPECIALIZADA', 'especializada'),
        ('COMUNITARIA', 'comunitaria'),
    ]
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='biblioteca_profile', null=True, blank=True)
    nome = models.CharField(_('Nome Completo'), max_length=100)
    # email and senha are now in usuario
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True, null=True)
    codigo_registro = models.CharField(_('Codigo de registro'), max_length=100, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    tipo = models.CharField(_('Tipo de Biblioteca'), max_length=50, choices=TIPO_BIBLIOTECA_CHOICES)
    
    def __str__(self):
        return f"Bibliotecário: {self.nome}"

class Empresa(models.Model):
    TIPO_RAMO_ATUACAO = [
        ('TECNOLOGIA_INFORMACAO', 'tecnologia de informacao'),
        ('NEGOCIO', 'negocio'),
        ('LINGUAS', 'linguas'),
        ('ESPECIALIZADA', 'especializada'),
        ('CIENCIAS', 'ciencias'),
        ('ARTES', 'artes'),
        ('ENGENHARIA', 'engenharia'),
        ('SAUDE', 'saude'),
        ('OUTRO', 'outro'),
    ]
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='empresa_profile', null=True, blank=True)
    nome = models.CharField(_('Nome Completo'), max_length=100)
    # email and senha are now in usuario
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True, null=True)
    experiencia_anos = models.IntegerField(_('Anos de Experiência'), default=0)
    nif = models.CharField(_('NIF'), max_length=18, unique=True)
    ramo_atuacao = models.CharField(_('Ramo de Atuação'), max_length=100, choices=TIPO_RAMO_ATUACAO)    
    numero_funcionarios = models.IntegerField(_('Número de Funcionários'))
    
    def __str__(self):
        return f"Empresa: {self.nome}"


    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        db_table = 'empresas'

class CodigoVerificacao(models.Model):
    TIPO_CHOICES = [
        ('CADASTRO', 'Cadastro'),
        ('RECUPERACAO', 'Recuperação de Senha'),
    ]
    
    email = models.EmailField(_('E-mail'))
    codigo = models.CharField(_('Código'), max_length=6)
    tipo = models.CharField(_('Tipo'), max_length=20, choices=TIPO_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Código para {self.email} ({self.tipo})"
