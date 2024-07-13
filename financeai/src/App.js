import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [dadosUsuario, setDadosUsuario] = useState({
    nome: '',
    idade: '',
    objetivo: '',
    tolerancia_risco: '',
    investimentos: '',
    renda_mensal: '',
    despesas_mensais: ''
  });
  const [recomendacao, setRecomendacao] = useState('');

  const handleChange = (e) => {
    setDadosUsuario({
      ...dadosUsuario,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const resposta = await axios.post('http://localhost:5000/gerar-recomendacao', dadosUsuario);
      setRecomendacao(resposta.data.recomendacao);
    } catch (error) {
      console.error("Erro ao obter recomendação", error);
      setRecomendacao("Erro ao obter recomendação");
    }
  };

  return (
    <div className="App">
      <h1>Consultor de Investimentos Pessoais</h1>
      <form onSubmit={handleSubmit}>
        <input name="nome" placeholder="Nome" onChange={handleChange} />
        <input name="idade" placeholder="Idade" type="number" onChange={handleChange} />
        <input name="objetivo" placeholder="Objetivo financeiro" onChange={handleChange} />
        <input name="tolerancia_risco" placeholder="Tolerância ao risco" onChange={handleChange} />
        <input name="investimentos" placeholder="Investimentos atuais" onChange={handleChange} />
        <input name="renda_mensal" placeholder="Renda mensal" type="number" onChange={handleChange} />
        <input name="despesas_mensais" placeholder="Despesas mensais" type="number" onChange={handleChange} />
        <button type="submit">Obter Recomendação</button>
      </form>
      {recomendacao && (
        <div>
          <h2>Recomendação de Investimento</h2>
          <p>{recomendacao}</p>
        </div>
      )}
    </div>
  );
}

export default App;