from django.core.management.base import BaseCommand
from django.utils import timezone
from usuarios.models import Usuario
from core.email_utils import enviar_email_brevo
from datetime import timedelta

class Command(BaseCommand):
    help = 'Verifica se há feriados nos próximos 2 dias e envia e-mail aos utilizadores.'

    def handle(self, *args, **kwargs):
        # Lista de feriados fixos em Angola com explicação
        feriados = {
            "01-01": {
                "nome": "Ano Novo",
                "motivo": "Celebração da passagem de ano civil e renovação de esperanças para o futuro."
            },
            "02-04": {
                "nome": "Dia do Início da Luta Armada",
                "motivo": "Homenagem aos heróis que em 1961 iniciaram a luta contra o colonialismo para a libertação de Angola."
            },
            "08-03": {
                "nome": "Dia Internacional da Mulher",
                "motivo": "Celebração das conquistas sociais, políticas e económicas das mulheres, e reflexão sobre a igualdade."
            },
            "04-04": {
                "nome": "Dia da Paz e da Reconciliação Nacional",
                "motivo": "Marca o fim da guerra civil em 2002 e a assinatura dos acordos que trouxeram a paz definitiva ao país."
            },
            "01-05": {
                "nome": "Dia Internacional do Trabalhador",
                "motivo": "Homenagem às lutas históricas dos trabalhadores por direitos e melhores condições de trabalho."
            },
            "25-05": {
                "nome": "Dia de África",
                "motivo": "Celebração da fundação da Organização da Unidade Africana (atual União Africana) em 1963, simbolizando a luta pela libertação do continente."
            },
            "17-09": {
                "nome": "Dia do Fundador da Nação e do Herói Nacional",
                "motivo": "Homenagem ao Dr. António Agostinho Neto, primeiro Presidente de Angola, pelo seu papel na independência."
            },
            "02-11": {
                "nome": "Dia dos Finados",
                "motivo": "Dia dedicado à memória e homenagem aos entes queridos que já partiram."
            },
            "11-11": {
                "nome": "Dia da Independência Nacional",
                "motivo": "Celebração da histórica Proclamação da Independência de Angola em 1975."
            },
            "25-12": {
                "nome": "Natal",
                "motivo": "Celebração cristã do nascimento de Jesus Cristo, marcada pela união familiar e partilha."
            }
        }

        # Data de hoje + 2 dias
        data_alvo = timezone.now() + timedelta(days=2)
        mes_dia = data_alvo.strftime('%d-%m') # Formato "04-04"
        
        self.stdout.write(f"A verificar feriados para a data: {mes_dia}")

        if mes_dia in feriados:
            feriado = feriados[mes_dia]
            nome = feriado["nome"]
            motivo = feriado["motivo"]
            
            self.stdout.write(f"Feriado encontrado: {nome}. A preparar envio de emails...")
            
            # Construir email
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
                    <div style="background: linear-gradient(135deg, #7c3aed 0%, #ec4899 100%); padding: 20px; border-radius: 8px; text-align: center; color: white;">
                        <span style="font-size: 40px;">📅</span>
                        <h1 style="margin: 10px 0 0; font-size: 22px;">Aviso de Feriado: {nome}</h1>
                    </div>
                    <div style="padding: 20px; line-height: 1.6;">
                        <p>Olá,</p>
                        <p>Lembramos que daqui a 2 dias (no dia {data_alvo.strftime('%d/%m')}) será feriado nacional em Angola: <strong>{nome}</strong>.</p>
                        
                        <div style="background: #f8fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #7c3aed; margin: 20px 0;">
                            <p style="margin: 0; font-weight: bold; color: #1e293b;">Por que é feriado?</p>
                            <p style="margin: 5px 0 0; color: #475569;">{motivo}</p>
                        </div>
                        
                        <p>Aproveite este dia para descansar e, se quiser, colocar os seus estudos em dia na nossa plataforma!</p>
                        
                        <p>Bons estudos!</p>
                        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                        <p style="font-size: 12px; color: #94a3b8; text-align: center;">Equipa EdukAngola</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            usuarios = Usuario.objects.filter(is_active=True)
            for u in usuarios:
                enviar_email_brevo(
                    to_email=u.email,
                    to_name=u.nome,
                    subject=f"📢 Aviso de Feriado: {nome} (Daqui a 2 dias)",
                    html_content=html_content,
                    text_content=f"Lembramos que daqui a 2 dias será feriado: {nome}. {motivo}"
                )
                self.stdout.write(f"Email enviado para {u.email}")
                
            self.stdout.write(self.style.SUCCESS("Processo concluído com sucesso!"))
        else:
            self.stdout.write("Nenhum feriado previsto para daqui a 2 dias.")
