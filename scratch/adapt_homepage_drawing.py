import re

def adapt_drawing():
    template_content = """{% load static %}
{% load i18n %}
{% load curso_filters %}
<!DOCTYPE html>
<html lang="{{ request.LANGUAGE_CODE|default:'pt' }}">
<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>EdukAngola | O mercado de cursos e centros de formação de Angola</title>
    <meta name="description" content="A maior plataforma de cursos e centros de formação em Angola. Encontre especializações, cursos técnicos e formação online de elite.">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    
    <!-- Ícones e CSS Base da Plataforma -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/feather-icons/dist/feather.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    
    {% include 'include/css.html' %}
    
    <style>
      :root {
        --color-primary: #2f57ef;
        --color-heading: #192335;
        --color-body: #6b7385;
        --color-border: #e6e3f1;
        --color-bg: #F5F7FA;
      }
      body {
        background-color: #F5F7FA !important;
        font-family: "IBM Plex Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #192335;
        -webkit-font-smoothing: antialiased;
      }
      a { color: #192335; text-decoration: none; }
      a:hover { color: #2f57ef; }
    </style>
</head>
<body class="rbt-header-sticky">

    {% include 'include/header.html' %}

    <main class="rbt-main-wrapper" style="background: #F5F7FA; padding-bottom: 60px;">
        <div class="container" style="max-width: 1400px;">

            <!-- SUB NAV CATEGORIAS -->
            <div style="display: flex; align-items: center; gap: 26px; padding: 12px 24px; background: #ffffff; border: 1px solid #e6e3f1; border-radius: 12px; margin-top: 20px; font-size: 13.5px; overflow-x: auto; white-space: nowrap;">
                <a href="{% url 'todo_curso' %}" style="display: flex; align-items: center; gap: 7px; font-weight: 600; color: #2f57ef; flex-shrink: 0;"><i class="feather-grid"></i> Todas as categorias</a>
                <span style="width: 1px; height: 18px; background: #e6e3f1; flex-shrink: 0"></span>
                {% for cat in categorias|slice:":8" %}
                    <a href="{% url 'cursos_por_categoria' cat.slug %}" style="color: #4A463C; flex-shrink: 0">{{ cat.nome }}</a>
                {% endfor %}
                <span style="width: 1px; height: 18px; background: #e6e3f1; flex-shrink: 0"></span>
                <a href="{% url 'todo_curso' %}" style="color: #4A463C; font-weight: 600; flex-shrink: 0">Internacional</a>
                <a href="{% url 'buscar_cursos' %}?desconto=1" style="margin-left: auto; color: #2f57ef; font-weight: 600; flex-shrink: 0">Bolsas e descontos</a>
            </div>

            <!-- HERO DRAWING LAYOUT -->
            <div style="padding: 20px 0 0; display: grid; grid-template-columns: 1fr 336px; gap: 16px">
                <div style="min-height: 340px; border-radius: 14px; background: linear-gradient(135deg, #020c26 0%, #1e3bb3 60%, #2f57ef 100%); padding: 40px 44px; display: flex; flex-direction: row; align-items: center; justify-content: space-between; position: relative; overflow: hidden; color: #ffffff;">
                    <div style="position: relative; max-width: 480px; z-index: 2;">
                        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: #ffffff; background: rgba(255,255,255,0.2); padding: 4px 9px; border-radius: 999px; display: inline-block; margin-bottom: 18px">Publicidade · Jovem Digital</div>
                        <h2 style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 38px; letter-spacing: -0.035em; line-height: 1.05; color: #ffffff; margin: 0 0 12px">Bolsas de 50% em cursos de tecnologia</h2>
                        <p style="font-size: 15.5px; line-height: 1.55; color: rgba(255,255,255,0.85); margin: 0 0 24px;">Até 30 de Setembro, em centros de Luanda, Benguela e Huambo. Vagas limitadas por turma.</p>
                        <a href="{% url 'buscar_cursos' %}?q=tecnologia" class="rbt-btn btn-white radius-round">Ver bolsas</a>
                    </div>
                    <div style="width: 220px; height: 250px; border-radius: 14px; overflow: hidden; flex-shrink: 0; box-shadow: 0 10px 25px rgba(0,0,0,0.3); border: 2px solid rgba(255,255,255,0.25); margin-left: 20px;">
                        <img src="{% static 'assets/images/banner/hero_bolsas_photo.png' %}" alt="Bolsas de Tecnologia" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                </div>
                <div style="display: grid; grid-template-rows: 1fr 1fr; gap: 16px">
                    <div style="border-radius: 14px; background: #ffffff; border: 1px solid #e6e3f1; padding: 22px 24px; display: flex; flex-direction: column; justify-content: center">
                        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 9.5px; letter-spacing: 0.12em; text-transform: uppercase; color: #2f57ef; margin-bottom: 10px">Destaque</div>
                        <div style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 20px; letter-spacing: -0.025em; line-height: 1.15; margin-bottom: 8px; color: #192335;">Inglês em 3 meses, com certificado internacional</div>
                        <div style="font-size: 13px; color: #6b7385; margin-bottom: 14px">British Language Centre · Luanda</div>
                        <a href="{% url 'buscar_cursos' %}?q=ingles" style="font-size: 13px; font-weight: 600; color: #2f57ef; align-self: flex-start;">Saber mais →</a>
                    </div>
                    <div style="border-radius: 14px; background: #ffffff; border: 1px solid #e6e3f1; padding: 22px 24px; display: flex; flex-direction: column; justify-content: center">
                        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 9.5px; letter-spacing: 0.12em; text-transform: uppercase; color: #3EB75E; margin-bottom: 10px">Facilidade</div>
                        <div style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 20px; letter-spacing: -0.025em; line-height: 1.15; margin-bottom: 8px; color: #192335;">Pague o seu curso em 6 prestações sem juros</div>
                        <div style="font-size: 13px; color: #6b7385; margin-bottom: 14px">Disponível em {{ centros.count|default:"68" }} centros parceiros</div>
                        <a href="{% url 'faq' %}" style="font-size: 13px; font-weight: 600; color: #3EB75E; align-self: flex-start;">Como funciona →</a>
                    </div>
                </div>
            </div>

            <!-- 8 NUMBERED CATEGORY CARDS (01, 02... 08) -->
            <div style="padding: 28px 0 0">
                <div style="display: grid; grid-template-columns: repeat(8, 1fr); gap: 10px">
                    {% for cat in categorias|slice:":8" %}
                        <a href="{% url 'cursos_por_categoria' cat.slug %}" style="background: #ffffff; border: 1px solid #e6e3f1; border-radius: 10px; padding: 14px 12px; display: block; text-align: center">
                            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #2f57ef; margin-bottom: 10px">0{{ forloop.counter }}</div>
                            <div style="font-family: Archivo, sans-serif; font-weight: 600; font-size: 13.5px; line-height: 1.2; color: #192335;">{{ cat.nome }}</div>
                            <div style="font-size: 11.5px; color: #6b7385; margin-top: 3px">{{ cat.num_cursos|default:"0" }}</div>
                        </a>
                    {% endfor %}
                </div>
            </div>

            <!-- CURSOS EM DESTAQUE -->
            <div style="padding: 44px 0 16px; display: flex; align-items: flex-end; justify-content: space-between">
                <div>
                    <h2 style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 30px; letter-spacing: -0.03em; margin: 0; line-height: 1.05; color: #192335;">Cursos em destaque</h2>
                    <div style="font-size: 13.5px; color: #6b7385; margin-top: 6px">{{ cursos_destaque.count|default:"1 248" }} cursos com inscrições abertas · actualizado hoje</div>
                </div>
                <div style="display: flex; align-items: center; gap: 8px">
                    <a href="{% url 'todo_curso' %}" style="font-size: 13px; font-weight: 600; color: #2f57ef;">Ver todos →</a>
                </div>
            </div>

            <!-- CURSOS GRID DRAWING STYLE -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px">
                {% for curso in cursos_destaque|slice:":8" %}
                    <a href="{% url 'curso_detalhe' curso.id %}" style="background: #ffffff; border: 1px solid #e6e3f1; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; text-decoration: none;">
                        <div style="height: 140px; background: #e2e8f0; border-bottom: 1px solid #e6e3f1; position: relative">
                            {% if curso.imagem %}
                                <img src="{{ curso.imagem.url }}" alt="{{ curso.titulo }}" style="width:100%; height:100%; object-fit:cover;" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&auto=format&fit=crop&q=80';">
                            {% else %}
                                <img src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&auto=format&fit=crop&q=80" alt="{{ curso.titulo }}" style="width:100%; height:100%; object-fit:cover;">
                            {% endif %}
                            <div style="position: absolute; top: 10px; left: 10px; display: flex; gap: 6px">
                                <span style="font-size: 10.5px; font-weight: 600; padding: 4px 9px; border-radius: 999px; background: {% if curso.modalidade == 'ONLINE' %}#DCEAE6; color: #1F5F55{% else %}#e0e7ff; color: #2f57ef{% endif %}">
                                    {{ curso.get_modalidade_display|default:curso.modalidade|default:"Presencial" }}
                                </span>
                                {% if curso.preco_promocional %}
                                    <span style="font-size: 10.5px; font-weight: 700; padding: 4px 9px; border-radius: 999px; background: #FF0003; color: #ffffff">-25%</span>
                                {% endif %}
                            </div>
                        </div>
                        <div style="padding: 16px; display: flex; flex-direction: column; flex: 1">
                            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 0.07em; text-transform: uppercase; color: #2f57ef">{{ curso.categoria.nome }}</div>
                            <div style="font-family: Archivo, sans-serif; font-weight: 600; font-size: 16px; letter-spacing: -0.02em; line-height: 1.25; margin: 7px 0 6px; color: #192335;">{{ curso.titulo }}</div>
                            <div style="font-size: 12.5px; color: #6b7385; margin-bottom: 10px">{{ curso.centro.nome }}</div>
                            <div style="display: flex; align-items: center; gap: 8px; font-size: 11.5px; color: #6b7385; margin-bottom: 14px">
                                <span style="color: #ff9d2d; font-weight: 600"><i class="fas fa-star me-1"></i>4.8</span>
                                <span>(312)</span>
                                <span style="color: #e6e3f1">·</span>
                                <span>{{ curso.duracao|default:"6 meses" }}</span>
                            </div>
                            <div style="display: flex; align-items: baseline; gap: 8px; margin-top: auto; padding-top: 12px; border-top: 1px solid #e6e3f1">
                                <span style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 17px; color: #192335;">
                                    {% if curso.is_gratuito %}Gratuito{% else %}{{ curso.preco|floatformat:0 }} Kz{% endif %}
                                </span>
                                {% if curso.preco_promocional %}
                                    <span style="font-size: 12.5px; color: #94a3b8; text-decoration: line-through">{{ curso.preco_promocional|floatformat:0 }} Kz</span>
                                {% endif %}
                                <span style="margin-left: auto; font-size: 12px; font-weight: 600; color: #2f57ef">Inscrever →</span>
                            </div>
                        </div>
                    </a>
                {% endfor %}
            </div>

            <!-- BANNER EMPRESAS -->
            <div style="padding: 32px 0 0">
                <div style="border-radius: 14px; background: linear-gradient(135deg, #020c26 0%, #192335 100%); border: 1px solid #e6e3f1; padding: 26px 32px; display: flex; align-items: center; gap: 32px; color: #ffffff;">
                    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 9.5px; letter-spacing: 0.12em; text-transform: uppercase; color: #ff9d2d; border: 1px solid rgba(255,255,255,0.2); padding: 4px 9px; border-radius: 999px; flex-shrink: 0">Publicidade</div>
                    <div style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 24px; letter-spacing: -0.03em; line-height: 1.2">Formação para empresas: forme a sua equipa com desconto por volume</div>
                    <div style="font-size: 13.5px; color: rgba(255,255,255,0.8); max-width: 260px; flex-shrink: 0">A partir de 10 colaboradores, em qualquer centro parceiro.</div>
                    <a href="{% url 'contato' %}" class="rbt-btn btn-gradient radius-round" style="margin-left: auto; flex-shrink: 0;">Pedir proposta</a>
                </div>
            </div>

            <!-- MAIS PROCURADOS ESTA SEMANA (01 A 06) -->
            <div style="padding: 44px 0 16px; display: flex; align-items: flex-end; justify-content: space-between">
                <div>
                    <h2 style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 30px; letter-spacing: -0.03em; margin: 0; line-height: 1.05; color: #192335;">Mais procurados esta semana</h2>
                    <div style="font-size: 13.5px; color: #6b7385; margin-top: 6px">Ranking por número de inscrições confirmadas</div>
                </div>
                <a href="{% url 'todo_curso' %}" style="font-size: 13px; font-weight: 600; color: #2f57ef;">Ver o top 50 →</a>
            </div>

            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px">
                {% for curso in cursos_destaque|slice:":6" %}
                    <a href="{% url 'curso_detalhe' curso.id %}" style="background: #ffffff; border: 1px solid #e6e3f1; border-radius: 12px; padding: 16px 18px; display: flex; align-items: center; gap: 16px">
                        <span style="font-family: Archivo, sans-serif; font-weight: 800; font-size: 26px; letter-spacing: -0.04em; color: #cbd5e1; flex-shrink: 0; width: 38px">0{{ forloop.counter }}</span>
                        <div style="flex: 1; min-width: 0">
                            <div style="font-family: Archivo, sans-serif; font-weight: 600; font-size: 15px; letter-spacing: -0.015em; line-height: 1.25; color: #192335;">{{ curso.titulo }}</div>
                            <div style="font-size: 12px; color: #6b7385; margin-top: 3px">{{ curso.centro.nome }}</div>
                        </div>
                        <span style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 14.5px; color: #2f57ef; flex-shrink: 0">
                            {% if curso.is_gratuito %}Gratuito{% else %}{{ curso.preco|floatformat:0 }} Kz{% endif %}
                        </span>
                    </a>
                {% endfor %}
            </div>

            <!-- CATEGORIA 01 TECNOLOGIA -->
            <div style="padding: 48px 0 16px; display: flex; align-items: flex-end; justify-content: space-between">
                <div>
                    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10.5px; letter-spacing: 0.1em; text-transform: uppercase; color: #2f57ef; margin-bottom: 8px">Categoria 01</div>
                    <h2 style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 30px; letter-spacing: -0.03em; margin: 0; line-height: 1.05; color: #192335;">Tecnologia e Informática</h2>
                </div>
                <a href="{% url 'buscar_cursos' %}?q=tecnologia" style="font-size: 13px; font-weight: 600; color: #2f57ef;">Ver os 312 cursos →</a>
            </div>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px">
                {% for curso in cursos_destaque|slice:":4" %}
                    <a href="{% url 'curso_detalhe' curso.id %}" style="background: #ffffff; border: 1px solid #e6e3f1; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column">
                        <div style="height: 110px; background: #e2e8f0; border-bottom: 1px solid #e6e3f1; position: relative">
                            <img src="https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&auto=format&fit=crop&q=80" alt="{{ curso.titulo }}" style="width:100%; height:100%; object-fit:cover;">
                        </div>
                        <div style="padding: 14px 16px 16px; display: flex; flex-direction: column; flex: 1">
                            <div style="font-family: Archivo, sans-serif; font-weight: 600; font-size: 15px; letter-spacing: -0.02em; line-height: 1.25; margin-bottom: 5px; color: #192335;">{{ curso.titulo }}</div>
                            <div style="font-size: 12px; color: #6b7385; margin-bottom: 9px">{{ curso.centro.nome }}</div>
                            <div style="display: flex; align-items: baseline; gap: 7px; margin-top: auto; padding-top: 11px; border-top: 1px solid #e6e3f1">
                                <span style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 15.5px; color: #192335;">180 000 Kz</span>
                                <span style="margin-left: auto; font-size: 11.5px; font-weight: 600; color: #2f57ef">Inscrever →</span>
                            </div>
                        </div>
                    </a>
                {% endfor %}
            </div>

            <!-- CATEGORIA 02 IDIOMAS -->
            <div style="padding: 48px 0 16px; display: flex; align-items: flex-end; justify-content: space-between">
                <div>
                    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10.5px; letter-spacing: 0.1em; text-transform: uppercase; color: #2f57ef; margin-bottom: 8px">Categoria 02</div>
                    <h2 style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 30px; letter-spacing: -0.03em; margin: 0; line-height: 1.05; color: #192335;">Idiomas</h2>
                </div>
                <a href="{% url 'buscar_cursos' %}?q=ingles" style="font-size: 13px; font-weight: 600; color: #2f57ef;">Ver os 164 cursos →</a>
            </div>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px">
                {% for curso in cursos_destaque|slice:":4" %}
                    <a href="{% url 'curso_detalhe' curso.id %}" style="background: #ffffff; border: 1px solid #e6e3f1; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column">
                        <div style="height: 110px; background: #e2e8f0; border-bottom: 1px solid #e6e3f1; position: relative">
                            <img src="https://images.unsplash.com/photo-1543269865-cbf427effbad?w=600&auto=format&fit=crop&q=80" alt="{{ curso.titulo }}" style="width:100%; height:100%; object-fit:cover;">
                        </div>
                        <div style="padding: 14px 16px 16px; display: flex; flex-direction: column; flex: 1">
                            <div style="font-family: Archivo, sans-serif; font-weight: 600; font-size: 15px; letter-spacing: -0.02em; line-height: 1.25; margin-bottom: 5px; color: #192335;">Curso de Inglês Intensivo B2</div>
                            <div style="font-size: 12px; color: #6b7385; margin-bottom: 9px">British Language Centre</div>
                            <div style="display: flex; align-items: baseline; gap: 7px; margin-top: auto; padding-top: 11px; border-top: 1px solid #e6e3f1">
                                <span style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 15.5px; color: #192335;">95 000 Kz</span>
                                <span style="margin-left: auto; font-size: 11.5px; font-weight: 600; color: #2f57ef">Inscrever →</span>
                            </div>
                        </div>
                    </a>
                {% endfor %}
            </div>

            <!-- NOVOS NA PLATAFORMA -->
            <div style="padding: 48px 0 16px; display: flex; align-items: flex-end; justify-content: space-between">
                <div>
                    <h2 style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 30px; letter-spacing: -0.03em; margin: 0; line-height: 1.05; color: #192335;">Novos na plataforma</h2>
                    <div style="font-size: 13.5px; color: #6b7385; margin-top: 6px">Publicados nos últimos 14 dias</div>
                </div>
                <a href="{% url 'todo_curso' %}" style="font-size: 13px; font-weight: 600; color: #2f57ef;">Ver novidades →</a>
            </div>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px">
                {% for curso in cursos_destaque|slice:":4" %}
                    <a href="{% url 'curso_detalhe' curso.id %}" style="background: #ffffff; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 18px; display: flex; flex-direction: column">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px">
                            <span style="font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 999px; background: #020c26; color: #ff9d2d">NOVO</span>
                            <span style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 0.07em; text-transform: uppercase; color: #2f57ef">{{ curso.categoria.nome }}</span>
                        </div>
                        <div style="font-family: Archivo, sans-serif; font-weight: 600; font-size: 15.5px; letter-spacing: -0.02em; line-height: 1.25; margin-bottom: 6px; color: #192335;">{{ curso.titulo }}</div>
                        <div style="font-size: 12px; color: #6b7385; margin-bottom: 6px">{{ curso.centro.nome }}</div>
                        <div style="display: flex; align-items: baseline; margin-top: auto; padding-top: 11px; border-top: 1px solid #e6e3f1">
                            <span style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 15.5px; color: #192335;">
                                {% if curso.is_gratuito %}Gratuito{% else %}{{ curso.preco|floatformat:0 }} Kz{% endif %}
                            </span>
                            <span style="margin-left: auto; font-size: 11.5px; font-weight: 600; color: #2f57ef">Inscrever →</span>
                        </div>
                    </a>
                {% endfor %}
            </div>

            <!-- INTERNACIONAL -->
            <div style="margin: 56px 0 0; padding: 44px; background: #ffffff; border-radius: 16px; border: 1px solid #e6e3f1;">
                <div style="display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 20px">
                    <div>
                        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10.5px; letter-spacing: 0.1em; text-transform: uppercase; color: #2f57ef; margin-bottom: 8px">Internacional</div>
                        <h2 style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 30px; letter-spacing: -0.03em; margin: 0; line-height: 1.05; color: #192335;">Cursos de instituições estrangeiras</h2>
                        <div style="font-size: 13.5px; color: #6b7385; margin-top: 6px">Estuda online a partir de Angola ou candidata-te a vagas presenciais no estrangeiro. Preços convertidos a Kz.</div>
                    </div>
                    <a href="{% url 'todo_curso' %}" style="font-size: 13px; font-weight: 600; color: #2f57ef;">Ver os 214 cursos internacionais →</a>
                </div>

                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px">
                    {% for curso in cursos_destaque|slice:":4" %}
                        <a href="{% url 'curso_detalhe' curso.id %}" style="background: #F5F7FA; border: 1px solid #e6e3f1; border-radius: 12px; padding: 18px; display: flex; flex-direction: column">
                            <div style="display: flex; align-items: center; gap: 9px; margin-bottom: 13px">
                                <span style="font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 500; background: #020c26; color: #ffffff; padding: 4px 8px; border-radius: 5px">PT</span>
                                <span style="font-size: 12px; color: #6b7385">Portugal</span>
                                <span style="margin-left: auto; font-size: 10px; font-weight: 600; padding: 3px 8px; border-radius: 999px; background: #DCEAE6; color: #1F5F55">Online</span>
                            </div>
                            <div style="font-family: Archivo, sans-serif; font-weight: 600; font-size: 15.5px; letter-spacing: -0.02em; line-height: 1.25; margin-bottom: 6px; color: #192335;">Pós-Graduação em Gestão de Projetos</div>
                            <div style="font-size: 12px; color: #6b7385; margin-bottom: 10px">Universidade de Lisboa · 1 ano</div>
                            <div style="margin-top: auto; padding-top: 12px; border-top: 1px solid #e6e3f1">
                                <div style="display: flex; align-items: baseline">
                                    <span style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 15.5px; color: #192335;">1 200 €</span>
                                    <span style="margin-left: auto; font-size: 11.5px; font-weight: 600; color: #2f57ef">Candidatar →</span>
                                </div>
                                <div style="font-size: 11px; color: #94a3b8; margin-top: 3px">~ 1.100.000 Kz</div>
                            </div>
                        </a>
                    {% endfor %}
                </div>
            </div>

            <!-- CENTROS DE FORMAÇÃO -->
            <div style="padding: 44px 0 16px; display: flex; align-items: flex-end; justify-content: space-between">
                <div>
                    <h2 style="font-family: Archivo, sans-serif; font-weight: 700; font-size: 30px; letter-spacing: -0.03em; margin: 0; line-height: 1.05; color: #192335;">Centros de formação</h2>
                    <div style="font-size: 13.5px; color: #6b7385; margin-top: 6px">{{ centros.count|default:"142" }} instituições certificadas em Angola</div>
                </div>
                <a href="{% url 'lista_centros' %}" style="font-size: 13px; font-weight: 600; color: #2f57ef;">Ver todos os centros →</a>
            </div>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px">
                {% for ct in centros|slice:":8" %}
                    <a href="{% url 'cursos_por_centro' ct.id %}" style="background: #ffffff; border: 1px solid #e6e3f1; border-radius: 12px; padding: 18px; display: flex; flex-direction: column">
                        <div style="display: flex; align-items: center; gap: 11px; margin-bottom: 14px">
                            <div style="width: 44px; height: 44px; border-radius: 9px; background: #F5F7FA; border: 1px solid #e6e3f1; display: flex; align-items: center; justify-content: center; font-family: Archivo, sans-serif; font-weight: 700; font-size: 16px; color: #2f57ef; flex-shrink: 0; overflow: hidden;">
                                {% if ct.perfil.imagem %}
                                    <img src="{{ ct.perfil.imagem.url }}" alt="{{ ct.nome }}" style="width: 100%; height: 100%; object-fit: cover;">
                                {% else %}
                                    {{ ct.nome|slice:":2"|upper }}
                                {% endif %}
                            </div>
                            <div>
                                <div style="font-family: Archivo, sans-serif; font-weight: 600; font-size: 14.5px; color: #192335; line-height: 1.2">{{ ct.nome }}</div>
                                <div style="font-size: 12px; color: #6b7385; margin-top: 2px"><i class="feather-map-pin me-1"></i>{{ ct.provincia|default:"Luanda" }}</div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: auto; padding-top: 12px; border-top: 1px solid #e6e3f1; font-size: 12px; color: #6b7385">
                            <span>{{ ct.curso_set.count|default:"10" }} cursos</span>
                            <span style="color: #ff9d2d; font-weight: 600"><i class="fas fa-star me-1"></i>4.8</span>
                        </div>
                    </a>
                {% endfor %}
            </div>

            <div style="display: flex; justify-content: center; margin-top: 28px; margin-bottom: 40px;">
                <a href="{% url 'lista_centros' %}" class="rbt-btn btn-border radius-round">Carregar mais centros</a>
            </div>

        </div>
    </main>

    {% include 'include/footer.html' %}
    {% include 'include/java.html' %}

</body>
</html>
"""
    with open('core/templates/core/index.html', 'w', encoding='utf-8') as f:
        f.write(template_content)
    print("Writing completed successfully!")

if __name__ == "__main__":
    adapt_drawing()
