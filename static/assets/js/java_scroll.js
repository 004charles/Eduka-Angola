document.addEventListener('DOMContentLoaded', function() {
    // Dados dos centros (simplificado para exemplo)
    const centers = [
        {
            name: "Cinfotec",
            logo: "https://via.placeholder.com/40x40",
            location: "Luanda, Angola",
            courses: [
                {
                    title: "Desenvolvimento Web Fullstack",
                    image: "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
                    difficulty: "Avançado",
                    duration: "240h",
                    rating: "94% aprovação",
                    price: "kz 1.299",
                    originalPrice: "kz 1.599"
                },
                // ... outros cursos
            ]
        },
        // ... outros centros
    ];

    // Configurações
    const SCROLL_DURATION = 300; // Reduzido para mais suavidade
    const AUTO_SCROLL_DELAY = 5000;
    
    // Cache de elementos e estado
    const centerCards = document.querySelectorAll('.main-card');
    let activeAnimations = [];
    
    // Função de scroll suave otimizada
    function smoothScroll(element, target, duration) {
        // Cancela animações anteriores para o mesmo elemento
        activeAnimations.forEach(anim => {
            if (anim.element === element) anim.stop();
        });
        
        const start = element.scrollLeft;
        const change = target - start;
        const startTime = performance.now();
        let requestId;
        
        // Usando requestAnimationFrame com polyfill para melhor performance
        const animateScroll = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = easeOutQuad(progress);
            
            // Usando transform para melhor performance (GPU accelerated)
            element.style.transform = `translateX(${-(start + (change * easeProgress))}px)`;
            
            if (progress < 1) {
                requestId = requestAnimationFrame(animateScroll);
            } else {
                // Finaliza a animação
                element.style.transform = 'none';
                element.scrollLeft = target;
                activeAnimations = activeAnimations.filter(anim => anim.id !== requestId);
            }
        };
        
        function easeOutQuad(t) {
            return t * (2 - t);
        }
        
        // Inicia a animação
        element.style.willChange = 'transform'; // Otimização para o browser
        requestId = requestAnimationFrame(animateScroll);
        
        const animation = {
            id: requestId,
            element: element,
            stop: () => {
                cancelAnimationFrame(requestId);
                element.style.transform = 'none';
                element.style.willChange = 'auto';
            }
        };
        
        activeAnimations.push(animation);
        return animation;
    }

    // Inicialização dos sliders otimizada
    centerCards.forEach((card, index) => {
        const slider = card.querySelector('.courses-slider');
        const prevBtn = card.querySelector('.prev-btn');
        const nextBtn = card.querySelector('.next-btn');
        const counter = card.querySelector('.center-counter');
        
        // Variáveis de estado
        let currentCourseIndex = 0;
        let autoScrollTimeout;
        let isUserInteracting = false;
        
        // Configuração inicial do slider
        function setupSlider() {
            const items = slider.querySelectorAll('.course-item');
            if (!items.length) return;
            
            // Otimização: pré-carrega imagens dos próximos slides
            if (currentCourseIndex < items.length - 1) {
                const nextItem = items[currentCourseIndex + 1];
                const img = nextItem.querySelector('.course-bg');
                if (img) {
                    const tempImg = new Image();
                    tempImg.src = img.style.backgroundImage.replace(/url\(['"]?(.*?)['"]?\)/i, '$1');
                }
            }
            
            // Atualiza contador
            if (counter) {
                counter.textContent = `${currentCourseIndex + 1}/${items.length}`;
            }
        }
        
        // Navegação entre cursos
        function goToSlide(index, animate = true) {
            const items = slider.querySelectorAll('.course-item');
            if (!items.length) return;
            
            index = Math.max(0, Math.min(index, items.length - 1));
            currentCourseIndex = index;
            
            const target = items[index].offsetLeft;
            
            if (animate) {
                smoothScroll(slider, target, SCROLL_DURATION);
            } else {
                slider.scrollLeft = target;
            }
            
            setupSlider();
            
            // Reinicia o auto-scroll após interação
            if (isUserInteracting) {
                resetAutoScroll();
            }
        }
        
        // Controle do auto-scroll
        function startAutoScroll() {
            clearTimeout(autoScrollTimeout);
            if (!isUserInteracting) {
                autoScrollTimeout = setTimeout(() => {
                    const items = slider.querySelectorAll('.course-item');
                    if (currentCourseIndex < items.length - 1) {
                        goToSlide(currentCourseIndex + 1);
                    } else {
                        goToSlide(0);
                    }
                }, AUTO_SCROLL_DELAY);
            }
        }
        
        function resetAutoScroll() {
            clearTimeout(autoScrollTimeout);
            startAutoScroll();
        }
        
        // Event listeners otimizados
        function addEventListeners() {
            // Navegação por botões
            if (prevBtn) {
                prevBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    isUserInteracting = true;
                    const items = slider.querySelectorAll('.course-item');
                    goToSlide((currentCourseIndex - 1 + items.length) % items.length);
                    setTimeout(() => { isUserInteracting = false; }, 1000);
                });
            }
            
            if (nextBtn) {
                nextBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    isUserInteracting = true;
                    const items = slider.querySelectorAll('.course-item');
                    goToSlide((currentCourseIndex + 1) % items.length);
                    setTimeout(() => { isUserInteracting = false; }, 1000);
                });
            }
            
            // Touch events melhorados
            let touchStartX = 0;
            let touchEndX = 0;
            
            slider.addEventListener('touchstart', (e) => {
                touchStartX = e.touches[0].clientX;
                isUserInteracting = true;
                clearTimeout(autoScrollTimeout);
            }, { passive: true });
            
            slider.addEventListener('touchmove', (e) => {
                touchEndX = e.touches[0].clientX;
            }, { passive: true });
            
            slider.addEventListener('touchend', () => {
                const diff = touchStartX - touchEndX;
                if (Math.abs(diff) > 50) {
                    if (diff > 0) { // Swipe left
                        const items = slider.querySelectorAll('.course-item');
                        goToSlide(Math.min(currentCourseIndex + 1, items.length - 1));
                    } else { // Swipe right
                        goToSlide(Math.max(currentCourseIndex - 1, 0));
                    }
                }
                setTimeout(() => { isUserInteracting = false; }, 1000);
                resetAutoScroll();
            }, { passive: true });
            
            // Otimização: Intersection Observer para lazy loading
            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const bg = entry.target.querySelector('.course-bg');
                            if (bg && !bg.dataset.loaded) {
                                bg.dataset.loaded = true;
                                // Pode adicionar lógica de carregamento otimizado aqui
                            }
                        }
                    });
                }, { threshold: 0.1 });
                
                slider.querySelectorAll('.course-item').forEach(item => {
                    observer.observe(item);
                });
            }
        }
        
        // Inicialização
        setupSlider();
        addEventListeners();
        startAutoScroll();
        
        // Pausa auto-scroll quando o mouse está sobre o card
        card.addEventListener('mouseenter', () => {
            isUserInteracting = true;
            clearTimeout(autoScrollTimeout);
        });
        
        card.addEventListener('mouseleave', () => {
            isUserInteracting = false;
            resetAutoScroll();
        });
    });
    
    // Efeito 3D otimizado
    if (!('ontouchstart' in window)) { // Apenas para dispositivos não touch
        const cards = document.querySelectorAll('.main-card');
        
        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                requestAnimationFrame(() => {
                    const rect = card.getBoundingClientRect();
                    const x = (e.clientX - rect.left) / rect.width;
                    const y = (e.clientY - rect.top) / rect.height;
                    const centerX = 0.5;
                    const centerY = 0.5;
                    const angleY = (x - centerX) * 10;
                    const angleX = (centerY - y) * 10;
                    
                    card.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg)`;
                    card.style.transition = 'transform 0.1s ease-out';
                });
            });
            
            card.addEventListener('mouseleave', () => {
                requestAnimationFrame(() => {
                    card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
                    card.style.transition = 'transform 0.5s ease-out';
                });
            });
        });
    }
});