import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function GestaoEventosPage() {
  const navigate = useNavigate();
  const [loggedIn, setLoggedIn] = useState(false);
  const [userRole, setUserRole] = useState(null);

  useEffect(() => {
    // Simples verificação: verifica se há um cookie de login
    const user = document.cookie.match(/usuario=([^;]+)/);
    if (user) {
      setLoggedIn(true);
      setUserRole(user[1]);
    } else {
      // Sem cookie - mostrar tela de login
      setLoggedIn(false);
    }
  }, []);

  if (!loggedIn) {
    // Tela de login
    return (
      <div style={{
        minHeight: '100vh',
        background: '#f5f7fa',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem'
      }}>
        <div style={{
          background: 'white', padding: '2rem', borderRadius: '8px',
          width: '300px', textAlign: 'center', boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}>
          <h2>Área de Eventos</h2>
          <p>Digite a senha para acessar:</p>
          <input 
            id="senha" 
            type="password" 
            style={{ width: '100%', padding: '0.5rem', margin: '0.5rem 0' }}
            placeholder="senha123"
          />
          <button 
            onClick={() => {
              // Simples verificação
              const cookie = document.cookie.match(/usuario=([^;]+)/);
              if (cookie) {
                alert('Login bem-sucedido!');
              } else {
                document.cookie = 'usuario=gestor123; path=/';
                setLoggedIn(true);
                setUserRole('gestor');
              }
            }}
            style={{ width: '100%', padding: '0.5rem', marginTop: '0.5rem' }}
          >
            Entrar
          </button>
        </div>
      </div>
    );
  }

  // Usuário logado - mostrar eventos
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Gerenciamento de Eventos</h1>
      <p>Usuário: <strong>{userRole}</strong></p>
      <p>Bem-vindo ao painel de eventos!</p>
      <button onClick={() => alert('Funcionalidade de evento')}>
        Gerenciar Eventos
      </button>
      <p>Se você está vendo esta mensagem, a página carregou com sucesso!</p>
    </div>
  );
}
