from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()

from core.models import PerguntaFrequente

FAQS = {
    'pt': [
        ('Cursos e inscrições', 'Como me inscrevo num curso presencial?', 'Abra a ficha do curso, confirme a turma e as condições de inscrição. A plataforma mostra o que é pago agora e o que será tratado pelo centro.'),
        ('Cursos e inscrições', 'Como compro um curso em vídeo?', 'Os cursos em vídeo são comprados uma única vez quando existe valor. Depois da confirmação do pagamento, ficam disponíveis na área de aprendizagem.'),
        ('Biblioteca', 'Os livros da Biblioteca são gratuitos?', 'Nesta primeira fase, as obras próprias da Edukangola têm leitura gratuita. Cada obra informa claramente as condições de acesso.'),
        ('Biblioteca', 'Posso retomar a leitura onde parei?', 'Sim. Ao voltar ao livro, pode continuar na página guardada ou começar novamente. Também pode usar a leitura em voz alta quando o navegador disponibilizar uma voz compatível.'),
        ('Eventos e bilhetes', 'Como compro um bilhete para um evento?', 'Abra o evento, escolha o lote de bilhete disponível e avance para o pagamento. A confirmação fica associada ao seu pedido.'),
        ('Eventos e bilhetes', 'Onde encontro os meus bilhetes?', 'Os bilhetes confirmados estarão disponíveis na sua área de aluno, separados dos cursos e livros guardados.'),
        ('Conta e segurança', 'Preciso de criar conta para explorar?', 'Não. Pode pesquisar cursos, centros, eventos e livros sem conta. A conta é necessária para guardar conteúdos, comprar e acompanhar acessos.'),
        ('Conta e segurança', 'O GestorEduka é público?', 'Não. O GestorEduka é a área privada de gestão dos centros. Os alunos utilizam a experiência pública da Edukangola.'),
    ],
    'en': [
        ('Courses and enrolment', 'How do I enrol in an in-person course?', 'Open the course page, confirm the class and enrolment conditions. The platform shows what is paid now and what the centre will handle.'),
        ('Courses and enrolment', 'How do I buy a video course?', 'Video courses are bought once when a price applies. Once payment is confirmed, they become available in the learning area.'),
        ('Library', 'Are Library books free?', 'At this first stage, Edukangola own books are free to read. Each book clearly states its access terms.'),
        ('Library', 'Can I resume where I stopped?', 'Yes. When you return, you can continue at the saved page or restart. You can also use read aloud when the browser provides a compatible voice.'),
        ('Events and tickets', 'How do I buy an event ticket?', 'Open the event, choose an available ticket tier and continue to payment. Confirmation is linked to your order.'),
        ('Events and tickets', 'Where are my tickets?', 'Confirmed tickets will be available in your student area, separate from saved courses and books.'),
        ('Account and safety', 'Do I need an account to explore?', 'No. You can browse courses, centres, events and books without an account. You need one to save content, buy and track access.'),
        ('Account and safety', 'Is GestorEduka public?', 'No. GestorEduka is the private management area for centres. Students use the public Edukangola experience.'),
    ],
    'fr': [
        ('Cours et inscriptions', 'Comment m’inscrire à un cours en présentiel ?', 'Ouvrez la fiche du cours, confirmez le groupe et les conditions. La plateforme montre ce qui est payé maintenant et ce que le centre traite.'),
        ('Cours et inscriptions', 'Comment acheter un cours vidéo ?', 'Les cours vidéo sont achetés une fois lorsqu’un prix est appliqué. Après confirmation du paiement, ils deviennent disponibles dans l’espace d’apprentissage.'),
        ('Bibliothèque', 'Les livres sont-ils gratuits ?', 'À cette première étape, les œuvres propres à Edukangola sont gratuites à lire. Chaque livre indique clairement ses conditions d’accès.'),
        ('Bibliothèque', 'Puis-je reprendre ma lecture ?', 'Oui. Vous pouvez continuer à la page enregistrée ou recommencer. La lecture à voix haute est disponible si le navigateur propose une voix compatible.'),
        ('Événements et billets', 'Comment acheter un billet ?', 'Ouvrez l’événement, choisissez une catégorie de billet et continuez vers le paiement. La confirmation est liée à votre commande.'),
        ('Événements et billets', 'Où sont mes billets ?', 'Les billets confirmés seront disponibles dans votre espace étudiant, séparés des cours et livres enregistrés.'),
        ('Compte et sécurité', 'Faut-il un compte pour explorer ?', 'Non. Vous pouvez parcourir les cours, centres, événements et livres sans compte. Un compte est nécessaire pour enregistrer, acheter et suivre les accès.'),
        ('Compte et sécurité', 'GestorEduka est-il public ?', 'Non. GestorEduka est l’espace de gestion privé des centres. Les étudiants utilisent l’expérience publique Edukangola.'),
    ],
    'zh': [
        ('课程与报名', '如何报名线下课程？', '打开课程详情，确认班级和报名条件。平台会说明当前支付内容以及由中心处理的事项。'),
        ('课程与报名', '如何购买视频课程？', '视频课程在需要付费时一次购买。付款确认后，可在学习空间内使用。'),
        ('图书馆', '图书馆的书免费吗？', '在第一阶段，Edukangola 自有作品可免费阅读。每本书会明确说明访问条件。'),
        ('图书馆', '可以从上次阅读位置继续吗？', '可以。返回图书时，可继续已保存页面或重新开始。若浏览器提供兼容语音，也可使用朗读功能。'),
        ('活动与门票', '如何购买活动门票？', '打开活动，选择可用票种，然后继续付款。确认信息会关联到您的订单。'),
        ('活动与门票', '在哪里查看我的门票？', '确认后的门票将显示在学习空间中，与已保存课程和图书分开。'),
        ('账户与安全', '探索时需要账户吗？', '不需要。无需账户即可浏览课程、中心、活动和图书。保存内容、购买和跟踪访问时需要账户。'),
        ('账户与安全', 'GestorEduka 对外公开吗？', '不公开。GestorEduka 是培训中心的私有管理区。学生使用 Edukangola 公共体验。'),
    ],
}

for idioma, entries in FAQS.items():
    for ordem, (categoria, pergunta, resposta) in enumerate(entries, start=1):
        PerguntaFrequente.objects.update_or_create(
            idioma=idioma, categoria=categoria, pergunta=pergunta,
            defaults={'resposta': resposta, 'ordem': ordem, 'publicada': True},
        )
print(PerguntaFrequente.objects.filter(publicada=True).count())
