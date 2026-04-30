from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Artigo, Comentario
from .forms import ArtigoForm, ComentarioForm

def artigos_view(request):
    artigos = Artigo.objects.all().order_by('-data_criacao')
    return render(request, 'artigos/artigos.html', {'artigos': artigos})

def artigo_view(request, pk):
    artigo = get_object_or_404(Artigo, pk=pk)
    form = ComentarioForm()
    if request.method == 'POST' and request.user.is_authenticated:
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.artigo = artigo
            comentario.autor = request.user
            comentario.save()
            return redirect('artigo', pk=pk)
    return render(request, 'artigos/artigo.html', {'artigo': artigo, 'form': form})

@login_required
def artigo_criar(request):
    if not request.user.groups.filter(name='autores').exists():
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    form = ArtigoForm()
    if request.method == 'POST':
        form = ArtigoForm(request.POST, request.FILES)
        if form.is_valid():
            artigo = form.save(commit=False)
            artigo.autor = request.user
            artigo.save()
            return redirect('artigos')
    return render(request, 'artigos/artigo_form.html', {'form': form})

@login_required
def artigo_editar(request, pk):
    artigo = get_object_or_404(Artigo, pk=pk)
    if artigo.autor != request.user:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    form = ArtigoForm(instance=artigo)
    if request.method == 'POST':
        form = ArtigoForm(request.POST, request.FILES, instance=artigo)
        if form.is_valid():
            form.save()
            return redirect('artigo', pk=pk)
    return render(request, 'artigos/artigo_form.html', {'form': form})

@login_required
def like_artigo(request, pk):
    artigo = get_object_or_404(Artigo, pk=pk)
    if request.user in artigo.likes.all():
        artigo.likes.remove(request.user)
    else:
        artigo.likes.add(request.user)
    return redirect('artigo', pk=pk)
