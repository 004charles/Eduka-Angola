document.addEventListener('DOMContentLoaded', function() {
    // Carrega imagens lazy
    function loadVisibleImages() {
        const lazyImages = document.querySelectorAll('.course-bg.lazy-load:not(.loaded)');
        
        lazyImages.forEach(img => {
            if (isElementInViewport(img)) {
                const bgUrl = img.getAttribute('data-bg');
                img.style.setProperty('--bg-image', `url(${bgUrl})`);
                img.classList.add('loaded');
            }
        });
    }

    // Verifica se elemento está visível
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.bottom >= 0
        );
    }

    // Carrega primeira imagem imediatamente
    const firstImage = document.querySelector('.course-bg.lazy-load');
    if (firstImage) {
        const bgUrl = firstImage.getAttribute('data-bg');
        firstImage.style.setProperty('--bg-image', `url(${bgUrl})`);
        firstImage.classList.add('loaded');
    }

    // Carrega outras imagens quando visíveis
    window.addEventListener('scroll', loadVisibleImages);
    window.addEventListener('resize', loadVisibleImages);
    loadVisibleImages();

    // Restante do código do slider...
});