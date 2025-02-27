import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configurar o estilo das visualizações
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('Blues_r')

def carregar_dados_processados(diretorio, prefixo_arquivo):
    """
    Carrega os dados processados mais recentes de um determinado tipo.
    
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
    Cria um diretório para armazenar os resultados, se não existir.
    
    Args:
        nome_diretorio (str): Nome do diretório a ser criado
    
    Returns:
        str: Caminho do diretório
    """
    if not os.path.exists(nome_diretorio):
        os.makedirs(nome_diretorio)
    return nome_diretorio

def analisar_desempenho_por_regiao(fato, dim_geografia, dim_tempo):
    """
    Analisa o desempenho por região.
    
    Args:
        fato (pandas.DataFrame): DataFrame com a tabela fato
        dim_geografia (pandas.DataFrame): DataFrame com a dimensão geografia
        dim_tempo (pandas.DataFrame): DataFrame com a dimensão tempo
    
    Returns:
        pandas.DataFrame: DataFrame com o desempenho médio por região
    """
    print("Analisando desempenho por região...")
    
    # Mesclar fato com dimensões
    df_analise = fato.merge(
        dim_geografia[['id_geografia', 'id_regiao']],
        on='id_geografia',
        how='left'
    ).merge(
        dim_tempo[['id_tempo', 'ano']],
        on='id_tempo',
        how='left'
    )
    
    # Calcular métricas por região e ano
    desempenho_regiao = df_analise.groupby(['id_regiao', 'ano'])['proficiencia_media'].agg(
        proficiencia_media=('mean'),
        quantidade_alunos=('count')
    ).reset_index()
    
    # Adicionar nome da região se disponível
    if 'regiao_desc' in dim_geografia.columns:
        mapa_regioes = dim_geografia[['id_regiao', 'regiao_desc']].drop_duplicates().set_index('id_regiao')['regiao_desc'].to_dict()
        desempenho_regiao['regiao_desc'] = desempenho_regiao['id_regiao'].map(mapa_regioes)
    
    print("Análise de desempenho por região concluída!")
    return desempenho_regiao

def analisar_desempenho_por_tipo_escola(fato, dim_escola, dim_tempo):
    """
    Analisa o desempenho por tipo de escola (pública vs privada).
    
    Args:
        fato (pandas.DataFrame): DataFrame com a tabela fato
        dim_escola (pandas.DataFrame): DataFrame com a dimensão escola
        dim_tempo (pandas.DataFrame): DataFrame com a dimensão tempo
    
    Returns:
        pandas.DataFrame: DataFrame com o desempenho médio por tipo de escola
    """
    print("Analisando desempenho por tipo de escola...")
    
    # Verificar se temos a coluna de descrição do tipo de dependência administrativa
    cols_escola = ['id_dim_escola', 'id_dependencia_adm']
    if 'id_dependencia_adm_desc' in dim_escola.columns:
        cols_escola.append('id_dependencia_adm_desc')
    
    # Mesclar fato com dimensões
    df_analise = fato.merge(
        dim_escola[cols_escola],
        on='id_dim_escola',
        how='left'
    ).merge(
        dim_tempo[['id_tempo', 'ano']],
        on='id_tempo',
        how='left'
    )
    
    # Calcular métricas por tipo de escola e ano
    grupo_by = ['id_dependencia_adm', 'ano']
    if 'id_dependencia_adm_desc' in cols_escola:
        grupo_by = ['id_dependencia_adm', 'id_dependencia_adm_desc', 'ano']
    
    desempenho_escola = df_analise.groupby(grupo_by)['proficiencia_media'].agg(
        proficiencia_media=('mean'),
        quantidade_alunos=('count')
    ).reset_index()
    
    print("Análise de desempenho por tipo de escola concluída!")
    return desempenho_escola

