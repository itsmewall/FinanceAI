import yfinance as yf
import pandas as pd
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)

def coletar_dados_financeiros(tickers, periodo="1y"):
    dados = []
    
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=periodo)
        
        if hist.empty:
            logging.warning(f"Sem dados históricos para {ticker}")
            continue
        
        # Calcular crescimento (CAGR) e risco (volatilidade)
        cagr = (hist['Close'].iloc[-1] / hist['Close'].iloc[0]) ** (1 / (len(hist) / 252)) - 1
        volatilidade = hist['Close'].pct_change().std() * np.sqrt(252)
        
        dados.append({
            "ticker": ticker,
            "cagr": cagr,
            "volatilidade": volatilidade
        })
    
    return pd.DataFrame(dados)

if __name__ == "__main__":
    tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "FB", "NFLX", "NVDA", "BABA", "V"]
    dados_financeiros = coletar_dados_financeiros(tickers)
    
    # Salvar os dados em CSV
    dados_financeiros.to_csv("dados_financeiros.csv", index=False)
    
    logging.info("Dados financeiros coletados e salvos em dados_financeiros.csv")
    logging.info(dados_financeiros)
