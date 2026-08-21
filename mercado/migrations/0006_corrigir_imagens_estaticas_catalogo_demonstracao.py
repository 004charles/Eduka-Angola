from django.db import migrations


LOJA_SLUG = "edukangola-mercado-demonstracao"

IMAGENS = {
    "Portátil Estudo 14": "/static/assets/images/product/mercado/portatil-estudo.webp",
    "Portátil Campus 15": "/static/assets/images/product/mercado/portatil-estudo.webp",
    "Portátil Essencial 14": "/static/assets/images/product/mercado/portatil-estudo.webp",
    "Caderno de Fundamentos de Informática": "/static/assets/images/product/mercado/livros-estudo.webp",
    "Guia de Matemática Essencial": "/static/assets/images/product/mercado/livros-estudo.webp",
    "Comunicação Profissional": "/static/assets/images/product/mercado/livros-estudo.webp",
    "Mochila Campus Verde 20L": "/static/assets/images/product/mercado/mochila-estudo.webp",
    "Mochila Estudo Urbana 18L": "/static/assets/images/product/mercado/mochila-estudo.webp",
    "Mochila Secure Laptop 22L": "/static/assets/images/product/mercado/mochila-estudo.webp",
}


def corrigir_imagens(apps, schema_editor):
    ProdutoMercado = apps.get_model("mercado", "ProdutoMercado")
    for titulo, imagem_url_publica in IMAGENS.items():
        ProdutoMercado.objects.filter(loja__slug=LOJA_SLUG, titulo=titulo).update(imagem_url_publica=imagem_url_publica)


class Migration(migrations.Migration):
    dependencies = [
        ("mercado", "0005_seed_catalogo_demonstracao_producao"),
    ]

    operations = [
        migrations.RunPython(corrigir_imagens, migrations.RunPython.noop),
    ]
