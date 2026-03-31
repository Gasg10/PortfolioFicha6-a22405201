# Making Of — Portfolio Django
**Aluno:** Gonçalo Gonçalves
**Número:** 22405201
**Curso:** Licenciatura em Engenharia Informática (LEI)
**Universidade:** Universidade Lusófona
**Projeto:** PortfolioFicha6

---

## 1. Introdução

Este documento é o meu diário de bordo do processo de desenvolvimento do projeto **PortfolioFicha6**, uma aplicação web em Django que funciona como portefólio académico pessoal. A ideia é ir registando as decisões que fui tomando, os erros que encontrei, como os resolvi, e a evolução geral do projeto.

O portefólio serve para agregar de forma organizada toda a minha informação académica: o curso que frequento, as unidades curriculares, os professores, os projetos que desenvolvi, as tecnologias que uso, os TFCs do DEISI, as competências que fui adquirindo, formações complementares e este próprio registo reflexivo do processo de construção.

Tecnicamente, a aplicação usa **Django** com base de dados **SQLite** em desenvolvimento, na estrutura padrão com uma app chamada `portfolio`.

---

## 2. Decisões de Modelação por Entidade

### 2.1 Licenciatura

O modelo `Licenciatura` representa o meu curso — LEI na Lusófona.

**Decisão 1 — Campo `grau` com choices:**
Decidi usar um `CharField` com `choices` (`licenciatura`, `mestrado`, `doutoramento`, `ctesp`) em vez de texto livre. A razão é simples: se deixar campo aberto, facilmente ficava com "Licenc.", "licenciatura" e "Licenciatura" todos na base de dados a referir a mesma coisa. Com choices, isso não acontece e ainda consigo filtrar no admin por tipo de grau sem complicações.

**Decisão 2 — `duracao_anos` e `ects_total` como `IntegerField`:**
São valores inteiros por natureza — não faz sentido ter 3.5 anos de duração ou 180.7 ECTS. O `IntegerField` é mais semântico e eficiente que `FloatField` para estes casos, e também é mais fácil de usar em cálculos (por exemplo, ECTS por ano = `ects_total / duracao_anos`).

**Decisão 3 — `logo` como `ImageField` com `upload_to='licenciatura/'`:**
Preferi guardar o logótipo no servidor (via `MEDIA_ROOT`) em vez de usar uma URL externa. Assim tenho controlo total sobre os ficheiros. A pasta `licenciatura/` serve para organizar as imagens por entidade e evitar colisões de nomes entre ficheiros de entidades diferentes.

**Decisão 4 — `url_lusofona` como `URLField`:**
Podia ter usado um `CharField` normal, mas o `URLField` valida automaticamente o formato da URL, tanto nos formulários como no admin. É um pormenor pequeno mas evita ficar com links mal formatados na base de dados.

---

### 2.2 Docente

O modelo `Docente` representa os professores associados às UCs do curso.

**Decisão 1 — `email` como `EmailField`:**
Além da validação automática de formato, decidi usar o email como identificador único no script de carregamento via API da Lusófona. Quando carrego os docentes, faço `get_or_create` pelo email, o que é mais fiável do que pelo nome (que pode ter variações de capitalização ou abreviaturas).

**Decisão 2 — Sem `ForeignKey` para `Licenciatura`:**
Um professor pode lecionar em vários cursos, por isso associá-lo diretamente a uma licenciatura não faz sentido e violaria a normalização da base de dados. A ligação ao curso é feita indiretamente através da relação ManyToMany com `UnidadeCurricular`, que já está ligada à `Licenciatura`.

**Decisão 3 — `foto` com `blank=True, null=True`:**
Quando carrego os docentes a partir da API pública da Lusófona, os dados não incluem fotos. Se o campo fosse obrigatório, o script falharia em todos os docentes. Tornei-o opcional para que o carregamento automático funcione e as fotos possam ser adicionadas manualmente depois.

---

### 2.3 UnidadeCurricular

O modelo `UnidadeCurricular` representa cada disciplina do plano curricular.

