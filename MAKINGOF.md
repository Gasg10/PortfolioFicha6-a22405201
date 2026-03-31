# Making Of — Portfolio Django
**Aluno:** Gonçalo Gonçalves
**Número:** 22405201
**Curso:** Licenciatura em Engenharia Informática (LEI)
**Universidade:** Universidade Lusófona
**Projeto:** PortfolioFicha6

---

## 1. Introdução

Este documento é um diário de bordo do processo de desenvolvimento do projeto **PortfolioFicha6**, uma aplicação web Django que serve de portefólio académico pessoal. O objetivo é documentar todas as decisões de modelação, erros encontrados, correções aplicadas e a evolução geral do projeto ao longo do tempo.

O portefólio pretende agregar de forma estruturada toda a informação académica relevante: a licenciatura frequentada, as unidades curriculares, os docentes, os projetos realizados, as tecnologias utilizadas, os Trabalhos Finais de Curso (TFC) do DEISI, as competências adquiridas, as formações complementares e um registo reflexivo do próprio processo de construção (Making Of).

A aplicação foi criada com **Django** (framework Python), com base de dados **SQLite** em desenvolvimento, e segue a estrutura padrão de projeto Django com uma app chamada `portfolio`.

---

## 2. Decisões de Modelação por Entidade

### 2.1 Licenciatura

O modelo `Licenciatura` representa o curso que o aluno frequenta — neste caso, LEI na Universidade Lusófona.

**Decisão 1 — Campo `grau` com choices:**
Optou-se por usar um `CharField` com `choices` (`licenciatura`, `mestrado`, `doutoramento`, `ctesp`) em vez de um campo de texto livre. Isto garante consistência nos dados e permite filtrar facilmente no admin por tipo de grau, evitando variações como "Licenc.", "Licenciatura", "licenciatura" que causariam inconsistências.

**Decisão 2 — Campos `duracao_anos` e `ects_total` como `IntegerField`:**
Estes valores são numéricos discretos e não necessitam de casas decimais. O uso de `IntegerField` em vez de `FloatField` ou `DecimalField` é mais semântico e eficiente para valores como 3 anos ou 180 ECTS. Além disso, facilita cálculos futuros (ex: ECTS por ano = `ects_total / duracao_anos`).

**Decisão 3 — `logo` como `ImageField` com `upload_to='licenciatura/'`:**
Guardar o logótipo no sistema de ficheiros do servidor (via `MEDIA_ROOT`) em vez de numa base de dados ou URL externa permite maior controlo sobre os ativos do projeto. A pasta `licenciatura/` organiza os ficheiros por entidade, evitando colisões de nomes.

**Decisão 4 — `url_lusofona` como `URLField`:**
O uso de `URLField` em vez de `CharField` adiciona validação automática do formato de URL pelo Django, tanto nos formulários como no admin, prevenindo dados malformados.

---

### 2.2 Docente

O modelo `Docente` representa os professores associados às unidades curriculares do curso.

**Decisão 1 — `email` como `EmailField`:**
O uso de `EmailField` em vez de `CharField` garante validação de formato de endereço de email pelo Django. Isto é importante porque os emails dos docentes são usados como identificadores únicos no processo de carregamento via API da Lusófona (script `load_curso_ucs.py`).

**Decisão 2 — Sem `ForeignKey` para `Licenciatura`:**
Um docente pode lecionar em múltiplos cursos, por isso não faz sentido associá-lo diretamente a uma licenciatura. A associação é feita indiretamente através da relação `ManyToManyField` com `UnidadeCurricular`. Esta decisão evita redundância e respeita a normalização da base de dados.

**Decisão 3 — `foto` com `blank=True, null=True`:**
Nem todos os docentes têm foto disponível, especialmente os que são carregados via API e para os quais não existe imagem associada nos dados públicos. Tornar o campo opcional evita erros de validação no carregamento automático de dados.

---

### 2.3 UnidadeCurricular

O modelo `UnidadeCurricular` (UC) representa cada disciplina do plano curricular do curso.

**Decisão 1 — `semestre` com choices `(1, 2)` em vez de texto:**
Usar um `IntegerField` com choices numéricas em vez de texto ("1º Semestre", "Semestral") permite ordenações e filtros mais eficientes na base de dados. É também mais fácil de trabalhar em código (ex: `if uc.semestre == 1:`). No script de carregamento, o mapeamento `semesterCode → inteiro` resolve os casos especiais da API (`'S'`, `'A'`).

