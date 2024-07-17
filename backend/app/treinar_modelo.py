import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import joblib
import logging

logging.basicConfig(level=logging.INFO)

def treinar_modelo(casos, dados_financeiros):
    # Criar categorias de recomendação
    categorias = []
    for _, row in dados_financeiros.iterrows():
        if row['cagr'] > 0.2 and row['volatilidade'] < 0.3:
            categoria = 'alta_crescimento_baixo_risco'
        elif row['cagr'] > 0.2:
            categoria = 'alta_crescimento_alto_risco'
        elif row['volatilidade'] < 0.3:
            categoria = 'baixo_crescimento_baixo_risco'
        else:
            categoria = 'baixo_crescimento_alto_risco'
        categorias.append((row['ticker'], categoria))
    
    # Preparar dados para treinamento
    df = pd.DataFrame(casos)
    df['profissao'] = df['profissao'].astype('category').cat.codes
    df['objetivo'] = df['objetivo'].astype('category').cat.codes
    df['tolerancia_risco'] = df['tolerancia_risco'].astype('category').cat.codes
    
    X = df[['idade', 'profissao', 'objetivo', 'tolerancia_risco']]
    
    # Mapear as categorias para tickers
    tickers_para_categorias = {ticker: categoria for ticker, categoria in categorias}
    categorias_filtradas = [tickers_para_categorias[ticker] for ticker in df['recomendacao'] if ticker in tickers_para_categorias]

    if len(X) != len(categorias_filtradas):
        raise ValueError("Número de amostras e rótulos não correspondem. Verifique os dados de entrada.")

    y = categorias_filtradas
    
    # Treinar o modelo diretamente
    modelo = DecisionTreeClassifier()
    modelo.fit(X, y)
    joblib.dump(modelo, "modelo_investimento.pkl")
    logging.info("Modelo treinado com sucesso.")

if __name__ == "__main__":
    # Carregar dados financeiros coletados
    dados_financeiros = pd.read_csv("dados_financeiros.csv")
    
    casos = [
        {
            "idade": 25,
            "profissao": "engenheiro",
            "objetivo": "crescimento de capital",
            "tolerancia_risco": "alta",
            "recomendacao": "AAPL"
        },
        {
            "idade": 45,
            "profissao": "medico",
            "objetivo": "aposentadoria",
            "tolerancia_risco": "baixa",
            "recomendacao": "V"
        }
    ]

    treinar_modelo(casos, dados_financeiros)