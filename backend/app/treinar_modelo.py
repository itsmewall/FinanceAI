import pandas as pd
import joblib
from sklearn.tree import DecisionTreeClassifier
import logging

def treinar_modelo(casos, dados_financeiros_path="dados_financeiros.csv"):
    dados_financeiros = pd.read_csv(dados_financeiros_path)

    df = pd.DataFrame(casos)
    df['profissao'] = df['profissao'].astype('category').cat.codes
    df['objetivo'] = df['objetivo'].astype('category').cat.codes
    df['tolerancia_risco'] = df['tolerancia_risco'].astype('category').cat.codes

    X = df[['idade', 'profissao', 'objetivo', 'tolerancia_risco']]
    
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

    global tickers_para_categorias
    tickers_para_categorias = {ticker: categoria for ticker, categoria in categorias}
    categorias_filtradas = [tickers_para_categorias.get(ticker, None) for ticker in df['recomendacao']]
    
    valid_indices = [i for i, categoria in enumerate(categorias_filtradas) if categoria is not None]
    X = X.iloc[valid_indices]
    y = [categorias_filtradas[i] for i in valid_indices]

    if len(X) != len(y):
        raise ValueError("Número de amostras e rótulos não correspondem. Verifique os dados de entrada.")

    modelo = DecisionTreeClassifier()
    modelo.fit(X, y)
    joblib.dump(modelo, "modelo_investimento.pkl")
    logging.info("Modelo treinado com sucesso.")

if __name__ == "__main__":
    casos = [
        {"idade": 25, "profissao": "engenheiro", "objetivo": "aposentadoria", "tolerancia_risco": "alta", "recomendacao": "AAPL"},
        {"idade": 40, "profissao": "médico", "objetivo": "crescimento de capital", "tolerancia_risco": "baixa", "recomendacao": "GOOGL"},
        # Adicione mais casos aqui
    ]
    treinar_modelo(casos)