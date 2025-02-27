import os
import pandas as pd
import numpy as np
from datetime import datetime

def carregar_dados(diretorio, prefixo_arquivo):
    """
    Carrega os dados mais recentes de um determinado tipo.
    
    Args:
        diretorio (str): Diretório onde os dados estão armazenados
        prefixo_arquivo (str): Prefixo do nome do arquivo
    
    Returns:
        pandas.DataFrame: DataFrame com os dados carregados
    """
    # Encontra o arquivo mais recente com o prefixo especificado
    arquivos = [f for f in os.listdir(diretorio) if f.startswith(prefixo_arquivo)]
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo encontrado com o prefixo {prefixo_arquivo}")
    
    arquivo_mais_recente = max(arquivos)
    caminho_arquivo = os.path.join(diretorio, arquivo_mais_recente)
    
    print(f"Carregando dados de: {caminho_arquivo}")
    return pd.read_csv(caminho_arquivo)

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

def aplicar_dicionario(df_dados, df_dicionario):
    """
    Aplica as traduções do dicionário aos dados.
    
    Args:
        df_dados (pandas.DataFrame): DataFrame com os dados a serem traduzidos
        df_dicionario (pandas.DataFrame): DataFrame com o dicionário
    
    Returns:
        pandas.DataFrame: DataFrame com os dados traduzidos
    """
    print("Aplicando dicionário aos dados...")
    df_transformado = df_dados.copy()
    
    # Filtra apenas as entradas do dicionário relevantes para os dados atuais
    colunas_dados = set(df_dados.columns)
    df_dicionario_filtrado = df_dicionario[df_dicionario['variavel'].isin(colunas_dados)]
    
    # Agrupa o dicionário por variável para facilitar a aplicação
    dicionario_agrupado = df_dicionario_filtrado.groupby('variavel')
    
    # Para cada variável no dicionário
    for variavel, grupo in dicionario_agrupado:
        if variavel in df_transformado.columns:
            # Cria um mapeamento de código para valor
            mapeamento = dict(zip(grupo['chave'], grupo['valor']))
            
            # Verifica se a coluna é numérica para evitar erros de tipo
            if pd.api.types.is_numeric_dtype(df_transformado[variavel]):
                # Converte chaves para o mesmo tipo da coluna
                mapeamento_tipado = {int(k) if pd.notna(k) else k: v for k, v in mapeamento.items()}
                # Aplica o mapeamento e cria uma nova coluna com o sufixo _desc
                df_transformado[f"{variavel}_desc"] = df_transformado[variavel].map(mapeamento_tipado)
            else:
                df_transformado[f"{variavel}_desc"] = df_transformado[variavel].map(mapeamento)
    
    print("Dicionário aplicado com sucesso!")
    return df_transformado

def limpar_dados_saeb(df_saeb):
    """
    Limpa e prepara os dados do SAEB para análise.
    
    Args:
        df_saeb (pandas.DataFrame): DataFrame com os dados do SAEB
    
    Returns:
        pandas.DataFrame: DataFrame com os dados limpos
    """
    print("Limpando e preparando dados do SAEB...")
    df_limpo = df_saeb.copy()
    
    # Converte as notas para numérico, lidando com valores ausentes
    colunas_nota = [col for col in df_limpo.columns if col.startswith('proficiencia_')]
    for col in colunas_nota:
        df_limpo[col] = pd.to_numeric(df_limpo[col], errors='coerce')
    
    # Filtrar apenas registros com notas válidas
    df_limpo = df_limpo.dropna(subset=colunas_nota, how='all')
    
    # Calcular média das proficiências por aluno (quando disponíveis)
    df_limpo['proficiencia_media'] = df_limpo[colunas_nota].mean(axis=1)
    
    # Remover colunas desnecessárias ou com muitos valores ausentes
    # Ajuste conforme necessidade após análise exploratória
    colunas_a_manter = [
        'ano', 'id_regiao', 'sigla_uf', 'id_municipio', 'id_escola', 
        'id_dependencia_adm', 'id_localizacao', 'id_turma', 'id_aluno',
        'proficiencia_media'
    ] + colunas_nota + [col for col in df_limpo.columns if col.endswith('_desc')]
    
    # Incluir colunas importantes para análises específicas
    colunas_relevantes = [
        'tx_resp_q001', 'tx_resp_q002', 'tx_resp_q003', 'tx_resp_q004',
        'tx_resp_q005', 'tx_resp_q006', 'tx_resp_q007', 'tx_resp_q008'
    ]
    
    for col in colunas_relevantes:
        if col in df_limpo.columns:
            colunas_a_manter.append(col)
            # Adicionar também a coluna traduzida se existir
            if f"{col}_desc" in df_limpo.columns:
                colunas_a_manter.append(f"{col}_desc")
    
    # Manter apenas as colunas necessárias
    colunas_a_manter = list(set(colunas_a_manter).intersection(df_limpo.columns))
    df_limpo = df_limpo[colunas_a_manter]
    
    print("Limpeza concluída com sucesso!")
    return df_limpo

