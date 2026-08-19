from django.db import migrations


PLANS = [
    {
        "nome": "Essencial",
        "descricao": "Para centros que querem criar uma presença pública e começar a receber pedidos de alunos.",
        "preco": "0.00",
        "limite_cursos": 5,
        "alcance_km": 30,
        "selo_verificacao": False,
        "prioridade_busca": 1,
        "destaque_home": False,
        "acesso_relatorios": False,
        "permite_inscricao_manual": False,
        "permite_gerar_certificado": False,
        "permite_cursos_video": False,
        "limite_cursos_video": 0,
        "ativo": True,
    },
    {
        "nome": "Crescimento",
        "descricao": "Para centros em expansão que precisam de catálogo maior e mais controlo sobre inscrições.",
        "preco": "15000.00",
        "limite_cursos": 20,
        "alcance_km": 100,
        "selo_verificacao": False,
        "prioridade_busca": 4,
        "destaque_home": False,
        "acesso_relatorios": False,
        "permite_inscricao_manual": True,
        "permite_gerar_certificado": False,
        "permite_cursos_video": False,
        "limite_cursos_video": 0,
        "ativo": True,
    },
    {
        "nome": "Profissional",
        "descricao": "Para centros consolidados que combinam formação presencial, vídeo e acompanhamento de resultados.",
        "preco": "30000.00",
        "limite_cursos": 50,
        "alcance_km": 250,
        "selo_verificacao": True,
        "prioridade_busca": 8,
        "destaque_home": False,
        "acesso_relatorios": True,
        "permite_inscricao_manual": True,
        "permite_gerar_certificado": True,
        "permite_cursos_video": True,
        "limite_cursos_video": 20,
        "ativo": True,
    },
    {
        "nome": "Rede",
        "descricao": "Para instituições com várias ofertas e ambição nacional de descoberta e crescimento.",
        "preco": "55000.00",
        "limite_cursos": 150,
        "alcance_km": 1000,
        "selo_verificacao": True,
        "prioridade_busca": 12,
        "destaque_home": True,
        "acesso_relatorios": True,
        "permite_inscricao_manual": True,
        "permite_gerar_certificado": True,
        "permite_cursos_video": True,
        "limite_cursos_video": 50,
        "ativo": True,
    },
]


def seed_four_center_plans(apps, schema_editor):
    Plano = apps.get_model("planos", "Plano")

    for values in PLANS:
        defaults = {key: value for key, value in values.items() if key != "nome"}
        Plano.objects.update_or_create(nome=values["nome"], defaults=defaults)

    Plano.objects.filter(nome="Demonstração Integral").update(ativo=False)


def unseed_four_center_plans(apps, schema_editor):
    Plano = apps.get_model("planos", "Plano")
    Plano.objects.filter(nome__in=[plan["nome"] for plan in PLANS]).delete()
    Plano.objects.filter(nome="Demonstração Integral").update(ativo=True)


class Migration(migrations.Migration):
    dependencies = [("planos", "0004_plano_limite_cursos_video_plano_permite_cursos_video")]

    operations = [migrations.RunPython(seed_four_center_plans, unseed_four_center_plans)]