**Decisão 2 — `licenciatura` como `ForeignKey` com `on_delete=CASCADE`:**
Cada UC pertence a uma única licenciatura (relação many-to-one). O `CASCADE` garante que, se uma licenciatura for eliminada, todas as suas UCs são também removidas automaticamente, mantendo a integridade referencial.

**Decisão 3 — `ativo` como `BooleanField`:**
O plano curricular pode evoluir ao longo dos anos — UCs podem ser descontinuadas mas é importante manter o histórico. O campo `ativo` permite "desativar" uma UC sem a eliminar, preservando os projetos e dados associados.

**Decisão 4 — `codigo` como campo separado de `sigla`:**
O código oficial da UC (ex: `ULHT260-1656`) é diferente da sigla legível (ex: `MD`). Manter os dois campos separados permite usar o código como identificador único para o `get_or_create` no script de carregamento, enquanto a sigla é usada para apresentação.

---

### 2.4 Projeto

O modelo `Projeto` representa os trabalhos práticos realizados no âmbito das UCs.

**Decisão 1 — `classificacao` como `DecimalField(max_digits=4, decimal_places=2)`:**
As classificações académicas em Portugal usam valores como 17.50 ou 9.75. O `DecimalField` é mais preciso que `FloatField` para representar valores monetários e classificações, evitando erros de arredondamento de vírgula flutuante. `max_digits=4` suporta valores até 99.99, suficiente para qualquer escala de classificação.

**Decisão 2 — `destaque` como `BooleanField`:**
Permite identificar rapidamente os projetos mais relevantes para apresentar em destaque na página principal do portefólio, sem necessidade de lógica adicional de ordenação por classificação.

**Decisão 3 — `unidade_curricular` como `ForeignKey`:**
Cada projeto é realizado no contexto de uma UC específica (relação many-to-one). Um projeto não existe de forma isolada — está sempre associado a uma disciplina, o que também serve de contexto pedagógico para o visitante do portefólio.

**Decisão 4 — `tecnologias` como `ManyToManyField`:**
Um projeto pode usar múltiplas tecnologias (Django, PostgreSQL, JavaScript, etc.) e uma tecnologia pode ser usada em múltiplos projetos. A relação many-to-many é a mais adequada para este caso.

---

### 2.5 Tecnologia

O modelo `Tecnologia` representa as ferramentas, linguagens e frameworks utilizadas nos projetos.

**Decisão 1 — `nivel_interesse` com validators `MinValueValidator(1)` e `MaxValueValidator(5)`:**
Em vez de usar choices com valores fixos, optou-se por validators que permitem qualquer inteiro entre 1 e 5. Isto mantém a flexibilidade do campo (poderia ser alterado para 1-10 no futuro) enquanto valida os dados automaticamente em qualquer formulário Django.

**Decisão 2 — `tipo` com choices:**
Categorizar as tecnologias (linguagem, framework, biblioteca, ferramenta, base de dados) permite filtrar e agrupar no admin e na interface do portefólio. Sem esta categorização, a listagem de tecnologias seria uma mistura heterogénea difícil de apresentar de forma organizada.

**Decisão 3 — `em_uso` como `BooleanField`:**
O portefólio deve refletir não só o que o aluno usa atualmente mas também o histórico. Tecnologias que já não são usadas (ex: uma ferramenta de um projeto de 1º ano) podem ser mantidas na base de dados com `em_uso=False`, permitindo mostrar a evolução tecnológica ao longo do curso.

---

### 2.6 TFC

O modelo `TFC` representa os Trabalhos Finais de Curso do DEISI, carregados a partir do ficheiro JSON fornecido.

**Decisão 1 — `titulo` como campo de `get_or_create`:**
No script de carregamento `load_tfcs.py`, o título é usado como identificador único para o `get_or_create`. Embora não seja garantidamente único (o JSON continha títulos duplicados como "IMOinvestor" e "Interface Azure para ERP"), é o melhor identificador disponível nos dados fornecidos. Os duplicados foram tratados com atualização dos dados existentes.

