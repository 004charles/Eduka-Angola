document.addEventListener('DOMContentLoaded', function() {
    // Array de centros educacionais com seus cursos
    const centers = [
        {
            id: 'tech-center',
            name: 'Centro de Tecnologia',
            location: 'Luanda, Angola',
            logo: 'https://via.placeholder.com/40x40',
            courses: [
                {
                    title: 'Desenvolvimento Web Fullstack',
                    image: 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
                    difficulty: 'Avançado',
                    duration: '240h',
                    rating: '94% aprovação',
                    price: 'kz 1.299',
                    originalPrice: 'kz 1.599'
                },
                {
                    title: 'Data Science',
                    image: 'https://images.unsplash.com/photo-1555774698-0b77e0d5fac6?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
                    difficulty: 'Intermediário',
                    duration: '200h',
                    rating: '89% aprovação',
                    price: 'kz 1.099',
                    originalPrice: 'kz 1.399'
                },
                {
                    title: 'Mobile Development',
                    image: 'https://images.unsplash.com/photo-1517430816045-df4b7de11d1d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
                    difficulty: 'Avançado',
                    duration: '180h',
                    rating: '91% aprovação',
                    price: 'kz 999',
                    originalPrice: 'kz 1.299'
                }
            ]
        },
        {
            id: 'business-center',
            name: 'Centro de Negócios',
            location: 'Luanda, Angola',
            logo: 'https://via.placeholder.com/40x40',
            courses: [
                {
                    title: 'Gestão de Projetos',
                    image: 'https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
                    difficulty: 'Intermediário',
                    duration: '180h',
                    rating: '92% aprovação',
                    price: 'kz 899',
                    originalPrice: 'kz 1.199'
                },
                {
                    title: 'Marketing Digital',
                    image: 'https://images.unsplash.com/photo-1434626881859-194d67b2b86f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
                    difficulty: 'Iniciante',
                    duration: '150h',
                    rating: '88% aprovação',
                    price: 'kz 799',
                    originalPrice: 'kz 999'
                },
                {
                    title: 'UX/UI Design',
                    image: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
                    difficulty: 'Intermediário',
                    duration: '160h',
                    rating: '95% aprovação',
                    price: 'kz 1.099',
                    originalPrice: 'kz 1.399'
                }
            ]
        },
        {
            id: 'design-center',
            name: 'Centro de Design',
            location: 'Luanda, Angola',
            logo: 'https://via.placeholder.com/40x40',
            courses: [
                {
                    title: 'Design Gráfico',
                    image: 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
                    difficulty: 'Intermediário',
                    duration: '160h',
                    rating: '93% aprovação',
                    price: 'kz 1.199',
                    originalPrice: 'kz 1.499'
                },
                {
                    title: 'Motion Design',
                    image: 'https://images.unsplash.com/photo-1626785774573-4b799315345d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80',
                    difficulty: 'Avançado',
                    duration: '200h',
                    rating: '90% aprovação',
                    price: 'kz 1.499',
                    originalPrice: 'kz 1.799'
                }
            ]
        }
    ];

    // Inicializa os sliders para cada centro
    const centerCards = document.querySelectorAll('.main-card');
    
    centerCards.forEach((card, index) => {
        const slider = card.querySelector('.courses-slider');
        const prevBtn = card.querySelector('.prev-btn');
        const nextBtn = card.querySelector('.next-btn');
        const counter = card.querySelector('.center-counter');
        
        let currentCenterIndex = 0;
        let currentCourseIndex = 0;
        let autoChangeTimeout;
        
        // Atualiza o slider com os cursos do centro atual
        function updateSlider() {
            const center = centers[index];
            
            // Atualiza o cabeçalho do centro
            const header = card.querySelector('.center-info');
            header.querySelector('.center-logo').src = center.logo;
            header.querySelector('.center-name').textContent = center.name;
            header.querySelector('.center-location span').textContent = center.location;
            
            // Limpa os cursos existentes
            slider.innerHTML = '';
            
            // Adiciona os cursos do centro atual
            center.courses.forEach((course, i) => {
                const courseItem = document.createElement('div');
                courseItem.className = 'course-item';
                courseItem.innerHTML = `
                    <div class="course-bg" style="background-image: url('${course.image}')">
                        <div class="${index === 0 ? 'tech-overlay' : 'business-overlay'}"></div>
                    </div>
                    <div class="course-content">
                        <div class="difficulty">${course.difficulty}</div>
                        <h4>${course.title}</h4>
                        <div class="course-meta">
                            <span><i class="fas fa-clock"></i> ${course.duration}</span>
                            <span><i class="fas fa-certificate"></i> Certificado</span>
                            <span><i class="fas fa-user-graduate"></i> ${course.rating}</span>
                        </div>
                        <div class="price-tag">${course.price} <span class="original-price">${course.originalPrice}</span></div>
                        <a href="#" class="rbt-btn gradient-btn">Explorar Curso <i class="fas fa-arrow-right"></i></a>
                    </div>
                    <div class="${index === 0 ? 'tech-corner' : 'business-corner'}"></div>
                `;
                slider.appendChild(courseItem);
            });
            
            // Atualiza o contador
            counter.textContent = `${index + 1}/${centers.length}`;
            
            // Rola para o curso atual
            scrollToCourse(0);
        }
        
        // Rola para um curso específico
        function scrollToCourse(courseIndex) {
            const items = slider.querySelectorAll('.course-item');
            if (items.length > 0 && courseIndex >= 0 && courseIndex < items.length) {
                const item = items[courseIndex];
                // Substitua o scrollIntoView por transform/translate
                slider.scrollTo({
                    left: item.offsetLeft,
                    behavior: 'auto' // Comportamento instantâneo
                });
                currentCourseIndex = courseIndex;
                
                if (courseIndex === items.length - 1) {
                    clearTimeout(autoChangeTimeout);
                    autoChangeTimeout = setTimeout(() => {
                        nextCenter();
                    }, 3000);
                }
            }
        }
        
        // Avança para o próximo centro
        function nextCenter() {
            currentCenterIndex = (currentCenterIndex + 1) % centers.length;
            updateSlider();
        }
        
        // Retrocede para o centro anterior
        function prevCenter() {
            currentCenterIndex = (currentCenterIndex - 1 + centers.length) % centers.length;
            updateSlider();
        }
        
        // Event listeners para navegação
        prevBtn.addEventListener('click', () => {
            clearTimeout(autoChangeTimeout);
            if (currentCourseIndex > 0) {
                scrollToCourse(currentCourseIndex - 1);
            } else {
                prevCenter();
            }
        });
        
        nextBtn.addEventListener('click', () => {
            clearTimeout(autoChangeTimeout);
            const items = slider.querySelectorAll('.course-item');
            if (currentCourseIndex < items.length - 1) {
                scrollToCourse(currentCourseIndex + 1);
            } else {
                nextCenter();
            }
        });
        
        // Suporte para touch/swipe
        let touchStartX = 0;
        let touchEndX = 0;
        
        slider.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
            clearTimeout(autoChangeTimeout);
        }, {passive: true});
        
        slider.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, {passive: true});
        
        function handleSwipe() {
            if (touchEndX < touchStartX - 50) { // Swipe para a esquerda
                const items = slider.querySelectorAll('.course-item');
                if (currentCourseIndex < items.length - 1) {
                    scrollToCourse(currentCourseIndex + 1);
                } else {
                    nextCenter();
                }
            }
            if (touchEndX > touchStartX + 50) { // Swipe para a direita
                if (currentCourseIndex > 0) {
                    scrollToCourse(currentCourseIndex - 1);
                } else {
                    prevCenter();
                }
            }
        }
        
        // Inicializa o slider
        updateSlider();
        
        // Configura rotação automática
        setInterval(() => {
            const items = slider.querySelectorAll('.course-item');
            if (currentCourseIndex < items.length - 1) {
                scrollToCourse(currentCourseIndex + 1);
            } else {
                nextCenter();
            }
        }, 5000); // Muda a cada 5 segundos
    });
    
    // Efeito 3D nos cards
    const cards = document.querySelectorAll('.main-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const angleY = (x - centerX) / 20;
            const angleX = (centerY - y) / 20;
            
            card.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
        });
    });
});
