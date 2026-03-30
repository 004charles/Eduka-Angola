import os

# Files to fix
files = [
    r'C:\Users\IT - Carlos - OX4\Documents\Eduka-Angola\usuarios\decorators.py',
    r'C:\Users\IT - Carlos - OX4\Documents\Eduka-Angola\cursos_app\views.py',
    r'C:\Users\IT - Carlos - OX4\Documents\Eduka-Angola\cursos_app\templates\curso_detalhe.html',
    r'C:\Users\IT - Carlos - OX4\Documents\Eduka-Angola\cursos_app\templates\cursos_app\ficha.html',
    r'C:\Users\IT - Carlos - OX4\Documents\Eduka-Angola\cursovideoapp\templates\cursos\detalhe.html',
]

for file_path in files:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Replace hardcoded path /auth/Login_aluno with /auth/login_aluno/
    # Note: adding trailing slash as per Django convention
    new_content = content.replace('/auth/Login_aluno', '/auth/login_aluno/')
    
    # 2. Replace URL name 'Login_aluno' with 'login_aluno'
    # This covers {% url 'Login_aluno' %}, redirect('Login_aluno'), and login_url='Login_aluno'
    new_content = new_content.replace("'Login_aluno'", "'login_aluno'")
    new_content = new_content.replace('"Login_aluno"', '"login_aluno"')
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(new_content)
        print(f"Fixed: {file_path}")
    else:
        print(f"No changes needed: {file_path}")
