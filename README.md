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

        WHERE ano >= 2019
        LIMIT 500000  # Modificar este valor
    """,
    # ...
}
```
