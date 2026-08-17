from django.test import TestCase
import json

from cursos_app.models import Categoria, Curso, Instrutor, Turma, Inscricao, NotaAluno, Presenca
from usuarios.models import Aluno, Usuario
from .models import CentroDeFormacao


class ReactGestorDashboardTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(email='gestor.react@test.com', nome='Gestor React', password='SenhaSegura123', tipo_usuario='GESTOR')
        self.centro = CentroDeFormacao.objects.create(usuario=self.user, nome='Centro React', email=self.user.email)
        categoria = Categoria.objects.create(nome='Tecnologia React', slug='tecnologia-react')
        self.instrutor = Instrutor.objects.create(centro_de_formacao=self.centro, nome='Formador React', biografia='Formador responsável pelos testes React.', email='formador.react@test.com', area_especializacao='TECNOLOGIA_INFORMACAO')
        self.curso = Curso.objects.create(centro=self.centro, titulo='Curso React', descricao='Curso de teste com uma descrição suficientemente detalhada.', categoria=categoria, carga_horaria=12, preco=1000, publicado=False, ativo=True)
        self.curso.instrutores.add(self.instrutor)

    def test_dashboard_exige_sessao_e_restringe_os_dados_ao_centro_do_gestor(self):
        self.assertEqual(self.client.get('/gestoreduka/api/react/dashboard/').status_code, 302)
        self.client.force_login(self.user)
        response = self.client.get('/gestoreduka/api/react/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['centro']['id'], self.centro.id)
        self.assertEqual(response.json()['cursos'][0]['id'], self.curso.id)

    def test_gestor_publica_apenas_curso_do_proprio_centro(self):
        self.client.force_login(self.user)
        response = self.client.post(f'/gestoreduka/api/react/cursos/{self.curso.id}/publicacao/', data='{"publicado": true}', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.curso.refresh_from_db()
        self.assertTrue(self.curso.publicado)

    def test_gestor_principal_remove_o_proprio_curso_pelo_endpoint_react(self):
        self.client.force_login(self.user)
        response = self.client.post(f'/gestoreduka/api/react/cursos/{self.curso.id}/remover/')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Curso.objects.filter(pk=self.curso.id).exists())

    def test_gestor_actualiza_o_proprio_curso_pelo_endpoint_patch_react(self):
        self.client.force_login(self.user)
        payload = self.client.get(f'/gestoreduka/api/react/cursos/{self.curso.id}/').json()['curso']
        payload['titulo'] = 'Curso React actualizado'

        response = self.client.patch(
            f'/gestoreduka/api/react/cursos/{self.curso.id}/',
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200, response.content.decode())
        self.curso.refresh_from_db()
        self.assertEqual(self.curso.titulo, 'Curso React actualizado')

    def test_gestor_cria_e_actualiza_turma_pelos_endpoints_react(self):
        self.client.force_login(self.user)
        payload = {
            'curso_id': self.curso.id, 'nome': 'Turma React A', 'codigo': 'REACT-A',
            'data_inicio': '2026-09-01', 'data_fim': '2026-10-01', 'turno': 'MANHA',
            'horario_inicio': '08:00', 'horario_fim': '11:00', 'dias_semana': ['SEG', 'QUA', 'SEX'],
            'vagas_totais': 20, 'local': 'Sede', 'sala': 'Sala 2', 'status': 'ABERTA',
            'instrutor_principal_id': self.instrutor.id,
        }
        create_response = self.client.post('/gestoreduka/api/react/turmas/', data=json.dumps(payload), content_type='application/json')

        self.assertEqual(create_response.status_code, 201, create_response.content.decode())
        turma_id = create_response.json()['turma']['id']
        payload['nome'] = 'Turma React Actualizada'
        payload['status'] = 'EM_ANDAMENTO'
        update_response = self.client.patch(f'/gestoreduka/api/react/turmas/{turma_id}/', data=json.dumps(payload), content_type='application/json')

        self.assertEqual(update_response.status_code, 200, update_response.content.decode())
        turma = Turma.objects.get(pk=turma_id)
        self.assertEqual(turma.nome, 'Turma React Actualizada')
        self.assertEqual(turma.status, 'EM_ANDAMENTO')

    def test_gestor_regista_presencas_e_notas_da_turma_pelo_react(self):
        turma = Turma.objects.create(curso=self.curso, nome='Turma de Avaliação', codigo='REACT-NOTAS', data_inicio='2026-09-01', data_fim='2026-10-01', turno='MANHA', horario_inicio='08:00', horario_fim='11:00', dias_semana='SEG,QUA', vagas_totais=10)
        aluno = Aluno.objects.create(nome='Aluno React')
        inscricao = Inscricao.objects.create(aluno=aluno, curso=self.curso, turma_escolhida=turma, status='A')
        self.client.force_login(self.user)

        presence_response = self.client.put(f'/gestoreduka/api/react/turmas/{turma.id}/presencas/', data=json.dumps({'data': '2026-09-02', 'registos': [{'inscricao_id': inscricao.id, 'estado': 'ATRASO', 'observacao': 'Chegou depois do início.'}]}), content_type='application/json')
        grade_response = self.client.put(f'/gestoreduka/api/react/turmas/{turma.id}/notas/', data=json.dumps({'registos': [{'inscricao_id': inscricao.id, 'nota': '17.5', 'observacao': 'Bom desempenho.'}]}), content_type='application/json')

        self.assertEqual(presence_response.status_code, 200, presence_response.content.decode())
        self.assertEqual(grade_response.status_code, 200, grade_response.content.decode())
        self.assertEqual(Presenca.objects.get(turma=turma, inscricao=inscricao).estado, 'ATRASO')
        self.assertEqual(str(NotaAluno.objects.get(turma=turma, inscricao=inscricao).nota), '17.50')

    def test_gestor_aprova_inscricao_do_proprio_centro_pelo_react(self):
        turma = Turma.objects.create(curso=self.curso, nome='Turma de Inscrições', codigo='REACT-INSCR', data_inicio='2026-09-01', data_fim='2026-10-01', turno='MANHA', horario_inicio='08:00', horario_fim='11:00', dias_semana='SEG,QUA', vagas_totais=10)
        aluno = Aluno.objects.create(nome='Aluno Inscrição React')
        inscricao = Inscricao.objects.create(aluno=aluno, curso=self.curso, turma_escolhida=turma, status='P')
        self.client.force_login(self.user)

        response = self.client.patch(f'/gestoreduka/api/react/inscricoes/{inscricao.id}/', data=json.dumps({'status': 'A'}), content_type='application/json')

        self.assertEqual(response.status_code, 200, response.content.decode())
        inscricao.refresh_from_db()
        self.assertEqual(inscricao.status, 'A')

    def test_formulario_react_de_cursos_devolve_apenas_metadados_do_centro(self):
        self.client.force_login(self.user)
        response = self.client.get('/gestoreduka/api/react/cursos/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('categorias', response.json())
        self.assertIn('instrutores', response.json())
        self.assertIn('modalidade', response.json()['escolhas'])