def criar_dimensao_tempo(df_saeb):
    """
    Cria a dimensão tempo a partir dos dados do SAEB.
    
    Args:
        df_saeb (pandas.DataFrame): DataFrame com os dados do SAEB
    
    Returns:
        pandas.DataFrame: DataFrame com a dimensão tempo
    """
    print("Criando dimensão tempo...")
    # Extrair anos únicos
    anos = df_saeb['ano'].unique()
    
    # Criar DataFrame para a dimensão tempo
    dim_tempo = pd.DataFrame({
        'id_tempo': range(1, len(anos) + 1),
        'ano': anos,
        'descricao': [f"Ano {ano}" for ano in anos],
        'pre_pandemia': [1 if ano < 2020 else 0 for ano in anos],
        'durante_pandemia': [1 if ano in [2020, 2021] else 0 for ano in anos],
        'pos_pandemia': [1 if ano > 2021 else 0 for ano in anos]
    })
    
    print("Dimensão tempo criada com sucesso!")
    return dim_tempo

def criar_dimensao_geografia(df_saeb, df_populacao):
    """
    Cria a dimensão geografia a partir dos dados do SAEB e IBGE.
    
    Args:
        df_saeb (pandas.DataFrame): DataFrame com os dados do SAEB
        df_populacao (pandas.DataFrame): DataFrame com os dados de população do IBGE
    
    Returns:
        pandas.DataFrame: DataFrame com a dimensão geografia
    """
    print("Criando dimensão geografia...")
    # Extrair dados geográficos únicos do SAEB
    geografia_saeb = df_saeb[['id_regiao', 'sigla_uf', 'id_municipio']].drop_duplicates()
    
    # Adicionar região_desc se existir
    if 'id_regiao_desc' in df_saeb.columns:
        geografia_saeb['regiao_desc'] = df_saeb['id_regiao_desc']
    
    # Preparar dados de população
    df_pop_municipios = df_populacao[['ano', 'id_municipio', 'populacao']].copy()
    
    # Obter população mais recente disponível
    pop_mais_recente = df_pop_municipios.sort_values('ano', ascending=False)
    pop_mais_recente = pop_mais_recente.drop_duplicates(subset=['id_municipio'])
    
    # Mesclar dados geográficos com população
    dim_geografia = geografia_saeb.merge(
        pop_mais_recente[['id_municipio', 'populacao']],
        on='id_municipio',
        how='left'
    )
    
    # Adicionar identificador único
    dim_geografia['id_geografia'] = range(1, len(dim_geografia) + 1)
    
    # Organizar colunas
    colunas_ordem = ['id_geografia', 'id_regiao']
    if 'regiao_desc' in dim_geografia.columns:
        colunas_ordem.append('regiao_desc')
    colunas_ordem.extend(['sigla_uf', 'id_municipio', 'populacao'])
    
    dim_geografia = dim_geografia[colunas_ordem]
    
    print("Dimensão geografia criada com sucesso!")
    return dim_geografia

