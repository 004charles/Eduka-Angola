"""Cria obras próprias de demonstração para a Biblioteca Edukangola.

O conteúdo abaixo é original e serve apenas para demonstrar a experiência de
leitura gratuita da plataforma. O script pode ser executado várias vezes.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")

import django

django.setup()

from django.utils import timezone

from biblioteca.models import Autor, Livro


BOOKS = [
    {
        "author": {"nome": "Edukangola Editorial", "biografia": "Núcleo editorial da Edukangola dedicado a materiais de aprendizagem acessíveis e contextualizados para Angola.", "pais": "Angola"},
        "titulo": "O Próximo Passo", "subtitulo": "Um guia prático para aprender, colaborar e avançar", "categoria": "Gestão e Negócios", "temas": "Carreira, Liderança, Comunidade", "paginas": 64,
        "descricao_curta": "Pequenas decisões de aprendizagem que fortalecem a carreira e a comunidade.",
        "sinopse": "Este ensaio breve apresenta uma forma simples de transformar curiosidade em progresso: observar o contexto, escolher uma competência útil, praticar com outras pessoas e partilhar o que se aprendeu.",
        "excerto": "O próximo passo não precisa de ser grande. Precisa de ser claro, possível e repetido.",
        "capa_url": "/media/biblioteca/capas/o-proximo-passo.jpg",
        "conteudo_leitura": "# O Próximo Passo\n\n## Começar pelo que está perto\n\nAprender não começa quando se encontra a ferramenta perfeita. Começa quando se reconhece uma necessidade concreta: comunicar melhor, organizar uma ideia, resolver um problema ou apoiar alguém da equipa. A primeira escolha é pequena: reservar tempo, fazer uma pergunta e praticar.\n\n## Uma competência por vez\n\nQuando tentamos aprender tudo ao mesmo tempo, a atenção dispersa-se. Escolha uma competência que tenha utilidade nesta semana. Escreva aquilo que quer conseguir fazer. Depois, transforme o objectivo em uma prática curta e repetível.\n\n## Aprender com outras pessoas\n\nUma comunidade cresce quando cada pessoa partilha uma descoberta útil. Explique o que aprendeu, peça uma opinião e aceite correcções. O conhecimento que circula torna-se mais forte e chega mais longe.\n\n## O compromisso final\n\nNo fim de cada semana, anote um avanço e um próximo passo. Não é uma medida de perfeição. É uma forma de tornar visível a caminhada.",
        "selecao_semana": True,
    },
    {
        "author": {"nome": "Edukangola Editorial", "biografia": "Núcleo editorial da Edukangola dedicado a materiais de aprendizagem acessíveis e contextualizados para Angola.", "pais": "Angola"},
        "titulo": "Dados que Contam Histórias", "subtitulo": "Fundamentos para ler informação com clareza", "categoria": "Tecnologia e Dados", "temas": "Dados, Tecnologia, Pensamento crítico", "paginas": 52,
        "descricao_curta": "Uma introdução leve para transformar números em perguntas melhores.",
        "sinopse": "Dados não são apenas tabelas. São sinais sobre pessoas, processos e escolhas. Este livro introduz perguntas, comparações e hábitos de verificação que ajudam a interpretar informação sem perder o contexto.",
        "excerto": "Antes de confiar num número, pergunte de onde ele veio e o que ficou de fora.",
        "capa_url": "/media/biblioteca/capas/dados-que-contam-historias.jpg",
        "conteudo_leitura": "# Dados que Contam Histórias\n\n## Um número é o início da pergunta\n\nUm valor isolado raramente explica uma realidade inteira. Para compreender um número, procure a comparação: com o mês anterior, com outro grupo, com uma meta ou com a experiência de quem vive aquele resultado.\n\n## Organizar antes de concluir\n\nComece por dar nomes claros às colunas, separar datas de texto e confirmar se os valores estão completos. Uma tabela simples e bem organizada permite descobrir padrões que uma lista confusa esconde.\n\n## Contar a história com cuidado\n\nUma boa explicação de dados mostra o que se sabe, o que ainda não se sabe e qual é a próxima pergunta. O objectivo não é impressionar. É ajudar alguém a decidir melhor.",
        "em_destaque": True,
    },
    {
        "author": {"nome": "Edukangola Editorial", "biografia": "Núcleo editorial da Edukangola dedicado a materiais de aprendizagem acessíveis e contextualizados para Angola.", "pais": "Angola"},
        "titulo": "Palavras que Abrem Portas", "subtitulo": "Comunicação profissional com presença", "categoria": "Idiomas e Comunicação", "temas": "Comunicação, Empregabilidade, Idiomas", "paginas": 48,
        "descricao_curta": "Ferramentas simples para se apresentar, escutar e comunicar com confiança.",
        "sinopse": "Comunicar bem não é falar mais. É preparar a mensagem, reconhecer quem escuta e escolher palavras que tornam a intenção compreensível. Esta leitura propõe exercícios curtos para entrevistas, reuniões e conversas profissionais.",
        "excerto": "Clareza é respeito pelo tempo de quem fala e de quem escuta.",
        "capa_url": "/media/biblioteca/capas/palavras-que-abrem-portas.jpg",
        "conteudo_leitura": "# Palavras que Abrem Portas\n\n## Preparar a intenção\n\nAntes de uma conversa importante, descreva numa frase aquilo que deseja alcançar. Pode ser apresentar uma ideia, pedir apoio ou resolver uma dúvida. Essa frase é a bússola da conversa.\n\n## Escutar para responder\n\nEscutar não é apenas esperar pela sua vez de falar. É observar as palavras, o tom e a dúvida que ainda não foi dita. Uma pergunta bem feita mostra atenção e cria espaço para uma resposta mais útil.\n\n## Praticar a presença\n\nFale devagar o suficiente para que a mensagem possa ser recebida. Use exemplos concretos. No fim, confirme o próximo passo. Comunicação profissional é também combinação de expectativas.",
    },
    {
        "author": {"nome": "Edukangola Editorial", "biografia": "Núcleo editorial da Edukangola dedicado a materiais de aprendizagem acessíveis e contextualizados para Angola.", "pais": "Angola"},
        "titulo": "Caderno de Ideias Visuais", "subtitulo": "Exercícios para observar, combinar e criar", "categoria": "Design e Criatividade", "temas": "Criatividade, Design, Projectos", "paginas": 56,
        "descricao_curta": "Um convite para desenvolver ideias com observação, contraste e prática.",
        "sinopse": "Criatividade é uma prática que pode ser treinada. A obra propõe exercícios de observação, combinação de referências e construção de alternativas para quem quer começar um projecto visual ou renovar uma ideia antiga.",
        "excerto": "Uma ideia ganha força quando encontra uma forma que outras pessoas conseguem ver.",
        "capa_url": "/media/biblioteca/capas/caderno-de-ideias-visuais.jpg",
        "conteudo_leitura": "# Caderno de Ideias Visuais\n\n## Olhar antes de criar\n\nA observação é matéria-prima. Repare em cores, materiais, percursos, palavras e gestos que se repetem no seu dia. Guarde aquilo que chama a atenção, mesmo quando ainda não sabe para que servirá.\n\n## Criar alternativas\n\nEm vez de procurar a primeira solução perfeita, faça três versões. Mude a ordem, o contraste, o formato ou a escala. Comparar alternativas torna mais fácil perceber o que cada escolha comunica.\n\n## Mostrar cedo\n\nUma ideia só melhora quando encontra uma pessoa real. Mostre um rascunho, faça uma pergunta específica e ouça a reacção. O feedback não decide por si; ajuda a ver o que ainda está invisível.",
    },
    {
        "author": {"nome": "Edukangola Editorial", "biografia": "Núcleo editorial da Edukangola dedicado a materiais de aprendizagem acessíveis e contextualizados para Angola.", "pais": "Angola"},
        "titulo": "Ritmo para Aprender", "subtitulo": "Hábitos de estudo e bem-estar no dia a dia", "categoria": "Saúde e Bem-estar", "temas": "Bem-estar, Estudo, Hábitos", "paginas": 44,
        "descricao_curta": "Uma abordagem humana para criar constância sem abandonar o descanso.",
        "sinopse": "Aprender exige energia, tempo e recuperação. Este guia apresenta pequenas rotinas para planear o estudo, fazer pausas conscientes e reconhecer que descanso também é parte do progresso.",
        "excerto": "A constância não é fazer tudo. É voltar ao que importa com um ritmo possível.",
        "capa_url": "/media/biblioteca/capas/ritmo-para-aprender.jpg",
        "conteudo_leitura": "# Ritmo para Aprender\n\n## Um tempo que cabe no dia\n\nUma rotina sustentável começa pequena. Escolha um período que caiba no seu dia e proteja-o como um encontro consigo. Vinte minutos de atenção real podem valer mais do que uma tarde inteira de interrupções.\n\n## Pausar também é aprender\n\nO descanso permite consolidar o que foi estudado. Levante-se, beba água, respire e volte com uma pergunta simples: o que compreendi até agora? A pausa não interrompe o processo; organiza-o.\n\n## Registar o percurso\n\nNo fim de uma sessão, anote uma ideia, uma dúvida e uma acção para amanhã. Assim, recomeçar deixa de exigir esforço para lembrar onde parou.",
    },
]


def run():
    for item in BOOKS:
        author_data = item.pop("author")
        author, _ = Autor.objects.get_or_create(nome=author_data["nome"], defaults=author_data)
        Livro.objects.update_or_create(
            titulo=item["titulo"],
            defaults={
                **item,
                "autor": author,
                "editora": "Edukangola Editorial",
                "formato": Livro.FORMATO_DIGITAL,
                "gratuito": True,
                "direitos_confirmados": True,
                "estado": Livro.ESTADO_PUBLICADO,
                "publicado_em": timezone.now(),
            },
        )
    print(f"Biblioteca pronta: {Livro.objects.filter(estado=Livro.ESTADO_PUBLICADO).count()} livros publicados.")


if __name__ == "__main__":
    run()
