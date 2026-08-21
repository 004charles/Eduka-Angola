from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from mercado.models import CategoriaMercado, LojaParceira, ProdutoMercado


IMAGENS = {
    "computadores": "/manus-storage/mercado-laptop-estudante_c7f7893a.png",
    "livros": "/manus-storage/mercado-livros-estudo_a0178266.png",
    "mochilas": "/manus-storage/mercado-mochila-estudo_3ee5e228.png",
}


PRODUTOS = [
    {
        "categoria": "Computadores", "titulo": "Portátil Estudo 14", "resumo": "Leve, prático e preparado para trabalhos, aulas e pesquisa.",
        "descricao": "Computador portátil de demonstração para estudantes que precisam de produtividade diária, pesquisa e trabalhos académicos.",
        "preco": "475000", "custo": "405000", "quantidade": 4, "garantia": "Garantia demonstrativa de 12 meses", "imagem": "computadores",
        "especificacoes": {"Ecrã": "14 polegadas", "Memória": "8 GB RAM", "Armazenamento": "256 GB SSD", "Condição": "Novo"},
    },
    {
        "categoria": "Computadores", "titulo": "Portátil Campus 15", "resumo": "Mais espaço de trabalho para cursos técnicos e tarefas exigentes.",
        "descricao": "Modelo demonstrativo com desempenho adequado para aulas online, documentação, apresentações e ferramentas de estudo.",
        "preco": "555000", "custo": "470000", "quantidade": 3, "garantia": "Garantia demonstrativa de 12 meses", "imagem": "computadores",
        "especificacoes": {"Ecrã": "15,6 polegadas", "Memória": "16 GB RAM", "Armazenamento": "512 GB SSD", "Condição": "Novo"},
    },
    {
        "categoria": "Computadores", "titulo": "Portátil Essencial 14", "resumo": "Uma escolha compacta para iniciar o percurso digital.",
        "descricao": "Computador demonstrativo focado em navegação, documentos, videoconferências e organização de estudos.",
        "preco": "390000", "custo": "330000", "quantidade": 5, "garantia": "Garantia demonstrativa de 12 meses", "imagem": "computadores",
        "especificacoes": {"Ecrã": "14 polegadas", "Memória": "8 GB RAM", "Armazenamento": "128 GB SSD", "Condição": "Novo"},
    },
    {
        "categoria": "Livros físicos", "titulo": "Caderno de Fundamentos de Informática", "resumo": "Leitura de apoio para iniciar competências digitais.",
        "descricao": "Livro físico demonstrativo para mostrar a apresentação de material de estudo no Mercado Edukangola.",
        "preco": "8500", "custo": "6200", "quantidade": 12, "garantia": "Produto físico de demonstração", "imagem": "livros",
        "especificacoes": {"Formato": "Livro físico", "Idioma": "Português", "Área": "Tecnologia", "Condição": "Novo"},
    },
    {
        "categoria": "Livros físicos", "titulo": "Guia de Matemática Essencial", "resumo": "Exercícios e explicações para reforçar a base matemática.",
        "descricao": "Livro físico demonstrativo destinado a representar materiais de reforço escolar e preparação académica.",
        "preco": "12000", "custo": "8800", "quantidade": 9, "garantia": "Produto físico de demonstração", "imagem": "livros",
        "especificacoes": {"Formato": "Livro físico", "Idioma": "Português", "Área": "Matemática", "Condição": "Novo"},
    },
    {
        "categoria": "Livros físicos", "titulo": "Comunicação Profissional", "resumo": "Ferramentas de escrita e apresentação para o futuro profissional.",
        "descricao": "Livro físico demonstrativo que exemplifica materiais para competências de comunicação e empregabilidade.",
        "preco": "15500", "custo": "11200", "quantidade": 8, "garantia": "Produto físico de demonstração", "imagem": "livros",
        "especificacoes": {"Formato": "Livro físico", "Idioma": "Português", "Área": "Carreira", "Condição": "Novo"},
    },
    {
        "categoria": "Mochilas", "titulo": "Mochila Campus Verde 20L", "resumo": "Organização confortável para livros, cadernos e portátil.",
        "descricao": "Mochila demonstrativa para estudantes, com compartimento principal amplo e desenho pensado para uso diário.",
        "preco": "16000", "custo": "11300", "quantidade": 10, "garantia": "Produto físico de demonstração", "imagem": "mochilas",
        "especificacoes": {"Capacidade": "20 litros", "Material": "Tecido resistente", "Compartimento": "Portátil até 14 polegadas", "Condição": "Novo"},
    },
    {
        "categoria": "Mochilas", "titulo": "Mochila Estudo Urbana 18L", "resumo": "Compacta, leve e pronta para a rotina de aulas.",
        "descricao": "Mochila demonstrativa compacta, adequada para quem transporta materiais essenciais durante o dia.",
        "preco": "24000", "custo": "17500", "quantidade": 7, "garantia": "Produto físico de demonstração", "imagem": "mochilas",
        "especificacoes": {"Capacidade": "18 litros", "Material": "Canvas", "Compartimento": "Materiais de estudo", "Condição": "Novo"},
    },
    {
        "categoria": "Mochilas", "titulo": "Mochila Secure Laptop 22L", "resumo": "Protecção adicional para portátil e material de estudo.",
        "descricao": "Mochila demonstrativa com espaço organizado para portátil, carregador, cadernos e acessórios.",
        "preco": "32000", "custo": "23500", "quantidade": 6, "garantia": "Produto físico de demonstração", "imagem": "mochilas",
        "especificacoes": {"Capacidade": "22 litros", "Material": "Tecido acolchoado", "Compartimento": "Portátil até 15 polegadas", "Condição": "Novo"},
    },
]


