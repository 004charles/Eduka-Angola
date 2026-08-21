from django.db import migrations


def criar_categorias(apps, schema_editor):
    CategoriaMercado = apps.get_model("mercado", "CategoriaMercado")
    categorias = [
        ("Computadores", "computadores", "Computadores e tecnologia", 10),
        ("Livros físicos", "livros-fisicos", "Leitura e apoio ao estudo", 20),
        ("Cadernos e papelaria", "cadernos-e-papelaria", "Organização para estudar", 30),
        ("Mochilas", "mochilas", "Transporte e organização", 40),
        ("Calculadoras", "calculadoras", "Ferramentas para disciplinas técnicas", 50),
        ("Acessórios", "acessorios", "Acessórios úteis para aprendizagem", 60),
    ]
    for nome, slug, descricao, ordem in categorias:
        CategoriaMercado.objects.get_or_create(
            nome=nome,
            defaults={"slug": slug, "descricao": descricao, "ordem": ordem, "ativa": True},
        )


class Migration(migrations.Migration):
    dependencies = [("mercado", "0002_pedidomercado_estafeta_nome_and_more")]

    operations = [migrations.RunPython(criar_categorias, migrations.RunPython.noop)]
