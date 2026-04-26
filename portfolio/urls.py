from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='portfolio_index'),
    path('licenciatura/', views.licenciatura_view, name='licenciatura'),
    path('docentes/', views.docentes_view, name='docentes'),
    path('ucs/', views.ucs_view, name='ucs'),

    path('projetos/', views.projetos_view, name='projetos'),
    path('projetos/novo/', views.projeto_criar, name='projeto_criar'),
    path('projetos/<int:pk>/editar/', views.projeto_editar, name='projeto_editar'),
    path('projetos/<int:pk>/apagar/', views.projeto_apagar, name='projeto_apagar'),

    path('tecnologias/', views.tecnologias_view, name='tecnologias'),
    path('tecnologias/novo/', views.tecnologia_criar, name='tecnologia_criar'),
    path('tecnologias/<int:pk>/editar/', views.tecnologia_editar, name='tecnologia_editar'),
    path('tecnologias/<int:pk>/apagar/', views.tecnologia_apagar, name='tecnologia_apagar'),

    path('tfcs/', views.tfcs_view, name='tfcs'),

    path('competencias/', views.competencias_view, name='competencias'),
    path('competencias/novo/', views.competencia_criar, name='competencia_criar'),
    path('competencias/<int:pk>/editar/', views.competencia_editar, name='competencia_editar'),
    path('competencias/<int:pk>/apagar/', views.competencia_apagar, name='competencia_apagar'),

    path('formacoes/', views.formacoes_view, name='formacoes'),
    path('formacoes/novo/', views.formacao_criar, name='formacao_criar'),
    path('formacoes/<int:pk>/editar/', views.formacao_editar, name='formacao_editar'),
    path('formacoes/<int:pk>/apagar/', views.formacao_apagar, name='formacao_apagar'),

    path('makingof/', views.makingof_view, name='makingof'),
    path('sobre/', views.sobre_view, name='sobre'),
]
