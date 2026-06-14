import os, glob
for f in glob.glob('core/templates/**/*.html', recursive=True):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    new_content = content.replace('<body class="rbt-header-sticky">', '<body class="active-dark-mode rbt-header-sticky">').replace('<body>', '<body class="active-dark-mode">')
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
print('Done')
