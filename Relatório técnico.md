# Relatório Técnico - Projeto SAEB Analytics

## 1. Introdução

Este relatório apresenta a documentação técnica do projeto SAEB Analytics, desenvolvido para a Letrus como parte de um case técnico para a posição de Analytics Engineer Sr. O projeto consiste na transformação dos microdados do Sistema de Avaliação da Educação Básica (SAEB) em um modelo analítico dimensionalmente modelado, visando facilitar análises educacionais estratégicas.

## 2. Visão Geral da Solução

A solução implementa um pipeline completo de ETL (Extração, Transformação e Carga) que processa os microdados do SAEB, com foco nos alunos do 9º ano do Ensino Fundamental, e os disponibiliza em um modelo OLAP para análise através de dashboards interativos.

### 2.1 Arquitetura da Solução

![Fluxo do Processo](docs/fluxo_processo.png)

A arquitetura é composta por três camadas principais:

1. **Camada de Extração**: Responsável por obter os dados do BigQuery e preparar os arquivos brutos para processamento.
2. **Camada de Transformação**: Implementa limpeza, aplicação do dicionário, engenharia de features e validação de qualidade.
3. **Camada de Carregamento**: Cria o modelo dimensional no Data Warehouse e prepara os dados para visualização.

## 3. Extração de Dados

### 3.1 Fonte de Dados

Os dados são extraídos da base pública do SAEB disponível no BigQuery:
- Tabela: `basedosdados.br_inep_saeb.aluno_ef_9ano`
- Dicionário: `basedosdados.br_inep_saeb.dicionario`

### 3.2 Processo de Extração

O processo de extração foi implementado utilizando a API do BigQuery para Python, com os seguintes componentes:

- **BigQueryConnector**: Classe responsável por estabelecer conexão com o BigQuery e executar consultas.
- **SAEBExtractor**: Classe especializada na extração dos dados do SAEB e do dicionário correspondente.

Exemplo de código de extração:

```python
# Extração de dados do SAEB
saeb_df = connector.extract_saeb_data(ano=2021)

# Extração do dicionário
dictionary_df = connector.extract_dictionary()
```

Os dados extraídos são salvos em formato Parquet para processamento posterior, garantindo eficiência e preservação dos tipos de dados.

## 4. Transformação de Dados

### 4.1 Etapas de Transformação

O processo de transformação foi dividido em quatro etapas principais:

1. **Limpeza de Dados**: Tratamento de valores ausentes e outliers.
2. **Aplicação do Dicionário**: Transformação dos códigos numéricos em valores descritivos.
3. **Engenharia de Features**: Criação de novas variáveis analíticas.
4. **Validação de Qualidade**: Verificação de integridade e consistência dos dados.

### 4.2 Engenharia de Features

Foram criadas as seguintes features derivadas para enriquecer as análises:

- **NIVEL_LP/NIVEL_MT**: Categorização dos níveis de proficiência (Insuficiente, Básico, Proficiente, Avançado).
- **PROFICIENCIA_MEDIA**: Média das proficiências em Língua Portuguesa e Matemática.
- **REGIAO**: Derivada a partir do código da UF.
- **TIPO_ESCOLA**: Simplificação do tipo de escola (Federal, Estadual, Municipal, Privada).
- **ESCOLA_ABAIXO_MEDIA**: Flag para identificar escolas com desempenho abaixo da média nacional.
- **NIVEL_APOIO_FAMILIAR**: Indicador de apoio familiar calculado a partir das respostas ao questionário.
- **PRETENDE_UNIVERSIDADE**: Flag indicando se o aluno tem aspirações de ingressar na universidade.

### 4.3 Controle de Qualidade

Um componente dedicado de validação de qualidade foi implementado para verificar:

- Presença de valores ausentes
- Identificação de outliers
- Verificação de valores inválidos
- Conformidade com regras de negócio (ex.: faixas de proficiência válidas)

Os resultados das verificações são registrados e podem ser consultados para monitoramento da qualidade dos dados.

## 5. Modelagem Dimensional

### 5.1 Escolha do Modelo Dimensional

Foi adotado o modelo Estrela (Star Schema) devido às seguintes vantagens:

- **Simplicidade**: Facilita o entendimento por parte dos usuários de negócio.
- **Performance**: Oferece melhor desempenho para queries analíticas.
- **Flexibilidade**: Permite expandir o modelo com novas dimensões e métricas.
- **Adequação**: Ideal para o cenário de análise educacional com dimensões claras (aluno, escola, localização, tempo).

### 5.2 Estrutura do Modelo


O modelo é composto por:

#### Tabelas de Dimensão:

1. **dim_aluno**: Características dos alunos e respostas ao questionário.
   - Atributos principais: SEXO, RACA_COR, IDADE, respostas ao questionário, NIVEL_APOIO_FAMILIAR, PRETENDE_UNIVERSIDADE.

2. **dim_escola**: Informações sobre as escolas.
   - Atributos principais: TIPO_ESCOLA, ID_DEPENDENCIA_ADM, ID_LOCALIZACAO, ESCOLA_ABAIXO_MEDIA, ESCOLA_MEDIA.

3. **dim_localizacao**: Dados geográficos.
   - Atributos principais: REGIAO, SIGLA_UF, NOME_UF, NOME_MUNICIPIO.

4. **dim_tempo**: Dimensão temporal.
   - Atributos principais: ANO, DECADA, POS_PANDEMIA.