class Command(BaseCommand):
    help = "Popula o Mercado Edukangola local com produtos claramente marcados como demonstração."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Este catálogo de demonstração só pode ser executado com DEBUG=True.")

        loja, _ = LojaParceira.objects.update_or_create(
            slug="edukangola-mercado-demonstracao",
            defaults={
                "nome": "Edukangola Mercado — Demonstração",
                "descricao": "Catálogo local de demonstração. Não representa uma loja comercial activa.",
                "email_operacional": "demo.mercado@edukangola.local",
                "telefone_operacional": "+244 900 000 000",
                "endereco_recolha": "Local de demonstração, Luanda",
                "bairro": "Luanda", "municipio": "Luanda", "provincia": "Luanda",
                "politica_garantia": "Produtos apenas para demonstração visual.",
                "verificada": True, "ativa": True,
            },
        )
        criados = atualizados = 0
        for dados in PRODUTOS:
            categoria = CategoriaMercado.objects.get(nome=dados["categoria"])
            produto, criado = ProdutoMercado.objects.update_or_create(
                loja=loja,
                titulo=dados["titulo"],
                defaults={
                    "categoria": categoria,
                    "resumo": dados["resumo"],
                    "descricao": dados["descricao"],
                    "imagem_url_publica": IMAGENS[dados["imagem"]],
                    "especificacoes": dados["especificacoes"],
                    "garantia": dados["garantia"],
                    "custo_aquisicao": Decimal(dados["custo"]),
                    "preco": Decimal(dados["preco"]),
                    "quantidade_disponivel": dados["quantidade"],
                    "prazo_entrega_dias": 2,
                    "status": "PUBLICADO",
                    "destaque": True,
                },
            )
            criados += int(criado)
            atualizados += int(not criado)
            self.stdout.write(f"{'Criado' if criado else 'Actualizado'}: {produto.titulo}")
        self.stdout.write(self.style.SUCCESS(f"Mercado de demonstração pronto: {criados} criados, {atualizados} actualizados."))
