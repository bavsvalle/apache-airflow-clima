import pandas as pd
import requests
from airflow import DAG
from airflow.decorators import task
from datetime import datetime

# URL de base para a API de livros
base_url = "https://my.meteoblue.com/packages/basic-day?apikey=1iMwbQSygalO6K5N&lat=-23.0847&lon=-50.5223&asl=608&format=json"
# Caminho para salvar o arquivo CSV
output_path = "/home/barbara/projetos_linux/airflow_clima/clima.csv"

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
            df = pd.DataFrame(df_dict) # Converte o dicionário de volta para DataFrame
            df.to_csv(output_path, index=False)
            print(f"Dados salvos em {output_path}")

    # Definição da ordem de execução das tasks
    dados = coletar_dados_clima()
    dados_processados = processar_dados(dados)
    salvar_dados_csv(dados_processados)