#### Tabela de Fato:

- **fato_desempenho**: Contém as métricas de proficiência e chaves para todas as dimensões.
   - Métricas principais: PROFICIENCIA_LP_SAEB, PROFICIENCIA_MT_SAEB, PROFICIENCIA_MEDIA.
   - Chaves estrangeiras: SK_ALUNO, SK_ESCOLA, SK_LOCALIZACAO, SK_TEMPO.

## 6. Implementação do ETL

### 6.1 Tecnologias Utilizadas

- **Linguagem**: Python 3.8+
- **Processamento de Dados**: Pandas, NumPy
- **Conexão com Fontes**: Google Cloud BigQuery
- **Armazenamento Intermediário**: Parquet
- **Data Warehouse**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Transformações Adicionais**: DBT
- **Visualização**: Streamlit

### 6.2 Estrutura do Código

O código foi organizado seguindo princípios de modularidade, reutilização e manutenibilidade:

```
saeb_analytics/
├── src/
│   ├── extraction/       # Módulos de extração
│   ├── transformation/   # Módulos de transformação
│   ├── loading/          # Módulos de carregamento
│   └── utils/            # Utilitários
├── dbt/                  # Modelos DBT
├── streamlit/            # Dashboard Streamlit
└── main.py               # Orquestrador do pipeline
```

### 6.3 Configuração Flexível

Todas as configurações são centralizadas em um arquivo YAML, permitindo ajustes sem modificação de código:

```yaml
bigquery:
  credentials_path: "path_to_credentials.json"
  project_id: "project-id"

extraction:
  output_dir: "data/raw"

transformation:
  input_dir: "data/raw"
  output_dir: "data/transformed"

loading:
  db_uri: "sqlite:///data/saeb_dw.db"
  schema_name: "saeb_dw"
```

## 7. Visualização e Análise

### 7.1 Dashboard Streamlit

Foi desenvolvido um dashboard interativo utilizando Streamlit, com as seguintes seções:

1. **Visão Geral**: Resumo das principais métricas e distribuição de proficiência.
2. **Desempenho Regional**: Análise por região, estado e município.
3. **Comparativo entre Escolas**: Análise por tipo de escola (pública vs. privada).
4. **Evolução Temporal**: Tendências ao longo dos anos.
5. **Fatores de Influência**: Correlação entre desempenho e fatores como apoio familiar.
6. **Análise Pós-Pandemia**: Comparativo antes e após a pandemia de COVID-19.

### 7.2 Exemplos de Análises

O modelo dimensional permite responder questões estratégicas como:

- **Quais regiões apresentam o melhor e pior desempenho?**
  - A análise regional evidencia disparidades significativas entre as diferentes regiões do Brasil.

- **Como o desempenho varia entre escolas públicas e privadas?**
  - O dashboard permite visualizar as diferenças de desempenho por tipo de escola.

- **Qual a relação entre o desempenho e o apoio familiar?**
  - A análise mostra forte correlação entre o nível de apoio familiar e o desempenho dos alunos.

- **Como a pandemia afetou o desempenho educacional?**
  - A comparação pré e pós-pandemia evidencia os impactos da interrupção das aulas presenciais.

## 8. Boas Práticas Implementadas

### 8.1 Engenharia de Software

- **Modularidade**: Componentes com responsabilidades bem definidas.
- **Reutilização**: Classes e funções genéricas que podem ser reaproveitadas.
- **Documentação**: Docstrings detalhadas e comentários explicativos.
- **Tratamento de Erros**: Estruturas try-except para lidar com falhas.
- **Logging**: Sistema de logs para rastreamento de operações.

### 8.2 Engenharia de Dados

- **Idempotência**: O pipeline pode ser executado múltiplas vezes sem efeitos colaterais.
- **Validação de Dados**: Verificações de qualidade em cada etapa do pipeline.
- **Eficiência**: Uso de formatos otimizados como Parquet.
- **Rastreabilidade**: Metadados de carga e atualização em cada tabela.
- **Escalabilidade**: Estrutura preparada para crescimento do volume de dados.

## 9. Conclusões e Próximos Passos

### 9.1 Resultados Alcançados

O projeto entrega um pipeline ETL completo e um modelo dimensional que atende às necessidades de análise educacional, permitindo uma visão abrangente do desempenho dos alunos do 9º ano no SAEB, com identificação de fatores de influência e disparidades regionais.

### 9.2 Próximos Passos

Para evolução futura do projeto, recomenda-se:

1. **Integração com dados adicionais**: Incorporar dados do IBGE (contexto socioeconômico) e ENEM (continuidade educacional).
2. **Orquestração**: Implementar Apache Airflow para gerenciamento de fluxos de trabalho.
3. **Automação de Testes**: Desenvolver testes unitários e de integração.
4. **Infraestrutura como Código**: Containerização com Docker e implantação em ambientes cloud.
5. **Pipeline de CI/CD**: Implementar integração e entrega contínuas.
6. **Machine Learning**: Desenvolver modelos preditivos para identificação precoce de riscos educacionais.

## 10. Referências

- Documentação do SAEB: https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/saeb
- Base dos Dados: https://basedosdados.org/dataset/br-inep-saeb
- Kimball, R. & Ross, M. (2013). The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling.
- Documentação do DBT: https://docs.getdbt.com/
- Documentação do Streamlit: https://docs.streamlit.io/