**Decisão 1 — `semestre` com choices `(1, 2)` em vez de texto:**
Usar inteiros em vez de "1º Semestre" ou "Semestral" facilita muito o trabalho em código — posso fazer `if uc.semestre == 1:` sem comparações de strings. Também é mais eficiente em ordenações e filtros na base de dados. No script de carregamento tive de mapear os códigos da API (`S1`, `S2`, `S`, `A`) para estes inteiros, o que foi simples.

**Decisão 2 — `licenciatura` como `ForeignKey` com `on_delete=CASCADE`:**
Cada UC pertence a uma única licenciatura — é uma relação one-to-many clara. O `CASCADE` garante que se eliminar uma licenciatura, as UCs associadas também saem automaticamente, mantendo a integridade da base de dados.

**Decisão 3 — `ativo` como `BooleanField`:**
O plano curricular pode mudar ao longo dos anos e algumas UCs podem ser descontinuadas. Em vez de as eliminar e perder o historial (e todos os projetos associados), preferi ter um campo `ativo` para as "desativar" mantendo os dados.

**Decisão 4 — `codigo` como campo separado de `sigla`:**
O código oficial da UC (ex: `ULHT260-1656`) é diferente da sigla legível que uso na apresentação (ex: `MD`). Separei os dois porque no script de carregamento uso o código como identificador único para o `get_or_create`, enquanto a sigla é apenas para mostrar na interface.

---

### 2.4 Projeto

O modelo `Projeto` representa os trabalhos práticos que desenvolvi no âmbito das UCs.

**Decisão 1 — `classificacao` como `DecimalField(max_digits=4, decimal_places=2)`:**
As classificações académicas em Portugal têm valores como 17.50 ou 9.75. Usei `DecimalField` em vez de `FloatField` porque evita erros de arredondamento de vírgula flutuante — o `FloatField` pode representar 17.50 como 17.499999... internamente, o que é problemático para uma classificação. O `max_digits=4` suporta até 99.99, mais que suficiente.

**Decisão 2 — `destaque` como `BooleanField`:**
Quero poder destacar os projetos mais relevantes na página principal do portefólio sem ter de ordenar sempre por classificação. Com este campo booleano consigo filtrar facilmente os projetos que quero mostrar em destaque.

**Decisão 3 — `unidade_curricular` como `ForeignKey`:**
Um projeto nasce sempre no contexto de uma disciplina específica. Esta ligação é importante para dar contexto ao visitante do portefólio — não é só mostrar o projeto, é mostrar em que cadeira foi feito e o que se pretendia aprender.

**Decisão 4 — `tecnologias` como `ManyToManyField`:**
Um projeto usa várias tecnologias e a mesma tecnologia aparece em vários projetos. É o caso clássico de many-to-many e não faria sentido modelar de outra forma.

---

### 2.5 Tecnologia

O modelo `Tecnologia` representa as ferramentas, linguagens e frameworks que uso ou já usei.

**Decisão 1 — `nivel_interesse` com validators `MinValueValidator(1)` e `MaxValueValidator(5)`:**
Em vez de choices com valores fixos (o que criaria um campo de seleção no admin), usei validators para aceitar qualquer inteiro entre 1 e 5. Fica mais flexível — se um dia quiser mudar para uma escala de 1 a 10, só altero os validators sem tocar na estrutura da base de dados.

**Decisão 2 — `tipo` com choices:**
Sem categorizar as tecnologias, a listagem no portefólio seria uma mistura de linguagens, frameworks, bases de dados e ferramentas sem organização. Com o campo `tipo` posso agrupar e apresentar tudo de forma estruturada — "Linguagens que domino", "Frameworks que uso", etc.

**Decisão 3 — `em_uso` como `BooleanField`:**
Não quero apagar tecnologias que usei em projetos antigos mas já não uso ativamente — isso seria perder historial. Com `em_uso=False` consigo mostrar a evolução tecnológica ao longo do curso sem sujar a lista de tecnologias atuais.

---

### 2.6 TFC

O modelo `TFC` representa os Trabalhos Finais de Curso do DEISI.

