# Por que a página /gestao-eventos aparece em branco?

## Causas Mais Comuns

### 1. Servidores não estão rodando
**O frontend (React) e o backend (Django) precisam estar rodando simultaneamente.**

```bash
# No terminal 1 - Iniciar frontend
cd frontend && npm run dev
# Ou: npx vite

# No terminal 2 - Iniciar backend  
cd . && python3 manage.py runserver
```

### 2. Console do navegador (F12) - Erros ocultos
Pressione **F12** e vá na aba **Console**. Procure por:
- `fetch failed` - API não disponível
- `CORS policy` - problema de domínio
- `Cannot read property 'split' of undefined` - erro no CSRF token
- Erros em vermelho que indicam o problema real

### 3. Componente mostrando estado de loading
O componente exibe "Carregando..." por alguns segundos enquanto busca os dados. Espere alguns instantes.

### 3. Usuário não é gestor
Se o usuário logado não tiver perfil de gestor, a página redireciona para o login e mostra nada (ou o login).

---

## Passo a Passo para Funcionar

### Etapa 1: Iniciar os servidores

```bash
# Terminal 1 - Frontend (porta 5173)
cd /home/sckj-muquissi/Eduka-Angola/frontend
npm run dev
# ou apenas: npx vite

# Terminal 2 - Backend (porta 8000)  
cd /home/sckj-muquissi/Eduka-Angola
python3 manage.py runserver
```

### Etapa 2: Acessar a página
Abra: `http://localhost:5173/gestao-eventos`

### Etapa 3: Verificar o Console (F12)
Se ainda aparecer branco, abra o console e procure por mensagens como:
- `Session response status: 401` - precisa fazer login
- `Events fetch status: 404` - endpoint errado  
- `Events data received: {}` - dados vindo, mas lista vazia
- `User is gestor: true` - sucesso!

### 4. Se ainda estiver branco
1. Verifique se `http://localhost:8000/backend/gestoreduka/api/react/gestor/sessao/` funciona no navegador
2. Verifique se `http://localhost:8000/backend/gestoreduka/api/react/eventos/` retorna dados JSON
3. Confirme que você está logado como gestor (não como aluno ou visitante)

---

## Verificações Rápidas

```bash
# Testar API no terminal (enquanto o backend roda)
curl -b "SESSIONID=sua_sessao" http://localhost:8000/backend/gestoreduka/api/react/gestor/sessao/
# Deverá retornar JSON com dados do usuário logado

curl -b "SESSIONID=sua_sessao" http://localhost:8000/backend/gestoreduka/api/react/eventos/
# Deverá retornar JSON com lista de eventos
```

---

## Se nada funcionar

1. Teste o login em `/gestoreduka/login_gestor` primeiro
2. Confirme que o perfil do usuário tem `tipo_usuario = 'GESTOR'`
3. Reinicie ambos os servidores (frontend + backend)
4. Limpe o cache do navegador (Ctrl+Shift+Delete -> Imagens e arquivos em cache)
