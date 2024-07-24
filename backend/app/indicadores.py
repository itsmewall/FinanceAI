import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import os
from tqdm import tqdm

# Suprimir FutureWarnings específicos
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Função para obter dados históricos desde o início da ação
def obter_dados(ticker, periodo='max'):
    dados = yf.download(ticker, period=periodo)
    return dados

# Função para plotar e salvar o gráfico de candlestick com médias móveis
def plotar_grafico(ticker, dados):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.1, row_heights=[0.8, 0.2])

    # Gráfico de velas
    candle = go.Candlestick(x=dados.index,
                            open=dados['Open'],
                            high=dados['High'],
                            low=dados['Low'],
                            close=dados['Close'],
                            name='Candlestick')
    fig.add_trace(candle, row=1, col=1)

    # Médias móveis
    for periodo, cor in zip([9, 20, 200], ['blue', 'red', 'green']):
        dados[f'MA{periodo}'] = dados['Close'].rolling(window=periodo).mean()
        ma = go.Scatter(x=dados.index, y=dados[f'MA{periodo}'],
                        mode='lines', name=f'MA{periodo}', line=dict(color=cor))
        fig.add_trace(ma, row=1, col=1)

    # Volume
    volume = go.Bar(x=dados.index, y=dados['Volume'],
                    name='Volume', marker={'color': 'blue'})
    fig.add_trace(volume, row=2, col=1)

    fig.update_layout(title=f'Gráfico de Candlestick para {ticker}',
                      xaxis_title='Data', yaxis_title='Preço',
                      template='plotly_dark')

    # Exibir o gráfico interativo
    fig.show()

# Função para obter indicadores financeiros de um ativo
def obter_indicadores(ticker):
    ativo = yf.Ticker(ticker)
    indicadores = {
        'Ticker': ticker,
        'Relação P/L': ativo.info.get('forwardPE'),
        'Rendimento de Dividendos': ativo.info.get('dividendYield'),
        'Capitalização de Mercado': ativo.info.get('marketCap'),
        'Alta de 52 Semanas': ativo.info.get('fiftyTwoWeekHigh'),
        'Baixa de 52 Semanas': ativo.info.get('fiftyTwoWeekLow'),
        'Beta': ativo.info.get('beta'),
        'Lucro por Ação (EPS)': ativo.info.get('trailingEps'),
        'Retorno sobre o Patrimônio (ROE)': ativo.info.get('returnOnEquity')
    }
    return indicadores

# Função para exibir indicadores financeiros, gráfico de candlestick e médias móveis
def exibir_indicadores(tickers):
    # DataFrame para armazenar os indicadores financeiros
    df_indicadores = pd.DataFrame()

    # Iterar sobre cada ticker e coletar dados com barra de progresso
    for ticker in tqdm(tickers, desc="Processando tickers", unit="ticker"):
        indicadores = obter_indicadores(ticker)
        df_temp = pd.DataFrame([indicadores])
        if not df_temp.empty:
            df_indicadores = pd.concat([df_indicadores, df_temp], ignore_index=True)

    # Exibir a tabela com os indicadores financeiros
    print(df_indicadores)

    # Salvar a tabela em um arquivo CSV para acessos futuros
    df_indicadores.to_csv('indicadores_financeiros_atualizados.csv', index=False)

    return df_indicadores

# Carregar a lista de tickers a partir do arquivo CSV
def carregar_tickers_csv(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
    tickers = df['Ticker'].tolist()
    return tickers

# Função principal para obter dados e gerar gráficos
def analisar_ticker(ticker, periodo='max'):
    dados = obter_dados(ticker, periodo)
    plotar_grafico(ticker, dados)

# Nome do arquivo CSV que contém os tickers
arquivo_csv = 'todos_tickers.csv'

# Carregar os tickers a partir do arquivo CSV
tickers = carregar_tickers_csv(arquivo_csv)

# Exibir os indicadores para os tickers carregados
df_indicadores = exibir_indicadores(tickers)

# Exemplo de chamada para analisar um ticker específico
# O usuário pode alterar o ticker e o período conforme necessário
analisar_ticker('AAPL', '1y')  # Exemplo para exibir o gráfico do ticker 'AAPL' no período de 1 ano
