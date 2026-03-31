from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Licenciatura(models.Model):
    GRAU_CHOICES = [
        ('licenciatura', 'Licenciatura'),
        ('mestrado', 'Mestrado'),
        ('doutoramento', 'Doutoramento'),
        ('ctesp', 'CTeSP'),
    ]
    nome = models.CharField(max_length=200)
    sigla = models.CharField(max_length=20)
    grau = models.CharField(max_length=20, choices=GRAU_CHOICES)
    area_cientifica = models.CharField(max_length=200)
    duracao_anos = models.IntegerField()
    ects_total = models.IntegerField()
    descricao = models.TextField()
    url_lusofona = models.URLField()
    logo = models.ImageField(upload_to='licenciatura/', blank=True, null=True)
    ano_inicio = models.IntegerField()

    def __str__(self):
        return f"{self.sigla} - {self.nome}"

    class Meta:
        verbose_name = 'Licenciatura'
        verbose_name_plural = 'Licenciaturas'


class Docente(models.Model):
    nome = models.CharField(max_length=200)
    url_lusofona = models.URLField()
    foto = models.ImageField(upload_to='docentes/', blank=True, null=True)
    email = models.EmailField()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Docente'
        verbose_name_plural = 'Docentes'


class Tecnologia(models.Model):
    TIPO_CHOICES = [
        ('linguagem', 'Linguagem de Programação'),
        ('framework', 'Framework'),
        ('biblioteca', 'Biblioteca'),
        ('ferramenta', 'Ferramenta'),
        ('base_dados', 'Base de Dados'),
        ('outro', 'Outro'),
    ]
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField()
    logo = models.ImageField(upload_to='tecnologias/', blank=True, null=True)
    url_website = models.URLField(blank=True)
    nivel_interesse = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    ano_inicio = models.IntegerField()
    em_uso = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Tecnologia'
        verbose_name_plural = 'Tecnologias'


class UnidadeCurricular(models.Model):
    SEMESTRE_CHOICES = [
        (1, '1º Semestre'),
        (2, '2º Semestre'),
    ]
    nome = models.CharField(max_length=200)
    sigla = models.CharField(max_length=20)
    ano_curricular = models.IntegerField()
    semestre = models.IntegerField(choices=SEMESTRE_CHOICES)
    ects = models.IntegerField()
    descricao = models.TextField()
    imagem = models.ImageField(upload_to='ucs/', blank=True, null=True)
    codigo = models.CharField(max_length=20)
    ativo = models.BooleanField(default=True)
    licenciatura = models.ForeignKey(
        Licenciatura, on_delete=models.CASCADE, related_name='unidades_curriculares'
    )
    docentes = models.ManyToManyField(Docente, blank=True, related_name='unidades_curriculares')

    def __str__(self):
        return f"{self.sigla} - {self.nome}"

    class Meta:
        verbose_name = 'Unidade Curricular'
        verbose_name_plural = 'Unidades Curriculares'


class Projeto(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    conceitos_aplicados = models.TextField()
    imagem = models.ImageField(upload_to='projetos/', blank=True, null=True)
    video_demo = models.URLField(blank=True)
    repositorio_github = models.URLField(blank=True)
    data_realizacao = models.DateField()
    classificacao = models.DecimalField(max_digits=4, decimal_places=2)
    destaque = models.BooleanField(default=False)
    unidade_curricular = models.ForeignKey(
        UnidadeCurricular, on_delete=models.CASCADE, related_name='projetos'
    )
    tecnologias = models.ManyToManyField(Tecnologia, blank=True, related_name='projetos')

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'


class TFC(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    ano = models.IntegerField()
    autor = models.CharField(max_length=200)
    orientador = models.CharField(max_length=200)
    url_repositorio = models.URLField(blank=True)
    url_documento = models.URLField(blank=True)
    destaque = models.BooleanField(default=False)
    tecnologias = models.ManyToManyField(Tecnologia, blank=True, related_name='tfcs')

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'TFC'
        verbose_name_plural = 'TFCs'


class Competencia(models.Model):
    TIPO_CHOICES = [
        ('tecnica', 'Técnica'),
        ('transversal', 'Transversal'),
        ('soft', 'Soft Skill'),
    ]
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField()
    nivel = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    tecnologias = models.ManyToManyField(Tecnologia, blank=True, related_name='competencias')
    projetos = models.ManyToManyField(Projeto, blank=True, related_name='competencias')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Competência'
        verbose_name_plural = 'Competências'


class Formacao(models.Model):
    TIPO_CHOICES = [
        ('curso', 'Curso'),
        ('workshop', 'Workshop'),
        ('certificacao', 'Certificação'),
        ('mooc', 'MOOC'),
        ('outro', 'Outro'),
    ]
    titulo = models.CharField(max_length=200)
    instituicao = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField()
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    certificado = models.ImageField(upload_to='formacoes/', blank=True, null=True)
    url = models.URLField(blank=True)
    tecnologias = models.ManyToManyField(Tecnologia, blank=True, related_name='formacoes')

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Formação'
        verbose_name_plural = 'Formações'


class MakingOf(models.Model):
    TIPO_CHOICES = [
        ('decisao', 'Decisão'),
        ('erro', 'Erro'),
        ('correcao', 'Correção'),
        ('evolucao', 'Evolução'),
    ]
    titulo = models.CharField(max_length=200)
    entidade_relacionada = models.CharField(max_length=200)
    descricao = models.TextField()
    fotografia = models.ImageField(upload_to='makingof/', blank=True, null=True)
    data = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    uso_ia = models.TextField(blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Making Of'
        verbose_name_plural = 'Making Of'
