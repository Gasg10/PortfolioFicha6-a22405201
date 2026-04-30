from django.urls import path
from . import views

urlpatterns = [
    path('', views.artigos_view, name='artigos'),
    path('<int:pk>/', views.artigo_view, name='artigo'),
    path('novo/', views.artigo_criar, name='artigo_criar'),
    path('<int:pk>/editar/', views.artigo_editar, name='artigo_editar'),
    path('<int:pk>/like/', views.like_artigo, name='like_artigo'),
]
