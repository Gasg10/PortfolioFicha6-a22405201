from django.contrib import admin
from .models import (
    Licenciatura, Docente, Tecnologia, UnidadeCurricular,
    Projeto, TFC, Competencia, Formacao, MakingOf
)


@admin.register(Licenciatura)
class LicenciaturaAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'nome', 'grau', 'area_cientifica', 'duracao_anos', 'ects_total', 'ano_inicio')
    search_fields = ('nome', 'sigla', 'area_cientifica')
    list_filter = ('grau', 'duracao_anos')


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email')
    search_fields = ('nome', 'email')
    list_filter = ()


@admin.register(Tecnologia)
class TecnologiaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'nivel_interesse', 'ano_inicio', 'em_uso')
    search_fields = ('nome', 'descricao')
    list_filter = ('tipo', 'em_uso', 'nivel_interesse')


@admin.register(UnidadeCurricular)
class UnidadeCurricularAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'nome', 'ano_curricular', 'semestre', 'ects', 'ativo', 'licenciatura')
    search_fields = ('nome', 'sigla', 'codigo')
    list_filter = ('ano_curricular', 'semestre', 'ativo', 'licenciatura')
    filter_horizontal = ('docentes',)


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'unidade_curricular', 'data_realizacao', 'classificacao', 'destaque')
    search_fields = ('titulo', 'descricao', 'conceitos_aplicados')
    list_filter = ('destaque', 'unidade_curricular', 'data_realizacao')
    filter_horizontal = ('tecnologias',)


@admin.register(TFC)
class TFCAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'orientador', 'ano', 'destaque')
    search_fields = ('titulo', 'autor', 'orientador', 'descricao')
    list_filter = ('ano', 'destaque')
    filter_horizontal = ('tecnologias',)


@admin.register(Competencia)
class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'nivel')
    search_fields = ('nome', 'descricao')
    list_filter = ('tipo', 'nivel')
    filter_horizontal = ('tecnologias', 'projetos')


@admin.register(Formacao)
class FormacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'instituicao', 'tipo', 'data_inicio', 'data_fim')
    search_fields = ('titulo', 'instituicao', 'descricao')
    list_filter = ('tipo', 'instituicao', 'data_inicio')
    filter_horizontal = ('tecnologias',)


@admin.register(MakingOf)
class MakingOfAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'entidade_relacionada', 'data')
    search_fields = ('titulo', 'descricao', 'entidade_relacionada')
    list_filter = ('tipo', 'data')
