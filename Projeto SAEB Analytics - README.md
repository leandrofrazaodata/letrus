# SAEB Analytics - Projeto de Engenharia de Dados

Este projeto implementa um pipeline de ETL e modelagem dimensional para análise dos dados do SAEB (Sistema de Avaliação da Educação Básica), com foco nos alunos do 9º ano do Ensino Fundamental.

## Visão Geral

O projeto transforma os microdados do SAEB em um modelo OLAP (Star Schema) para facilitar análises educacionais estratégicas. O pipeline extrai dados do BigQuery, aplica transformações utilizando Python, e carrega em um Data Warehouse para visualização através de dashboards interativos.

## Estrutura do Projeto

```
saeb_analytics/
├── README.md                 # Este arquivo
├── src/                      # Código-fonte do pipeline ETL
│   ├── extraction/           # Módulos de extração de dados
│   ├── transformation/       # Módulos de transformação de dados
│   ├── loading/              # Módulos de carregamento no DW
│   └── utils/                # Utilitários (configuração, logging)
├── dbt/                      # Modelos DBT para transformações
├── notebooks/                # Notebooks de análise exploratória
├── streamlit/                # Dashboard Streamlit
├── docs/                     # Documentação
├── data/                     # Dados (ignorados pelo git)
├── config.yml                # Arquivo de configuração
└── main.py                   # Script principal do pipeline
```

## Modelo de Dados

O projeto utiliza um modelo dimensional Estrela (Star Schema) com as seguintes tabelas:

### Tabelas Dimensão
- **dim_aluno**: Características dos alunos e respostas ao questionário
- **dim_escola**: Informações sobre as escolas (tipo, dependência administrativa)
- **dim_localizacao**: Dados geográficos (região, UF, município)
- **dim_tempo**: Dimensão temporal (ano, pré/pós-pandemia)

### Tabela Fato
- **fato_desempenho**: Medidas de proficiência em Língua Portuguesa e Matemática

## Tecnologias Utilizadas

- **Extração**: Python, Google BigQuery
- **Transformação**: Python (Pandas), DBT
- **Carregamento**: SQLAlchemy, SQLite/PostgreSQL
- **Visualização**: Streamlit
- **Controle de Qualidade**: Validação de dados integrada
- **DevOps**: Logging, configuração modular

## Configuração e Instalação

### Pré-requisitos
- Python 3.8+
- Conta Google Cloud com acesso ao BigQuery
- Pip ou Conda

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/saeb-analytics.git
cd saeb-analytics
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