def analisar_desempenho_apoio_familiar(fato, dim_aluno, dim_tempo):
    """
    Analisa a relação entre desempenho e apoio familiar.
    
    Args:
        fato (pandas.DataFrame): DataFrame com a tabela fato
        dim_aluno (pandas.DataFrame): DataFrame com a dimensão aluno
        dim_tempo (pandas.DataFrame): DataFrame com a dimensão tempo
    
    Returns:
        pandas.DataFrame: DataFrame com o desempenho relacionado ao apoio familiar
    """
    print("Analisando relação entre desempenho e apoio familiar...")
    
    # Identificar colunas que podem representar apoio familiar
    # Ajustar conforme os dados disponíveis no seu caso
    colunas_apoio = [col for col in dim_aluno.columns if col.startswith('tx_resp_q') and col.endswith('_desc')]
    
    if not colunas_apoio:
        print("Não foram encontradas colunas que representam apoio familiar!")
        return None
    
    # Mesclar fato com dimensões
    df_analise = fato.merge(
        dim_aluno[['id_dim_aluno'] + colunas_apoio],
        on='id_dim_aluno',
        how='left'
    ).merge(
        dim_tempo[['id_tempo', 'ano']],
        on='id_tempo',
        how='left'
    )
    
    # Para cada coluna de apoio, analisar a relação com o desempenho
    resultados = []
    for coluna in colunas_apoio:
        # Calcular média por categoria de apoio
        desempenho_por_apoio = df_analise.groupby([coluna, 'ano'])['proficiencia_media'].agg(
            proficiencia_media=('mean'),
            quantidade_alunos=('count')
        ).reset_index()
        
        # Adicionar identificador da coluna
        desempenho_por_apoio['tipo_apoio'] = coluna
        resultados.append(desempenho_por_apoio)
    
    # Combinar resultados
    if resultados:
        resultado_final = pd.concat(resultados)
        print("Análise de relação entre desempenho e apoio familiar concluída!")
        return resultado_final
    
    return None

def analisar_evolucao_desempenho(fato, dim_tempo):
    """
    Analisa a evolução do desempenho ao longo dos anos.
    
    Args:
        fato (pandas.DataFrame): DataFrame com a tabela fato
        dim_tempo (pandas.DataFrame): DataFrame com a dimensão tempo
    
    Returns:
        pandas.DataFrame: DataFrame com a evolução do desempenho
    """
    print("Analisando evolução do desempenho ao longo dos anos...")
    
    # Mesclar fato com dimensão tempo
    df_analise = fato.merge(
        dim_tempo[['id_tempo', 'ano']],
        on='id_tempo',
        how='left'
    )
    
    # Calcular métricas por ano
    evolucao = df_analise.groupby('ano')['proficiencia_media'].agg(
        proficiencia_media=('mean'),
        desvio_padrao=('std'),
        quantidade_alunos=('count'),
        minimo=('min'),
        maximo=('max')
    ).reset_index()
    
    # Calcular variação percentual em relação ao ano anterior
    evolucao['variacao_percentual'] = evolucao['proficiencia_media'].pct_change() * 100
    
    print("Análise de evolução do desempenho concluída!")
    return evolucao

def analisar_desempenho_e_pretensao_futura(fato, dim_aluno, dim_tempo):
    """
    Analisa a relação entre desempenho e pretensão futura dos alunos.
    
    Args:
        fato (pandas.DataFrame): DataFrame com a tabela fato
        dim_aluno (pandas.DataFrame): DataFrame com a dimensão aluno
        dim_tempo (pandas.DataFrame): DataFrame com a dimensão tempo
    
    Returns:
        pandas.DataFrame: DataFrame com o desempenho relacionado à pretensão futura
    """
    print("Analisando relação entre desempenho e pretensão futura...")
    
    # Identificar coluna que representa pretensão futura
    # Esta coluna pode variar dependendo dos dados disponíveis
    colunas_pretensao = [col for col in dim_aluno.columns if col.endswith('_desc') and 'futur' in col.lower()]
    
    # Se não encontrar automaticamente, tentar algumas colunas específicas
    if not colunas_pretensao:
        possiveis_colunas = ['tx_resp_q024_desc', 'tx_resp_q025_desc', 'tx_resp_q026_desc']
        colunas_pretensao = [col for col in possiveis_colunas if col in dim_aluno.columns]
    
    if not colunas_pretensao:
        print("Não foram encontradas colunas que representam pretensão futura!")
        return None
    
    # Usar a primeira coluna identificada
    coluna_pretensao = colunas_pretensao[0]
    print(f"Usando a coluna {coluna_pretensao} para análise de pretensão futura.")
    
    # Mesclar fato com dimensões
    df_analise = fato.merge(
        dim_aluno[['id_dim_aluno', coluna_pretensao]],
        on='id_dim_aluno',
        how='left'
    ).merge(
        dim_tempo[['id_tempo', 'ano']],
        on='id_tempo',
        how='left'
    )
    
    # Calcular desempenho por pretensão futura
    desempenho_pretensao = df_analise.groupby([coluna_pretensao, 'ano'])['proficiencia_media'].agg(
        proficiencia_media=('mean'),
        quantidade_alunos=('count')
    ).reset_index()
    
    print("Análise de relação entre desempenho e pretensão futura concluída!")
    return desempenho_pretensao

