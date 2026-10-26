import os
from pathlib import Path

import pandas as pd
import pendulum
import requests
from airflow.sdk import DAG, get_current_context, task

# API Meteoblue (pacote basic-day, previsão diária). Parâmetros fixos: latitude, longitude e altitude do local
URL_API = "https://my.meteoblue.com/packages/basic-day"
PARAMETROS = {"lat": -23.0847, "lon": -50.5223, "asl": 608, "format": "json"}

# Pasta de saída dos CSVs: a variável de ambiente CLIMA_OUTPUT_DIR ou, se não existir, a pasta output/ do repositório
PASTA_SAIDA = Path(os.environ.get("CLIMA_OUTPUT_DIR", Path(__file__).resolve().parent.parent / "output"))

# Definição do DAG (toda sexta-feira às 09:00, horário de Brasília)
with DAG(
    dag_id = "clima_dag",
    start_date = pendulum.datetime(2025, 11, 28, tz="America/Sao_Paulo"),
    schedule = "0 9 * * 5",
    catchup = False
):

    # Task 1: Coletar dados da API de clima
    @task
    def coletar_dados_clima():
        # A chave da API não fica no código: defina a variável de ambiente METEOBLUE_API_KEY antes de iniciar o Airflow
        chave_api = os.environ.get("METEOBLUE_API_KEY")
        if not chave_api:
            raise ValueError("Defina a variável de ambiente METEOBLUE_API_KEY com a chave da API Meteoblue.")

        response = requests.get(URL_API, params={**PARAMETROS, "apikey": chave_api}, timeout=30)

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

    # Task 3: Salvar os dados processados em CSV na pasta de saída
    @task
    def salvar_dados_csv(df_dict): # Recebe os dados processados da Task 2
            context = get_current_context() # Obtém o contexto atual do Airflow - "puxa" as informações do DAG
            # Data do nome do arquivo: fim do intervalo de dados (execuções agendadas). Num disparo manual sem data lógica
            # (Airflow 3) esse campo não existe, então usa a data lógica ou, na falta dela, a data de hoje em Brasília
            data_ref = context.get('data_interval_end') or context.get('logical_date') or pendulum.now("America/Sao_Paulo")
            data_atual = data_ref.strftime("%Y%m%d") # Formata a data para o nome do arquivo

            PASTA_SAIDA.mkdir(parents=True, exist_ok=True) # Cria a pasta de saída se ela não existir
            output_path = PASTA_SAIDA / f"clima_{data_atual}.csv" # Define o caminho do arquivo de saída

            df = pd.DataFrame(df_dict) # Converte o dicionário de volta para DataFrame
            df.to_csv(output_path, index=False) # Salva o DataFrame em CSV sem o índice
            print(f"Arquivo salvo em: {output_path}") # Confirmação de salvamento do arquivo

    # Definição da ordem de execução das tasks
    dados = coletar_dados_clima()
    dados_processados = processar_dados(dados)
    salvar_dados_csv(dados_processados)