**Decisão 1 — `titulo` como campo de `get_or_create`:**
No script `load_tfcs.py` usei o título como identificador para o `get_or_create`. Não é o identificador ideal (o JSON tinha títulos duplicados como "IMOinvestor" e "Interface Azure para ERP"), mas é o melhor disponível nos dados fornecidos. Os duplicados são tratados atualizando os dados existentes em vez de criar registos repetidos.

**Decisão 2 — `destaque` mapeado de `rating >= 4`:**
O JSON tinha um campo `rating` numérico de 1 a 5. Em vez de guardar o rating diretamente, decidi mapear para um booleano `destaque` — é mais semântico para o portefólio e consistente com o campo `destaque` do modelo `Projeto`. TFCs com rating 4 ou 5 são marcados como destaque.

**Decisão 3 — `descricao` mapeada do campo `resumo`:**
O JSON usa `resumo` mas o meu modelo usa `descricao`, que é mais genérico e consistente com os outros modelos. Fiz o mapeamento explicitamente no script para ficar claro de onde vêm os dados.

**Decisão 4 — Tecnologias criadas dinamicamente:**
O campo `tecnologias` no JSON é uma string separada por `;` (ex: `"Docker; PostgreSQL"`). Implementei lógica no script para separar, fazer strip e criar automaticamente os objetos `Tecnologia` em falta, com valores por defeito razoáveis. Assim não precisei de pré-popular manualmente dezenas de tecnologias.

---

### 2.7 Competência

O modelo `Competencia` representa as competências que fui desenvolvendo ao longo do curso.

**Decisão 1 — `tipo` com choices `(tecnica, transversal, soft)`:**
Para um portefólio profissional, a distinção entre competências técnicas (programação, bases de dados), transversais (gestão de projetos, metodologias ágeis) e soft skills (comunicação, trabalho em equipa) é essencial. Permite organizar a apresentação de forma que faça sentido a quem visita, nomeadamente potenciais empregadores.

**Decisão 2 — `nivel` com validators em vez de choices:**
Mesma lógica do `nivel_interesse` das Tecnologias — validators de 1 a 5 são mais flexíveis que choices fixas e a escala é intuitiva. É uma convenção muito usada em CVs e portefólios profissionais.

**Decisão 3 — Relações ManyToMany com `Tecnologia` e `Projeto`:**
Uma competência pode ser demonstrada por múltiplos projetos e associada a várias tecnologias. Por exemplo, a competência "Desenvolvimento Web Backend" liga-se aos projetos Django que fiz e às tecnologias Python, Django, PostgreSQL. As duas relações ManyToMany permitem navegar nessa teia de ligações no portefólio.

---

### 2.8 Formação

O modelo `Formacao` representa cursos, certificações e workshops que fiz para além da licenciatura.

**Decisão 1 — `data_fim` com `null=True, blank=True`:**
Algumas formações ainda estão em curso quando as registo. Uma data de fim em branco significa "ainda a decorrer", que é semanticamente diferente de uma formação já terminada. Tornar o campo opcional evita ter de inventar datas ou deixar campos a zeros.

**Decisão 2 — `tipo` com choices:**
Uma certificação oficial (AWS, Google, Microsoft) tem um peso muito diferente de um MOOC ou workshop informal. Categorizar permite apresentar as formações de forma organizada e filtrar por tipo no admin, o que é útil quando a lista cresce.

**Decisão 3 — `certificado` como `ImageField`:**
Ter a imagem do certificado no portefólio aumenta a credibilidade de forma visual e imediata. O campo é opcional porque nem todas as formações emitem certificado físico ou digital.

---

### 2.9 MakingOf

O modelo `MakingOf` é o mais peculiar — é um diário de bordo estruturado do próprio processo de construção do projeto.

**Decisão 1 — `tipo` com choices `(decisao, erro, correcao, evolucao)`:**
Se cada entrada fosse apenas texto livre, o historial tornava-se difícil de analisar. Com a categorização em decisões, erros, correções e evoluções, consigo filtrar no admin e ter uma visão clara do processo — quantos erros cometi, que tipo de decisões tomei, como o modelo foi evoluindo.