**Decisão 2 — `destaque` mapeado a partir de `rating >= 4`:**
O JSON dos TFCs continha um campo `rating` numérico. Em vez de guardar o rating diretamente, decidiu-se mapear para um booleano `destaque`, que é mais semântico para o contexto do portefólio. TFCs com rating 4 ou 5 são considerados de destaque.

**Decisão 3 — `descricao` mapeada do campo `resumo`:**
O JSON usa `resumo` mas o modelo usa `descricao` (nome mais genérico e consistente com os outros modelos). O mapeamento é feito explicitamente no script, tornando clara a correspondência entre a fonte de dados e o modelo Django.

**Decisão 4 — `tecnologias` criadas dinamicamente a partir do campo `tecnologias` do JSON:**
O campo `tecnologias` no JSON é uma string separada por `;` (ex: `"Docker; PostgreSQL"`). O script separa, faz strip e cria automaticamente objetos `Tecnologia` com valores por defeito (`tipo='outro'`, `nivel_interesse=3`). Isto evita pré-popular manualmente dezenas de tecnologias e aproveita os dados existentes.

---

### 2.7 Competência

O modelo `Competencia` representa as competências técnicas e transversais adquiridas ao longo do curso.

**Decisão 1 — `tipo` com choices `(tecnica, transversal, soft)`:**
A distinção entre competências técnicas (programação, bases de dados), transversais (gestão de projetos, metodologias) e soft skills (comunicação, trabalho em equipa) é fundamental num portefólio profissional. Permite organizar e apresentar as competências de forma estruturada a potenciais empregadores.

**Decisão 2 — `nivel` com validators em vez de choices:**
Tal como em `Tecnologia.nivel_interesse`, usar validators (1-5) em vez de choices fixas dá mais flexibilidade. A escala de 1 a 5 é intuitiva e amplamente usada em CVs e portefólios profissionais.

**Decisão 3 — Relações `ManyToMany` com `Tecnologia` e `Projeto`:**
Uma competência pode ser demonstrada por múltiplos projetos e pode envolver várias tecnologias. Inversamente, um projeto pode demonstrar múltiplas competências. As relações many-to-many permitem esta associação bidirecional flexível.

---

### 2.8 Formação

O modelo `Formacao` representa cursos, certificações e workshops complementares à licenciatura.

**Decisão 1 — `data_fim` com `null=True, blank=True`:**
Algumas formações são contínuas ou ainda estão em curso no momento do registo. Tornar a data de fim opcional é a abordagem correta — uma formação sem data de fim significa que ainda está em curso, o que é semanticamente diferente de uma formação com data de fim definida.

**Decisão 2 — `tipo` com choices `(curso, workshop, certificacao, mooc, outro)`:**
A distinção entre tipos de formação complementar é importante para o portefólio. Uma certificação oficial (ex: AWS, Google) tem peso diferente de um MOOC ou workshop informal. As choices permitem filtrar e apresentar as formações de forma categorizada.

**Decisão 3 — `certificado` como `ImageField`:**
Guardar uma imagem do certificado permite apresentá-lo visualmente no portefólio, aumentando a credibilidade. O campo é opcional (`blank=True, null=True`) pois nem todas as formações emitem certificado.

---

### 2.9 MakingOf

O modelo `MakingOf` é o mais reflexivo — serve de diário de bordo estruturado das decisões, erros, correções e evoluções do próprio projeto.

**Decisão 1 — `tipo` com choices `(decisao, erro, correcao, evolucao)`:**
Categorizar cada entrada do diário permite filtrar e visualizar separadamente as decisões de design, os erros cometidos, as correções aplicadas e a evolução geral. Sem esta categorização, o historial seria uma lista homogénea difícil de analisar.

**Decisão 2 — `uso_ia` como `TextField` com `blank=True`:**
Num contexto académico atual, documentar o uso de IA generativa (GitHub Copilot, Claude, ChatGPT) é uma boa prática e pode ser um requisito. Tornar o campo opcional (`blank=True`) respeita os casos em que a IA não foi usada, sem forçar um valor.

**Decisão 3 — `entidade_relacionada` como `CharField` em vez de `ForeignKey`:**
O Making Of pode referenciar qualquer entidade do sistema (UC, Projeto, Tecnologia, etc.) sem uma relação formal de base de dados. Usar um `CharField` descritivo é mais flexível e evita a complexidade de uma `GenericForeignKey` do Django para este caso de uso.

