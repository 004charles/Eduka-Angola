import os

import requests


class EmailSender:
    def __init__(self):
        self.api_key = os.getenv('BREVO_API_KEY', '')
        self.sender_email = os.getenv('DEFAULT_FROM_EMAIL', '')
        self.sender_name = os.getenv('DEFAULT_FROM_NAME', 'Edukangola')

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.sender_email)

    def send(self, *, recipient_email: str, recipient_name: str, subject: str, message: str, link: str = '/') -> None:
        if not self.configured:
            raise RuntimeError('Canal de e-mail não configurado')
        response = requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers={'api-key': self.api_key, 'accept': 'application/json', 'content-type': 'application/json'},
            json={
                'sender': {'name': self.sender_name, 'email': self.sender_email},
                'to': [{'email': recipient_email, 'name': recipient_name or recipient_email}],
                'subject': subject,
                'htmlContent': f'<p>{message}</p><p><a href="{link}">Abrir na Edukangola</a></p>',
                'textContent': f'{message}\n\nAbrir na Edukangola: {link}',
            },
            timeout=10,
        )
        response.raise_for_status()
