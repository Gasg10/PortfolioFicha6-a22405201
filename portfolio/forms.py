from django import forms
from .models import Projeto, Tecnologia, Competencia, Formacao


class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = [
            'titulo', 'descricao', 'conceitos_aplicados', 'imagem',
            'video_demo', 'repositorio_github', 'data_realizacao',
            'classificacao', 'destaque', 'unidade_curricular', 'tecnologias'
        ]
        widgets = {
            'data_realizacao': forms.DateInput(attrs={'type': 'date'}),
            'tecnologias': forms.CheckboxSelectMultiple(),
        }


class TecnologiaForm(forms.ModelForm):
    class Meta:
        model = Tecnologia
        fields = [
            'nome', 'tipo', 'descricao', 'logo',
            'url_website', 'nivel_interesse', 'ano_inicio', 'em_uso'
        ]
        widgets = {
            'nivel_interesse': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }


class CompetenciaForm(forms.ModelForm):
    class Meta:
        model = Competencia
        fields = ['nome', 'tipo', 'descricao', 'nivel', 'tecnologias', 'projetos']
        widgets = {
            'nivel': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'tecnologias': forms.CheckboxSelectMultiple(),
            'projetos': forms.CheckboxSelectMultiple(),
        }


class FormacaoForm(forms.ModelForm):
    class Meta:
        model = Formacao
        fields = [
            'titulo', 'instituicao', 'tipo', 'descricao',
            'data_inicio', 'data_fim', 'certificado', 'url', 'tecnologias'
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'tecnologias': forms.CheckboxSelectMultiple(),
        }
