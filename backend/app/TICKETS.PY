import csv
import yfinance as yf
import requests
import pandas as pd
from io import StringIO

# Função para obter tickers do S&P 500
def obter_tickers_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = requests.get(url).text
    tickers = pd.read_html(StringIO(html))[0]['Symbol'].tolist()
    return tickers

# Função para obter tickers do NASDAQ
def obter_tickers_nasdaq():
    url = "https://api.nasdaq.com/api/screener/stocks?exchange=nasdaq"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    data = response.json()
    tickers = [item['symbol'] for item in data.get('data', {}).get('rows', [])]
    return tickers

# Função para obter tickers da NYSE
def obter_tickers_nyse():
    url = "https://api.nasdaq.com/api/screener/stocks?exchange=nyse"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    data = response.json()
    tickers = [item['symbol'] for item in data.get('data', {}).get('rows', [])]
    return tickers

# Função para obter tickers da B3 (Bolsa de Valores do Brasil)
def obter_tickers_b3():
    # Use uma lista fixa como exemplo
    tickers_b3 = [
        'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA', 
        'BBAS3.SA', 'B3SA3.SA', 'WEGE3.SA', 'MGLU3.SA', 'RENT3.SA'
        # Adicione mais tickers conforme necessário
    ]
    return tickers_b3

# Função para obter tickers de criptomoedas do CoinGecko
def obter_tickers_crypto():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    data = response.json()
    tickers = [coin['symbol'].upper() + "-USD" for coin in data]
    return tickers

# Obter todas as listas de tickers
tickers_usa = obter_tickers_sp500() + obter_tickers_nasdaq() + obter_tickers_nyse()
tickers_brazil = obter_tickers_b3()
tickers_crypto = obter_tickers_crypto()

# Combine todas as listas em uma única lista
todos_tickers = tickers_usa + tickers_brazil + tickers_crypto

# Nome do arquivo CSV
arquivo_csv = 'todos_tickers.csv'

# Escrever os tickers no arquivo CSV
with open(arquivo_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Ticker'])  # Cabeçalho
    for ticker in todos_tickers:
        writer.writerow([ticker])

print(f"Arquivo {arquivo_csv} criado com sucesso contendo {len(todos_tickers)} tickers.")
