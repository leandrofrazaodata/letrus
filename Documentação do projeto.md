# Documentação do Projeto - Análise de Dados SAEB

## 1. Introdução

Este documento apresenta a documentação do projeto de transformação dos microdados do SAEB (Sistema de Avaliação da Educação Básica) em um modelo OLAP para análise educacional. O projeto foca especificamente nos dados do 9º ano do Ensino Fundamental e visa responder a questões estratégicas sobre o desempenho educacional no Brasil.

## 2. Visão Geral do Projeto

### 2.1. Objetivo

O objetivo principal deste projeto é transformar os microdados do SAEB em um modelo dimensional otimizado para análise, permitindo que equipes internas e externas utilizem esses dados para tomada de decisões estratégicas na área educacional.

### 2.2. Fontes de Dados

As seguintes fontes de dados foram utilizadas neste projeto:

- **SAEB (9º ano)**: `basedosdados.br_inep_saeb.aluno_ef_9ano`
- **Dicionário SAEB**: `basedosdados.br_inep_saeb.dicionario`
- **IBGE (População)**: `basedosdados.br_ibge_populacao.municipio`
- **ENEM (Dados complementares)**: `basedosdados.br_inep_enem.microdados`

### 2.3. Tecnologias Utilizadas

- **Linguagem de Programação**: Python
- **Bibliotecas**: Pandas, NumPy, Matplotlib, Seaborn
- **Armazenamento de Dados**: Arquivos CSV (para simplicidade, poderia ser expandido para um banco de dados/Data warehouse)
- **Visualização**: Matplotlib, Seaborn, Power BI

## 3. Arquitetura da Solução

### 3.1. Fluxo de Processamento (Pipeline)

O pipeline de dados segue um fluxo de ELT (Extract, Load, Transform) com as seguintes etapas:

1. **Extração (Extract)**: Extração dos dados brutos do BigQuery.
2. **Carga (Load)**: Carregamento dos dados em arquivos CSV.
3. **Transformação (Transform)**: Aplicação do dicionário, limpeza, criação de dimensões e fatos.
4. **Análise**: Processamento analítico para responder às questões de negócio.
5. **Visualização**: Criação de visualizações e preparação para o Power BI.

### 3.2. Estrutura de Diretórios

```
projeto_saeb/
│
├── dados_raw/               # Dados brutos extraídos
├── dados_processados/       # Dados transformados (dimensões e fatos)
├── resultados_analise/      # Resultados das análises
│   └── dados_powerbi/       # Dados preparados para o Power BI
└── scripts/                 # Scripts de processamento
    ├── extract_data.py      # Script de extração
    ├── transform_data.py    # Script de transformação
    └── analyze_data.py      # Script de análise
```

## 4. Modelagem de Dados

### 4.1. Modelo Conceitual

Para este projeto, optou-se por utilizar um modelo dimensional do tipo **Estrela (Star Schema)**, devido à sua simplicidade, desempenho para consultas analíticas e facilidade de compreensão pelos usuários de negócio.

O modelo consiste em uma tabela fato central (`fato_desempenho`) conectada a várias tabelas de dimensão, conforme ilustrado abaixo:

```
                     ┌─────────────┐
                     │  dim_tempo  │
                     └──────┬──────┘
                            │
┌──────────────┐      ┌─────┴─────┐      ┌───────────────┐
│ dim_geografia ├──────┤    FATO   ├──────┤  dim_escola   │
└──────────────┘      │ desempenho │      └───────────────┘
                      └─────┬─────┘
                            │
                     ┌──────┴──────┐
                     │  dim_aluno  │
                     └─────────────┘
```

### 4.2. Descrição das Dimensões

#### 4.2.1. Dimensão Tempo (dim_tempo)

Contém informações temporais para análise histórica.

| Atributo | Descrição |
|----------|-----------|
| id_tempo | Identificador único da dimensão tempo |
| ano | Ano de referência dos dados |
| descricao | Descrição textual do ano |
| pre_pandemia | Indicador de período pré-pandemia (antes de 2020) |
| durante_pandemia | Indicador de período durante a pandemia (2020-2021) |
| pos_pandemia | Indicador de período pós-pandemia (após 2021) |

#### 4.2.2. Dimensão Geografia (dim_geografia)

Contém informações geográficas para análise regional.

| Atributo | Descrição |
|----------|-----------|
| id_geografia | Identificador único da dimensão geografia |
| id_regiao | Código da região brasileira |
| regiao_desc | Nome da região (Norte, Nordeste, etc.) |
| sigla_uf | Sigla da Unidade Federativa |
| id_municipio | Código do município (IBGE) |
| populacao | População do município (dados mais recentes) |

#### 4.2.3. Dimensão Escola (dim_escola)

Contém informações sobre as escolas.

| Atributo | Descrição |
|----------|-----------|
| id_dim_escola | Identificador único da dimensão escola |
| id_escola | Código original da escola |
| id_dependencia_adm | Código do tipo de dependência administrativa |
| id_dependencia_adm_desc | Descrição do tipo de escola (Federal, Estadual, Municipal, Privada) |
| id_localizacao | Código de localização da escola |
| id_localizacao_desc | Descrição da localização (Urbana, Rural) |

#### 4.2.4. Dimensão Aluno (dim_aluno)

Contém informações sobre os alunos e suas características socioeconômicas.

| Atributo | Descrição |
|----------|-----------|
| id_dim_aluno | Identificador único da dimensão aluno |
| id_aluno | Código original do aluno |
| tx_resp_q001, tx_resp_q002, ... | Respostas às questões socioeconômicas |
| tx_resp_q001_desc, tx_resp_q002_desc, ... | Descrições das respostas às questões |

### 4.3. Tabela Fato

