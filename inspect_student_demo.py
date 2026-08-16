import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()
from usuarios.models import Usuario, Aluno

email = 'aluno.demo@eduka-angola.test'
user = Usuario.objects.filter(email=email).first()
print('EXISTE_USUARIO=', bool(user))
if user:
    print(f'USUARIO={user.id}|nome={user.nome}|tipo={user.tipo_usuario}|ativo={user.is_active}|tem_password={user.has_usable_password()}')
    print('TEM_ALUNO=', Aluno.objects.filter(usuario=user).exists())
