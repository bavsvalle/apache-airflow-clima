## 🌦️ Airflow Clima – Pipeline de Coleta de Dados Meteorológicos

DAG do Apache Airflow para coletar dados da API Meteoblue, processá-los com Pandas e salvar arquivos CSV datados em execução automática semanal.

### 🔍 Etapas do Pipeline
1️. Extração – API Meteoblue
- Endpoint utilizado: packages/basic-day
- Parâmetros fixos: latitude, longitude, altitude e formato JSON
- Dados retornados: previsão/resumo diário (data_day)

2️. Transformação – Python
- Conversão do JSON em DataFrame
- Seleção e visualização inicial dos dados
- Conversão para dicionário (compatível com XCom)

3. Carga – CSV
- Geração de um arquivo CSV com timestamp baseado na execução do DAG
- Estrutura: clima_YYYYMMDD.csv
- Local de saída: /home/barbara/projetos_linux/airflow_clima/

### ▶️ Como Executar
1. Ativar o ambiente virtual  
source venv/bin/activate

3. Iniciar o Airflow  
   airflow standalone

5. Verificar a DAG no UI  
   Acessar: http://localhost:8080  
   A DAG aparecerá como clima_dag

### 📅 Agendamento
- Execução automática toda sexta-feira às 09:00
- schedule="0 9 * * 5"

### 🛠️ Tecnologias
Apache Airflow · Python · Pandas · Requests

### 📂 Estrutura do Repositório
    airflow_clima/
    │
    ├── dags/
    │   └── clima_dag.py
    └── output/
        └── clima_YYYYMMDD.csv  # arquivos gerados