**Decisão 2 — `uso_ia` como `TextField` com `blank=True`:**
Documentar quando e como usei ferramentas de IA é uma boa prática académica e cada vez mais um requisito. Tornei o campo opcional porque nem todas as entradas do diário envolvem uso de IA — algumas são puramente técnicas ou reflexivas.

**Decisão 3 — `entidade_relacionada` como `CharField` em vez de `ForeignKey`:**
Uma entrada do Making Of pode referenciar qualquer entidade do sistema — uma UC, um projeto, uma tecnologia, o próprio script de carregamento. Usar uma `GenericForeignKey` do Django seria demasiado complexo para este caso. Um simples `CharField` descritivo é mais prático e suficiente.

---

## 3. Relações entre Entidades

### 3.1 Licenciatura → UnidadeCurricular (ForeignKey)
Uma UC pertence sempre a uma única licenciatura. O `CASCADE` garante a integridade referencial — se remover a licenciatura, as UCs também saem. É a relação mais direta e natural do modelo.

### 3.2 UnidadeCurricular ↔ Docente (ManyToMany)
Uma UC pode ter vários docentes (o professor teórico, o prático, o de laboratório) e um docente pode lecionar várias UCs. A tabela intermédia automática do Django é suficiente aqui — não preciso de guardar atributos adicionais na relação como o semestre em que o docente leciona.

### 3.3 UnidadeCurricular → Projeto (ForeignKey)
Cada projeto nasce no âmbito de uma UC. A relação one-to-many com `CASCADE` é a correta — uma UC pode ter vários projetos associados, e um projeto sem UC perde o contexto académico que lhe dá significado no portefólio.

### 3.4 Projeto ↔ Tecnologia (ManyToMany)
Provavelmente a relação mais consultada no portefólio inteiro — permite responder a "que tecnologias usei neste projeto?" e também "em que projetos usei Python?". É many-to-many por natureza e é uma das ligações mais ricas do modelo.

### 3.5 TFC ↔ Tecnologia (ManyToMany)
Tal como nos projetos, os TFCs envolvem múltiplas tecnologias. Esta relação foi especialmente útil no script de carregamento, onde as tecnologias são criadas dinamicamente a partir dos dados do JSON e associadas a cada TFC.

### 3.6 Competencia ↔ Tecnologia + Projeto (ManyToMany duplo)
Uma competência é demonstrada com evidências concretas — os projetos onde a apliquei e as tecnologias que usei para o fazer. Por exemplo, "Desenvolvimento de APIs REST" liga-se ao Django, Django REST Framework e aos projetos web que desenvolvi. As duas relações ManyToMany permitem construir essa narrativa no portefólio.

---

## 4. Erros Encontrados e Correções

### Erro 1 — `Pillow` não instalado

**Tipo:** Erro de configuração de ambiente
**Quando aconteceu:** Ao correr `python manage.py makemigrations` pela primeira vez depois de definir os modelos com `ImageField`.
**Mensagem de erro:**
```
SystemCheckError: System check identified some issues:
ERRORS:
portfolio.Docente.foto: (fields.E210) Cannot use ImageField because Pillow is not installed.
    HINT: Get Pillow at https://pypi.org/project/Pillow/ or run command "python -m pip install Pillow".
```
**Causa:** O Django precisa da biblioteca `Pillow` para processar imagens, mas eu não a tinha instalada no ambiente virtual. Só me apercebi quando tentei correr as migrações.
**Correção:** Simples — instalar com pip:
```bash
pip install Pillow
```
Depois disso as migrações correram sem problemas.
**Lição aprendida:** Quando uso `ImageField` num projeto Django, a `Pillow` tem de estar nas dependências desde o início. Devo adicionar ao `requirements.txt` para não esquecer noutros ambientes.

---

### Erro 2 — `GetSIGESCurricularUnitDetails` devolve erro 7

