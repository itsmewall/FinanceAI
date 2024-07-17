import openai
import logging
import yfinance as yf
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import numpy as np
import joblib

logging.basicConfig(level=logging.INFO)

modelo_treinado = None

def carregar_modelo():
    global modelo_treinado
    try:
        modelo_treinado = joblib.load("modelo_investimento.pkl")
        logging.info("Modelo de investimento carregado com sucesso.")
    except FileNotFoundError:
        modelo_treinado = None
        logging.warning("Modelo de investimento não encontrado. Certifique-se de treinar o modelo antes de utilizá-lo.")
    except Exception as e:
        modelo_treinado = None
        logging.error(f"Erro ao carregar o modelo: {e}")

carregar_modelo()

def coletar_dados_financeiros(tickers, periodo="1y"):
    dados = []
    
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=periodo)
        
        if hist.empty:
            continue
        
        # Calcular crescimento (CAGR) e risco (volatilidade)
        cagr = (hist['Close'].iloc[-1] / hist['Close'].iloc[0]) ** (1 / (len(hist) / 252)) - 1
        volatilidade = hist['Close'].pct_change().std() * np.sqrt(252)
        
        dados.append({
            "ticker": ticker,
            "cagr": float(cagr),
            "volatilidade": float(volatilidade)
        })
    
    return dados

