![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?logo=Apache%20Airflow&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![DAG](https://img.shields.io/badge/DAG-Pipeline-blue)

# 🌦️ Airflow Clima – Pipeline de Coleta de Dados Meteorológicos

## 🎯 Sobre o projeto

**O problema:** Acompanhar a previsão do tempo de um local fixo ao longo das semanas exige repetir a consulta e guardar cada resultado. Fazer isso à mão é fácil de esquecer e deixa os arquivos sem padrão.

**O que o projeto entrega:** Uma DAG do Apache Airflow que, toda sexta-feira às 09:00 (horário de Brasília), consulta a API da Meteoblue, organiza a resposta com pandas e salva um CSV com a data no nome (`clima_YYYYMMDD.csv`).

**Quem usaria:** Um cenário plausível é uma pessoa que queira montar, com o tempo, uma coleção semanal de previsões de um local para análise. O projeto é um exercício de orquestração com dados públicos de previsão e não tem cliente real, então esse uso é um cenário, não um caso aplicado.

**O resultado:** A cada execução, um CSV com a previsão diária dos próximos 7 dias e 29 variáveis (temperatura, precipitação, vento, umidade, pressão, índice UV, entre outras). Há um exemplo real em [`exemplo/clima_20251205.csv`](exemplo/clima_20251205.csv).

**Ressalvas importantes:** a DAG precisa de uma chave de API da Meteoblue, que cada pessoa deve obter e informar por variável de ambiente (a chave não fica no código). Os dados são **previsão**, não medições históricas.

---

## 🔍 Etapas do Pipeline

**1. Extração – API Meteoblue**
- Endpoint: `packages/basic-day` (resumo diário), formato JSON.
- Parâmetros fixos: latitude -23,0847, longitude -50,5223 e altitude 608 m.
- Dado usado: `data_day`, a previsão diária.

**2. Transformação – Python**
- Conversão do JSON em DataFrame (pandas).
- Conversão para dicionário, para o resultado poder passar entre tarefas pelo XCom do Airflow.

**3. Carga – CSV**
- Gera um arquivo `clima_YYYYMMDD.csv` na pasta `output/` (ou na pasta indicada em `CLIMA_OUTPUT_DIR`; ela é criada se não existir).
- A data do nome é a data da execução no Airflow, e não a data da previsão. No exemplo do repositório, o nome é `20251205` e a previsão começa em 2025-12-10.
- Em um disparo manual sem data lógica, o nome usa a data de hoje em Brasília.

### 📅 Agendamento

- Toda sexta-feira às 09:00, no fuso `America/Sao_Paulo` (`schedule="0 9 * * 5"`).
- `catchup=False`: execuções passadas não são recuperadas.
- A DAG (`clima_dag`) **é criada pausada**: ative-a na interface para o agendamento valer.

---

## ⚠️ Limitações

- **Precisa de chave de API própria** da Meteoblue.
- **Local fixo.** Latitude, longitude e altitude estão no código (`dags/dag_api_clima.py`).
- **Cada arquivo é uma previsão de 7 dias.** Os arquivos semanais se sobrepõem e não são consolidados num histórico.
- **Sem tentativas automáticas nem alertas.** Se a API falhar, a execução falha e espera a próxima sexta (ou um disparo manual).
- **Sem testes automatizados** e sem validação do conteúdo da resposta além do código HTTP 200.

---

## ⚙️ Como Executar

Testado com Python 3.11 e Apache Airflow 3.1.7.

**1. Instalar**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Configurar** (a partir da raiz do repositório)

```bash
export METEOBLUE_API_KEY="sua_chave"
export AIRFLOW__CORE__DAGS_FOLDER="$(pwd)/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
```

Opcional: `export CLIMA_OUTPUT_DIR="/caminho/da/pasta"` para escolher onde salvar os CSVs. A variável da chave precisa estar definida no mesmo terminal em que o Airflow for iniciado.

**3. Iniciar o Airflow**

```bash
airflow standalone
```

Acesse http://localhost:8080. O login é `admin`, e a senha aparece no terminal ao iniciar (fica também no arquivo `simple_auth_manager_passwords.json.generated`, dentro da pasta do Airflow). A DAG `clima_dag` aparece na lista.

**4. Executar**

- **Pela interface:** ative a DAG e use o botão de disparo manual.
- **Só uma vez, pelo terminal, sem iniciar o servidor:** na primeira vez, crie o banco do Airflow com `airflow db migrate`; depois, `airflow dags test clima_dag 2025-12-05`.

Os CSVs aparecem em `output/`.

<details>
<summary><b>📂 Estrutura do repositório</b></summary>

    apache-airflow-clima/
    ├── dags/
    │   └── dag_api_clima.py
    ├── exemplo/
    │   └── clima_20251205.csv      # exemplo de arquivo gerado
    ├── requirements.txt
    ├── .gitignore
    └── README.md

A pasta `output/` (CSVs gerados) é criada na execução e não é versionada.

</details>

---

## 🛠️ Tecnologias

Apache Airflow · Python · Pandas · Requests
