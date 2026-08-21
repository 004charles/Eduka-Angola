import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from usuarios.models import Aluno

from .models import CategoriaMercado, LojaParceira, PedidoMercado, ProdutoMercado


class MercadoApiTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            email="comprador.mercado@edukangola.local",
            nome="Comprador Mercado",
            password="TesteSeguro2026!",
            tipo_usuario="ALUNO",
        )
        Aluno.objects.create(usuario=self.user, nome=self.user.nome)
        categoria = CategoriaMercado.objects.create(nome="Tecnologia", ordem=1)
        loja = LojaParceira.objects.create(
            nome="Loja Teste Luanda",
            email_operacional="loja@edukangola.local",
            endereco_recolha="Rua da Teste, Luanda",
            verificada=True,
        )
        self.produto = ProdutoMercado.objects.create(
            loja=loja,
            categoria=categoria,
            titulo="Computador de teste",
            resumo="Equipamento para estudar",
            descricao="Computador de demonstração para validar o Mercado.",
            custo_aquisicao=Decimal("100000"),
            preco=Decimal("120000"),
            quantidade_disponivel=3,
            status="PUBLICADO",
        )

    def test_catalogo_publico_expoe_apenas_produtos_publicados(self):
        response = self.client.get("/api/public/mercado/")

        self.assertEqual(response.status_code, 200)
        titulos = [produto["titulo"] for produto in response.json()["produtos"]]
        self.assertIn(self.produto.titulo, titulos)
        self.assertEqual(response.json()["cidade"], "Luanda")

    def test_aluno_cria_pedido_com_dados_de_entrega(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/api/react/mercado/pedidos/",
            data=json.dumps({
                "produto_id": self.produto.id,
                "quantidade": 1,
                "telefone": "+244 923 000 000",
                "endereco_entrega": "Rua das Acácias, 10",
                "bairro": "Talatona",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        pedido = PedidoMercado.objects.get(referencia=response.json()["pedido"])
        self.assertEqual(pedido.status, "AGUARDA_PAGAMENTO")
        self.assertTrue(pedido.reserva_ativa)
        self.assertEqual(pedido.total, Decimal("120000"))
        self.assertEqual(pedido.itens.count(), 1)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade_disponivel, 2)
        self.assertEqual(self.produto.status, "PUBLICADO")

    def test_ultima_unidade_reservada_sai_do_catalogo(self):
        self.produto.quantidade_disponivel = 1
        self.produto.save(update_fields=["quantidade_disponivel"])
        self.client.force_login(self.user)

        response = self.client.post(
            "/api/react/mercado/pedidos/",
            data=json.dumps({
                "produto_id": self.produto.id,
                "quantidade": 1,
                "telefone": "+244 923 000 000",
                "endereco_entrega": "Rua das Acácias, 10",
                "bairro": "Talatona",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade_disponivel, 0)
        self.assertEqual(self.produto.status, "INDISPONIVEL")
        catalogo = self.client.get("/api/public/mercado/")
        self.assertNotIn(self.produto.titulo, [item["titulo"] for item in catalogo.json()["produtos"]])

    def test_cancelamento_devolve_stock_e_publica_produto(self):
        self.client.force_login(self.user)
        resposta = self.client.post(
            "/api/react/mercado/pedidos/",
            data=json.dumps({
                "produto_id": self.produto.id,
                "quantidade": 3,
                "telefone": "+244 923 000 000",
                "endereco_entrega": "Rua das Acácias, 10",
                "bairro": "Talatona",
            }),
            content_type="application/json",
        )
        pedido = PedidoMercado.objects.get(referencia=resposta.json()["pedido"])
        self.assertTrue(pedido.liberar_reserva("Teste de cancelamento."))
        self.produto.refresh_from_db()
        pedido.refresh_from_db()
        self.assertEqual(self.produto.quantidade_disponivel, 3)
        self.assertEqual(self.produto.status, "PUBLICADO")
        self.assertEqual(pedido.status, "CANCELADO")
        self.assertFalse(pedido.reserva_ativa)
