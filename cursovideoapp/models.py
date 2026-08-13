import uuid
from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import os
from datetime import timedelta
from usuarios.models import Aluno
from cursos_app.models import Categoria, Instrutor

class Curso_video(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    instrutor = models.ForeignKey(Instrutor, on_delete=models.CASCADE, related_name="cursos_video", null=True, blank=True)
    centro = models.ForeignKey('gestoreduka.CentroDeFormacao', on_delete=models.CASCADE, related_name="cursos_video_centro", null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="cursos_video")
    data_publicacao = models.DateTimeField(auto_now_add=True, db_index=True)
    capa = models.ImageField(upload_to="cursos/capas/", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    inscritos = models.ManyToManyField('usuarios.Aluno', related_name='cursos_inscritos_video', blank=True)
    destaque = models.BooleanField(default=False, db_index=True)
    
    # Novos campos para monetização e origem
    is_pago = models.BooleanField(default=False, verbose_name=_("Curso Pago?"), db_index=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Preço (KZ)"))
    is_original_edukangola = models.BooleanField(default=False, verbose_name=_("Original EdukAngola?"), help_text=_("Indica se o vídeo-curso foi produzido pela própria plataforma EdukAngola."), db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def total_inscritos(self):
        return self.inscritos.count()

    @property
    def get_imagem_url(self):
        """Retorna a URL da capa ou a imagem padrão caso esteja ausente."""
        if self.capa and hasattr(self.capa, 'url'):
            try:
                return self.capa.url
            except Exception:
                pass
        from django.templatetags.static import static
        return static('assets/images/course/course-01.jpg')

    @property
    def modalidade(self):
        return 'ONLINE'

    @property
    def get_modalidade_display(self):
        return 'Online'

    @property
    def is_gratuito(self):
        return not self.is_pago

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('cursovideoapp:detalhe_curso', kwargs={'slug': self.slug})
    
    def duracao_total_segundos(self):
        return sum(aula.duracao_segundos for aula in self.aulas.all() if aula.duracao_segundos)

    def duracao_total(self):
        total_segundos = self.duracao_total_segundos()
        if total_segundos == 0:
            return None
        horas, remainder = divmod(total_segundos, 3600)
        minutos, segundos = divmod(remainder, 60)
        
        if horas > 0:
            return f"{int(horas)}h {int(minutos)}min"
        return f"{int(minutos)}min"
    
    def total_visualizacoes(self):
        return sum(aula.visualizacoes for aula in self.aulas.all())
    
    def verificar_conclusao(self, aluno):
        """
        Verifica se o aluno concluiu todas as aulas do curso.
        """
        total_aulas = self.aulas.count()
        if total_aulas == 0:
            return False
            
        aulas_concluidas = ProgressoAula.objects.filter(
            aluno=aluno, 
            aula__curso=self, 
            concluida=True
        ).count()
        
        return aulas_concluidas == total_aulas

    @property
    def get_media_avaliacoes(self):
        """Retorna a média das avaliações do curso em vídeo (apenas comentários principais)"""
        from django.db.models import Avg
        avg = self.comentarios.filter(parent__isnull=True).aggregate(media=Avg('avaliacao'))['media']
        return round(avg, 1) if avg else 0.0

    @property
    def get_distribuicao_avaliacoes(self):
        """Retorna a distribuição percentual das notas de 1 a 5 estrelas"""
        total = self.comentarios.filter(parent__isnull=True).count()
        distribuicao = []
        for i in range(5, 0, -1):
            count = self.comentarios.filter(parent__isnull=True, avaliacao=i).count()
            percentagem = (count / total * 100) if total > 0 else 0
            distribuicao.append({
                'nota': i,
                'count': count,
                'percentagem': int(percentagem)
            })
        return distribuicao

    @property
    def get_relevancia(self):
        """Retorna uma percentagem de relevância baseada nas avaliações e popularidade"""
        media = self.get_media_avaliacoes
        total_inscritos = self.total_inscritos()
        
        # Base de cálculo: 90% (valor base premium)
        score = 90
        
        # Bónus por média de estrelas
        if media > 0:
            score += (media - 3) * 2 # Ex: 4.5 estrelas adiciona 3%
        
        # Bónus por popularidade
        if total_inscritos > 100:
            score += 2
        elif total_inscritos > 50:
            score += 1
            
        # Limitar entre 92 e 99
        return min(max(int(score), 92), 99)

    @property
    def get_video_quality(self):
        """Retorna a qualidade do vídeo baseada no curso (simplificado)"""
        # Por agora retorna Full HD como padrão se houver aulas, 
        # mas pode ser expandido para verificar metadados reais futuramente.
        if self.aulas.exists():
            return "Full HD"
        return "HD"

    def __str__(self):
        return self.titulo

class Aula(models.Model):
    curso = models.ForeignKey(Curso_video, on_delete=models.CASCADE, related_name="aulas", null=True)
    titulo = models.CharField(max_length=200)
    video_url = models.URLField(
        _('URL do Vídeo'), 
        max_length=500, 
        blank=True, 
        null=True,
        help_text="Link do YouTube, Vimeo ou ficheiro de vídeo externo"
    )
    ordem = models.PositiveIntegerField(default=0, db_index=True)
    duracao_segundos = models.PositiveIntegerField(default=0, help_text="Duração em segundos")
    visualizacoes = models.PositiveIntegerField(default=0, db_index=True)
    descricao = models.TextField(blank=True, null=True, verbose_name=_("Descrição da Aula"))
    resumo_ia = models.TextField(blank=True, null=True, verbose_name=_("Resumo da IA"))
    requer_conclusao_anterior = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        # Automação via API do YouTube
        if self.video_url and ("youtube.com" in self.video_url or "youtu.be" in self.video_url):
            # Só buscar se o título estiver vazio ou a duração for 0
            if not self.titulo or self.duracao_segundos == 0:
                from .utils import fetch_youtube_metadata
                metadata = fetch_youtube_metadata(self.video_url)
                if metadata:
                    if not self.titulo:
                        self.titulo = metadata['titulo']
                    if not self.descricao:
                        self.descricao = metadata['descricao']
                    if self.duracao_segundos == 0:
                        self.duracao_segundos = metadata['duracao_segundos']
        
        super().save(*args, **kwargs)

    def duracao_formatada(self):
        if self.duracao_segundos:
            minutos, segundos = divmod(self.duracao_segundos, 60)
            horas, minutos = divmod(minutos, 60)
            
            if horas > 0:
                return f"{int(horas)}:{int(minutos):02d}:{int(segundos):02d}"
            return f"{int(minutos)}:{int(segundos):02d}"
        return "0:00"
    
    def __str__(self):
        return f"{self.ordem} - {self.titulo}"

class ProgressoAula(models.Model):
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, null=True)
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, null=True)
    concluida = models.BooleanField(default=False, db_index=True)
    tempo_assistido = models.PositiveIntegerField(default=0, help_text="Tempo assistido em segundos")
    data_ultimo_acesso = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        unique_together = ['aluno', 'aula']
    
    def progresso_percentual(self):
        if self.aula.duracao_segundos > 0:
            return min(100, int((self.tempo_assistido / self.aula.duracao_segundos) * 100))
        return 0

class Certificado(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='certificados')
    curso = models.ForeignKey(Curso_video, on_delete=models.CASCADE, related_name='certificados_emitidos')
    data_emissao = models.DateTimeField(auto_now_add=True)
    codigo_verificacao = models.CharField(max_length=20, unique=True, blank=True)
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EMITIDO', 'Emitido'),
        ('REJEITADO', 'Rejeitado')
    ]
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='EMITIDO')
    aprovado_por = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='certificados_aprovados')
    
    # Novos campos para avaliação
    nota_final = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name=_("Nota Final"))
    total_exercicios_concluidos = models.IntegerField(default=0, verbose_name=_("Total de Exercícios Concluídos"))
    analise_ia_competencias = models.TextField(blank=True, null=True, verbose_name=_("Perfil de Competências (IA)"))
    
    class Meta:
        unique_together = ('aluno', 'curso')
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'

    def save(self, *args, **kwargs):
        if not self.codigo_verificacao:
            self.codigo_verificacao = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificado - {self.aluno.nome} - {self.curso.titulo}"