def analisar_desempenho_estados_abaixo_media(fato, dim_geografia, dim_tempo):
    """
    Analisa os estados/municípios com maior número de escolas abaixo da média.
    
    Args:
        fato (pandas.DataFrame): DataFrame com a tabela fato
        dim_geografia (pandas.DataFrame): DataFrame com a dimensão geografia
        dim_tempo (pandas.DataFrame): DataFrame com a dimensão tempo
    
    Returns:
        pandas.DataFrame: DataFrame com os estados/municípios com mais escolas abaixo da média
    """
    print("Analisando estados/municípios com escolas abaixo da média...")
    
    # Mesclar fato com dimensões
    df_analise = fato.merge(
        dim_geografia[['id_geografia', 'id_regiao', 'sigla_uf', 'id_municipio']],
        on='id_geografia',
        how='left'
    ).merge(
        dim_tempo[['id_tempo', 'ano']],
        on='id_tempo',
        how='left'
    )
    
    # Calcular média nacional por ano
    media_nacional = df_analise.groupby('ano')['proficiencia_media'].mean().reset_index()
    media_nacional.rename(columns={'proficiencia_media': 'media_nacional'}, inplace=True)
    
    # Mesclar com média nacional
    df_analise = df_analise.merge(media_nacional, on='ano', how='left')
    
    # Identificar registros abaixo da média
    df_analise['abaixo_media'] = df_analise['proficiencia_media'] < df_analise['media_nacional']
    
    # Análise por estado
    estados_abaixo_media = df_analise.groupby(['sigla_uf', 'ano']).agg(
        qtd_total=('id_dim_escola', 'nunique'),
        qtd_abaixo_media=(pd.Series(df_analise['abaixo_media'] & (df_analise['id_dim_escola'] >= 0)), 'sum'),
    ).reset_index()
    
    # Calcular percentual abaixo da média
    estados_abaixo_media['percentual_abaixo_media'] = (estados_abaixo_media['qtd_abaixo_media'] / estados_abaixo_media['qtd_total'] * 100).round(2)
    
    # Ordenar por percentual abaixo da média (decrescente)
    estados_abaixo_media = estados_abaixo_media.sort_values(['ano', 'percentual_abaixo_media'], ascending=[True, False])
    
    print("Análise de estados/municípios com escolas abaixo da média concluída!")
    return estados_abaixo_media

def analisar_desempenho_pos_pandemia(fato, dim_tempo):
    """
    Analisa o desempenho pós-pandemia comparado com anos anteriores.
    
    Args:
        fato (pandas.DataFrame): DataFrame com a tabela fato
        dim_tempo (pandas.DataFrame): DataFrame com a dimensão tempo
    
    Returns:
        pandas.DataFrame: DataFrame com o desempenho comparativo
    """
    print("Analisando desempenho pós-pandemia...")
    
    # Mesclar fato com dimensão tempo
    df_analise = fato.merge(
        dim_tempo[['id_tempo', 'ano', 'pre_pandemia', 'durante_pandemia', 'pos_pandemia']],
        on='id_tempo',
        how='left'
    )
    
    # Criar categoria de período
    df_analise['periodo'] = 'Outro'
    df_analise.loc[df_analise['pre_pandemia'] == 1, 'periodo'] = 'Pré-Pandemia'
    df_analise.loc[df_analise['durante_pandemia'] == 1, 'periodo'] = 'Durante Pandemia'
    df_analise.loc[df_analise['pos_pandemia'] == 1, 'periodo'] = 'Pós-Pandemia'
    
    # Calcular desempenho por período e ano
    desempenho_pandemia = df_analise.groupby(['periodo', 'ano'])['proficiencia_media'].agg(
        proficiencia_media=('mean'),
        quantidade_alunos=('count')
    ).reset_index()
    
    print("Análise de desempenho pós-pandemia concluída!")
    return desempenho_pandemia

