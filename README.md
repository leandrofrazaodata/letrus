# Projeto de Análise de Dados SAEB

Este projeto visa transformar os microdados do SAEB (Sistema de Avaliação da Educação Básica) em um modelo dimensional para análise educacional, com foco no 9º ano do Ensino Fundamental.

## Estrutura do Projeto

```
projeto_saeb/
│
├── dados_raw/               # Dados brutos extraídos
├── dados_processados/       # Dados transformados (dimensões e fatos)
├── resultados_analise/      # Resultados das análises
│   └── dados_powerbi/       # Dados preparados para o Power BI
├── scripts/                 # Scripts de processamento
│   ├── extract_data.py      # Script de extração
│   ├── transform_data.py    # Script de transformação
│   └── analyze_data.py      # Script de análise
└── docs/                    # Documentação
    └── documentacao.md      # Documentação detalhada do projeto
```

## Pré-requisitos

- Python 3.8 ou superior
- Bibliotecas Python (ver `requirements.txt`)
- Acesso ao BigQuery (para extração dos dados)
- Power BI Desktop (para visualização final)

## Instalação

1. Clone este repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd projeto_saeb
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure suas credenciais do BigQuery:
```bash
# Configure o caminho para o arquivo de credenciais
export GOOGLE_APPLICATION_CREDENTIALS="caminho/para/seu/arquivo/de/credenciais.json"
```

## Uso

### 1. Extração de Dados

Para extrair os dados do BigQuery:

```bash
python scripts/extract_data.py
```

Este script extrairá os dados do SAEB, dicionário, IBGE e ENEM para o diretório `dados_raw/`.

### 2. Transformação de Dados

Para transformar os dados e criar o modelo dimensional:

```bash
python scripts/transform_data.py
```

Este script aplicará o dicionário, limpará os dados e criará as dimensões e fatos no diretório `dados_processados/`.

### 3. Análise de Dados

Para realizar análises e gerar visualizações:

```bash
python scripts/analyze_data.py
```

Este script realizará as análises principais e gerará visualizações no diretório `resultados_analise/`.

### 4. Visualização no Power BI

1. Abra o Power BI Desktop
2. Importe os dados do diretório `resultados_analise/dados_powerbi/`
3. Use o modelo fornecido como base para criar seu dashboard

## Análises Principais

O projeto permite responder às seguintes questões:

1. Quais regiões apresentam o melhor e o pior desempenho educacional?
2. Como o desempenho dos alunos varia entre escolas públicas e privadas?
3. Qual é a relação entre o desempenho e os níveis de apoio familiar?
4. Houve melhoria ou queda no desempenho ao longo dos anos?
5. Como a pretensão futura dos alunos está correlacionada com o desempenho?
6. Quais tipos de escolas apresentam melhor desempenho?
7. Quais estados apresentam maior número de escolas abaixo da média?
8. Como o desempenho em 2021 (pós-pandemia) se compara com anos anteriores?

## Modelo de Dados

O projeto utiliza um modelo dimensional do tipo Estrela (Star Schema) com as seguintes tabelas:

- **Dimensões**:
  - dim_tempo: Informações temporais
  - dim_geografia: Informações geográficas
  - dim_escola: Informações sobre as escolas
  - dim_aluno: Informações sobre os alunos

- **Fatos**:
  - fato_desempenho: Métricas de desempenho dos alunos

Para mais detalhes sobre o modelo, consulte a documentação completa.

## Customização

### Filtros de Dados

Para ajustar a quantidade de dados extraídos, modifique os parâmetros LIMIT nas consultas SQL em `extract_data.py`:

```python
# Exemplo para aumentar a quantidade de dados do SAEB
queries = {
    'saeb_aluno_9ano': """
        SELECT *
        FROM `basedosdados.br_inep_saeb.aluno_ef_9ano`
        WHERE ano >= 2019
        LIMIT 500000  # Modificar este valor
    """,
    # ...
}
```
