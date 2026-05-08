import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.core.files import File
from portfolio.models import Licenciatura, Docente, Tecnologia, UnidadeCurricular, Projeto, MakingOf, Formacao

models_fields = [
    (Licenciatura, 'logo'),
    (Docente, 'foto'),
    (Tecnologia, 'logo'),
    (UnidadeCurricular, 'imagem'),
    (Projeto, 'imagem'),
    (MakingOf, 'fotografia'),
    (Formacao, 'certificado'),
]

for model, field_name in models_fields:
    for obj in model.objects.all():
        field = getattr(obj, field_name)
        if field and field.name:
            local_path = os.path.join('media', field.name)
            if os.path.exists(local_path):
                with open(local_path, 'rb') as f:
                    getattr(obj, field_name).save(
                        os.path.basename(local_path),
                        File(f),
                        save=True
                    )
                print(f"Migrado: {obj} - {field_name}")