def visualizar_desempenho_por_regiao(dados, dir_saida):
    """
    Cria visualização do desempenho por região.
    
    Args:
        dados (pandas.DataFrame): DataFrame com os dados de desempenho por região
        dir_saida (str): Diretório para salvar a visualização
    """
    print("Criando visualização do desempenho por região...")
    
    # Verificar se temos a coluna de descrição da região
    if 'regiao_desc' in dados.columns:
        coluna_x = 'regiao_desc'
    else:
        coluna_x = 'id_regiao'
    
    # Configurar a figura
    plt.figure(figsize=(12, 7))
    
    # Preparar dados para o gráfico
    ultimo_ano = dados['ano'].max()
    dados_ultimo_ano = dados[dados['ano'] == ultimo_ano]
    
    # Criar gráfico de barras
    ax = sns.barplot(x=coluna_x, y='proficiencia_media', data=dados_ultimo_ano)
    
    # Adicionar rótulos e título
    plt.title(f'Desempenho Médio por Região no Ano {ultimo_ano}', fontsize=16)
    plt.xlabel('Região', fontsize=12)
    plt.ylabel('Proficiência Média', fontsize=12)
    plt.xticks(rotation=45)
    
    # Adicionar rótulos de valores
    for p in ax.patches:
        ax.annotate(f"{p.get_height():.1f}", 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='bottom', fontsize=10)
    
    # Salvar gráfico
    caminho_arquivo = os.path.join(dir_saida, 'desempenho_por_regiao.png')
    plt.tight_layout()
    plt.savefig(caminho_arquivo, dpi=300)
    plt.close()
    
    print(f"Visualização salva em: {caminho_arquivo}")

def visualizar_desempenho_por_tipo_escola(dados, dir_saida):
    """
    Cria visualização do desempenho por tipo de escola.
    
    Args:
        dados (pandas.DataFrame): DataFrame com os dados de desempenho por tipo de escola
        dir_saida (str): Diretório para salvar a visualização
    """
    print("Criando visualização do desempenho por tipo de escola...")
    
    # Verificar se temos a coluna de descrição do tipo de escola
    if 'id_dependencia_adm_desc' in dados.columns:
        coluna_x = 'id_dependencia_adm_desc'
    else:
        coluna_x = 'id_dependencia_adm'
    
    # Configurar a figura
    plt.figure(figsize=(12, 7))
    
    # Preparar dados para o gráfico
    pivot_data = dados.pivot(index=coluna_x, columns='ano', values='proficiencia_media')
    
    # Criar gráfico de barras agrupadas
    ax = pivot_data.plot(kind='bar', figsize=(12, 7))
    
    # Adicionar rótulos e título
    plt.title('Desempenho Médio por Tipo de Escola ao Longo dos Anos', fontsize=16)
    plt.xlabel('Tipo de Escola', fontsize=12)
    plt.ylabel('Proficiência Média', fontsize=12)
    plt.legend(title='Ano')
    
    # Salvar gráfico
    caminho_arquivo = os.path.join(dir_saida, 'desempenho_por_tipo_escola.png')
    plt.tight_layout()
    plt.savefig(caminho_arquivo, dpi=300)
    plt.close()
    
    print(f"Visualização salva em: {caminho_arquivo}")

