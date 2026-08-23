from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0008_feriadonacional'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recurso', models.CharField(db_index=True, max_length=80)),
                ('objeto_id', models.CharField(db_index=True, max_length=80)),
                ('acao', models.CharField(max_length=80)),
                ('antes', models.JSONField(blank=True, default=dict)),
                ('depois', models.JSONField(blank=True, default=dict)),
                ('criado_em', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auditorias_administrativas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Registo de auditoria administrativa',
                'verbose_name_plural': 'Registos de auditoria administrativa',
                'ordering': ('-criado_em',),
            },
        ),
        migrations.AddIndex(
            model_name='adminauditlog',
            index=models.Index(fields=['recurso', 'objeto_id', 'criado_em'], name='core_admin_audit_obj_idx'),
        ),
    ]
