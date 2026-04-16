from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name="portfolio_index"),
    path('licenciatura/', views.licenciatura_view, name="licenciatura"),
    path('docentes/', views.docentes_view, name="docentes"),
    path('ucs/', views.ucs_view, name="ucs"),
    path('projetos/', views.projetos_view, name="projetos"),
    path('tecnologias/', views.tecnologias_view, name="tecnologias"),
    path('tfcs/', views.tfcs_view, name="tfcs"),
    path('competencias/', views.competencias_view, name="competencias"),
    path('formacoes/', views.formacoes_view, name="formacoes"),
    path('makingof/', views.makingof_view, name="makingof"),
]
