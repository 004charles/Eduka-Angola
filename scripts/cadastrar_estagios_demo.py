import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
import django

django.setup()

from django.utils.text import slugify
from estagio.models import AreaEstagio, Estagio
from gestoreduka.models import CentroDeFormacao

areas = [
    ("Tecnologia e Dados", "Desenvolvimento, suporte e análise de soluções digitais."),
    ("Gestão e Negócios", "Operações, atendimento, administração e apoio à gestão."),
    ("Design e Comunicação", "Criação visual, conteúdos e comunicação digital."),
    ("Saúde e Bem-estar", "Apoio, promoção de saúde e acompanhamento comunitário."),
    ("Construção e Manutenção", "Apoio técnico, obra, instalações e manutenção."),
]
area_map = {}
for nome, descricao in areas:
    area, _ = AreaEstagio.objects.get_or_create(
        slug=slugify(nome),
        defaults={"nome": nome, "descricao": descricao, "ativa": True},
    )
    area_map[nome] = area

centros = {centro.nome: centro for centro in CentroDeFormacao.objects.filter(ativo=True)}
necessarios = {
    "Centro Atlas Digital",
    "Centro Horizonte Profissional",
    "Instituto Kwanza Formação",
    "Escola Criativa do Lobito",
    "Academia Vida & Cuidado",
}
missing = sorted(necessarios - set(centros))
if missing:
    raise RuntimeError(f"Centros activos em falta: {', '.join(missing)}")