---

## 3. Relações entre Entidades

### 3.1 Licenciatura → UnidadeCurricular (ForeignKey)
**Justificação:** Uma UC pertence a exatamente uma licenciatura (relação one-to-many). O `CASCADE` garante integridade referencial — se a licenciatura for eliminada, as UCs associadas também são removidas. É a relação mais natural e eficiente para este caso.

### 3.2 UnidadeCurricular ↔ Docente (ManyToMany)
**Justificação:** Uma UC pode ter múltiplos docentes (teórico, prático, laboratorial) e um docente pode lecionar múltiplas UCs ao longo do curso. A tabela intermédia gerada automaticamente pelo Django é suficiente para este caso, sem necessidade de atributos adicionais na relação.

### 3.3 UnidadeCurricular → Projeto (ForeignKey)
**Justificação:** Cada projeto é desenvolvido no contexto de uma UC específica. A relação one-to-many (uma UC pode ter vários projetos) com `CASCADE` é a mais adequada, pois um projeto sem UC perde o seu contexto académico.

### 3.4 Projeto ↔ Tecnologia (ManyToMany)
**Justificação:** Um projeto usa múltiplas tecnologias e uma tecnologia aparece em múltiplos projetos. Esta é uma das relações mais importantes do portefólio, pois permite mostrar a experiência acumulada com cada tecnologia ao longo dos projetos.

### 3.5 TFC ↔ Tecnologia (ManyToMany)
**Justificação:** Tal como nos projetos, os TFCs do DEISI envolvem múltiplas tecnologias. A relação ManyToMany permite cruzar dados: "quantos TFCs usam Python?" ou "quais os TFCs que usam Docker?".

### 3.6 Competencia ↔ Tecnologia + Projeto (ManyToMany duplo)
**Justificação:** Uma competência é demonstrada através de projetos concretos e associada a tecnologias específicas. Por exemplo, a competência "Desenvolvimento Web" está associada às tecnologias Django, JavaScript, CSS e aos projetos onde essas tecnologias foram usadas. As duas relações ManyToMany permitem esta navegação bidirecional no portefólio.

---

## 4. Erros Encontrados e Correções

### Erro 1 — `Pillow` não instalado

**Tipo:** Erro de configuração de ambiente
**Ocorrência:** Ao tentar correr `python manage.py makemigrations` pela primeira vez depois de definir os modelos com `ImageField`.
**Mensagem de erro:**
```
SystemCheckError: System check identified some issues:
ERRORS:
portfolio.Docente.foto: (fields.E210) Cannot use ImageField because Pillow is not installed.
    HINT: Get Pillow at https://pypi.org/project/Pillow/ or run command "python -m pip install Pillow".
```
**Causa:** O Django requer a biblioteca `Pillow` para processar imagens, mas ela não estava instalada no ambiente virtual.
**Correção:** Instalação via pip:
```bash
pip install Pillow
```
Após a instalação, as migrações correram sem erros.
**Lição aprendida:** Sempre incluir `Pillow` nas dependências do projeto quando se usam `ImageField`. Idealmente, adicionar ao `requirements.txt`.

---

### Erro 2 — `GetSIGESCurricularUnitDetails` retorna erro 7

**Tipo:** Erro de integração com API externa
**Ocorrência:** Durante o desenvolvimento do script `load_curso_ucs.py`, ao tentar obter detalhes de cada UC individualmente.
**Resposta da API:**
```json
{"errorCode": "7"}
```
**Causa:** O endpoint `GetSIGESCurricularUnitDetails` da API pública da Lusófona não disponibiliza dados para o curso 260 (LEI) através do acesso público. O código de erro 7 indica dados não disponíveis ou acesso não autorizado para esta combinação de parâmetros. Foram testadas múltiplas variações de payload (com e sem `courseCode`, diferentes `schoolYear`, língua EN/PT) sem sucesso.
**Correção:** O script foi adaptado para tratar graciosamente este erro — tenta o endpoint e, se receber erro, regista `(sem detalhes API)` no output e continua com os dados disponíveis no `GetCourseDetail`. A descrição das UCs fica vazia mas todos os outros campos (nome, código, ano curricular, semestre, ECTS) são preenchidos corretamente.
**Lição aprendida:** Nunca assumir que todos os endpoints de uma API pública estão acessíveis. Tratar erros de forma robusta e manter o script funcional mesmo com dados parciais.

