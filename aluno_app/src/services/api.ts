import { getAccessToken, getRefreshToken, saveTokens, clearAll } from './storage';

const BASE_URL = 'http://192.168.13.184:8000';

interface RequestOptions {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
}

async function request<T = any>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers: extraHeaders = {} } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...extraHeaders,
  };

  const token = await getAccessToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${await getAccessToken()}`;
      const retry = await fetch(`${BASE_URL}${endpoint}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
      });
      if (!retry.ok) throw new Error(`API error: ${retry.status}`);
      return retry.json();
    }
    await clearAll();
    throw new Error('Sessão expirada. Faça login novamente.');
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || error.message || `API error: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

async function tryRefreshToken(): Promise<boolean> {
  try {
    const refresh = await getRefreshToken();
    if (!refresh) return false;

    const res = await fetch(`${BASE_URL}/api/v1/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });

    if (!res.ok) return false;

    const data = await res.json();
    await saveTokens(data.access, refresh);
    return true;
  } catch {
    return false;
  }
}

async function uploadFile<T = any>(endpoint: string, uri: string, fieldName = 'comprovativo'): Promise<T> {
  const token = await getAccessToken();
  const formData = new FormData();
  formData.append(fieldName, {
    uri,
    name: 'comprovativo.jpg',
    type: 'image/jpeg',
  } as any);

  const res = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: formData,
  });

  if (!res.ok) throw new Error(`Upload error: ${res.status}`);
  return res.json();
}

// ============ AUTH ============

export const auth = {
  login(email: string, password: string) {
    return request<{ access: string; refresh: string }>('/api/v1/token/', {
      method: 'POST',
      body: { email, password },
    });
  },

  register(data: {
    nome: string;
    email: string;
    telefone: string;
    password: string;
  }) {
    return request<{ aluno: any; tokens: { access: string; refresh: string } }>('/api/v1/alunos/register/', {
      method: 'POST',
      body: { nome: data.nome, email: data.email, password: data.password },
    });
  },

  esqueciSenha(email: string) {
    return request('/api/v1/alunos/esqueci-senha/', {
      method: 'POST',
      body: { email },
    });
  },

  redefinirSenha(email: string, codigo: string, nova_senha: string) {
    return request('/api/v1/alunos/redefinir-senha/', {
      method: 'POST',
      body: { email, codigo, nova_senha },
    });
  },
};

// ============ PROFILE ============

export const perfil = {
  get() {
    return request('/api/v1/alunos/me/');
  },

  update(data: Record<string, any>) {
    return request('/api/v1/alunos/me/', {
      method: 'PATCH',
      body: data,
    });
  },

  onboarding(data: { interesses: number[]; nivel_conhecimento: string; meta_semanal: string }) {
    return request('/api/v1/alunos/onboarding/', {
      method: 'POST',
      body: data,
    });
  },
};

// ============ CURSOS ============

export const cursos = {
  list(params?: { search?: string; categoria?: number }) {
    const query = new URLSearchParams();
    if (params?.search) query.set('search', params.search);
    if (params?.categoria) query.set('categoria', String(params.categoria));
    const qs = query.toString();
    return request(`/api/v1/cursos/${qs ? '?' + qs : ''}`);
  },

  get(id: number) {
    return request(`/api/v1/cursos/${id}/`);
  },

  getEmenta(id: number) {
    return request(`/api/v1/cursos/${id}/ementa/`);
  },

  inscrever(id: number, data?: { turma?: number; forma_pagamento?: string }) {
    return request(`/api/v1/cursos/${id}/inscrever/`, {
      method: 'POST',
      body: data || {},
    });
  },

  enviarComprovativo(id: number, uri: string) {
    return uploadFile(`/api/v1/cursos/${id}/enviar-comprovante/`, uri);
  },

  favoritar(id: number) {
    return request(`/api/v1/cursos/${id}/favoritar/`, { method: 'POST' });
  },
};

// ============ CATEGORIAS ============

export const categorias = {
  list() {
    return request('/api/v1/categorias/');
  },
};

// ============ VIDEO CURSOS ============

export const videoCursos = {
  list() {
    return request('/api/v1/video-cursos/');
  },

  get(slug: string) {
    return request(`/api/v1/video-cursos/${slug}/`);
  },
};

// ============ AULAS ============

