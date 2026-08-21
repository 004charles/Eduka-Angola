from decimal import Decimal

from django.db import migrations
from django.utils.text import slugify


LOJA_SLUG = "edukangola-mercado-demonstracao"

IMAGENS = {
    "computadores": "/manus-storage/mercado-laptop-estudante_c7f7893a.png",
    "livros": "/manus-storage/mercado-livros-estudo_a0178266.png",
    "mochilas": "/manus-storage/mercado-mochila-estudo_3ee5e228.png",
}


PRODUTOS = [
    ("Computadores", "Portátil Estudo 14", "Leve, prático e preparado para trabalhos, aulas e pesquisa.", "Computador portátil de demonstração para estudantes que precisam de produtividade diária, pesquisa e trabalhos académicos.", "475000", "405000", 4, "Garantia demonstrativa de 12 meses", "computadores", {"Ecrã": "14 polegadas", "Memória": "8 GB RAM", "Armazenamento": "256 GB SSD", "Condição": "Novo"}),
    ("Computadores", "Portátil Campus 15", "Mais espaço de trabalho para cursos técnicos e tarefas exigentes.", "Modelo demonstrativo com desempenho adequado para aulas online, documentação, apresentações e ferramentas de estudo.", "555000", "470000", 3, "Garantia demonstrativa de 12 meses", "computadores", {"Ecrã": "15,6 polegadas", "Memória": "16 GB RAM", "Armazenamento": "512 GB SSD", "Condição": "Novo"}),
    ("Computadores", "Portátil Essencial 14", "Uma escolha compacta para iniciar o percurso digital.", "Computador demonstrativo focado em navegação, documentos, videoconferências e organização de estudos.", "390000", "330000", 5, "Garantia demonstrativa de 12 meses", "computadores", {"Ecrã": "14 polegadas", "Memória": "8 GB RAM", "Armazenamento": "128 GB SSD", "Condição": "Novo"}),
    ("Livros físicos", "Caderno de Fundamentos de Informática", "Leitura de apoio para iniciar competências digitais.", "Livro físico demonstrativo para mostrar a apresentação de material de estudo no Mercado Edukangola.", "8500", "6200", 12, "Produto físico de demonstração", "livros", {"Formato": "Livro físico", "Idioma": "Português", "Área": "Tecnologia", "Condição": "Novo"}),
    ("Livros físicos", "Guia de Matemática Essencial", "Exercícios e explicações para reforçar a base matemática.", "Livro físico demonstrativo destinado a representar materiais de reforço escolar e preparação académica.", "12000", "8800", 9, "Produto físico de demonstração", "livros", {"Formato": "Livro físico", "Idioma": "Português", "Área": "Matemática", "Condição": "Novo"}),
    ("Livros físicos", "Comunicação Profissional", "Ferramentas de escrita e apresentação para o futuro profissional.", "Livro físico demonstrativo que exemplifica materiais para competências de comunicação e empregabilidade.", "15500", "11200", 8, "Produto físico de demonstração", "livros", {"Formato": "Livro físico", "Idioma": "Português", "Área": "Carreira", "Condição": "Novo"}),
    ("Mochilas", "Mochila Campus Verde 20L", "Organização confortável para livros, cadernos e portátil.", "Mochila demonstrativa para estudantes, com compartimento principal amplo e desenho pensado para uso diário.", "16000", "11300", 10, "Produto físico de demonstração", "mochilas", {"Capacidade": "20 litros", "Material": "Tecido resistente", "Compartimento": "Portátil até 14 polegadas", "Condição": "Novo"}),
    ("Mochilas", "Mochila Estudo Urbana 18L", "Compacta, leve e pronta para a rotina de aulas.", "Mochila demonstrativa compacta, adequada para quem transporta materiais essenciais durante o dia.", "24000", "17500", 7, "Produto físico de demonstração", "mochilas", {"Capacidade": "18 litros", "Material": "Canvas", "Compartimento": "Materiais de estudo", "Condição": "Novo"}),
    ("Mochilas", "Mochila Secure Laptop 22L", "Protecção adicional para portátil e material de estudo.", "Mochila demonstrativa com espaço organizado para portátil, carregador, cadernos e acessórios.", "32000", "23500", 6, "Produto físico de demonstração", "mochilas", {"Capacidade": "22 litros", "Material": "Tecido acolchoado", "Compartimento": "Portátil até 15 polegadas", "Condição": "Novo"}),
]


def seed_catalogo(apps, schema_editor):
    LojaParceira = apps.get_model("mercado", "LojaParceira")
    CategoriaMercado = apps.get_model("mercado", "CategoriaMercado")
    ProdutoMercado = apps.get_model("mercado", "ProdutoMercado")

    loja, _ = LojaParceira.objects.update_or_create(
        slug=LOJA_SLUG,
        defaults={
            "nome": "Edukangola Mercado — Demonstração",
            "descricao": "Catálogo de demonstração da Edukangola. Não representa uma loja comercial activa.",
            "email_operacional": "demo.mercado@edukangola.local",
            "telefone_operacional": "+244 900 000 000",
            "endereco_recolha": "Local de demonstração, Luanda",
            "bairro": "Luanda",
            "municipio": "Luanda",
            "provincia": "Luanda",
            "politica_garantia": "Produtos apresentados apenas para demonstração visual.",
            "verificada": True,
            "ativa": True,
        },
    )

    for categoria_nome, titulo, resumo, descricao, preco, custo, quantidade, garantia, imagem, especificacoes in PRODUTOS:
        categoria = CategoriaMercado.objects.get(nome=categoria_nome)
        ProdutoMercado.objects.update_or_create(
            loja=loja,
            titulo=titulo,
            defaults={
                "categoria": categoria,
                "slug": slugify(titulo),
                "resumo": resumo,
                "descricao": descricao,
                "imagem_url_publica": IMAGENS[imagem],
                "imagens": [],
                "especificacoes": especificacoes,
                "condicao": "NOVO",
                "garantia": garantia,
                "custo_aquisicao": Decimal(custo),
                "preco": Decimal(preco),
                "moeda": "AOA",
                "quantidade_disponivel": quantidade,
                "prazo_entrega_dias": 2,
                "status": "PUBLICADO",
                "destaque": True,
            },
        )


def remover_catalogo(apps, schema_editor):
    LojaParceira = apps.get_model("mercado", "LojaParceira")
    ProdutoMercado = apps.get_model("mercado", "ProdutoMercado")
    ProdutoMercado.objects.filter(loja__slug=LOJA_SLUG).delete()
    LojaParceira.objects.filter(slug=LOJA_SLUG).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("mercado", "0004_produtomercado_imagem_url_publica"),
    ]

    operations = [
        migrations.RunPython(seed_catalogo, remover_catalogo),
    ]
