import os
import sys
import django
from django.test import Client
import json

# Adicionar o diretório do projeto ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from usuarios.models import Aluno, PerfilAluno
from gestoreduka.models import CentroDeFormacao
from cursos_app.models import Curso

User = get_user_model()
client = Client()

def run_tests():
    print("=== INICIANDO TESTES DA API MOBILE ===")
    
    # 1. Teste de Registo de Aluno (POST /api/v1/alunos/register/)
    email = "mobile.student@edukangola.ao"
    # Garantir que o utilizador de teste não existe
    User.objects.filter(email=email).delete()
    
    register_data = {
        "nome": "Mobile Student",
        "email": email,
        "password": "supersecurepassword123"
    }
    
    response = client.post(
        '/api/v1/alunos/register/', 
        data=json.dumps(register_data), 
        content_type='application/json'
    )
    
    assert response.status_code == 201, f"Falha no registo: {response.content}"
    res_json = response.json()
    print("[OK] Registo do Aluno: SUCESSO")

    # 1.1 Teste de Handler de Exceções Customizado (POST inválido)
    invalid_register_data = {
        "nome": "Mobile Student"
    }
    error_response = client.post(
        '/api/v1/alunos/register/', 
        data=json.dumps(invalid_register_data), 
        content_type='application/json'
    )
    assert error_response.status_code == 400, f"Deveria retornar 400: {error_response.content}"
    error_json = error_response.json()
    assert error_json['status'] == 'error', "Formato do erro incorreto: status deve ser 'error'"
    assert 'message' in error_json, "Formato do erro incorreto: deve conter a chave 'message'"
    assert 'details' in error_json, "Formato do erro incorreto: deve conter a chave 'details'"
    print("[OK] Handler de Exceções Customizado: SUCESSO")
    
    access_token = res_json['tokens']['access']
    auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
    
    # 2. Teste de Consulta de Perfil (GET /api/v1/alunos/me/)
    response = client.get('/api/v1/alunos/me/', **auth_headers)
    assert response.status_code == 200, f"Falha ao obter perfil: {response.content}"
    print("[OK] Obter Perfil do Aluno ('me'): SUCESSO")
    
    # 3. Teste de Onboarding (POST /api/v1/alunos/onboarding/)
    onboarding_data = {
        "nivel_conhecimento": "I",
        "interesses": [] # Sem categorias para o teste básico
    }
    response = client.post(
        '/api/v1/alunos/onboarding/',
        data=json.dumps(onboarding_data),
        content_type='application/json',
        **auth_headers
    )
    assert response.status_code == 200, f"Falha no onboarding: {response.content}"
    assert response.json()['perfil']['nivel_conhecimento'] == 'I', "Nível incorreto"
    print("[OK] Onboarding do Aluno: SUCESSO")
    
    # 4. Teste de Listagem de Centros (GET /api/v1/centros/)
    response = client.get('/api/v1/centros/')
    assert response.status_code == 200, f"Falha ao listar centros: {response.content}"
    centros_data = response.json()
    assert 'results' in centros_data, "Falta chave 'results' na listagem de centros paginada"
    assert isinstance(centros_data['results'], list), "results deve ser uma lista"
    print("[OK] Listagem de Escolas/Centros: SUCESSO")
    
    # 5. Teste de Detalhes do Centro e Ação Seguir (POST /api/v1/centros/<id>/seguir/)
    # Criar um centro de teste se não houver
    centro = CentroDeFormacao.objects.filter(ativo=True).first()
    if not centro:
        centro = CentroDeFormacao.objects.create(
            nome="Centro de Teste Mobile",
            email="centro.mobile@edukangola.ao",
            ativo=True
        )
    
    response = client.post(f'/api/v1/centros/{centro.id}/seguir/', **auth_headers)
    assert response.status_code == 200, f"Falha ao seguir centro: {response.content}"
    print("[OK] Ação Seguir Centro: SUCESSO")
    
    # 6. Teste de Listagem de Cursos (GET /api/v1/cursos/)
    response = client.get('/api/v1/cursos/')
    assert response.status_code == 200, f"Falha ao listar cursos: {response.content}"
    cursos_data = response.json()
    assert 'results' in cursos_data, "Falta chave 'results' na listagem de cursos paginada"
    assert isinstance(cursos_data['results'], list), "results de cursos deve ser uma lista"
    print("[OK] Listagem de Cursos: SUCESSO")
    
    # 7. Teste de Ementa de Curso (GET /api/v1/cursos/<id>/ementa/)
    curso = Curso.objects.filter(publicado=True, ativo=True).first()
    if not curso:
        curso = Curso.objects.create(
            titulo="Curso de Teste Mobile",
            descricao="Descricao Completa",
            descricao_curta="Desc",
            preco=1000,
            publicado=True,
            ativo=True,
            centro=centro,
            carga_horaria=40
        )
    response = client.get(f'/api/v1/cursos/{curso.id}/ementa/')
    assert response.status_code == 200, f"Falha ao obter ementa: {response.content}"
    print("[OK] Ementa do Curso: SUCESSO")
    
    # 8. Teste de Inscrição em Curso (POST /api/v1/cursos/{id}/inscrever/)
    response = client.post(f'/api/v1/cursos/{curso.id}/inscrever/', **auth_headers)
    assert response.status_code in [200, 201], f"Falha ao inscrever: {response.content}"
    print("[OK] Inscrição em Curso: SUCESSO")
    # 8.1 Teste de Favoritar Curso (POST /api/v1/cursos/{id}/favoritar/)
    response = client.post(f'/api/v1/cursos/{curso.id}/favoritar/', **auth_headers)
    assert response.status_code == 200, f"Falha ao favoritar curso: {response.content}"
    assert response.json()['favorito'] is True, "Deveria ter favoritado"
    print("[OK] Favoritar Curso: SUCESSO")

    # 8.2 Teste de Listar Favoritos (GET /api/v1/alunos/favoritos/)
    response = client.get('/api/v1/alunos/favoritos/', **auth_headers)
    assert response.status_code == 200, f"Falha ao listar favoritos: {response.content}"
    assert len(response.json()) > 0, "Deveria ter pelo menos 1 favorito"
    print("[OK] Listagem de Favoritos do Aluno: SUCESSO")

    # 8.3 Teste de Listar Inscrições (GET /api/v1/alunos/inscricoes/)
    response = client.get('/api/v1/alunos/inscricoes/', **auth_headers)
    assert response.status_code == 200, f"Falha ao listar inscrições: {response.content}"
    assert len(response.json()) > 0, "Deveria ter pelo menos 1 inscrição"
    print("[OK] Listagem de Inscrições do Aluno: SUCESSO")

    # 8.4 Teste de Progresso e Notas de Aula (POST /api/v1/aulas/{id}/progresso/)
    from cursovideoapp.models import Aula, Curso_video
    from cursos_app.models import Categoria
    cat_curso, _ = Categoria.objects.get_or_create(nome="Geral", slug="geral")
    
    # Criar um curso de video de teste (deletar primeiro se houver)
    Curso_video.objects.filter(slug="curso-video-teste").delete()
    curso_video = Curso_video.objects.create(
        titulo="Curso Video Teste",
        descricao="Descricao",
        slug="curso-video-teste",
        is_pago=False,
        categoria=cat_curso
    )
    # Deletar aula se houver
    Aula.objects.filter(curso=curso_video).delete()
    aula = Aula.objects.create(
        curso=curso_video,
        titulo="Aula 1 Teste",
        video_url="https://youtube.com/watch?v=123",
        ordem=1,
        duracao_segundos=120
    )
    
    response = client.post(
        f'/api/v1/aulas/{aula.id}/progresso/',
        data=json.dumps({'concluida': True, 'tempo_assistido': 45}),
        content_type='application/json',
        **auth_headers
    )
    assert response.status_code == 200, f"Falha ao salvar progresso de aula: {response.content}"
    assert response.json()['concluida'] is True, "Progresso deveria estar concluído"
    print("[OK] Progresso da Videoaula Salvo: SUCESSO")

    response = client.post(
        f'/api/v1/aulas/{aula.id}/nota/',
        data=json.dumps({'conteudo': 'Nota de teste na videoaula'}),
        content_type='application/json',
        **auth_headers
    )
    assert response.status_code == 200, f"Falha ao salvar nota de aula: {response.content}"
    assert response.json()['conteudo'] == 'Nota de teste na videoaula', "Nota de aula incorreta"
    print("[OK] Anotação de Estudo Criada: SUCESSO")

    # 8.5 Teste de Blog Posts (GET /api/v1/blog/)
    from blog.models import Post, Categoria as CategoriaBlog
    cat_blog, _ = CategoriaBlog.objects.get_or_create(nome="Notícias", slug="noticias")
    Post.objects.filter(slug="post-de-teste-mobile").delete()
    post = Post.objects.create(
        titulo="Post de Teste Mobile",
        slug="post-de-teste-mobile",
        categoria=cat_blog,
        conteudo="Conteudo do post",
        status="publicado"
    )
    response = client.get('/api/v1/blog/')
    assert response.status_code == 200, f"Falha ao listar posts: {response.content}"
    blog_data = response.json()
    assert 'results' in blog_data, "Falta chave 'results' na listagem de blog paginada"
    assert len(blog_data['results']) > 0, "Deveria retornar pelo menos 1 post"
    print("[OK] Listagem de Feed/Blog: SUCESSO")

    # 8.6 Teste de Estágios (GET /api/v1/estagios/ & POST /api/v1/estagios/{id}/candidatar/)
    from estagio.models import Estagio, AreaEstagio
    area_estagio, _ = AreaEstagio.objects.get_or_create(nome="Tecnologia", slug="tecnologia")
    
    # Deletar estágio antigo se houver
    Estagio.objects.filter(titulo="Estagiário de Dev", centro_formacao=centro).delete()
    estagio = Estagio.objects.create(
        titulo="Estagiário de Dev",
        descricao="Desc completa",
        resumo="Resumo",
        centro_formacao=centro,
        area=area_estagio,
        data_inicio=timezone.now().date(),
        data_limite_inscricao=timezone.now().date() + timezone.timedelta(days=5),
        local_trabalho="Escritório",
        cidade="Luanda",
        provincia="Luanda",
        requisitos="Conhecimento em Django",
        vagas_disponiveis=5,
        vagas_preenchidas=0,
        ativo=True
    )
    
    response = client.get('/api/v1/estagios/')
    assert response.status_code == 200, f"Falha ao listar estágios: {response.content}"
    estagios_data = response.json()
    assert 'results' in estagios_data, "Falta chave 'results' na listagem de estágios paginada"
    assert len(estagios_data['results']) > 0, "Deveria retornar pelo menos 1 estágio"
    print("[OK] Listagem de Estágios: SUCESSO")

    response = client.post(
        f'/api/v1/estagios/{estagio.id}/candidatar/',
        data=json.dumps({'carta_motivacao': 'Gostaria de estagiar'}),
        content_type='application/json',
        **auth_headers
    )
    assert response.status_code == 201, f"Falha ao se candidatar ao estágio: {response.content}"
    print("[OK] Candidatura a Estágio: SUCESSO")

    # 8.7 Teste de Recuperação de Senha via API
    response = client.post(
        '/api/v1/alunos/esqueci-senha/',
        data=json.dumps({'email': email}),
        content_type='application/json'
    )
    assert response.status_code == 200, f"Falha ao enviar esqueci-senha: {response.content}"
    print("[OK] API Esqueci-Senha (Código enviado): SUCESSO")

    from usuarios.models import CodigoVerificacao
    cod_ver = CodigoVerificacao.objects.filter(email=email, tipo='RECUPERACAO').latest('criado_em')

    response = client.post(
        '/api/v1/alunos/redefinir-senha/',
        data=json.dumps({
            'email': email,
            'codigo': cod_ver.codigo,
            'senha': 'newsecurepassword123',
            'confirmar_senha': 'newsecurepassword123'
        }),
        content_type='application/json'
    )
    assert response.status_code == 200, f"Falha ao redefinir senha via API: {response.content}"
    print("[OK] API Redefinir-Senha (Nova senha definida): SUCESSO")

    # 9. Teste de Autenticação via Chave de API de Cliente (M2M)
    from core.models import ClienteAPIKey
    key_obj = ClienteAPIKey.objects.create(nome_cliente="Test External Site")
    api_key_headers = {'HTTP_AUTHORIZATION': f'Api-Key {key_obj.chave}'}
    
    response = client.get('/api/v1/cursos/', **api_key_headers)
    assert response.status_code == 200, f"Falha ao autenticar via Api-Key: {response.content}"
    print("[OK] Autenticação via Chave de API de Cliente: SUCESSO")
    
    # Limpeza
    key_obj.delete()
    post.delete()
    estagio.delete()
    aula.delete()
    curso_video.delete()
    User.objects.filter(email=email).delete()
    print("=== TODOS OS TESTES PASSARAM COM SUCESSO ===")

if __name__ == '__main__':
    run_tests()
