
document.addEventListener('DOMContentLoaded', function () {
    const animatedText = document.getElementById('animatedText');
    const cursor = document.querySelector('.cursor-pulse');
    if (!animatedText) return;

    const solutionText = "Formação de Elite para Quem Exige o Topo do Mercado";
    const normalTexts = [
        "Domine as Competências Que os Recrutadores Priorizam",
        "Transforme Saber Técnico em Autoridade Profissional",
        "Forjamos Líderes Técnicos para a Indústria Angolana",
        "Capacite-se com Rigor. Lidere com Excelência.",
        "O Conhecimento Oficial Que o Seu Futuro Exige"
    ];

    let isShowingSolution = true;
    let textIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typingSpeed = 60;
    let deletingSpeed = 30;
    let pauseBetween = 3000;

    function createParticles(element, count = 8) {
        const rect = element.getBoundingClientRect();
        for (let i = 0; i < count; i++) {
            const particle = document.createElement('div');
            particle.className = 'text-particle';
            particle.style.setProperty('--tx', `${(Math.random() - 0.5) * 100}px`);
            particle.style.setProperty('--ty', `${-Math.random() * 80 - 20}px`);
            particle.style.left = `${Math.random() * rect.width}px`;
            particle.style.top = `${Math.random() * rect.height}px`;
            element.appendChild(particle);
            setTimeout(() => particle.remove(), 2000);
        }
    }

    function typeWriter() {
        if (isShowingSolution) return;
        const currentText = normalTexts[textIndex];

        if (!isDeleting && charIndex < currentText.length) {
            if (charIndex % 3 === 0) createParticles(animatedText, 3);
            animatedText.textContent = currentText.substring(0, charIndex + 1);
            animatedText.classList.add('typing-effect');
            setTimeout(() => animatedText.classList.remove('typing-effect'), 300);
            charIndex++;
            setTimeout(typeWriter, typingSpeed);
        } else if (isDeleting && charIndex > 0) {
            animatedText.textContent = currentText.substring(0, charIndex - 1);
            charIndex--;
            setTimeout(typeWriter, deletingSpeed);
        } else {
            if (!isDeleting) {
                createParticles(animatedText, 15);
                animatedText.classList.add('text-change-effect');
                setTimeout(() => animatedText.classList.remove('text-change-effect'), 1200);
            }
            isDeleting = !isDeleting;
            if (!isDeleting) textIndex = (textIndex + 1) % normalTexts.length;
            setTimeout(typeWriter, isDeleting ? pauseBetween / 2 : pauseBetween);
        }
    }

    function showSolutionText() {
        animatedText.textContent = solutionText;
        animatedText.classList.add('solution-text-effect', 'solution-glow');
        createParticles(animatedText, 25);
        setTimeout(() => {
            animatedText.classList.remove('solution-text-effect', 'solution-glow');
            isShowingSolution = false;
            typeWriter();
        }, 5000); // Reduzi para 5 segundos para demonstração mais rápida, o user pode ajustar
    }

    showSolutionText();
    
    // Sparkle button effect
    const sparkleBtn = document.querySelector('.btn-sparkle');
    if (sparkleBtn) {
        sparkleBtn.addEventListener('mouseenter', function () {
            createParticles(this, 20);
        });
    }
});
