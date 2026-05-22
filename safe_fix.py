import re

with open('cursovideoapp/templates/cursovideo/home.html', 'r') as f:
    content = f.read()

def replace_section(match):
    full_match = match.group(0)
    title = match.group(1)
    
    # Try to find a link
    link_match = re.search(r'<a href="([^"]+)" class="play-btn-link"[^>]*>(.*?)</a>', full_match, re.DOTALL)
    
    # Try to find the swiper-wrapper content
    wrapper_match = re.search(r'<div class="swiper-wrapper">(.*?)</div>\s*<div class="swiper-button-next">', full_match, re.DOTALL)
    
    if not wrapper_match:
        return full_match # Fallback if something is weird
        
    loop_content = wrapper_match.group(1)
    loop_content = loop_content.replace('class="swiper-slide"', 'class="swiper-slide p-2" style="width: 320px;"')
    
    left_col = f"""<div class="section-title text-start">
                                <h2 class="play-section-title mb-0 title" style="padding-left: 0; font-size: 24px; font-weight: 700;">{title}</h2>"""
    
    if link_match:
        href = link_match.group(1)
        inner_html = link_match.group(2).strip()
        left_col += f"""
                                <div class="mt--20">
                                    <a href="{href}" class="play-btn-link" style="color: var(--play-meta-dark); text-decoration: none; font-weight: 600; font-size: 14px;">
                                        {inner_html}
                                    </a>
                                </div>"""
                                
    left_col += """
                            </div>
                            <div class="d-flex justify-content-start gap-3 rbt-arrow-between mt--30">
                                <div class="rbt-swiper-arrow style_2 play-custom-prev">
                                    <div class="custom-overfolow">
                                        <i class="rbt-icon feather-arrow-left"></i>
                                        <i class="rbt-icon-top feather-arrow-left"></i>
                                    </div>
                                </div>
                                <div class="rbt-swiper-arrow style_2 play-custom-next">
                                    <div class="custom-overfolow">
                                        <i class="rbt-icon feather-arrow-right"></i>
                                        <i class="rbt-icon-top feather-arrow-right"></i>
                                    </div>
                                </div>
                            </div>"""
                            
    res = f"""<section class="play-section">
            <div class="container">
                <div class="bg-color-white rbt-shadow-box" style="padding: 40px; border-radius: 12px;">
                    <div class="row g-5 align-items-center">
                        <div class="col-lg-3 col-md-12">
                            {left_col}
                        </div>
                        <div class="col-lg-9 col-md-12">
                            <div class="swiper playSwiper-custom">
                                <div class="swiper-wrapper">{loop_content}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>"""
        
    return res

# We look for <section class="play-section"> ... </section> that contains playSwiper
pattern = r'<section class="play-section(?: mb--60)?">\s*<div class="d-flex justify-content-between align-items-center mb-3 pr-5" style="padding-right: 5%;">\s*<h2 class="play-section-title mb-0">([^<]+)</h2>.*?<div class="swiper playSwiper">.*?</div>\s*</div>\s*</section>'

new_content = re.sub(pattern, replace_section, content, flags=re.DOTALL)

# Now fix the JavaScript for initialization
js_old = """            new Swiper(".playSwiper", {
                slidesPerView: 'auto',
                spaceBetween: 20,
                watchOverflow: true,
                navigation: {
                    nextEl: ".swiper-button-next",
                    prevEl: ".swiper-button-prev",
                }
            });"""
            
js_new = """            // Inicializar sliders personalizados com botões na coluna da esquerda
            document.querySelectorAll('.play-section').forEach(function(section) {
                var customSwiperEl = section.querySelector('.playSwiper-custom, .playSwiper-recomendados');
                var prevBtn = section.querySelector('.play-custom-prev');
                var nextBtn = section.querySelector('.play-custom-next');
                
                if (customSwiperEl && prevBtn && nextBtn) {
                    new Swiper(customSwiperEl, {
                        slidesPerView: 'auto',
                        spaceBetween: 20,
                        watchOverflow: true,
                        navigation: {
                            nextEl: nextBtn,
                            prevEl: prevBtn,
                        }
                    });
                }
            });

            // Swipers convencionais
            new Swiper(".playSwiper", {
                slidesPerView: 'auto',
                spaceBetween: 20,
                watchOverflow: true,
                navigation: {
                    nextEl: ".swiper-button-next",
                    prevEl: ".swiper-button-prev",
                }
            });"""

new_content = new_content.replace(js_old, js_new)

with open('cursovideoapp/templates/cursovideo/home.html', 'w') as f:
    f.write(new_content)

print("Safely replaced sections")
