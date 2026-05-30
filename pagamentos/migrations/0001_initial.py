from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usuarios', '0001_initial'),
        ('cursos_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracaoPagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pagamentos_ativados', models.BooleanField(default=True, verbose_name='Pagamentos ativados')),
                ('gateway_padrao', models.CharField(
                    choices=[('PRONTU', 'Prontu'), ('STRIPE', 'Stripe'), ('PAYPAL', 'PayPal')],
                    default='PRONTU',
                    max_length=20,
                    verbose_name='Gateway padrão'
                )),
                ('moeda_padrao', models.CharField(default='AOA', max_length=3, verbose_name='Moeda padrão')),
                ('tempo_expiracao_link_minutos', models.PositiveIntegerField(
                    default=120,
                    validators=[django.core.validators.MinValueValidator(1)],
                    verbose_name='Tempo de expiração do link (minutos)'
                )),
                ('max_tentativas_pagamento', models.PositiveIntegerField(
                    default=3,
                    validators=[django.core.validators.MinValueValidator(1)],
                    verbose_name='Máximo de tentativas'
                )),
                ('desconto_inscricao_percentual', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    max_digits=5,
                    validators=[django.core.validators.MinValueValidator(0)],
                    verbose_name='Desconto inscrição (%)'
                )),
                ('notificar_admin_pagamento_recebido', models.BooleanField(
                    default=True,
                    verbose_name='Notificar admin quando pagamento é recebido'
                )),
                ('validar_webhook_signature', models.BooleanField(
                    default=True,
                    verbose_name='Validar assinatura do webhook'
                )),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data de atualização')),
            ],
            options={
                'verbose_name': 'Configuração de Pagamento',
                'verbose_name_plural': 'Configuração de Pagamento',
            },
        ),
        migrations.CreateModel(
            name='Pagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referencia_pagamento', models.CharField(
                    max_length=100,
                    unique=True,
                    verbose_name='Referência do pagamento'
                )),
                ('referencia_gateway', models.CharField(
                    blank=True,
                    max_length=255,
                    null=True,
                    verbose_name='Referência do gateway'
                )),
                ('tipo_pagamento', models.CharField(
                    choices=[('INSCRICAO', 'Inscrição em Curso'), ('RENOVACAO', 'Renovação'), ('BOLSA', 'Bolsa')],
                    max_length=20,
                    verbose_name='Tipo de pagamento'
                )),
                ('moeda', models.CharField(default='AOA', max_length=3, verbose_name='Moeda')),
                ('valor', models.DecimalField(
                    decimal_places=2,
                    max_digits=12,
                    validators=[django.core.validators.MinValueValidator(0)],
                    verbose_name='Valor'
                )),
                ('valor_desconto', models.DecimalField(
                    decimal_places=2,
                    default=0,
                    max_digits=12,
                    validators=[django.core.validators.MinValueValidator(0)],
                    verbose_name='Valor do desconto'
                )),
                ('valor_final', models.DecimalField(
                    decimal_places=2,
                    max_digits=12,
                    validators=[django.core.validators.MinValueValidator(0)],
                    verbose_name='Valor final'
                )),
                ('gateway', models.CharField(
                    choices=[('PRONTU', 'Prontu'), ('STRIPE', 'Stripe'), ('PAYPAL', 'PayPal')],
                    max_length=20,
                    verbose_name='Gateway'
                )),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('REQUESTED', 'Solicitado'),
                        ('PROCESSING', 'Processando'),
                        ('ACCEPTED', 'Aceito'),
                        ('REJECTED', 'Rejeitado'),
                        ('EXPIRED', 'Expirado'),
                        ('CANCELLED', 'Cancelado'),
                        ('REFUNDED', 'Reembolsado'),
                    ],
                    default='PENDING',
                    max_length=20,
                    verbose_name='Status'
                )),
                ('url_pagamento', models.URLField(blank=True, null=True, verbose_name='URL de pagamento')),
                ('url_sucesso', models.URLField(blank=True, null=True, verbose_name='URL de sucesso')),
                ('url_cancelamento', models.URLField(blank=True, null=True, verbose_name='URL de cancelamento')),
                ('numero_parcela', models.PositiveIntegerField(blank=True, null=True, verbose_name='Número da parcela')),
                ('tentativas_pagamento', models.PositiveIntegerField(default=0, verbose_name='Tentativas de pagamento')),
                ('metadados', models.JSONField(default=dict, verbose_name='Metadados')),
                ('resposta_gateway', models.JSONField(default=dict, verbose_name='Resposta do gateway')),
                ('webhook_processado', models.BooleanField(default=False, verbose_name='Webhook processado')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data de atualização')),
                ('data_vencimento', models.DateTimeField(blank=True, null=True, verbose_name='Data de vencimento')),
                ('data_pagamento', models.DateTimeField(blank=True, null=True, verbose_name='Data de pagamento')),
                ('curso', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    to='cursos_app.curso',
                    verbose_name='Curso'
                )),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='usuarios.usuario',
                    verbose_name='Usuário'
                )),
            ],
            options={
                'verbose_name': 'Pagamento',
                'verbose_name_plural': 'Pagamentos',
                'ordering': ['-data_criacao'],
                'indexes': [
                    models.Index(fields=['referencia_pagamento'], name='pagamentos_pag_referencia_idx'),
                    models.Index(fields=['usuario', 'status'], name='pagamentos_pag_usuario_status_idx'),
                    models.Index(fields=['status', 'data_criacao'], name='pagamentos_pag_status_data_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='TentativaPagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_tentativa', models.PositiveIntegerField(verbose_name='Número da tentativa')),
                ('status_resposta', models.CharField(max_length=20, verbose_name='Status da resposta')),
                ('codigo_erro', models.CharField(blank=True, max_length=50, null=True, verbose_name='Código de erro')),
                ('mensagem_erro', models.TextField(blank=True, verbose_name='Mensagem de erro')),
                ('resposta_gateway', models.JSONField(default=dict, verbose_name='Resposta do gateway')),
                ('tempo_resposta_ms', models.PositiveIntegerField(blank=True, null=True, verbose_name='Tempo de resposta (ms)')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
                ('pagamento', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tentativas',
                    to='pagamentos.pagamento',
                    verbose_name='Pagamento'
                )),
            ],
            options={
                'verbose_name': 'Tentativa de Pagamento',
                'verbose_name_plural': 'Tentativas de Pagamento',
                'ordering': ['-data_criacao'],
            },
        ),
        migrations.CreateModel(
            name='HistoricoPagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_anterior', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('REQUESTED', 'Solicitado'),
                        ('PROCESSING', 'Processando'),
                        ('ACCEPTED', 'Aceito'),
                        ('REJECTED', 'Rejeitado'),
                        ('EXPIRED', 'Expirado'),
                        ('CANCELLED', 'Cancelado'),
                        ('REFUNDED', 'Reembolsado'),
                    ],
                    max_length=20,
                    verbose_name='Status anterior'
                )),
                ('status_novo', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('REQUESTED', 'Solicitado'),
                        ('PROCESSING', 'Processando'),
                        ('ACCEPTED', 'Aceito'),
                        ('REJECTED', 'Rejeitado'),
                        ('EXPIRED', 'Expirado'),
                        ('CANCELLED', 'Cancelado'),
                        ('REFUNDED', 'Reembolsado'),
                    ],
                    max_length=20,
                    verbose_name='Status novo'
                )),
                ('motivo', models.TextField(blank=True, verbose_name='Motivo')),
                ('referencia_gateway', models.CharField(blank=True, max_length=255, null=True, verbose_name='Referência do gateway')),
                ('resposta_gateway', models.JSONField(default=dict, verbose_name='Resposta do gateway')),
                ('criado_por', models.CharField(
                    choices=[('SISTEMA', 'Sistema'), ('WEBHOOK', 'Webhook'), ('MANUAL', 'Manual'), ('ADMIN', 'Admin')],
                    default='SISTEMA',
                    max_length=20,
                    verbose_name='Criado por'
                )),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='Endereço IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
                ('pagamento', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='historico',
                    to='pagamentos.pagamento',
                    verbose_name='Pagamento'
                )),
            ],
            options={
                'verbose_name': 'Histórico de Pagamento',
                'verbose_name_plural': 'Histórico de Pagamentos',
                'ordering': ['-data_criacao'],
            },
        ),
    ]
