import polib
import os

langs = ['en', 'fr', 'es', 'it', 'ro', 'ar', 'umb', 'kik', 'kmb', 'cok', 'pt']

translations = {
    'Categorias': {
        'en': 'Categories', 'fr': 'Catégories', 'es': 'Categorías', 'it': 'Categorie', 
        'ro': 'Categorii', 'ar': 'الفئات', 'pt': 'Categorias'
    },
    'Categoria': {
        'en': 'Category', 'fr': 'Catégorie', 'es': 'Categoría', 'it': 'Categoria', 
        'ro': 'Categorie', 'ar': 'فئة', 'pt': 'Categoria'
    },
    'Cursos Acadêmicos': {
        'en': 'Academic Courses', 'fr': 'Cours Académiques', 'es': 'Cursos Académicos', 
        'it': 'Corsi Accademici', 'ro': 'Cursuri Academice', 'ar': 'الدورات الأكاديمية', 'pt': 'Cursos Acadêmicos'
    },
    'Formação Profissional': {
        'en': 'Professional Training', 'fr': 'Formation Professionnelle', 'es': 'Formación Profesional', 
        'it': 'Formazione Professionale', 'ro': 'Formare Profesională', 'ar': 'التدريب المهني', 'pt': 'Formação Profissional'
    },
    'Escolas': {
        'en': 'Schools', 'fr': 'Écoles', 'es': 'Escuelas', 'it': 'Scuole', 
        'ro': 'Şcoli', 'ar': 'المدارس', 'pt': 'Escolas'
    },
    'Estágios': {
        'en': 'Internships', 'fr': 'Stages', 'es': 'Pasantías', 'it': 'Tirocini', 
        'ro': 'Stagii', 'ar': 'فترات تدريب', 'pt': 'Estágios'
    },
    'Cursos': {
        'en': 'Courses', 'fr': 'Cours', 'es': 'Cursos', 'it': 'Corsi', 
        'ro': 'Cursuri', 'ar': 'الدورات', 'pt': 'Cursos'
    },
    'Parceiros': {
        'en': 'Partners', 'fr': 'Partenaires', 'es': 'Socios', 'it': 'Partner', 
        'ro': 'Parteneri', 'ar': 'الشركاء', 'pt': 'Parceiros'
    },
    'Recursos': {
        'en': 'Resources', 'fr': 'Ressources', 'es': 'Recursos', 'it': 'Risorse', 
        'ro': 'Resurse', 'ar': 'الموارد', 'pt': 'Recursos'
    },
    'Biblioteca Digital': {
        'en': 'Digital Library', 'fr': 'Bibliothèque Numérique', 'es': 'Biblioteca Digital', 
        'it': 'Biblioteca Digitale', 'ro': 'Bibliotecă Digitală', 'ar': 'المكتبة الرقمية', 'pt': 'Biblioteca Digital'
    },
    'Guias de Estudo': {
        'en': 'Study Guides', 'fr': 'Guides d\'Étude', 'es': 'Guías de Estudo', 
        'it': 'Guide di Studio', 'ro': 'Ghiduri de Studiu', 'ar': 'أدلة الدراسة', 'pt': 'Guias de Estudo'
    },
    'Bolsa de Emprego': {
        'en': 'Job Board', 'fr': 'Bourse d\'Emploi', 'es': 'Bolsa de Empleo', 
        'it': 'Bacheca di Lavoro', 'ro': 'Bursă de Locuri de Muncă', 'ar': 'لوحة الوظائف', 'pt': 'Bolsa de Emprego'
    },
    'Blog': {
        'en': 'Blog', 'fr': 'Blog', 'es': 'Blog', 'it': 'Blog', 
        'ro': 'Blog', 'ar': 'مدونة', 'pt': 'Blog'
    },
    'Sobre': {
        'en': 'About', 'fr': 'À Propos', 'es': 'Sobre', 'it': 'Informazioni', 
        'ro': 'Despre', 'ar': 'حول', 'pt': 'Sobre'
    },
    'Instalar App': {
        'en': 'Install App', 'fr': 'Installer l\'App', 'es': 'Instalar App', 
        'it': 'Installa App', 'ro': 'Instalează Aplicația', 'ar': 'تثبيت التطبيق', 'pt': 'Instalar App'
    },
    'Ver Perfil': {
        'en': 'View Profile', 'fr': 'Voir le Profil', 'es': 'Ver Perfil', 
        'it': 'Visualizza Profilo', 'ro': 'Vezi Profilul', 'ar': 'عرض الملف الشخصي', 'pt': 'Ver Perfil'
    },
    'Minha Dashboard': {
        'en': 'My Dashboard', 'fr': 'Mon Tableau de Bord', 'es': 'Mi Tablero', 
        'it': 'La Mia Dashboard', 'ro': 'Panoul Meu', 'ar': 'لوحة التحكم الخاصة بي', 'pt': 'Minha Dashboard'
    },
    'Sair': {
        'en': 'Logout', 'fr': 'Se déconnecter', 'es': 'Cerrar Sesión', 
        'it': 'Esci', 'ro': 'Deconectare', 'ar': 'تسجيل الخروج', 'pt': 'Sair'
    },
    'Entrar': {
        'en': 'Login', 'fr': 'Connexion', 'es': 'Entrar', 
        'it': 'Accedi', 'ro': 'Autentificare', 'ar': 'تسجيل الدخول', 'pt': 'Entrar'
    },
    'Pesquisar': {
        'en': 'Search', 'fr': 'Rechercher', 'es': 'Buscar', 
        'it': 'Cerca', 'ro': 'Caută', 'ar': 'بحث', 'pt': 'Pesquisar'
    },
    'O que você está procurando?': {
        'en': 'What are you looking for?', 'fr': 'Que cherchez-vous?', 'es': '¿Qué estás buscando?', 
        'it': 'Cosa stai cercando?', 'ro': 'Ce cauţi?', 'ar': 'ما الذي تبحث عنه؟', 'pt': 'O que você está procurando?'
    },
    'Cursos em Destaque': {
        'en': 'Featured Courses', 'fr': 'Cours à la Une', 'es': 'Cursos Destacados', 
        'it': 'Corsi in Evidenza', 'ro': 'Cursuri Recomandate', 'ar': 'الدورات المميزة', 'pt': 'Cursos em Destaque'
    },
    'Recentes': {
        'en': 'Recent', 'fr': 'Récents', 'es': 'Recientes', 'it': 'Recenti', 
        'ro': 'Recente', 'ar': 'حديثة', 'pt': 'Recentes'
    },
    'Gratuitos': {
        'en': 'Free', 'fr': 'Gratuits', 'es': 'Gratis', 'it': 'Gratuiti', 
        'ro': 'Gratuite', 'ar': 'مجاني', 'pt': 'Gratuitos'
    },
    'Mais Inscritos': {
        'en': 'Most Enrolled', 'fr': 'Plus Inscrits', 'es': 'Más Inscritos', 'it': 'Più Iscritti', 
        'ro': 'Cei Mai Înscrişi', 'ar': 'الأكثر تسجيلاً', 'pt': 'Mais Inscritos'
    },
    'Para Você': {
        'en': 'For You', 'fr': 'Pour Vous', 'es': 'Para Ti', 'it': 'Per Te', 
        'ro': 'Pentru Tine', 'ar': 'لك', 'pt': 'Para Você'
    },
    'Promoção': {
        'en': 'Promotion', 'fr': 'Promotion', 'es': 'Promoción', 'it': 'Promozione', 
        'ro': 'Promoţie', 'ar': 'عرض', 'pt': 'Promoção'
    },
    'Próximos': {
        'en': 'Upcoming', 'fr': 'À Venir', 'es': 'Próximos', 'it': 'Prossimi', 
        'ro': 'Viitoare', 'ar': 'القادمة', 'pt': 'Próximos'
    },
    'Vagas': {
        'en': 'Vacancies', 'fr': 'Places', 'es': 'Vacantes', 'it': 'Posti', 
        'ro': 'Locuri', 'ar': 'وظائف شاغرة', 'pt': 'Vagas'
    },
    'Ensino Médio': {
        'en': 'High School', 'fr': 'Lycée', 'es': 'Bachillerato', 'it': 'Scuola Superiore', 
        'ro': 'Liceu', 'ar': 'المدرسة الثانوية', 'pt': 'Ensino Médio'
    },
    'Ciências Exatas': {
        'en': 'Exact Sciences', 'fr': 'Sciences Exactes', 'es': 'Ciencias Exactas', 
        'it': 'Scienze Esatte', 'ro': 'Ştiinţe Exacte', 'ar': 'العلوم الدقيقة', 'pt': 'Ciências Exatas'
    },
    'Humanidades': {
        'en': 'Humanities', 'fr': 'Humanités', 'es': 'Humanidades', 'it': 'Umanistica', 
        'ro': 'Umanistice', 'ar': 'العلوم الإنسانية', 'pt': 'Humanidades'
    },
    'Artes': {
        'en': 'Arts', 'fr': 'Arts', 'es': 'Artes', 'it': 'Arti', 
        'ro': 'Arte', 'ar': 'الفنون', 'pt': 'Artes'
    },
    'Programação': {
        'en': 'Programming', 'fr': 'Programmation', 'es': 'Programación', 'it': 'Programmazione', 
        'ro': 'Programare', 'ar': 'برمجة', 'pt': 'Programação'
    },
    'Design Gráfico': {
        'en': 'Graphic Design', 'fr': 'Design Graphique', 'es': 'Diseño Gráfico', 
        'it': 'Graphic Design', 'ro': 'Design Grafic', 'ar': 'التصميم الجرافيكي', 'pt': 'Design Gráfico'
    },
    'Redes de Computadores': {
        'en': 'Computer Networks', 'fr': 'Réseaux Informatiques', 'es': 'Redes de Computadoras', 
        'it': 'Reti Informatiche', 'ro': 'Reţele de Calculatoare', 'ar': 'شبكات الحاسوب', 'pt': 'Redes de Computadores'
    },
    'Gestão Empresarial': {
        'en': 'Business Management', 'fr': 'Gestion d\'Entreprise', 'es': 'Gestión Empresarial', 
        'it': 'Gestione Aziendale', 'ro': 'Managementul Afacerilor', 'ar': 'إدارة الأعمال', 'pt': 'Gestão Empresarial'
    },
    'Marketing Digital': {
        'en': 'Digital Marketing', 'fr': 'Marketing Digital', 'es': 'Marketing Digital', 
        'it': 'Marketing Digitale', 'ro': 'Marketing Digital', 'ar': 'التسويق الرقمي', 'pt': 'Marketing Digital'
    },
    'Contabilidade': {
        'en': 'Accounting', 'fr': 'Comptabilité', 'es': 'Contabilidad', 'it': 'Contabilità', 
        'ro': 'Contabilitate', 'ar': 'محاسبة', 'pt': 'Contabilidade'
    },
    'Instituições': {
        'en': 'Institutions', 'fr': 'Institutions', 'es': 'Instituciones', 'it': 'Istituzioni', 
        'ro': 'Instituţii', 'ar': 'المؤسسات', 'pt': 'Instituições'
    },
    'Universidades': {
        'en': 'Universities', 'fr': 'Universités', 'es': 'Universidades', 'it': 'Università', 
        'ro': 'Universităţi', 'ar': 'الجامعات', 'pt': 'Universidades'
    },
    'Escolas Técnicas': {
        'en': 'Technical Schools', 'fr': 'Écoles Techniques', 'es': 'Escuelas Técnicas', 
        'it': 'Scuole Tecniche', 'ro': 'Şcoli Tehnice', 'ar': 'المدارس التقنية', 'pt': 'Escolas Técnicas'
    },
    'Oportunidades': {
        'en': 'Opportunities', 'fr': 'Opportunités', 'es': 'Oportunidades', 'it': 'Opportunità', 
        'ro': 'Oportunităţi', 'ar': 'فرص', 'pt': 'Oportunidades'
    },
    'Estágios em TI': {
        'en': 'IT Internships', 'fr': 'Stages en TI', 'es': 'Pasantías en TI', 
        'it': 'Tirocini IT', 'ro': 'Stagii în IT', 'ar': 'تدريب في تكنولوجيا المعلومات', 'pt': 'Estágios em TI'
    },
    'Estágios em Engenharia': {
        'en': 'Engineering Internships', 'fr': 'Stages en Ingénierie', 'es': 'Pasantías en Ingeniería', 
        'it': 'Tirocini in Ingegneria', 'ro': 'Stagii în Inginerie', 'ar': 'تدريب في الهندسة', 'pt': 'Estágios em Engenharia'
    },
    'Estágios em Administração': {
        'en': 'Admin Internships', 'fr': 'Stages en Administration', 'es': 'Pasantías en Administración', 
        'it': 'Tirocini Amministrativi', 'ro': 'Stagii în Administraţie', 'ar': 'تدريب في الإدارة', 'pt': 'Estágios em Administração'
    },
    'Home demo': {
        'en': 'Home demo', 'fr': 'Démo Accueil', 'es': 'Demo Inicio', 'it': 'Demo Home', 
        'ro': 'Demo Acasă', 'ar': 'عرض تجريبي للرئيسية', 'pt': 'Home demo'
    },
    'cursos': {
        'en': 'courses', 'fr': 'cours', 'es': 'cursos', 'it': 'corsi', 
        'ro': 'cursuri', 'ar': 'دورات', 'pt': 'cursos'
    },
    'biblioteca': {
        'en': 'library', 'fr': 'bibliothèque', 'es': 'biblioteca', 'it': 'biblioteca', 
        'ro': 'bibliotecă', 'ar': 'مكتبة', 'pt': 'biblioteca'
    },
    'Guias de estudo': {
        'en': 'Study guides', 'fr': 'Guides d\'étude', 'es': 'Guías de estudio', 
        'it': 'Guide di studio', 'ro': 'Ghiduri de studiu', 'ar': 'أدلة الدراسة', 'pt': 'Guias de estudo'
    },
    'Educação Infantil': {
        'en': 'Kindergarten', 'fr': 'Éducation Maternelle', 'es': 'Educación Infantil', 
        'it': 'Educazione Infantile', 'ro': 'Educaţie Preşcolară', 'ar': 'التعليم في مرحلة الطفولة المبكرة', 'pt': 'Educação Infantil'
    },
    'Idioma': {
        'en': 'Language', 'fr': 'Langue', 'es': 'Idioma', 'it': 'Lingua', 
        'ro': 'Limbă', 'ar': 'اللغة', 'pt': 'Idioma'
    },
    'Junte-se a Mais de 3000 Alunos': {
        'en': 'Join More Than 3000 Students', 'fr': 'Rejoignez plus de 3000 étudiants', 'es': 'Únete a más de 3000 alumnos', 'pt': 'Junte-se a Mais de 3000 Alunos'
    },
    'Transformando vidas através da educação.': {
        'en': 'Transforming lives through education.', 'fr': 'Transformer des vies par l\'éducation.', 'es': 'Transformando vidas a través de la educación.', 'pt': 'Transformando vidas através da educação.'
    },
    'Buscar centros de formação': {
        'en': 'Search training centers', 'fr': 'Rechercher des centres de formation', 'es': 'Buscar centros de formación', 'pt': 'Buscar centros de formação'
    },
    'Ver Cursos': {
        'en': 'View Courses', 'fr': 'Voir les cours', 'es': 'Ver Cursos', 'pt': 'Ver Cursos'
    },
    'Sobre a EdukaAngola': {
        'en': 'About EdukaAngola', 'fr': 'À propos d\'EdukaAngola', 'es': 'Sobre EdukaAngola', 'pt': 'Sobre a EdukaAngola'
    },
    'O que é a EdukaAngola?': {
        'en': 'What is EdukaAngola?', 'fr': 'Qu\'est-ce qu\'EdukaAngola?', 'es': '¿Qué es EdukaAngola?', 'pt': 'O que é a EdukaAngola?'
    },
    'EdukaAngola é uma plataforma educacional angolana criada para conectar estudantes, profissionais e instituições de ensino a cursos práticos, acessíveis e de qualidade. O nosso objetivo é facilitar o aprendizado, promover o desenvolvimento profissional e contribuir para o crescimento educacional e tecnológico de Angola.': {
        'en': 'EdukaAngola is an Angolan educational platform created to connect students, professionals and teaching institutions to practical, affordable and quality courses. Our goal is to facilitate learning, promote professional development and contribute to the educational and technological growth of Angola.',
        'pt': 'EdukaAngola é uma plataforma educacional angolana criada para conectar estudantes, profissionais e instituições de ensino a cursos práticos, acessíveis e de qualidade. O nosso objetivo é facilitar o aprendizado, promover o desenvolvimento profissional e contribuir para o crescimento educacional e tecnológico de Angola.'
    },
    'Saiba Mais Sobre Nós': {
        'en': 'Learn More About Us', 'fr': 'En savoir plus sur nous', 'es': 'Saber más sobre nosotros', 'pt': 'Saiba Mais Sobre Nós'
    },
    'Seu navegador não suporta a tag de vídeo.': {
        'en': 'Your browser does not support the video tag.', 'fr': 'Votre navigateur ne supporte pas la balise vidéo.', 'pt': 'Seu navegador não suporta a tag de vídeo.'
    },
    'Vídeo ainda não disponível.': {
        'en': 'Video not yet available.', 'fr': 'Vidéo pas encore disponible.', 'pt': 'Vídeo ainda não disponível.'
    },
    'Catálogo de Cursos - Edukangola': {
        'en': 'Course Catalog - Edukangola', 'fr': 'Catalogue de cours - Edukangola', 'es': 'Catálogo de cursos - Edukangola', 'pt': 'Catálogo de Cursos - Edukangola'
    },
    'Catálogo de Cursos': {
        'en': 'Course Catalog', 'fr': 'Catalogue de cours', 'es': 'Catálogo de cursos', 'pt': 'Catálogo de Cursos'
    },
    'Encontre o curso perfeito para alavancar sua carreira.': {
        'en': 'Find the perfect course to boost your career.', 'fr': 'Trouvez le cours parfait pour booster votre carrière.', 'es': 'Encuentra el curso perfecto para impulsar tu carrera.', 'pt': 'Encontre o curso perfeito para alavancar sua carreira.'
    },
    'Filtrar Resultados': {
        'en': 'Filter Results', 'fr': 'Filtrer les résultats', 'es': 'Filtrar resultados', 'pt': 'Filtrar Resultados'
    },
    'Palavra-chave': {
        'en': 'Keyword', 'fr': 'Mot-clé', 'es': 'Palabra clave', 'pt': 'Palavra-chave'
    },
    'Todas as categorias': {
        'en': 'All categories', 'fr': 'Toutes les catégories', 'es': 'Todas las categorías', 'pt': 'Todas as categorias'
    },
    'Nível': {
        'en': 'Level', 'fr': 'Niveau', 'es': 'Nivel', 'pt': 'Nível'
    },
    'Todos os níveis': {
        'en': 'All levels', 'fr': 'Tous les niveaux', 'es': 'Todos los niveles', 'pt': 'Todos os níveis'
    },
    'Básico': {
        'en': 'Basic', 'fr': 'Basique', 'es': 'Básico', 'pt': 'Básico'
    },
    'Intermediário': {
        'en': 'Intermediate', 'fr': 'Intermédiaire', 'es': 'Intermedio', 'pt': 'Intermediário'
    },
    'Avançado': {
        'en': 'Advanced', 'fr': 'Avancé', 'es': 'Avanzado', 'pt': 'Avançado'
    },
    'Modalidade': {
        'en': 'Modality', 'fr': 'Modalité', 'es': 'Modalidad', 'pt': 'Modalidade'
    },
    'Todas as modalidades': {
        'en': 'All modalities', 'fr': 'Toutes les modalités', 'es': 'Todas las modalidades', 'pt': 'Todas as modalidades'
    },
    'Presencial': {
        'en': 'In-person', 'fr': 'En présentiel', 'es': 'Presencial', 'pt': 'Presencial'
    },
    'Híbrido': {
        'en': 'Hybrid', 'fr': 'Hybride', 'es': 'Híbrido', 'pt': 'Híbrido'
    },
    'Todos os idiomas': {
        'en': 'All languages', 'fr': 'Toutes les langues', 'es': 'Todos los idiomas', 'pt': 'Todos os idiomas'
    },
    'Português': {
        'en': 'Portuguese', 'fr': 'Portugais', 'es': 'Portugués', 'pt': 'Português'
    },
    'Preço': {
        'en': 'Price', 'fr': 'Prix', 'es': 'Precio', 'pt': 'Preço'
    },
    'Todos os preços': {
        'en': 'All prices', 'fr': 'Tous les prix', 'es': 'Todos los precios', 'pt': 'Todos os preços'
    },
    'Até 100 KZ': {
        'en': 'Up to 100 KZ', 'pt': 'Até 100 KZ'
    },
    '100 - 500 KZ': {
        'en': '100 - 500 KZ', 'pt': '100 - 500 KZ'
    },
    'Acima de 500 KZ': {
        'en': 'Over 500 KZ', 'pt': 'Acima de 500 KZ'
    },
    'Aplicar Filtros': {
        'en': 'Apply Filters', 'fr': 'Appliquer les filtres', 'es': 'Aplicar filtros', 'pt': 'Aplicar Filtros'
    },
    'Limpar Filtros': {
        'en': 'Clear Filters', 'fr': 'Effacer les filtres', 'es': 'Limpiar filtros', 'pt': 'Limpar Filtros'
    },
    'Por que Edukangola?': {
        'en': 'Why Edukangola?', 'fr': 'Pourquoi Edukangola?', 'es': '¿Por qué Edukangola?', 'pt': 'Por que Edukangola?'
    },
    'Instrutores Verificados': {
        'en': 'Verified Instructors', 'fr': 'Instructeurs vérifiés', 'es': 'Instructores verificados', 'pt': 'Instrutores Verificados'
    },
    'Certificados Válidos': {
        'en': 'Valid Certificates', 'fr': 'Certificats valides', 'es': 'Certificados válidos', 'pt': 'Certificados Válidos'
    },
    'Suporte Dedicado': {
        'en': 'Dedicated Support', 'fr': 'Support dédié', 'es': 'Soporte dedicado', 'pt': 'Suporte Dedicado'
    },
    'Cursos Disponíveis': {
        'en': 'Courses Available', 'fr': 'Cours disponibles', 'es': 'Cursos disponibles', 'pt': 'Cursos Disponíveis'
    },
    'Ordenar por:': {
        'en': 'Sort by:', 'fr': 'Trier par :', 'es': 'Ordenar por:', 'pt': 'Ordenar por:'
    },
    'Mais Recentes': {
        'en': 'Most Recent', 'fr': 'Plus récents', 'es': 'Más recientes', 'pt': 'Mais Recentes'
    },
    'Mais Populares': {
        'en': 'Most Popular', 'fr': 'Plus populaires', 'es': 'Más populares', 'pt': 'Mais Populares'
    },
    'Menor Preço': {
        'en': 'Lowest Price', 'fr': 'Prix le plus bas', 'es': 'Menor precio', 'pt': 'Menor Preço'
    },
    'Nenhum curso encontrado': {
        'en': 'No courses found', 'fr': 'Aucun cours trouvé', 'es': 'No se encontraron cursos', 'pt': 'Nenhum curso encontrado'
    },
    'Tente usar outros termos ou limpe os filtros para ver mais resultados.': {
        'en': 'Try using other terms or clear the filters to see more results.', 'fr': 'Essayez d\'autres termes ou effacez les filtres pour voir plus de résultats.', 'es': 'Intenta usar otros términos o limpia los filtros para ver más resultados.', 'pt': 'Tente usar outros termos ou limpe os filtros para ver mais resultados.'
    },
    'Edukangola': {
        'en': 'Edukangola', 'pt': 'Edukangola'
    },
    'Okulonga wosuka okuno': {
        'en': 'Learning you need here', 'pt': 'Okulonga wosuka okuno'
    }
}

for lang in langs:
    po_path = f'locale/{lang}/LC_MESSAGES/django.po'
    if not os.path.exists(os.path.dirname(po_path)):
        os.makedirs(os.path.dirname(po_path))
    
    if os.path.exists(po_path):
        po = polib.pofile(po_path)
    else:
        po = polib.POFile()
        po.metadata = {
            'Project-Id-Version': 'Eduka Angola',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
            'Language': lang,
        }

    for msgid, lang_trans in translations.items():
        entry = po.find(msgid)
        if not entry:
            entry = polib.POEntry(msgid=msgid, msgstr=lang_trans.get(lang, ''))
            po.append(entry)
        else:
            if not entry.msgstr:
                entry.msgstr = lang_trans.get(lang, '')
    
    po.save(po_path)
    # Compile to MO
    po.save_as_mofile(po_path.replace('.po', '.mo'))
    print(f'Updated and compiled {lang}')
