import re

input_file = "gestoreduka/templates/gestoreduka template/metronic/tailwind/demo4/index.html"
output_file = "gestoreduka/templates/gestor_base.html"

with open(input_file, "r") as f:
    html = f.read()

# Substituir rotas de assets
html = re.sub(r'href="\.\./dist/assets/(.*?)"', r'href="{% static \'metronic/assets/\1\' %}"', html)
html = re.sub(r'src="\.\./dist/assets/(.*?)"', r'src="{% static \'metronic/assets/\1\' %}"', html)

# Encontrar o <main> e substituir o conteúdo
start_main = html.find('<main class="grow" role="content">')
end_main = html.find('</main>')

if start_main != -1 and end_main != -1:
    top_part = html[:start_main]
    bottom_part = html[end_main + 7:]
    
    # Substituições em português no top_part (header e sidebar)
    top_part = top_part.replace('>Dashboard<', '>Painel de Controlo<')
    top_part = top_part.replace('>Profile<', '>Perfil<')
    top_part = top_part.replace('>Account<', '>Conta<')
    top_part = top_part.replace('>Network<', '>Rede<')
    top_part = top_part.replace('Metronic - Tailwind CSS Light Sidebar', 'Eduka - Centro de Formação')
    top_part = top_part.replace('Quick Links', 'Links Rápidos')
    top_part = top_part.replace('Search', 'Pesquisar')
    top_part = top_part.replace('Notifications', 'Notificações')
    top_part = top_part.replace('Settings', 'Configurações')
    
    final_html = "{% load static %}\n" + top_part + """<main class="grow" role="content">
    <div class="kt-container-fluid pt-5">
        {% block content %}{% endblock %}
    </div>
</main>\n""" + bottom_part

    with open(output_file, "w") as out:
        out.write(final_html)
    print("Success: gestor_base.html criado.")
else:
    print("Error: Could not find main container")