def obter_dados_acao(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    return data

def gerar_relatorio_investidor(dados_usuario):
    try:
        idade = int(dados_usuario.get('idade', 0))
        profissao = dados_usuario.get('profissao', '').lower()
        objetivo = dados_usuario.get('objetivo', '').lower()
        tolerancia_risco = dados_usuario.get('tolerancia_risco', '').lower()

        profissao_code = pd.Series([profissao]).astype('category').cat.codes[0]
        objetivo_code = pd.Series([objetivo]).astype('category').cat.codes[0]
        tolerancia_risco_code = pd.Series([tolerancia_risco]).astype('category').cat.codes[0]

        perfil = np.array([[idade, profissao_code, objetivo_code, tolerancia_risco_code]])

        if modelo_treinado is None:
            raise ValueError("O modelo de investimento não foi carregado corretamente.")

        recomendacao = modelo_treinado.predict(perfil)[0]

        # Adicione aqui o código correto para mapear a recomendação aos tickers
        categorias = [
            ('AAPL', 'alta_crescimento_alto_risco'),
            ('GOOGL', 'alta_crescimento_alto_risco'),
            ('MSFT', 'alta_crescimento_baixo_risco'),
            ('TSLA', 'alta_crescimento_alto_risco'),
            ('AMZN', 'alta_crescimento_alto_risco'),
            ('FB', 'alta_crescimento_alto_risco'),
            ('NFLX', 'alta_crescimento_alto_risco'),
            ('NVDA', 'alta_crescimento_alto_risco'),
            ('BABA', 'alta_crescimento_alto_risco'),
            ('V', 'alta_crescimento_baixo_risco')
        ]

        tickers = [ticker for ticker, categoria in categorias if categoria == recomendacao]
        recomendacoes = []

        for ticker in tickers:
            dados_acao = obter_dados_acao(ticker)
            if not dados_acao.empty:
                preco_atual = dados_acao['Close'].iloc[-1]
                recomendacoes.append(f"Ação {ticker.upper()}: Preço Atual: ${preco_atual:.2f}")

        prompt = (
            f"Nome: {dados_usuario.get('nome', '')}\n"
            f"Idade: {dados_usuario.get('idade', '')}\n"
            f"Profissão: {dados_usuario.get('profissao', '')}\n"
            f"Objetivo Financeiro: {dados_usuario.get('objetivo', '')}\n"
            f"Tolerância ao Risco: {dados_usuario.get('tolerancia_risco', '')}\n\n"
            "Baseado nas informações fornecidas, por favor, forneça um relatório detalhado e personalizado do perfil de investidor. "
            "Inclua recomendações de investimentos adequados, estratégias financeiras, e qualquer outra informação relevante para ajudar no planejamento financeiro. "
            "Use um tom sarcástico e humorístico, mas sem exagerar e perder o tom, como o Bruno Perini faria, e mantenha as respostas curtas e diretas ao ponto, mas com recomendações.\n\n"
            "Resposta:"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um consultor financeiro experiente, sarcástico e com humor como o Bruno Perini."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        relatorio = response.choices[0].message['content'].strip()

        # Adicionando recomendações personalizadas ao relatório
        for recomendacao in recomendacoes:
            relatorio += f"\n- {recomendacao}"

        logging.info("Relatório gerado com sucesso: %s", relatorio)
        return relatorio
    except Exception as e:
        logging.error(f"Erro ao gerar relatório de investimento: {str(e)}")
        raise e

def verificar_consistencia_respostas(dados_usuario):
    for key, value in dados_usuario.items():
        if not value:
            return False, f"O campo '{key}' está vazio. Por favor, preencha todas as informações."
    return True, ""

def gerar_relatorio_com_verificacao(dados_usuario):
    consistencia, mensagem = verificar_consistencia_respostas(dados_usuario)
    if not consistencia:
        return mensagem
    return gerar_relatorio_investidor(dados_usuario)

def treinar_modelo_com_dados_financeiros(tickers, casos):
    dados_financeiros = coletar_dados_financeiros(tickers)
    
    categorias = []
    for row in dados_financeiros:
        if row['cagr'] > 0.2 and row['volatilidade'] < 0.3:
            categoria = 'alta_crescimento_baixo_risco'
        elif row['cagr'] > 0.2:
            categoria = 'alta_crescimento_alto_risco'
        elif row['volatilidade'] < 0.3:
            categoria = 'baixo_crescimento_baixo_risco'
        else:
            categoria = 'baixo_crescimento_alto_risco'
        categorias.append((row['ticker'], categoria))
    
    df = pd.DataFrame(casos)
    df['profissao'] = df['profissao'].astype('category').cat.codes
    df['objetivo'] = df['objetivo'].astype('category').cat.codes
    df['tolerancia_risco'] = df['tolerancia_risco'].astype('category').cat.codes
    
    X = df[['idade', 'profissao', 'objetivo', 'tolerancia_risco']]
    
    tickers_para_categorias = {ticker: categoria for ticker, categoria in categorias}
    categorias_filtradas = [tickers_para_categorias[ticker] for ticker in df['recomendacao'] if ticker in tickers_para_categorias]

    if len(X) != len(categorias_filtradas):
        raise ValueError("Número de amostras e rótulos não correspondem. Verifique os dados de entrada.")

    y = categorias_filtradas
    
    modelo = DecisionTreeClassifier()
    modelo.fit(X, y)
    joblib.dump(modelo, "modelo_investimento.pkl")
    logging.info("Modelo treinado com sucesso.")
    carregar_modelo()

def obter_acoes_recomendadas(dados_usuario):
    try:
        idade = int(dados_usuario.get('idade', 0))
        profissao = dados_usuario.get('profissao', '').lower()
        objetivo = dados_usuario.get('objetivo', '').lower()
        tolerancia_risco = dados_usuario.get('tolerancia_risco', '').lower()
        
        if modelo_treinado:
            profissao_code = pd.Series([profissao]).astype('category').cat.codes[0]
            objetivo_code = pd.Series([objetivo]).astype('category').cat.codes[0]
            tolerancia_risco_code = pd.Series([tolerancia_risco]).astype('category').cat.codes[0]
            
            perfil = np.array([[idade, profissao_code, objetivo_code, tolerancia_risco_code]])
            recomendacao = modelo_treinado.predict(perfil)
            acoes = []
            if recomendacao:
                tickers = recomendacao[0].split(',')
                for ticker in tickers:
                    dados_acao = obter_dados_acao(ticker)
                    if not dados_acao.empty:
                        preco_atual = dados_acao['Close'].iloc[-1]
                        acoes.append({
                            'nome': ticker,
                            'ticker': ticker,
                            'preco_atual': preco_atual,
                            'descricao': f"Recomendação baseada no perfil de {dados_usuario['nome']}."
                        })
            return acoes
        else:
            return []
    except Exception as e:
        logging.error(f"Erro ao obter ações recomendadas: {str(e)}")
        raise e