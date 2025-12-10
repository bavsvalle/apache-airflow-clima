import pandas as pd
import requests
from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import get_current_context
from datetime import datetime

# URL de base para a API de livros
base_url = "https://my.meteoblue.com/packages/basic-day?apikey=1iMwbQSygalO6K5N&lat=-23.0847&lon=-50.5223&asl=608&format=json"

# Definição do DAG
with DAG(
    dag_id = "clima_dag",
    start_date = datetime(2025, 11, 28),
    schedule = "0 9 * * 5",
    catchup = False
):

# Task 1: Coletar dados da API de clima
    @task
    def coletar_dados_clima():
        response = requests.get(base_url)

        if response.status_code == 200: # Verifica se a requisição foi bem-sucedida, cód 200 padrão HTTP
            data = response.json()
            print(data.keys()) # Verfica a estrutura

            dia = data ["data_day"]
            df_clima = pd.DataFrame(dia)
            
            print(df_clima.head())

            return data
        else:
            raise Exception(f"Erro na requisição: {response.status_code}")
    
    # Task 2: Processar os dados coletados
    @task
    def processar_dados(data): # Recebe os dados da Task 1 como parâmetro
            dia = data ["data_day"]
            df_clima = pd.DataFrame(dia)
            
            print("Processamento dentro da Task 2:") # Verifica a estrutura dos dados processados
            print(df_clima.head())

            return df_clima.to_dict() # Retorna como dicionário para evitar problemas de serialização

    # Task 3: Salvar os dados processados em CSV no output_path
    @task
    def salvar_dados_csv(df_dict): # Recebe os dados processados da Task 2
            context = get_current_context() # Obtém o contexto atual do Airflow - "puxa" as informações do DAG
            data_interval_end = context['data_interval_end'] # Obtém o final do intervalo de dados
            data_atual = data_interval_end.strftime("%Y%m%d") # Formata a data para o nome do arquivo

            output_path = f"/home/barbara/projetos_linux/airflow_clima/clima_{data_atual}.csv" # Define o caminho do arquivo de saída

            df = pd.DataFrame(df_dict) # Converte o dicionário de volta para DataFrame
            df.to_csv(output_path, index=False) # Salva o DataFrame em CSV sem o índice
            print(f"Arquivo salvo em: {output_path}") # Confirmação de salvamento do arquivo

    # Definição da ordem de execução das tasks
    dados = coletar_dados_clima()
    dados_processados = processar_dados(dados)
    salvar_dados_csv(dados_processados)