---

### Erro 3 — Títulos duplicados no JSON dos TFCs

**Tipo:** Qualidade dos dados de origem
**Ocorrência:** Durante o desenvolvimento e execução do script `load_tfcs.py`.
**Descrição:** O ficheiro `tfcs_deisi_2024_2025.json` continha entradas com o mesmo título mas dados ligeiramente diferentes (ex: "IMOinvestor: Inovação no Investimento Imobiliário – (Front-end – App & Web)" aparecia duas vezes, "Interface Azure para ERP" aparecia três vezes).
**Causa:** O JSON combinava TFCs de múltiplos anos ou registos duplicados da fonte de dados.
**Correção:** O script usa `get_or_create` pelo `titulo` e, quando já existe, atualiza os dados com os valores mais recentes. O output final mostrou 153 criados e 15 atualizados em 168 entradas totais.
**Lição aprendida:** Os dados reais raramente são limpos. É importante escrever scripts de carregamento que tratem duplicados de forma explícita e previsível.

---

### Erro 4 — Sigla gerada com caracteres especiais

**Tipo:** Comportamento inesperado na geração de siglas
**Ocorrência:** Na geração automática de siglas para UCs no script `load_curso_ucs.py`.
**Descrição:** A UC "Álgebra Linear" gerou a sigla `ÁL` (com acento), e "Sistemas de Suporte à Decisão" gerou `SSÀD` (com acento grave). Embora funcionais na base de dados UTF-8, siglas com acentos são pouco convencionais.
**Causa:** A função `sigla_from_name` usa a primeira letra de cada palavra, incluindo letras acentuadas como `Á` e `À`.
**Estado:** Identificado mas não crítico — as siglas são geradas automaticamente e podem ser corrigidas manualmente no admin. A funcionalidade do script não é afetada.
**Lição aprendida:** Normalização de strings (remoção de acentos) deve ser considerada em funções que geram identificadores a partir de texto em português.

---

## 5. Evolução do Modelo

### Fase 1 — Estrutura inicial do projeto
O projeto foi criado com a estrutura base do Django: `manage.py`, app `portfolio`, configurações em `project/settings.py`. Os ficheiros `models.py` e `admin.py` estavam praticamente vazios (apenas os imports por defeito).

### Fase 2 — Definição dos modelos (commit: `Implementados todos os modelos e admin do portfolio`)
Foram criados os 9 modelos principais:
- `Licenciatura`, `Docente`, `Tecnologia` (entidades base independentes)
- `UnidadeCurricular` (depende de `Licenciatura` e `Docente`)
- `Projeto` (depende de `UnidadeCurricular` e `Tecnologia`)
- `TFC` (depende de `Tecnologia`)
- `Competencia` (depende de `Tecnologia` e `Projeto`)
- `Formacao` (depende de `Tecnologia`)
- `MakingOf` (entidade independente)

Nesta fase, todos os modelos foram registados no admin com `list_display`, `search_fields`, `list_filter` e `filter_horizontal` para os campos ManyToMany.

### Fase 3 — Carregamento de TFCs (commit: `Script de carregamento de TFCs`)
Criação da pasta `data/` e do script `data/load_tfcs.py` para carregar 168 TFCs a partir do ficheiro `data/tfcs_deisi_2024_2025.json`. Esta fase demonstrou a utilidade do modelo `TFC` com as suas relações e validou o design do modelo em produção com dados reais.

### Fase 4 — Integração com API da Lusófona (commit: `Script carregamento curso e UCs da API Lusofona`)
Criação do script `data/load_curso_ucs.py` que integra com a API pública da Lusófona para carregar:
- 1 `Licenciatura` (EI — Engenharia Informática)
- 51 `Docentes` do curso
- 31 `UnidadesCurriculares` do plano curricular 2025/2026

Esta fase validou o modelo de `Licenciatura`, `Docente` e `UnidadeCurricular` com dados reais e identificou a limitação do endpoint `GetSIGESCurricularUnitDetails`.

---

## 6. Scripts de Carregamento de Dados

