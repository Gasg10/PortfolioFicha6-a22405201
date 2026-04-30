from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Licenciatura, Docente, UnidadeCurricular, Projeto, Tecnologia, TFC, Competencia, Formacao, MakingOf
from .forms import ProjetoForm, TecnologiaForm, CompetenciaForm, FormacaoForm


def index_view(request):
    return render(request, 'portfolio/index.html')

def licenciatura_view(request):
    licenciaturas = Licenciatura.objects.prefetch_related('unidades_curriculares').all()
    return render(request, 'portfolio/licenciatura.html', {'licenciaturas': licenciaturas})

def docentes_view(request):
    docentes = Docente.objects.prefetch_related('unidades_curriculares').all()
    return render(request, 'portfolio/docentes.html', {'docentes': docentes})

def ucs_view(request):
    ucs = UnidadeCurricular.objects.select_related('licenciatura').prefetch_related('docentes').all()
    return render(request, 'portfolio/ucs.html', {'ucs': ucs})

def projetos_view(request):
    projetos = Projeto.objects.select_related('unidade_curricular').prefetch_related('tecnologias').all()
    return render(request, 'portfolio/projetos.html', {'projetos': projetos})

def tecnologias_view(request):
    tecnologias = Tecnologia.objects.all()
    return render(request, 'portfolio/tecnologias.html', {'tecnologias': tecnologias})

def tfcs_view(request):
    tfcs = TFC.objects.prefetch_related('tecnologias').all()
    return render(request, 'portfolio/tfcs.html', {'tfcs': tfcs})

def competencias_view(request):
    competencias = Competencia.objects.prefetch_related('tecnologias', 'projetos').all()
    return render(request, 'portfolio/competencias.html', {'competencias': competencias})

def formacoes_view(request):
    formacoes = Formacao.objects.prefetch_related('tecnologias').all()
    return render(request, 'portfolio/formacoes.html', {'formacoes': formacoes})

def makingof_view(request):
    makingof = MakingOf.objects.all()
    return render(request, 'portfolio/makingof.html', {'makingof': makingof})


@login_required
def projeto_criar(request):
    form = ProjetoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('projetos')
    return render(request, 'portfolio/projeto_form.html', {'form': form, 'titulo': 'Novo Projeto'})


@login_required
def projeto_editar(request, pk):
    projeto = get_object_or_404(Projeto, pk=pk)
    form = ProjetoForm(request.POST or None, request.FILES or None, instance=projeto)
    if form.is_valid():
        form.save()
        return redirect('projetos')
    return render(request, 'portfolio/projeto_form.html', {'form': form, 'titulo': 'Editar Projeto'})


@login_required
def projeto_apagar(request, pk):
    projeto = get_object_or_404(Projeto, pk=pk)
    if request.method == 'POST':
        projeto.delete()
        return redirect('projetos')
    return render(request, 'portfolio/confirmar_apagar.html', {
        'objeto': projeto,
        'tipo': 'Projeto',
        'cancelar_url': 'projetos'
    })


@login_required
def tecnologia_criar(request):
    form = TecnologiaForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('tecnologias')
    return render(request, 'portfolio/tecnologia_form.html', {'form': form, 'titulo': 'Nova Tecnologia'})


@login_required
def tecnologia_editar(request, pk):
    tecnologia = get_object_or_404(Tecnologia, pk=pk)
    form = TecnologiaForm(request.POST or None, request.FILES or None, instance=tecnologia)
    if form.is_valid():
        form.save()
        return redirect('tecnologias')
    return render(request, 'portfolio/tecnologia_form.html', {'form': form, 'titulo': 'Editar Tecnologia'})


@login_required
def tecnologia_apagar(request, pk):
    tecnologia = get_object_or_404(Tecnologia, pk=pk)
    if request.method == 'POST':
        tecnologia.delete()
        return redirect('tecnologias')
    return render(request, 'portfolio/confirmar_apagar.html', {
        'objeto': tecnologia,
        'tipo': 'Tecnologia',
        'cancelar_url': 'tecnologias'
    })


@login_required
def competencia_criar(request):
    form = CompetenciaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('competencias')
    return render(request, 'portfolio/competencia_form.html', {'form': form, 'titulo': 'Nova Competência'})


@login_required
def competencia_editar(request, pk):
    competencia = get_object_or_404(Competencia, pk=pk)
    form = CompetenciaForm(request.POST or None, instance=competencia)
    if form.is_valid():
        form.save()
        return redirect('competencias')
    return render(request, 'portfolio/competencia_form.html', {'form': form, 'titulo': 'Editar Competência'})


@login_required
def competencia_apagar(request, pk):
    competencia = get_object_or_404(Competencia, pk=pk)
    if request.method == 'POST':
        competencia.delete()
        return redirect('competencias')
    return render(request, 'portfolio/confirmar_apagar.html', {
        'objeto': competencia,
        'tipo': 'Competência',
        'cancelar_url': 'competencias'
    })


@login_required
def formacao_criar(request):
    form = FormacaoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('formacoes')
    return render(request, 'portfolio/formacao_form.html', {'form': form, 'titulo': 'Nova Formação'})


@login_required
def formacao_editar(request, pk):
    formacao = get_object_or_404(Formacao, pk=pk)
    form = FormacaoForm(request.POST or None, request.FILES or None, instance=formacao)
    if form.is_valid():
        form.save()
        return redirect('formacoes')
    return render(request, 'portfolio/formacao_form.html', {'form': form, 'titulo': 'Editar Formação'})


@login_required
def formacao_apagar(request, pk):
    formacao = get_object_or_404(Formacao, pk=pk)
    if request.method == 'POST':
        formacao.delete()
        return redirect('formacoes')
    return render(request, 'portfolio/confirmar_apagar.html', {
        'objeto': formacao,
        'tipo': 'Formação',
        'cancelar_url': 'formacoes'
    })


def sobre_view(request):
    tecnologias = Tecnologia.objects.all().order_by('tipo', 'nome')
    makingof = MakingOf.objects.all().order_by('-data')

    tecnologias_agrupadas = {}
    for tec in tecnologias:
        chave = tec.get_tipo_display()
        if chave not in tecnologias_agrupadas:
            tecnologias_agrupadas[chave] = []
        tecnologias_agrupadas[chave].append(tec)

    return render(request, 'portfolio/sobre.html', {
        'tecnologias_agrupadas': tecnologias_agrupadas,
        'makingof': makingof,
    })
