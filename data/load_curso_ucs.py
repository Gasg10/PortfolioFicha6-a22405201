import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

import requests
from portfolio.models import Licenciatura, Docente, UnidadeCurricular

API_BASE = 'https://secure.ensinolusofona.pt/dados-publicos-academicos/resources'
COURSE_CODE = 260
SCHOOL_YEAR = '202526'
COURSE_URL = 'https://www.ulusofona.pt/licenciatura/engenharia-informatica'

SEMESTER_MAP = {
    'S1': 1,
    'S2': 2,
    'S':  1,  # Semestral sem semestre definido → 1
    'A':  1,  # Anual → 1
}


def post(endpoint, payload):
    r = requests.post(f'{API_BASE}/{endpoint}', json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


def get_course_detail():
    print(f'[API] GetCourseDetail para curso {COURSE_CODE} ({SCHOOL_YEAR})...')
    return post('GetCourseDetail', {
        'language': 'PT',
        'courseCode': COURSE_CODE,
        'schoolYear': SCHOOL_YEAR,
    })


def get_uc_details(uc_code):
    data = post('GetSIGESCurricularUnitDetails', {
        'language': 'PT',
        'curricularUnitCode': uc_code,
        'courseCode': COURSE_CODE,
        'schoolYear': SCHOOL_YEAR,
    })
    error = data.get('errorCode')
    if error and str(error) != '0':
        return None
    return data


def sigla_from_name(name):
    """Gera sigla a partir das iniciais das palavras principais (max 10 chars)."""
    stop = {'de', 'da', 'do', 'das', 'dos', 'e', 'em', 'a', 'o', 'para'}
    parts = [w for w in name.split() if w.lower() not in stop]
    sigla = ''.join(w[0].upper() for w in parts)
    return sigla[:10] if sigla else name[:10]


def create_or_update_licenciatura(detail):
    cd = detail['courseDetail']

    grau_raw = cd.get('degree', '').lower()
    if '1' in grau_raw or 'licenciatura' in grau_raw:
        grau = 'licenciatura'
    elif 'mestrado' in grau_raw or '2' in grau_raw:
        grau = 'mestrado'
    elif 'doutoramento' in grau_raw or '3' in grau_raw:
        grau = 'doutoramento'
    else:
        grau = 'licenciatura'

    semesters = cd.get('semesters', 6)
    duracao_anos = max(1, semesters // 2)

    defaults = {
        'grau': grau,
        'area_cientifica': cd.get('scientificArea', ''),
        'duracao_anos': duracao_anos,
        'ects_total': cd.get('courseECTS', 180),
        'descricao': cd.get('presentation', '') or cd.get('objectives', ''),
        'url_lusofona': cd.get('courseUrl', '') or COURSE_URL,
        'ano_inicio': int(SCHOOL_YEAR[:4]) - duracao_anos + 1,
    }

    nome = cd.get('courseName', 'Engenharia Informática')
    sigla = sigla_from_name(nome)

    lic, created = Licenciatura.objects.get_or_create(
        sigla=sigla,
        defaults={'nome': nome, **defaults},
    )
    if not created:
        lic.nome = nome
        for k, v in defaults.items():
            setattr(lic, k, v)
        lic.save()

    status = 'criada' if created else 'atualizada'
    print(f'[Licenciatura] {status}: {lic}')
    return lic


def create_or_update_docentes(teachers):
    docentes_map = {}
    for t in teachers:
        nome = t.get('academicName') or t.get('fullName', '').strip()
        if not nome:
            continue
        email = t.get('email', '') or ''
        employee_code = t.get('employeeCode', '')
        url = f'https://www.ulusofona.pt/docente/p{employee_code}' if employee_code else ''

        docente, created = Docente.objects.get_or_create(
            email=email if email else f'p{employee_code}@ulusofona.pt',
            defaults={'nome': nome, 'url_lusofona': url},
        )
        if not created:
            docente.nome = nome
            docente.url_lusofona = url
            docente.save()

        status = 'criado' if created else 'atualizado'
        print(f'  [Docente] {status}: {docente.nome}')
        docentes_map[employee_code] = docente

    return docentes_map


def create_or_update_uc(uc_data, licenciatura, all_docentes):
    code = uc_data['curricularUnitCode']
    nome = uc_data['curricularUnitName']
    readable_code = uc_data.get('curricularIUnitReadableCode', str(code))
    semestre_key = uc_data.get('semesterCode', 'S1')
    semestre = SEMESTER_MAP.get(semestre_key, 1)
    ano_curricular = uc_data.get('curricularYear', 1)
    ects = uc_data.get('ects', 6)

    # Tentar obter detalhes adicionais via API
    details = get_uc_details(code)
    descricao = ''
    docentes_uc = []

    if details:
        descricao = (
            details.get('objectives', '')
            or details.get('description', '')
            or details.get('syllabus', '')
            or ''
        )
        # Mapear docentes da UC se existirem nos detalhes
        for t in details.get('teachers', []):
            emp = t.get('employeeCode')
            if emp and emp in all_docentes:
                docentes_uc.append(all_docentes[emp])

    defaults = {
        'ano_curricular': ano_curricular,
        'semestre': semestre,
        'ects': ects,
        'descricao': descricao,
        'ativo': True,
        'licenciatura': licenciatura,
    }

    sigla = sigla_from_name(nome)

    uc, created = UnidadeCurricular.objects.get_or_create(
        codigo=readable_code,
        defaults={'nome': nome, 'sigla': sigla, **defaults},
    )
    if not created:
        uc.nome = nome
        uc.sigla = sigla
        for k, v in defaults.items():
            setattr(uc, k, v)
        uc.save()

    if docentes_uc:
        uc.docentes.set(docentes_uc)

    status = 'criada' if created else 'atualizada'
    detail_info = f'(detalhes API OK, {len(docentes_uc)} docentes)' if details else '(sem detalhes API)'
    print(f'  [UC] {status}: {uc.sigla} - {uc.nome} {detail_info}')
    return uc


def main():
    data = get_course_detail()

    if data.get('errorCode') and str(data['errorCode']) != '0':
        print(f'Erro da API: {data}')
        sys.exit(1)

    # 1. Criar/atualizar Licenciatura
    licenciatura = create_or_update_licenciatura(data)

    # 2. Criar/atualizar Docentes do curso
    print(f'\n[Docentes] A processar {len(data.get("teachers", []))} docentes...')
    all_docentes = create_or_update_docentes(data.get('teachers', []))

    # 3. Criar/atualizar UCs
    ucs = data.get('courseFlatPlan', [])
    print(f'\n[UCs] A processar {len(ucs)} unidades curriculares...')
    for i, uc_data in enumerate(ucs, start=1):
        print(f'[{i}/{len(ucs)}] {uc_data["curricularUnitName"]}')
        create_or_update_uc(uc_data, licenciatura, all_docentes)

    print(f'\nConcluído:')
    print(f'  Licenciatura: {licenciatura}')
    print(f'  Docentes processados: {len(all_docentes)}')
    print(f'  UCs processadas: {len(ucs)}')


if __name__ == '__main__':
    main()