def criar_dimensao_escola(df_saeb):
    """
    Cria a dimensão escola a partir dos dados do SAEB.
    
    Args:
        df_saeb (pandas.DataFrame): DataFrame com os dados do SAEB
    
    Returns:
        pandas.DataFrame: DataFrame com a dimensão escola
    """
    print("Criando dimensão escola...")
    # Extrair dados escolares únicos
    cols_escola = ['id_escola', 'id_dependencia_adm', 'id_localizacao']
    
    # Adicionar colunas traduzidas se existirem
    cols_desc = []
    for col in ['id_dependencia_adm', 'id_localizacao']:
        if f"{col}_desc" in df_saeb.columns:
            cols_desc.append(f"{col}_desc")
    
    escolas_saeb = df_saeb[cols_escola + cols_desc].drop_duplicates()
    
    # Adicionar identificador único
    dim_escola = escolas_saeb.copy()
    dim_escola['id_dim_escola'] = range(1, len(dim_escola) + 1)
    
    # Organizar colunas
    colunas_ordem = ['id_dim_escola', 'id_escola', 'id_dependencia_adm']
    if 'id_dependencia_adm_desc' in dim_escola.columns:
        colunas_ordem.append('id_dependencia_adm_desc')
    colunas_ordem.append('id_localizacao')
    if 'id_localizacao_desc' in dim_escola.columns:
        colunas_ordem.append('id_localizacao_desc')
    
    dim_escola = dim_escola[colunas_ordem]
    
    print("Dimensão escola criada com sucesso!")
    return dim_escola

def criar_dimensao_aluno(df_saeb):
    """
    Cria a dimensão aluno a partir dos dados do SAEB.
    
    Args:
        df_saeb (pandas.DataFrame): DataFrame com os dados do SAEB
    
    Returns:
        pandas.DataFrame: DataFrame com a dimensão aluno
    """
    print("Criando dimensão aluno...")
    # Colunas de interesse para informações do aluno
    # Ajuste conforme as colunas disponíveis no seu dataset
    cols_aluno = ['id_aluno']
    
    # Identificar colunas com características do aluno
    cols_caracteristicas = [col for col in df_saeb.columns if col.startswith('tx_resp_q')]
    # Adicionar suas descrições
    cols_desc = [f"{col}_desc" for col in cols_caracteristicas if f"{col}_desc" in df_saeb.columns]
    
    # Criar dimensão aluno
    dim_aluno = df_saeb[cols_aluno + cols_caracteristicas + cols_desc].drop_duplicates()
    
    # Adicionar identificador único
    dim_aluno['id_dim_aluno'] = range(1, len(dim_aluno) + 1)
    
    # Mover id_dim_aluno para a primeira coluna
    colunas_ordenadas = ['id_dim_aluno'] + [col for col in dim_aluno.columns if col != 'id_dim_aluno']
    dim_aluno = dim_aluno[colunas_ordenadas]
    
    print("Dimensão aluno criada com sucesso!")
    return dim_aluno

