import yfinance as yf
import pandas as pd

def coletar_dados_financeiros(tickers, periodo="1y"):
    dados = []
    
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=periodo)
        
        if hist.empty:
            continue
        
        cagr = (hist['Close'].iloc[-1] / hist['Close'].iloc[0]) ** (1 / (len(hist) / 252)) - 1
        volatilidade = hist['Close'].pct_change().std() * (252 ** 0.5)
        
        dados.append({
            "ticker": ticker,
            "cagr": float(cagr),
            "volatilidade": float(volatilidade)
        })
    
    df = pd.DataFrame(dados)
    df.to_csv("dados_financeiros.csv", index=False)

if __name__ == "__main__":
    tickers = [
        "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NFLX", "NVDA", "BABA", "V", "BRK.B", "DIS", "PYPL",
        "CSCO", "PEP", "INTC", "KO", "MRK", "ABT", "CRM", "ORCL", "IBM", "GE", "NKE", "COST", "JPM",
        "BAC", "WFC", "C", "HSBC", "RY", "TD", "ITUB", "BBDC4.SA", "BBAS3.SA", "PETR4.SA", "VALE3.SA",
        "ABEV3.SA", "ELET3.SA", "ITSA4.SA", "B3SA3.SA", "BBDC3.SA", "BBSE3.SA", "BIDI11.SA", "BRAP4.SA",
        "BRML3.SA", "BRKM5.SA", "BRPR3.SA", "CIEL3.SA", "COGN3.SA", "CPFE3.SA", "CRFB3.SA", "CSAN3.SA",
        "CSNA3.SA", "CYRE3.SA", "ECOR3.SA", "EGIE3.SA", "EMBR3.SA", "ENBR3.SA", "ENGI11.SA", "EQTL3.SA",
        "EZTC3.SA", "FLRY3.SA", "GGBR4.SA", "GNDI3.SA", "GOAU4.SA", "GOLL4.SA", "HAPV3.SA", "HGTX3.SA",
        "HYPE3.SA", "IGTA3.SA", "IRBR3.SA", "ITUB4.SA", "JBSS3.SA", "KLBN11.SA", "LAME4.SA", "LCAM3.SA",
        "LIGT3.SA", "LINX3.SA", "LREN3.SA", "MGLU3.SA", "MRFG3.SA", "MRVE3.SA", "MULT3.SA", "PCAR3.SA",
        "PETR3.SA", "PETR4.SA", "PRIO3.SA", "QUAL3.SA", "RADL3.SA", "RAIL3.SA", "RENT3.SA", "SANB11.SA",
        "SAPR11.SA", "SBSP3.SA", "SULA11.SA", "SUZB3.SA", "TAEE11.SA", "TIMS3.SA", "TOTS3.SA", "UGPA3.SA",
        "USIM5.SA", "VALE3.SA", "VIVT3.SA", "VVAR3.SA", "WEGE3.SA", "YDUQ3.SA"
    ]
    coletar_dados_financeiros(tickers)