class FavoritoCursoVideo(models.Model):
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='favoritos_video')
    curso = models.ForeignKey(Curso_video, on_delete=models.CASCADE, related_name='favoritado_por')
    data_adicao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favorito Curso Vídeo'
        verbose_name_plural = 'Favoritos Cursos Vídeo'
        unique_together = ('aluno', 'curso')
        ordering = ['-data_adicao']
class NotaAula(models.Model):
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='notas_video')
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='notas_alunos')
    conteudo = models.TextField(verbose_name=_("Conteúdo da Nota"))
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('aluno', 'aula')
        verbose_name = 'Nota de Aula'
        verbose_name_plural = 'Notas de Aula'

    def __str__(self):
        return f"Nota: {self.aluno.nome} - {self.aula.titulo}"
class ComentarioAula(models.Model):
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='comentarios_aulas', null=True, blank=True)
    instrutor = models.ForeignKey('cursos_app.Instrutor', on_delete=models.CASCADE, related_name='respostas_aulas', null=True, blank=True)
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name='comentarios')
    texto = models.TextField(verbose_name=_("Dúvida ou Comentário"))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respostas')
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comentário de Aula'
        verbose_name_plural = 'Comentários de Aula'
        ordering = ['data_criacao'] # Ordem cronológica para conversas

    def __str__(self):
        autor = self.aluno.nome if self.aluno else self.instrutor.nome
        return f"{autor} em {self.aula.titulo}"

    def __str__(self):
        return f"{self.aluno.nome} - {self.curso.titulo}"