def criar_fato_desempenho(df_saeb, dim_tempo, dim_geografia, dim_escola, dim_aluno):
    """
    Cria a tabela fato de desempenho a partir dos dados do SAEB e dimensões.
    
    Args:
        df_saeb (pandas.DataFrame): DataFrame com os dados do SAEB
        dim_tempo (pandas.DataFrame): DataFrame com a dimensão tempo
        dim_geografia (pandas.DataFrame): DataFrame com a dimensão geografia
        dim_escola (pandas.DataFrame): DataFrame com a dimensão escola
        dim_aluno (pandas.DataFrame): DataFrame com a dimensão aluno
    
    Returns:
        pandas.DataFrame: DataFrame com a tabela fato de desempenho
    """
    print("Criando tabela fato de desempenho...")
    # Colunas de métricas
    colunas_nota = [col for col in df_saeb.columns if col.startswith('proficiencia_')]
    
    # Criar tabela fato inicial com chaves naturais
    fato_base = df_saeb[['ano', 'id_municipio', 'id_escola', 'id_aluno'] + colunas_nota + ['proficiencia_media']].copy()
    
    # Mesclar com dimensão tempo
    fato_com_tempo = fato_base.merge(
        dim_tempo[['id_tempo', 'ano']],
        on='ano',
        how='left'
    )
    
    # Mesclar com dimensão geografia
    fato_com_geo = fato_com_tempo.merge(
        dim_geografia[['id_geografia', 'id_municipio']],
        on='id_municipio',
        how='left'
    )
    
    # Mesclar com dimensão escola
    fato_com_escola = fato_com_geo.merge(
        dim_escola[['id_dim_escola', 'id_escola']],
        on='id_escola',
        how='left'
    )
    
    # Mesclar com dimensão aluno
    fato_desempenho = fato_com_escola.merge(
        dim_aluno[['id_dim_aluno', 'id_aluno']],
        on='id_aluno',
        how='left'
    )
    
    # Selecionar apenas as colunas relevantes
    cols_fato = ['id_tempo', 'id_geografia', 'id_dim_escola', 'id_dim_aluno'] + colunas_nota + ['proficiencia_media']
    fato_desempenho = fato_desempenho[cols_fato]
    
    # Adicionar medidas calculadas
    fato_desempenho['nivel_desempenho'] = pd.cut(
        fato_desempenho['proficiencia_media'],
        bins=[0, 200, 250, 300, float('inf')],
        labels=['Insatisfatório', 'Básico', 'Adequado', 'Avançado']
    )
    
    print("Tabela fato de desempenho criada com sucesso!")
    return fato_desempenho

def main():
    """
    Função principal para transformar os dados e criar o modelo dimensional.
    """
    # Diretórios para dados
    diretorio_entrada = 'dados_raw'
    diretorio_saida = criar_diretorio('dados_processados')
    
    # Timestamp para identificar a execução
    timestamp = datetime.now().strftime('%Y%m%d')
    
    # Carregar dados
    try:
        df_saeb = carregar_dados(diretorio_entrada, 'saeb_aluno_9ano')
        df_dicionario = carregar_dados(diretorio_entrada, 'saeb_dicionario')
        df_populacao = carregar_dados(diretorio_entrada, 'ibge_populacao')
    except FileNotFoundError as e:
        print(f"Erro ao carregar dados: {e}")
        return
    
    # Aplicar dicionário
    df_saeb_traduzido = aplicar_dicionario(df_saeb, df_dicionario)
    
    # Limpar dados
    df_saeb_limpo = limpar_dados_saeb(df_saeb_traduzido)
    
    # Criar dimensões
    dim_tempo = criar_dimensao_tempo(df_saeb_limpo)
    dim_geografia = criar_dimensao_geografia(df_saeb_limpo, df_populacao)
    dim_escola = criar_dimensao_escola(df_saeb_limpo)
    dim_aluno = criar_dimensao_aluno(df_saeb_limpo)
    
    # Criar tabela fato
    fato_desempenho = criar_fato_desempenho(df_saeb_limpo, dim_tempo, dim_geografia, dim_escola, dim_aluno)
    
    # Salvar dimensões e fatos
    dim_tempo.to_csv(f"{diretorio_saida}/dim_tempo_{timestamp}.csv", index=False)
    dim_geografia.to_csv(f"{diretorio_saida}/dim_geografia_{timestamp}.csv", index=False)
    dim_escola.to_csv(f"{diretorio_saida}/dim_escola_{timestamp}.csv", index=False)
    dim_aluno.to_csv(f"{diretorio_saida}/dim_aluno_{timestamp}.csv", index=False)
    fato_desempenho.to_csv(f"{diretorio_saida}/fato_desempenho_{timestamp}.csv", index=False)
    
    print("Transformação concluída com sucesso!")
    print(f"Dimensões e fatos salvos no diretório: {diretorio_saida}")

if __name__ == "__main__":
    main()
