import os
import pandas as pd
from google.cloud import bigquery
from datetime import datetime

# Configuração do ambiente
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'caminho/para/seu/arquivo/de/credenciais.json'

def criar_diretorio(nome_diretorio):
    """
    Cria um diretório para armazenar os dados, se não existir.
    
    Args:
        nome_diretorio (str): Nome do diretório a ser criado
    
    Returns:
        str: Caminho do diretório
    """
    if not os.path.exists(nome_diretorio):
        os.makedirs(nome_diretorio)
    return nome_diretorio

def extrair_dados_bigquery(query, nome_arquivo):
    """
    Extrai dados do BigQuery e salva em um arquivo CSV.
    
    Args:
        query (str): Query SQL para extrair os dados
        nome_arquivo (str): Nome do arquivo para salvar os dados
    
    Returns:
        pandas.DataFrame: DataFrame com os dados extraídos
    """
    print(f"Extraindo dados para: {nome_arquivo}")
    cliente = bigquery.Client()
    df = cliente.query(query).to_dataframe()
    df.to_csv(nome_arquivo, index=False)
    print(f"Dados salvos com sucesso: {df.shape[0]} linhas e {df.shape[1]} colunas")
    return df

def main():
    """
    Função principal para extrair todos os dados necessários.
    """
    # Criação do diretório de dados
    diretorio_dados = criar_diretorio('dados_raw')
    
    # Timestamp para identificar a execução
    timestamp = datetime.now().strftime('%Y%m%d')
    
    # Consultas SQL para extração dos dados
    queries = {
        # SAEB - Alunos 9º Ano
        'saeb_aluno_9ano': """
            SELECT *
            FROM `basedosdados.br_inep_saeb.aluno_ef_9ano`
            WHERE ano >= 2019
            LIMIT 100000  -- Ajuste conforme necessidade (remova para todos os dados)
        """,
        
        # Dicionário SAEB
        'saeb_dicionario': """
            SELECT *
            FROM `basedosdados.br_inep_saeb.dicionario`
        """,
        
        # IBGE - População por Município
        'ibge_populacao': """
            SELECT *
            FROM `basedosdados.br_ibge_populacao.municipio`
            WHERE ano >= 2019
        """,
        
        # ENEM - Microdados (amostra para enriquecimento)
        'enem_microdados': """
            SELECT 
                ano, 
                sigla_uf, 
                id_municipio_residencia, 
                tp_escola, 
                tp_ensino, 
                nu_nota_mt, 
                nu_nota_lc, 
                nu_nota_ch, 
                nu_nota_cn, 
                nu_nota_redacao
            FROM `basedosdados.br_inep_enem.microdados`
            WHERE ano >= 2019
            LIMIT 50000  -- Ajuste conforme necessidade
        """,
        
        # ENEM - Dicionário
        'enem_dicionario': """
            SELECT *
            FROM `basedosdados.br_inep_enem.dicionario`
        """
    }
    
    # Extração dos dados
    dados_extraidos = {}
    for nome_query, query in queries.items():
        nome_arquivo = f"{diretorio_dados}/{nome_query}_{timestamp}.csv"
        dados_extraidos[nome_query] = extrair_dados_bigquery(query, nome_arquivo)
    
    print("Extração concluída com sucesso!")
    return dados_extraidos

if __name__ == "__main__":
    main()