def visualizar_evolucao_desempenho(dados, dir_saida):
    """
    Cria visualização da evolução do desempenho ao longo dos anos.
    
    Args:
        dados (pandas.DataFrame): DataFrame com os dados de evolução do desempenho
        dir_saida (str): Diretório para salvar a visualização
    """
    print("Criando visualização da evolução do desempenho...")
    
    # Configurar a figura
    plt.figure(figsize=(12, 7))
    
    # Criar gráfico de linha
    plt.plot(dados['ano'], dados['proficiencia_media'], marker='o', linestyle='-', linewidth=2, markersize=8)
    
    # Adicionar área de desvio padrão
    plt.fill_between(
        dados['ano'],
        dados['proficiencia_media'] - dados['desvio_padrao'],
        dados['proficiencia_media'] + dados['desvio_padrao'],
        alpha=0.2
    )
    
    # Adicionar rótulos e título
    plt.title('Evolução do Desempenho no SAEB ao Longo dos Anos', fontsize=16)
    plt.xlabel('Ano', fontsize=12)
    plt.ylabel('Proficiência Média', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Adicionar rótulos de valores
    for i, row in dados.iterrows():
        plt.text(row['ano'], row['proficiencia_media'] + 5, f"{row['proficiencia_media']:.1f}", ha='center')
    
    # Salvar gráfico
    caminho_arquivo = os.path.join(dir_saida, 'evolucao_desempenho.png')
    plt.tight_layout()
    plt.savefig(caminho_arquivo, dpi=300)
    plt.close()
    
    print(f"Visualização salva em: {caminho_arquivo}")

def visualizar_estados_abaixo_media(dados, dir_saida):
    """
    Cria visualização dos estados com mais escolas abaixo da média.
    
    Args:
        dados (pandas.DataFrame): DataFrame com os dados de estados abaixo da média
        dir_saida (str): Diretório para salvar a visualização
    """
    print("Criando visualização dos estados com escolas abaixo da média...")
    
    # Configurar a figura
    plt.figure(figsize=(14, 8))
    
    # Preparar dados para o gráfico
    ultimo_ano = dados['ano'].max()
    dados_ultimo_ano = dados[dados['ano'] == ultimo_ano].sort_values('percentual_abaixo_media', ascending=True).tail(10)
    
    # Criar gráfico de barras horizontais
    ax = sns.barplot(x='percentual_abaixo_media', y='sigla_uf', data=dados_ultimo_ano)
    
    # Adicionar rótulos e título
    plt.title(f'Top 10 Estados com Maior Percentual de Escolas Abaixo da Média ({ultimo_ano})', fontsize=16)
    plt.xlabel('Percentual de Escolas Abaixo da Média (%)', fontsize=12)
    plt.ylabel('Estado', fontsize=12)
    
    # Adicionar rótulos de valores
    for p in ax.patches:
        ax.annotate(f"{p.get_width():.1f}%", 
                    (p.get_width() + 1, p.get_y() + p.get_height() / 2.), 
                    va='center', fontsize=10)
    
    # Salvar gráfico
    caminho_arquivo = os.path.join(dir_saida, 'estados_abaixo_media.png')
    plt.tight_layout()
    plt.savefig(caminho_arquivo, dpi=300)
    plt.close()
    
    print(f"Visualização salva em: {caminho_arquivo}")

def visualizar_desempenho_pandemia(dados, dir_saida):
    """
    Cria visualização do desempenho comparativo pré/durante/pós pandemia.
    
    Args:
        dados (pandas.DataFrame): DataFrame com os dados de desempenho e pandemia
        dir_saida (str): Diretório para salvar a visualização
    """
    print("Criando visualização do desempenho pré/durante/pós pandemia...")
    
    # Configurar a figura
    plt.figure(figsize=(12, 7))
    
    # Criar gráfico de linha por período
    periodos = ['Pré-Pandemia', 'Durante Pandemia', 'Pós-Pandemia']
    cores = ['blue', 'red', 'green']
    
    for periodo, cor in zip(periodos, cores):
        dados_periodo = dados[dados['periodo'] == periodo]
        if not dados_periodo.empty:
            plt.plot(dados_periodo['ano'], dados_periodo['proficiencia_media'], 
                    marker='o', linestyle='-', linewidth=2, 
                    label=periodo, color=cor)
    
    # Adicionar rótulos e título
    plt.title('Impacto da Pandemia no Desempenho dos Estudantes', fontsize=16)
    plt.xlabel('Ano', fontsize=12)
    plt.ylabel('Proficiência Média', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Salvar gráfico
    caminho_arquivo = os.path.join(dir_saida, 'desempenho_pandemia.png')
    plt.tight_layout()
    plt.savefig(caminho_arquivo, dpi=300)
    plt.close()
    
    print(f"Visualização salva em: {caminho_arquivo}")

def salvar_dados_para_powerbi(dados_analise, dir_saida):
    """
    Salva os dados processados para uso no Power BI.
    
    Args:
        dados_analise (dict): Dicionário com os DataFrames de análise
        dir_saida (str): Diretório para salvar os dados
    """
    print("Salvando dados para o Power BI...")
    
    # Criar subdiretório para dados do Power BI
    diretorio_powerbi = criar_diretorio(os.path.join(dir_saida, 'dados_powerbi'))
    
    # Salvar cada DataFrame em formato CSV
    for nome, df in dados_analise.items():
        if df is not None:
            caminho_arquivo = os.path.join(diretorio_powerbi, f"{nome}.csv")
            df.to_csv(caminho_arquivo, index=False)
            print(f"Dados de {nome} salvos em: {caminho_arquivo}")
    
    print("Todos os dados foram salvos para uso no Power BI!")

def main():
    """
    Função principal para realizar análises e criar visualizações.
    """
    # Diretórios para dados
    diretorio_dados = 'dados_processados'
    diretorio_resultados = criar_diretorio('resultados_analise')
    
    try:
        # Carregar dimensões e fatos
        dim_tempo = carregar_dados_processados(diretorio_dados, 'dim_tempo')
        dim_geografia = carregar_dados_processados(diretorio_dados, 'dim_geografia')
        dim_escola = carregar_dados_processados(diretorio_dados, 'dim_escola')
        dim_aluno = carregar_dados_processados(diretorio_dados, 'dim_aluno')
        fato_desempenho = carregar_dados_processados(diretorio_dados, 'fato_desempenho')
    except FileNotFoundError as e:
        print(f"Erro ao carregar dados: {e}")
        return
    
    # Realizar análises
    resultados_analise = {}
    
    resultados_analise['desempenho_regiao'] = analisar_desempenho_por_regiao(
        fato_desempenho, dim_geografia, dim_tempo
    )
    
    resultados_analise['desempenho_escola'] = analisar_desempenho_por_tipo_escola(
        fato_desempenho, dim_escola, dim_tempo
    )
    
    resultados_analise['desempenho_apoio'] = analisar_desempenho_apoio_familiar(
        fato_desempenho, dim_aluno, dim_tempo
    )
    
    resultados_analise['evolucao_desempenho'] = analisar_evolucao_desempenho(
        fato_desempenho, dim_tempo
    )
    
    resultados_analise['desempenho_pretensao'] = analisar_desempenho_e_pretensao_futura(
        fato_desempenho, dim_aluno, dim_tempo
    )
    
    resultados_analise['estados_abaixo_media'] = analisar_desempenho_estados_abaixo_media(
        fato_desempenho, dim_geografia, dim_tempo
    )
    
    resultados_analise['desempenho_pandemia'] = analisar_desempenho_pos_pandemia(
        fato_desempenho, dim_tempo
    )
    
    # Criar visualizações
    visualizar_desempenho_por_regiao(
        resultados_analise['desempenho_regiao'], diretorio_resultados
    )
    
    visualizar_desempenho_por_tipo_escola(
        resultados_analise['desempenho_escola'], diretorio_resultados
    )
    
    visualizar_evolucao_desempenho(
        resultados_analise['evolucao_desempenho'], diretorio_resultados
    )
    
    visualizar_estados_abaixo_media(
        resultados_analise['estados_abaixo_media'], diretorio_resultados
    )
    
    visualizar_desempenho_pandemia(
        resultados_analise['desempenho_pandemia'], diretorio_resultados
    )
    
    # Salvar dados para Power BI
    salvar_dados_para_powerbi(resultados_analise, diretorio_resultados)
    
    print("Análise e visualizações concluídas com sucesso!")

if __name__ == "__main__":
    main()