class AvisoCurso(models.Model):
    curso = models.ForeignKey(Curso_video, on_delete=models.CASCADE, related_name="avisos")
    titulo = models.CharField(max_length=200, verbose_name=_("Assunto"))
    mensagem = models.TextField(verbose_name=_("Mensagem"))
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Aviso do Curso'
        verbose_name_plural = 'Avisos do Curso'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Aviso: {self.titulo} - {self.curso.titulo}"

class MaterialCurso(models.Model):
    curso = models.ForeignKey(Curso_video, on_delete=models.CASCADE, related_name="materiais_gerais")
    titulo = models.CharField(max_length=200, verbose_name=_("Nome do Recurso"))
    arquivo = models.FileField(
        upload_to="cursos/materiais_gerais/", 
        verbose_name=_("Arquivo"),
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'zip', 'rar', 'txt', 'docx', 'pptx'])]
    )
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Material do Curso'
        verbose_name_plural = 'Materiais do Curso'

    def __str__(self):
        return f"{self.titulo} (Curso: {self.curso.titulo})"

class MaterialAula(models.Model):
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name="materiais")
    titulo = models.CharField(max_length=200, verbose_name=_("Nome do Recurso"))
    arquivo = models.FileField(
        upload_to="cursos/materiais/", 
        verbose_name=_("Arquivo"),
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'zip', 'rar', 'txt', 'docx', 'pptx'])]
    )
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Material de Aula'
        verbose_name_plural = 'Materiais de Aula'

    def __str__(self):
        return f"{self.titulo} ({self.aula.titulo})"

class Exercicio(models.Model):
    aula = models.OneToOneField(Aula, on_delete=models.CASCADE, related_name="exercicio")
    titulo = models.CharField(max_length=200, default="Exercício de Fixação")
    descricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Exercício: {self.aula.titulo}"

class Questao(models.Model):
    exercicio = models.ForeignKey(Exercicio, on_delete=models.CASCADE, related_name="questoes")
    texto = models.TextField()
    explicacao = models.TextField(blank=True, null=True, help_text="Explicada após responder")

    def __str__(self):
        return f"Questão: {self.texto[:50]}..."

class Alternativa(models.Model):
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name="alternativas")
    texto = models.CharField(max_length=500)
    is_correta = models.BooleanField(default=False)

    def __str__(self):
        return self.texto

class ResultadoExercicio(models.Model):
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name="resultados_exercicios")
    exercicio = models.ForeignKey(Exercicio, on_delete=models.CASCADE, related_name="resultados")
    pontuacao = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentagem de acerto (0-100)")
    acertos = models.PositiveIntegerField(default=0)
    total_questoes = models.PositiveIntegerField(default=0)
    data_conclusao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('aluno', 'exercicio')

    def __str__(self):
        return f"{self.aluno.nome} - {self.exercicio.aula.titulo} ({self.pontuacao}%)"

class RespostaEstudante(models.Model):
    resultado = models.ForeignKey(ResultadoExercicio, on_delete=models.CASCADE, related_name="respostas")
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    alternativa_escolhida = models.ForeignKey(Alternativa, on_delete=models.CASCADE)
    correta = models.BooleanField(default=False)

    def __str__(self):
        return f"Resposta de {self.resultado.aluno.nome} para {self.questao.id}"
