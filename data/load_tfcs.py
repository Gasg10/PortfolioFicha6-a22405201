import os
import sys
import json

# Adiciona o diretório raiz do projeto ao path para encontrar o manage.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

from portfolio.models import TFC, Tecnologia

JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tfcs_deisi_2024_2025.json')


def get_or_create_tecnologia(nome):
    nome = nome.strip()
    if not nome:
        return None
    tecnologia, created = Tecnologia.objects.get_or_create(
        nome=nome,
        defaults={
            'tipo': 'outro',
            'descricao': '',
            'nivel_interesse': 3,
            'ano_inicio': 2024,
            'em_uso': True,
        }
    )
    if created:
        print(f"  [+] Tecnologia criada: {nome}")
    return tecnologia


def load_tfcs():
    with open(JSON_FILE, encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    criados = 0
    atualizados = 0

    for i, entry in enumerate(data, start=1):
        titulo = entry.get('titulo', '').strip()
        if not titulo:
            print(f"[{i}/{total}] Ignorado (sem título)")
            continue

        ano_raw = entry.get('ano', '')
        try:
            ano = int(str(ano_raw).strip())
        except (ValueError, TypeError):
            ano = 0

        rating = entry.get('rating', 0)
        try:
            rating = int(rating)
        except (ValueError, TypeError):
            rating = 0

        defaults = {
            'descricao': entry.get('resumo', '') or '',
            'ano': ano,
            'autor': entry.get('autor', '') or '',
            'orientador': entry.get('orientador', '') or '',
            'url_documento': entry.get('pdf', '') or '',
            'url_repositorio': '',
            'destaque': rating >= 4,
        }

        tfc, created = TFC.objects.get_or_create(titulo=titulo, defaults=defaults)

        if not created:
            for field, value in defaults.items():
                setattr(tfc, field, value)
            tfc.save()
            atualizados += 1
            status = 'atualizado'
        else:
            criados += 1
            status = 'criado'

        # Tecnologias
        tecnologias_raw = entry.get('tecnologias', '') or ''
        tfc.tecnologias.clear()
        for nome_tec in tecnologias_raw.split(';'):
            nome_tec = nome_tec.strip()
            if nome_tec:
                tec = get_or_create_tecnologia(nome_tec)
                if tec:
                    tfc.tecnologias.add(tec)

        print(f"[{i}/{total}] {status.upper()}: {titulo}")

    print(f"\nConcluído: {criados} criados, {atualizados} atualizados, {total} total.")


if __name__ == '__main__':
    load_tfcs()