**Tipo:** Erro de integração com API externa
**Quando aconteceu:** Durante o desenvolvimento do script `load_curso_ucs.py`, quando tentei obter detalhes individuais de cada UC.
**Resposta da API:**
```json
{"errorCode": "7"}
```
**Causa:** O endpoint `GetSIGESCurricularUnitDetails` da API pública da Lusófona não disponibiliza dados para o curso 260 (LEI) em acesso público. Testei várias combinações de parâmetros — com e sem `courseCode`, diferentes valores de `schoolYear`, em inglês e português — e todas devolveram o mesmo erro 7.
**Correção:** Adaptei o script para lidar com este caso graciosamente: tenta o endpoint e, se receber um erro, regista `(sem detalhes API)` no output e continua com os dados que já tinha do `GetCourseDetail`. As descrições das UCs ficam vazias mas todos os outros campos (nome, código, ano curricular, semestre, ECTS) são preenchidos corretamente.
**Lição aprendida:** Não posso assumir que todos os endpoints de uma API pública estão acessíveis. Tenho de escrever os scripts de forma defensiva, a tolerar falhas parciais sem quebrar tudo.

---

### Erro 3 — Títulos duplicados no JSON dos TFCs

**Tipo:** Problema de qualidade dos dados de origem
**Quando aconteceu:** Ao desenvolver e executar o script `load_tfcs.py`.
**Descrição:** O ficheiro `tfcs_deisi_2024_2025.json` tinha entradas com o mesmo título mas dados ligeiramente diferentes — por exemplo, "IMOinvestor: Inovação no Investimento Imobiliário – (Front-end – App & Web)" aparecia duas vezes e "Interface Azure para ERP" aparecia três vezes.
**Causa:** O JSON parece juntar TFCs de múltiplos anos ou tem registos duplicados na fonte original.
**Correção:** O script usa `get_or_create` pelo `titulo` e, quando o registo já existe, atualiza os dados com os valores mais recentes em vez de criar um duplicado. No final ficou: 153 criados e 15 atualizados num total de 168 entradas.
**Lição aprendida:** Os dados reais raramente chegam limpos. É sempre importante escrever scripts de carregamento que tratem duplicados de forma explícita e previsível, em vez de deixar crashar ou criar dados inconsistentes.

---

### Erro 4 — Siglas geradas com caracteres acentuados

**Tipo:** Comportamento inesperado na geração automática de siglas
**Quando aconteceu:** Durante a execução do script `load_curso_ucs.py`.
**Descrição:** A UC "Álgebra Linear" gerou a sigla `ÁL` (com acento no Á) e "Sistemas de Suporte à Decisão" gerou `SSÀD` (com acento grave). Funcionam bem tecnicamente numa base de dados UTF-8, mas siglas com acentos são pouco convencionais.
**Causa:** A função `sigla_from_name` que implementei pega na primeira letra de cada palavra, incluindo letras acentuadas como `Á` e `À`.
**Estado:** Identifiquei o problema mas não é crítico — as siglas são geradas automaticamente e podem ser corrigidas manualmente no admin do Django. A funcionalidade do script não é afetada.
**Lição aprendida:** Quando gero identificadores a partir de texto em português, devia normalizar as strings primeiro (remover acentos com `unicodedata`) para obter siglas mais limpas.

---

## 5. Evolução do Modelo

### Fase 1 — Estrutura base do projeto
Comecei com a estrutura padrão do Django criada com `django-admin startproject`. A app `portfolio` existia mas os ficheiros `models.py` e `admin.py` estavam praticamente vazios — só os imports por defeito.

### Fase 2 — Definição dos modelos (commit: `Implementados todos os modelos e admin do portfolio`)
Criei os 9 modelos principais, pensando nas dependências entre eles:
- `Licenciatura`, `Docente`, `Tecnologia` — entidades base, sem dependências
- `UnidadeCurricular` — depende de `Licenciatura` e `Docente`
- `Projeto` — depende de `UnidadeCurricular` e `Tecnologia`
- `TFC` — depende de `Tecnologia`
- `Competencia` — depende de `Tecnologia` e `Projeto`
- `Formacao` — depende de `Tecnologia`
- `MakingOf` — entidade independente

Registei também todos os modelos no admin com `list_display`, `search_fields`, `list_filter` e `filter_horizontal` para os campos ManyToMany, para que o backoffice ficasse utilizável desde o início.

