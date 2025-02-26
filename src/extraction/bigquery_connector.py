"""
Conector do BigQuery, para extração de dados
"""
import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import logging

from src.utils.logging_utils import setup_logger

logger = setup_logger("bigquery_connector")

class BigQueryConnector:
    """
    Classe de conexão do BQ.
    """
    
    def __init__(self, credentials_path=None, project_id=None):
        """
        Inicializa o conector BQ.
        
        Args:
            credentials_path (str, optional) 
            project_id (str, optional)
        """
        self.credentials_path = credentials_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        self.project_id = project_id
        self.client = None
        self._connect()
    
    def _connect(self):
        """Conexão com o BQ."""
        try:
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = bigquery.Client(
                    credentials=credentials,
                    project=self.project_id or credentials.project_id,
                )
            else:
                self.client = bigquery.Client(project=self.project_id)
            
            logger.info(f"Sucesso na conexão com o BigQuery: {self.client.project}")
        except Exception as e:
            logger.error(f"Falha na conexão com BigQuery: {str(e)}")
            raise
    
    def execute_query(self, query, params=None):
        """
        Executa uma query no BQ.
        
        Args:
            query (str)
            params (dict, optional)
            
        Returns:
            pandas.DataFrame: DF com o resultado da consulta.
        """
        try:
            job_config = bigquery.QueryJobConfig(
                query_parameters=params or []
            )
            query_job = self.client.query(query, job_config=job_config)
            
            results = query_job.result()
            
            # Converte para DataFrame
            df = results.to_dataframe()
            logger.info(f"Query executada com sucesso. {len(df)} registros retornados")
            return df
        
        except Exception as e:
            logger.error(f"Falha na execução da query: {str(e)}")
            raise
    
    def list_tables(self, dataset_id):
        """
        Lista todas as tabelas de um dataset.
        
        Args:
            dataset_id (str)
            
        Returns:
            list: Lista de tabelas
        """
        try:
            tables = list(self.client.list_tables(dataset_id))
            table_names = [table.table_id for table in tables]
            logger.info(f"Localizadas {len(table_names)} tabelas no dataset {dataset_id}")
            return table_names
        except Exception as e:
            logger.error(f"Falha ao obter as tabelas em {dataset_id}: {str(e)}")
            raise
    
    def get_table_schema(self, table_id):
        """
        Retorna o schema de uma tabela.
        
        Args:
            table_id (str)
            
        Returns:
            list: Lista de schemas de objetos
        """
        try:
            table = self.client.get_table(table_id)
            logger.info(f"Schema da tabela: {table_id}")
            return table.schema
        except Exception as e:
            logger.error(f"Falha ao obter o schema da tabela: {table_id}: {str(e)}")
            raise


    def close(self):
        """Encerra a conexão com o BQ"""
        self.client = None
        logger.info("Conexão com o BigQuery encerrada")