### `data/load_tfcs.py`

**Objetivo:** Carregar TFCs do DEISI a partir de um ficheiro JSON local.
**Fonte:** `data/tfcs_deisi_2024_2025.json`
**Registos carregados:** 168 TFCs (153 criados + 15 atualizados)
**Tecnologias criadas automaticamente:** ~80 objetos `Tecnologia`

**Lógica principal:**
1. Lê o JSON e itera por cada entrada
2. Usa `get_or_create` pelo `titulo` para evitar duplicados
3. Mapeia `resumo → descricao`, `pdf → url_documento`, `rating >= 4 → destaque`
4. Separa tecnologias por `;`, faz strip e cria/obtém cada `Tecnologia`
5. Imprime progresso em tempo real e totais no final

**Como correr:**
```bash
python data/load_tfcs.py
```

---

### `data/load_curso_ucs.py`

**Objetivo:** Carregar dados do curso LEI (código 260) a partir da API pública da Lusófona.
**API base:** `https://secure.ensinolusofona.pt/dados-publicos-academicos/resources/`
**Endpoints utilizados:**
- `GetCourseDetail` — dados do curso, lista de UCs e lista de docentes
- `GetSIGESCurricularUnitDetails` — detalhes de cada UC (retorna erro 7, tratado graciosamente)

**Registos carregados:**
- 1 `Licenciatura`
- 51 `Docentes`
- 31 `UnidadesCurriculares`

**Lógica principal:**
1. POST a `GetCourseDetail` com `courseCode=260` e `schoolYear=202526`
2. Cria/atualiza a `Licenciatura` com dados de `courseDetail`
3. Cria/atualiza todos os `Docentes` da lista `teachers`, gerando email por defeito quando ausente
4. Para cada UC em `courseFlatPlan`, tenta obter detalhes via `GetSIGESCurricularUnitDetails`; se falhar (erro 7), usa apenas os dados disponíveis
5. Mapeia `semesterCode` (`S1`, `S2`, `S`, `A`) para inteiro (`1` ou `2`)
6. Gera sigla automaticamente pelas iniciais das palavras não-stopword do nome

**Como correr:**
```bash
python data/load_curso_ucs.py
```

---

## 7. Uso de IA no Processo

Este projeto foi desenvolvido com apoio do assistente de IA **Claude** (Anthropic), utilizado através do **Claude Code** (CLI).

### Como a IA foi utilizada

**Geração de código:**
A IA gerou os ficheiros `portfolio/models.py` e `portfolio/admin.py` completos com base nas especificações fornecidas. O código foi revisado antes de ser aplicado.

**Exploração de API:**
A IA executou pedidos de teste à API da Lusófona antes de escrever os scripts, inspecionando a estrutura real das respostas JSON (campos disponíveis, códigos de erro, variações de payload). Isto permitiu escrever scripts robustos e adaptados aos dados reais, em vez de assumir uma estrutura hipotética.

**Diagnóstico de erros:**
Quando o `makemigrations` falhou por falta do Pillow, a IA identificou a causa a partir da mensagem de erro e aplicou a correção automaticamente. Quando o endpoint `GetSIGESCurricularUnitDetails` retornou erro 7, a IA testou múltiplas variações de payload antes de concluir que o endpoint não está disponível publicamente.

**Escrita de scripts de carregamento:**
Os scripts `load_tfcs.py` e `load_curso_ucs.py` foram gerados pela IA com base na análise prévia dos dados (estrutura do JSON, resposta da API), incluindo tratamento de erros, mapeamento de campos e lógica de `get_or_create`.

### Avaliação do uso de IA

O uso de IA foi produtivo para tarefas repetitivas e de estruturação (definição de modelos, configuração do admin, escrita de scripts). O maior valor acrescentado foi na **exploração iterativa da API** — a IA testou múltiplas hipóteses de forma autónoma antes de concluir sobre o comportamento real do sistema externo.

As decisões de design (que campos incluir, que relações estabelecer, que choices usar) foram sempre guiadas pelos requisitos do projeto e validadas pelo aluno. A IA funcionou como um assistente que implementa decisões, não como quem as toma.

---

*Documento gerado no âmbito da Ficha 6 — Portefólio Django*
*Universidade Lusófona — LEI — 2024/2025*
