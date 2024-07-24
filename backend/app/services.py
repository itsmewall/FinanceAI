import openai
import logging
import pandas as pd
import joblib
from sklearn.tree import DecisionTreeClassifier
import os
import json
from .auth import registrar_usuario, autenticar_usuario, carregar_dados_usuario, salvar_dados_usuario

logging.basicConfig(level=logging.INFO)

modelos_usuarios = {}
tickers_para_categorias = {}

def carregar_modelo_usuario(user_id):
    global modelos_usuarios
    try:
        modelo_usuario = joblib.load(f"usuarios/modelo_investimento_{user_id}.pkl")
        modelos_usuarios[user_id] = modelo_usuario
        logging.info(f"Modelo de investimento para o usuário {user_id} carregado com sucesso.")
    except FileNotFoundError:
        modelos_usuarios[user_id] = None
        logging.warning(f"Modelo de investimento para o usuário {user_id} não encontrado.")
    except Exception as e:
        modelos_usuarios[user_id] = None
        logging.error(f"Erro ao carregar o modelo do usuário {user_id}: {e}")

def carregar_analises_csv(arquivo_csv):
    try:
        df_analises = pd.read_csv(arquivo_csv)
        logging.info(f"Análises carregadas do arquivo {arquivo_csv} com sucesso.")
        return df_analises
    except FileNotFoundError:
        logging.error(f"Arquivo {arquivo_csv} não encontrado.")
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Erro ao carregar análises do arquivo {arquivo_csv}: {e}")
        return pd.DataFrame()

def calcular_cagr_volatilidade(df):
    df['CAGR'] = (df['Close'].pct_change().add(1).cumprod()**(1/df.shape[0])).subtract(1)
    df['Volatilidade'] = df['Close'].pct_change().rolling(window=252).std() * (252**0.5)
    return df

def gerar_relatorio_investidor(dados_usuario, df_analises):
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
            dados_acao = df_analises[df_analises['Ticker'] == ticker]
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

        # Classificação do perfil de investidor
        if tolerancia_risco == 'alta' and idade < 40:
            perfil_investidor = 'Arrojado'
        elif tolerancia_risco == 'média' and 40 <= idade < 60:
            perfil_investidor = 'Moderado'
        else:
            perfil_investidor = 'Conservador'

        logging.info("Relatório gerado com sucesso: %s", relatorio)
        return relatorio, perfil_investidor
    except Exception as e:
        logging.error(f"Erro ao gerar relatório de investimento: {str(e)}")
        raise e

def verificar_consistencia_respostas(dados_usuario):
    for key, value in dados_usuario.items():
        if not value:
            return False, f"O campo '{key}' está vazio. Por favor, preencha todas as informações."
    return True, ""

def gerar_relatorio_com_verificacao(dados_usuario, df_analises):
    consistencia, mensagem = verificar_consistencia_respostas(dados_usuario)
    if not consistencia:
        return mensagem
    return gerar_relatorio_investidor(dados_usuario, df_analises)

def treinar_modelo_com_dados_financeiros(user_id, casos, df_analises):
    df = pd.DataFrame(casos)
    df['profissao'] = df['profissao'].astype('category').cat.codes
    df['objetivo'] = df['objetivo'].astype('category').cat.codes
    df['tolerancia_risco'] = df['tolerancia_risco'].astype('category').cat.codes

    X = df[['idade', 'profissao', 'objetivo', 'tolerancia_risco']]
    
    if 'CAGR' not in df_analises.columns or 'Volatilidade' not in df_analises.columns:
        df_analises = calcular_cagr_volatilidade(df_analises)

    categorias = []
    for _, row in df_analises.iterrows():
        try:
            if row['CAGR'] > 0.2 and row['Volatilidade'] < 0.3:
                categoria = 'alta_crescimento_baixo_risco'
            elif row['CAGR'] > 0.2:
                categoria = 'alta_crescimento_alto_risco'
            elif row['Volatilidade'] < 0.3:
                categoria = 'baixo_crescimento_baixo_risco'
            else:
                categoria = 'baixo_crescimento_alto_risco'
            categorias.append((row['Ticker'], categoria))
        except KeyError as e:
            logging.error(f"Erro ao processar linha: {e}")
            continue

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
    joblib.dump(modelo, f"usuarios/modelo_investimento_{user_id}.pkl")
    logging.info(f"Modelo de investimento para o usuário {user_id} treinado com sucesso.")
    carregar_modelo_usuario(user_id)

def obter_acoes_recomendadas(dados_usuario, df_analises):
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
                dados_acao = df_analises[df_analises['Ticker'] == ticker]
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