#### 4.3.1. Fato Desempenho (fato_desempenho)

| Atributo | Descrição |
|----------|-----------|
| id_tempo | Chave estrangeira para dimensão tempo |
| id_geografia | Chave estrangeira para dimensão geografia |
| id_dim_escola | Chave estrangeira para dimensão escola |
| id_dim_aluno | Chave estrangeira para dimensão aluno |
| proficiencia_lp | Proficiência em Língua Portuguesa |
| proficiencia_mt | Proficiência em Matemática |
| proficiencia_media | Média das proficiências |
| nivel_desempenho | Classificação do desempenho (Insatisfatório, Básico, Adequado, Avançado) |

### 4.4. Justificativa do Modelo

Optou-se pelo modelo Estrela pelos seguintes motivos:

1. **Simplicidade**: Fácil de entender e implementar;
2. **Desempenho**: Otimizado para consultas analíticas com menos junções (joins);
3. **Flexibilidade**: Permite adicionar novas dimensões ou medidas conforme necessário;
4. **Usabilidade**: Facilita a criação de cubos OLAP e a navegação pelos dados.

## 5. ETL - Extração, Transformação e Carga

### 5.1. Extração de Dados

A extração dos dados foi realizada diretamente do BigQuery utilizando consultas SQL e a biblioteca `google-cloud-bigquery` do Python. Foram definidos limites para a quantidade de dados extraídos, considerando o escopo do projeto.

```python
# Exemplo de consulta utilizada
query_saeb = """
    SELECT *
    FROM `basedosdados.br_inep_saeb.aluno_ef_9ano`
    WHERE ano >= 2019
    LIMIT 100000
"""
```

### 5.2. Transformação dos Dados

#### 5.2.1. Aplicação do Dicionário

O dicionário SAEB foi utilizado para traduzir os códigos numéricos em descrições textuais, facilitando a interpretação dos dados.

```python
# Trecho de código para aplicação do dicionário
for variavel, grupo in dicionario_agrupado:
    if variavel in df_transformado.columns:
        mapeamento = dict(zip(grupo['chave'], grupo['valor']))
        df_transformado[f"{variavel}_desc"] = df_transformado[variavel].map(mapeamento)
```

#### 5.2.2. Limpeza de Dados

- Conversão de tipos de dados
- Tratamento de valores ausentes
- Cálculo de medidas adicionais (proficiência média)
- Filtro de colunas relevantes

#### 5.2.3. Criação de Dimensões e Fatos

As dimensões foram criadas a partir dos dados originais, extraindo atributos distintos e adicionando identificadores únicos. A tabela de fatos foi construída conectando as dimensões através de suas chaves e mantendo as métricas relevantes.

### 5.3. Carga de Dados

Os dados transformados foram salvos em arquivos CSV para facilitar o acesso e o uso posterior em ferramentas de visualização como o Power BI.

## 6. Análises Realizadas

Para atender às questões de negócio definidas no escopo do projeto, foram implementadas as seguintes análises:

### 6.1. Desempenho por Região

Análise do desempenho médio em cada região brasileira, identificando as regiões com melhor e pior desempenho educacional.

### 6.2. Desempenho por Tipo de Escola

Comparação do desempenho entre escolas públicas (federais, estaduais e municipais) e privadas.

### 6.3. Relação entre Desempenho e Apoio Familiar

Análise da correlação entre o desempenho dos alunos e os níveis de apoio familiar reportados.

### 6.4. Evolução do Desempenho ao Longo dos Anos

Análise da tendência do desempenho educacional ao longo do tempo, identificando melhorias ou quedas.

### 6.5. Relação entre Desempenho e Pretensão Futura

Análise de como a pretensão futura dos alunos (como ingressar em uma universidade) está correlacionada com os resultados de desempenho.

### 6.6. Estados com Escolas Abaixo da Média

Identificação dos estados ou municípios que apresentam maior número de escolas com desempenho abaixo da média nacional.

### 6.7. Impacto da Pandemia no Desempenho

Comparação do desempenho em 2021 (pós-pandemia) com os anos anteriores, avaliando o impacto da COVID-19 na educação.

## 7. Visualizações e Indicadores

### 7.1. Visualizações Geradas

1. **Mapa de Calor por Região**: Visualização do desempenho em diferentes regiões do Brasil.
2. **Evolução Temporal**: Gráfico de linha mostrando a tendência do desempenho ao longo dos anos.
3. **Comparativo Público vs Privado**: Gráfico de barras comparando o desempenho em diferentes tipos de escola.
4. **Ranking de Estados**: Top 10 estados com melhor e pior desempenho.
5. **Análise de Impacto da Pandemia**: Comparativo antes/durante/após a pandemia.

### 7.2. Indicadores-Chave (KPIs)

1. **Proficiência Média**: Média geral das notas em português e matemática.
2. **Variação Percentual**: Evolução do desempenho em relação ao ano anterior.
3. **Gap Público-Privado**: Diferença de desempenho entre escolas públicas e privadas.
4. **Percentual de Escolas Abaixo da Média**: Proporção de escolas com desempenho inferior à média nacional.
5. **Índice de Impacto da Pandemia**: Variação do desempenho entre períodos pré e pós-pandemia.
6. 

## 8. Conclusões

A implementação deste modelo OLAP para os dados do SAEB permitiu uma análise aprofundada do desempenho educacional no Brasil, com foco no 9º ano do Ensino Fundamental. As análises realizadas possibilitaram identificar padrões importantes, como:

- Diferenças significativas de desempenho entre regiões
- Impacto do tipo de escola no desempenho dos alunos
- Correlação entre apoio familiar e resultados educacionais
- Efeitos da pandemia no sistema educacional brasileiro