### Fase 3 — Carregamento dos TFCs (commit: `Script de carregamento de TFCs`)
Criei a pasta `data/` e o script `data/load_tfcs.py` para carregar 168 TFCs a partir do ficheiro JSON fornecido. Foi a primeira vez que testei o modelo `TFC` com dados reais, o que me permitiu validar as decisões de modelação e perceber o problema dos títulos duplicados.

### Fase 4 — Integração com a API da Lusófona (commit: `Script carregamento curso e UCs da API Lusofona`)
Desenvolvi o script `data/load_curso_ucs.py` que consome a API pública da Lusófona. Com ele carreguei:
- 1 `Licenciatura` (EI — Engenharia Informática)
- 51 `Docentes` do curso
- 31 `UnidadesCurriculares` do plano 2025/2026

Foi nesta fase que descobri a limitação do endpoint `GetSIGESCurricularUnitDetails` e tive de adaptar a abordagem.

---

## 6. Scripts de Carregamento de Dados

### `data/load_tfcs.py`

**Objetivo:** Carregar os TFCs do DEISI a partir do ficheiro JSON local.
**Fonte de dados:** `data/tfcs_deisi_2024_2025.json`
**Resultado:** 168 TFCs (153 criados + 15 atualizados), ~80 objetos `Tecnologia` criados automaticamente.

**O que o script faz:**
1. Lê o JSON e itera por cada entrada
2. Usa `get_or_create` pelo `titulo` para evitar duplicados
3. Mapeia os campos: `resumo → descricao`, `pdf → url_documento`, `rating >= 4 → destaque`
4. Separa as tecnologias por `;`, faz strip e cria ou obtém cada `Tecnologia`
5. Imprime o progresso em tempo real e os totais no final

**Como correr:**
```bash
python data/load_tfcs.py
```

---

### `data/load_curso_ucs.py`

**Objetivo:** Carregar os dados do curso LEI (código 260) diretamente da API pública da Lusófona.
**API:** `https://secure.ensinolusofona.pt/dados-publicos-academicos/resources/`
**Endpoints:**
- `GetCourseDetail` — dados do curso, lista de UCs e lista de docentes
- `GetSIGESCurricularUnitDetails` — tentado para detalhes de cada UC, mas devolve erro 7 para este curso

**Resultado:** 1 `Licenciatura`, 51 `Docentes`, 31 `UnidadesCurriculares`.

**O que o script faz:**
1. POST a `GetCourseDetail` com `courseCode=260` e `schoolYear=202526`
2. Cria ou atualiza a `Licenciatura` com os dados de `courseDetail`
3. Cria ou atualiza os `Docentes` da lista `teachers`, gerando email por defeito quando ausente
4. Para cada UC em `courseFlatPlan`, tenta obter detalhes via `GetSIGESCurricularUnitDetails`; se falhar, usa os dados disponíveis
5. Mapeia `semesterCode` (`S1`, `S2`, `S`, `A`) para inteiro (1 ou 2)
6. Gera a sigla automaticamente pelas iniciais das palavras relevantes do nome

**Como correr:**
```bash
python data/load_curso_ucs.py
```

---

## 7. Uso de IA no Processo

Ao longo deste projeto usei pontualmente ferramentas de IA — nomeadamente o **Claude** e o **ChatGPT** — principalmente para rever sintaxe do Django, tirar dúvidas sobre comportamentos específicos do ORM (como o `get_or_create` com campos ManyToMany) e confirmar boas práticas em situações onde não estava seguro.

Por exemplo, quando tive dúvidas sobre se devia usar `DecimalField` ou `FloatField` para as classificações, consultei para perceber as diferenças técnicas e tomei a decisão com base nisso. Quando o endpoint da API devolvia erro 7, usei como apoio para perceber que tipo de erros HTTP e de API devo tratar e como estruturar o código defensivo.

No entanto, todas as decisões de modelação — que campos criar, que relações estabelecer, que choices usar, como estruturar os scripts — foram minhas. O código foi desenvolvido por mim, com compreensão do que cada linha faz. A IA funcionou como uma espécie de documentação interativa, não como substituto do raciocínio próprio.

---

*Documento elaborado no âmbito da Ficha 6 — Portefólio Django*
*Universidade Lusófona — LEI — 2024/2025*