estagios = [
    {"titulo": "Assistente de Suporte Informático", "area": "Tecnologia e Dados", "centro": "Centro Atlas Digital", "modalidade": "presencial", "tipo_remuneracao": "bolsa_auxilio", "valor_remuneracao": 85000, "cidade": "Luanda", "provincia": "Luanda", "local_trabalho": "Mutamba, Luanda", "duracao_meses": 6, "carga_horaria_semanal": 30, "vagas_disponiveis": 2, "data_inicio": "2026-09-15", "data_fim": "2027-03-15", "data_limite_inscricao": "2026-09-05", "resumo": "Apoie a equipa na instalação, manutenção e atendimento técnico aos utilizadores.", "requisitos": "Conhecimentos básicos de informática, vontade de aprender e boa comunicação.", "competencias_desejadas": "Sistemas operativos, redes básicas e atendimento ao utilizador.", "beneficios": "Acompanhamento de um técnico sénior e certificado de participação.", "destaque": True},
    {"titulo": "Estágio em Análise de Dados", "area": "Tecnologia e Dados", "centro": "Centro Atlas Digital", "modalidade": "hibrido", "tipo_remuneracao": "remunerado", "valor_remuneracao": 120000, "cidade": "Luanda", "provincia": "Luanda", "local_trabalho": "Talatona, Luanda", "duracao_meses": 6, "carga_horaria_semanal": 25, "vagas_disponiveis": 1, "data_inicio": "2026-10-01", "data_fim": "2027-04-01", "data_limite_inscricao": "2026-09-20", "resumo": "Transforme dados operacionais em relatórios que apoiam decisões do centro.", "requisitos": "Formação ou experiência inicial em Excel, estatística ou programação.", "competencias_desejadas": "Excel, Power BI ou Python e pensamento analítico.", "beneficios": "Plano de acompanhamento, acesso a ferramentas e certificado.", "destaque": True},
    {"titulo": "Assistente de Gestão e Operações", "area": "Gestão e Negócios", "centro": "Centro Horizonte Profissional", "modalidade": "presencial", "tipo_remuneracao": "bolsa_auxilio", "valor_remuneracao": 90000, "cidade": "Benguela", "provincia": "Benguela", "local_trabalho": "Rua do Comércio, Benguela", "duracao_meses": 4, "carga_horaria_semanal": 30, "vagas_disponiveis": 2, "data_inicio": "2026-09-10", "data_fim": "2027-01-10", "data_limite_inscricao": "2026-08-31", "resumo": "Participe na organização de turmas, documentos e actividades administrativas.", "requisitos": "Organização, responsabilidade e conhecimentos básicos de ferramentas de escritório.", "competencias_desejadas": "Excel, comunicação profissional e gestão de prioridades.", "beneficios": "Mentoria de equipa e possibilidade de recomendação profissional.", "destaque": True},
    {"titulo": "Estágio de Atendimento ao Cliente", "area": "Gestão e Negócios", "centro": "Instituto Kwanza Formação", "modalidade": "presencial", "tipo_remuneracao": "nao_remunerado", "valor_remuneracao": None, "cidade": "Huambo", "provincia": "Huambo", "local_trabalho": "Centro da cidade, Huambo", "duracao_meses": 3, "carga_horaria_semanal": 25, "vagas_disponiveis": 3, "data_inicio": "2026-09-20", "data_fim": "2026-12-20", "data_limite_inscricao": "2026-09-12", "resumo": "Acompanhe o atendimento aos alunos e ajude a melhorar a experiência no centro.", "requisitos": "Boa comunicação, empatia e domínio básico de português.", "competencias_desejadas": "Atendimento, organização e resolução de problemas.", "beneficios": "Formação prática e certificado de estágio.", "destaque": True},
    {"titulo": "Designer de Conteúdos Educativos", "area": "Design e Comunicação", "centro": "Escola Criativa do Lobito", "modalidade": "hibrido", "tipo_remuneracao": "bolsa_auxilio", "valor_remuneracao": 100000, "cidade": "Lobito", "provincia": "Benguela", "local_trabalho": "Lobito, Benguela", "duracao_meses": 5, "carga_horaria_semanal": 25, "vagas_disponiveis": 1, "data_inicio": "2026-10-05", "data_fim": "2027-03-05", "data_limite_inscricao": "2026-09-25", "resumo": "Crie materiais visuais para divulgar cursos e actividades de formação.", "requisitos": "Portefólio inicial ou formação em design e domínio de ferramentas digitais.", "competencias_desejadas": "Canva, Photoshop, composição e narrativa visual.", "beneficios": "Portefólio com projectos reais e acompanhamento criativo.", "destaque": True},
    {"titulo": "Estágio em Marketing Digital", "area": "Design e Comunicação", "centro": "Escola Criativa do Lobito", "modalidade": "remoto", "tipo_remuneracao": "beneficios", "valor_remuneracao": None, "cidade": "Lobito", "provincia": "Benguela", "local_trabalho": "Remoto, com reuniões semanais", "duracao_meses": 4, "carga_horaria_semanal": 20, "vagas_disponiveis": 2, "data_inicio": "2026-09-25", "data_fim": "2027-01-25", "data_limite_inscricao": "2026-09-15", "resumo": "Ajude a planear conteúdos e campanhas para alcançar novos alunos.", "requisitos": "Interesse por redes sociais, escrita e comunicação digital.", "competencias_desejadas": "Planeamento editorial, copywriting e métricas básicas.", "beneficios": "Acesso a workshops internos e orientação de marketing.", "destaque": False},
    {"titulo": "Apoio a Projectos de Saúde Comunitária", "area": "Saúde e Bem-estar", "centro": "Academia Vida & Cuidado", "modalidade": "presencial", "tipo_remuneracao": "bolsa_auxilio", "valor_remuneracao": 75000, "cidade": "Luanda", "provincia": "Luanda", "local_trabalho": "Maianga, Luanda", "duracao_meses": 6, "carga_horaria_semanal": 30, "vagas_disponiveis": 2, "data_inicio": "2026-09-18", "data_fim": "2027-03-18", "data_limite_inscricao": "2026-09-08", "resumo": "Apoie actividades de sensibilização e acompanhamento em saúde comunitária.", "requisitos": "Formação inicial em saúde, serviço social ou área relacionada.", "competencias_desejadas": "Empatia, registo de informação e trabalho em equipa.", "beneficios": "Supervisão de profissionais e certificado de participação.", "destaque": True},
    {"titulo": "Assistente de Cuidados e Bem-estar", "area": "Saúde e Bem-estar", "centro": "Academia Vida & Cuidado", "modalidade": "presencial", "tipo_remuneracao": "nao_remunerado", "valor_remuneracao": None, "cidade": "Luanda", "provincia": "Luanda", "local_trabalho": "Viana, Luanda", "duracao_meses": 3, "carga_horaria_semanal": 24, "vagas_disponiveis": 2, "data_inicio": "2026-10-12", "data_fim": "2027-01-12", "data_limite_inscricao": "2026-10-01", "resumo": "Acompanhe actividades de bem-estar e apoio a utentes em contexto supervisionado.", "requisitos": "Responsabilidade, disponibilidade e interesse por cuidados humanos.", "competencias_desejadas": "Comunicação, higiene e trabalho colaborativo.", "beneficios": "Aprendizagem prática supervisionada e declaração de participação.", "destaque": False},
    {"titulo": "Apoio Técnico de Manutenção", "area": "Construção e Manutenção", "centro": "Centro Horizonte Profissional", "modalidade": "presencial", "tipo_remuneracao": "bolsa_auxilio", "valor_remuneracao": 95000, "cidade": "Benguela", "provincia": "Benguela", "local_trabalho": "Zona Industrial, Benguela", "duracao_meses": 5, "carga_horaria_semanal": 30, "vagas_disponiveis": 2, "data_inicio": "2026-09-28", "data_fim": "2027-02-28", "data_limite_inscricao": "2026-09-18", "resumo": "Aprenda a apoiar equipas em manutenção preventiva e organização de ferramentas.", "requisitos": "Formação técnica inicial e atenção às regras de segurança.", "competencias_desejadas": "Leitura de instruções, ferramentas manuais e prevenção de riscos.", "beneficios": "Acompanhamento técnico e experiência em ambiente profissional.", "destaque": False},
    {"titulo": "Assistente de Instalações Eléctricas", "area": "Construção e Manutenção", "centro": "Instituto Kwanza Formação", "modalidade": "presencial", "tipo_remuneracao": "remunerado", "valor_remuneracao": 110000, "cidade": "Huambo", "provincia": "Huambo", "local_trabalho": "Pólo Técnico, Huambo", "duracao_meses": 6, "carga_horaria_semanal": 30, "vagas_disponiveis": 1, "data_inicio": "2026-10-20", "data_fim": "2027-04-20", "data_limite_inscricao": "2026-10-10", "resumo": "Apoie instalações e verificações eléctricas sob orientação de técnicos experientes.", "requisitos": "Formação básica em electricidade e cumprimento rigoroso das normas de segurança.", "competencias_desejadas": "Medição, cablagem e leitura de esquemas simples.", "beneficios": "Supervisão técnica, equipamentos de protecção e certificado.", "destaque": False},
]

for item in estagios:
    slug = slugify(item["titulo"])
    area_nome = item.pop("area")
    centro_nome = item.pop("centro")
    defaults = {
        **item,
        "area": area_map[area_nome],
        "centro_formacao": centros[centro_nome],
        "slug": slug,
        "descricao": item["resumo"] + " " + item["requisitos"],
        "ativo": True,
        "vagas_preenchidas": 0,
    }
    Estagio.objects.update_or_create(slug=slug, defaults=defaults)

print(f"ÁREAS_ACTIVAS={AreaEstagio.objects.filter(ativa=True).count()}")
print(f"ESTAGIOS_CRIADOS_OU_ACTUALIZADOS={len(estagios)}")
print(f"ESTAGIOS_ACTIVOS={Estagio.objects.filter(ativo=True).count()}")
for estagio in Estagio.objects.filter(slug__in=[slugify(item["titulo"]) for item in estagios]).order_by("id"):
    print(estagio.id, estagio.titulo, estagio.centro_formacao.nome, estagio.vagas_restantes)
