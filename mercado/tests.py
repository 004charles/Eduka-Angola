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
        self.assertEqual(response.json()["produtos"][0]["titulo"], self.produto.titulo)
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
        self.assertEqual(pedido.status, "A_VALIDAR")
        self.assertEqual(pedido.total, Decimal("120000"))
        self.assertEqual(pedido.itens.count(), 1)