export const aulas = {
  list(cursoId?: number) {
    const qs = cursoId ? `?curso=${cursoId}` : '';
    return request(`/api/v1/aulas/${qs}`);
  },

  get(id: number) {
    return request(`/api/v1/aulas/${id}/`);
  },

  updateProgresso(id: number, data: { concluida: boolean; tempo_assistido?: number }) {
    return request(`/api/v1/aulas/${id}/progresso/`, {
      method: 'POST',
      body: data,
    });
  },

  saveNota(id: number, conteudo: string) {
    return request(`/api/v1/aulas/${id}/nota/`, {
      method: 'POST',
      body: { conteudo },
    });
  },
};

// ============ EXERCICIOS ============

export const exercicios = {
  list(cursoId?: number) {
    const qs = cursoId ? `?curso=${cursoId}` : '';
    return request(`/api/v1/exercicios/${qs}`);
  },

  get(id: number) {
    return request(`/api/v1/exercicios/${id}/`);
  },

  submeter(id: number, respostas: { questao_id: number; alternativa_id: number }[]) {
    return request(`/api/v1/exercicios/${id}/submeter/`, {
      method: 'POST',
      body: { respostas },
    });
  },
};

// ============ ALUNO ============

export const aluno = {
  getInscricoes() {
    return request('/api/v1/alunos/inscricoes/');
  },

  getFavoritos() {
    return request('/api/v1/alunos/favoritos/');
  },

  getCertificados() {
    return request('/api/v1/alunos/certificados/');
  },

  getNotificacoes() {
    return request('/api/v1/alunos/notificacoes/');
  },

  marcarNotificacaoLida(id: number) {
    return request(`/api/v1/alunos/notificacoes/${id}/lida/`, { method: 'POST' });
  },
};

// ============ CENTROS / ESCOLAS ============

export const centros = {
  list(params?: { search?: string }) {
    const qs = params?.search ? `?search=${params.search}` : '';
    return request(`/api/v1/centros/${qs}`);
  },

  get(id: number) {
    return request(`/api/v1/centros/${id}/`);
  },

  seguir(id: number) {
    return request(`/api/v1/centros/${id}/seguir/`, { method: 'POST' });
  },
};

// ============ PARCERIAS / CENTROS PARCEIROS ============

export const parcerias = {
  list(params?: { search?: string }) {
    const qs = params?.search ? `?search=${params.search}` : '';
    return request(`/api/v1/parcerias/${qs ? '?' + qs : ''}`);
  },
};

export const candidaturas = {
  list() {
    return request('/api/v1/candidaturas/');
  },

  get(id: number) {
    return request(`/api/v1/candidaturas/${id}/`);
  },

  create(data: {
    parceria: number;
    curso: number;
    nome_completo: string;
    email: string;
    telefone: string;
    bi?: string;
  }) {
    return request('/api/v1/candidaturas/', {
      method: 'POST',
      body: data,
    });
  },
};

// ============ PAGAMENTOS ============

export const pagamentos = {
  list() {
    return request('/api/v1/pagamentos/');
  },

  get(id: string) {
    return request(`/api/v1/pagamentos/${id}/`);
  },

  criar(data: {
    curso_id?: number;
    valor: number;
    moeda?: string;
    forma_pagamento: string;
    referencia_pagamento?: string;
  }) {
    return request('/api/v1/pagamentos/criar/', {
      method: 'POST',
      body: data,
    });
  },

  verificarStatus(id: string) {
    return request(`/api/v1/pagamentos/${id}/verificar-status/`);
  },
};

// ============ CHAT ============

export const chat = {
  getConversas() {
    return request('/api/v1/chat/conversas/');
  },

  getMensagens(conversaId: number) {
    return request(`/api/v1/chat/${conversaId}/mensagens/`);
  },

  enviarMensagem(conversaId: number, mensagem: string) {
    return request(`/api/v1/chat/${conversaId}/enviar/`, {
      method: 'POST',
      body: { mensagem },
    });
  },
};

// ============ MATERIAIS ============

export const materiais = {
  list(cursoId: number) {
    return request(`/api/v1/cursos/${cursoId}/materiais/`);
  },

  listAula(cursoId: number, aulaId: number) {
    return request(`/api/v1/video-cursos/${cursoId}/materiais-aula/${aulaId}/`);
  },
};

// ============ BLOG ============

export const blog = {
  list() {
    return request('/api/v1/blog/');
  },

  get(slug: string) {
    return request(`/api/v1/blog/${slug}/`);
  },
};

export default {
  auth,
  perfil,
  cursos,
  categorias,
  videoCursos,
  aulas,
  exercicios,
  aluno,
  centros,
  pagamentos,
  chat,
  materiais,
  blog,
};
