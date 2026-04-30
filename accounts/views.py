from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from .forms import RegistoForm

def login_view(request):
    erro = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('portfolio_index')
        else:
            erro = 'Credenciais inválidas.'
    return render(request, 'accounts/login.html', {'erro': erro})

def logout_view(request):
    logout(request)
    return redirect('portfolio_index')

def registo_view(request):
    form = RegistoForm()
    if request.method == 'POST':
        form = RegistoForm(request.POST)
        if form.is_valid():
            user = form.save()
            grupo, _ = Group.objects.get_or_create(name='gestor-portfolio')
            user.groups.add(grupo)
            grupo_autores, _ = Group.objects.get_or_create(name='autores')
            user.groups.add(grupo_autores)
            login(request, user)
            return redirect('portfolio_index')
    return render(request, 'accounts/registo.html', {'form': form})
