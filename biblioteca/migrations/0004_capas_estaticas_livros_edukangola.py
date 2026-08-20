from django.db import migrations


BOOK_COVERS = {
    'o-proximo-passo': 'o-proximo-passo.jpg',
    'dados-que-contam-historias': 'dados-que-contam-historias.jpg',
    'palavras-que-abrem-portas': 'palavras-que-abrem-portas.jpg',
    'caderno-de-ideias-visuais': 'caderno-de-ideias-visuais.jpg',
    'ritmo-para-aprender': 'ritmo-para-aprender.jpg',
}


def set_static_book_covers(apps, schema_editor):
    Livro = apps.get_model('biblioteca', 'Livro')
    for slug, filename in BOOK_COVERS.items():
        Livro.objects.filter(slug=slug).update(
            capa='',
            capa_url=f'https://api.edukangola.com/static/assets/images/library/{filename}',
        )


class Migration(migrations.Migration):
    dependencies = [('biblioteca', '0003_bibliotecapessoal_pagina_leitura')]
    operations = [migrations.RunPython(set_static_book_covers, migrations.RunPython.noop)]
