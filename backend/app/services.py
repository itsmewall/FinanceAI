import openai
import logging
import yfinance as yf
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import numpy as np
import joblib
import os

logging.basicConfig(level=logging.INFO)

modelos_usuarios = {}

def carregar_modelo_usuario(user_id):
    global modelos_usuarios
    try:
        modelo_usuario = joblib.load(f"modelo_investimento_{user_id}.pkl")
        modelos_usuarios[user_id] = modelo_usuario
        logging.info(f"Modelo de investimento para o usuário {user_id} carregado com sucesso.")
    except FileNotFoundError:
        modelos_usuarios[user_id] = None
        logging.warning(f"Modelo de investimento para o usuário {user_id} não encontrado.")
    except Exception as e:
        modelos_usuarios[user_id] = None
        logging.error(f"Erro ao carregar o modelo do usuário {user_id}: {e}")

def coletar_dados_financeiros(tickers, periodo="1y"):
    dados = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=periodo)
        if hist.empty:
            continue
        cagr = (hist['Close'].iloc[-1] / hist['Close'].iloc[0]) ** (1 / (len(hist) / 252)) - 1
        volatilidade = hist['Close'].pct_change().std() * np.sqrt(252)
        dados.append({"ticker": ticker, "cagr": float(cagr), "volatilidade": float(volatilidade)})
    return dados

def obter_dados_acao(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    return data

def gerar_relatorio_investidor(dados_usuario):
    try:
        user_id = dados_usuario.get('user_id')
        idade = int(dados_usuario.get('idade', 0))
        profissao = dados_usuario.get('profissao', '').lower()
        objetivo = dados_usuario.get('objetivo', '').lower()
        tolerancia_risco = dados_usuario.get('tolerancia_risco', '').lower()

        perfil_df = pd.DataFrame([{
            'idade': idade,
            'profissao': profissao,
            'objetivo': objetivo,
            'tolerancia_risco': tolerancia_risco
        }])
        
        profissao_code = pd.Series([profissao]).astype('category').cat.codes[0]
        objetivo_code = pd.Series([objetivo]).astype('category').cat.codes[0]
        tolerancia_risco_code = pd.Series([tolerancia_risco]).astype('category').cat.codes[0]

        perfil = pd.DataFrame([{
            'idade': idade,
            'profissao': profissao_code,
            'objetivo': objetivo_code,
            'tolerancia_risco': tolerancia_risco_code
        }])

        if user_id not in modelos_usuarios or modelos_usuarios[user_id] is None:
            raise ValueError(f"O modelo de investimento para o usuário {user_id} não foi carregado corretamente.")

        modelo_treinado = modelos_usuarios[user_id]
        recomendacao = modelo_treinado.predict(perfil)[0]

        tickers = [ticker for ticker, categoria in tickers_para_categorias.items() if categoria == recomendacao]
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

def treinar_modelo_com_dados_financeiros(user_id, tickers, casos):
    dados_financeiros = coletar_dados_financeiros(tickers)
    df = pd.DataFrame(casos)
    df['profissao'] = df['profissao'].astype('category').cat.codes
    df['objetivo'] = df['objetivo'].astype('category').cat.codes
    df['tolerancia_risco'] = df['tolerancia_risco'].astype('category').cat.codes

    X = df[['idade', 'profissao', 'objetivo', 'tolerancia_risco']]
    
    categorias = []
    for _, row in pd.DataFrame(dados_financeiros).iterrows():
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
    joblib.dump(modelo, f"modelo_investimento_{user_id}.pkl")
    logging.info(f"Modelo de investimento para o usuário {user_id} treinado com sucesso.")
    carregar_modelo_usuario(user_id)

def obter_acoes_recomendadas(dados_usuario):
    try:
        user_id = dados_usuario.get('user_id')
        idade = int(dados_usuario.get('idade', 0))
        profissao = dados_usuario.get('profissao', '').lower()
        objetivo = dados_usuario.get('objetivo', '').lower()
        tolerancia_risco = dados_usuario.get('tolerancia_risco', '').lower()

        perfil = pd.DataFrame([{
            'idade': idade,
            'profissao': profissao,
            'objetivo': objetivo,
            'tolerancia_risco': tolerancia_risco
        }])
        
        profissao_code = pd.Series([profissao]).astype('category').cat.codes[0]
        objetivo_code = pd.Series([objetivo]).astype('category').cat.codes[0]
        tolerancia_risco_code = pd.Series([tolerancia_risco]).astype('category').cat.codes[0]

        perfil = pd.DataFrame([{
            'idade': idade,
            'profissao': profissao_code,
            'objetivo': objetivo_code,
            'tolerancia_risco': tolerancia_risco_code
        }])

        if user_id not in modelos_usuarios or modelos_usuarios[user_id] is None:
            raise ValueError(f"O modelo de investimento para o usuário {user_id} não foi carregado corretamente.")

        modelo_treinado = modelos_usuarios[user_id]
        recomendacao = modelo_treinado.predict(perfil)[0]
        acoes = []
        if recomendacao:
            tickers = [ticker for ticker, categoria in tickers_para_categorias.items() if categoria == recomendacao]
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
    except Exception as e:
        logging.error(f"Erro ao obter ações recomendadas: {str(e)}")
        raise e
