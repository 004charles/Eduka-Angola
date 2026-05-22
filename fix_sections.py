import re

with open('cursovideoapp/templates/cursovideo/home.html', 'r') as f:
    content = f.read()

def replace_section(match):
    header = match.group(1)
    title = match.group(2)
    link = match.group(3)
    loop = match.group(4)
    
    # Check if the section contains 'Continuar a Ver', 'A Minha Lista', etc.
    # Basically we want to replace anything that uses <div class="swiper playSwiper">
    
    # Building the left column text
    left_col = f"""<div class="section-title text-start">
                                <h2 class="play-section-title mb-0" style="padding-left: 0; color: #1e293b; font-size: 24px; font-weight: 700;">{title}</h2>"""
    
    if link:
        left_col += f"""
                                <div class="mt--20">
                                    <a {link}
                                </div>"""
    
    left_col += """
                            </div>
                            <div class="d-flex justify-content-start gap-3 mt--30">
                                <div class="play-custom-prev" style="width: 40px; height: 40px; background: rgba(0,0,0,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #1e293b;"><i class="feather-arrow-left"></i></div>
                                <div class="play-custom-next" style="width: 40px; height: 40px; background: rgba(0,0,0,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #1e293b;"><i class="feather-arrow-right"></i></div>
                            </div>"""

    # Fix loop slides
    loop = loop.replace('class="swiper-slide"', 'class="swiper-slide p-2" style="width: 320px;"')
    
    res = f"""{header}
            <div class="container">
                <div class="rbt-shadow-box" style="background-color: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                    <div class="row g-5 align-items-center">
                        <div class="col-lg-3 col-md-12">
                            {left_col}
                        </div>
                        <div class="col-lg-9 col-md-12">
                            <div class="swiper playSwiper-custom">
                                <div class="swiper-wrapper">
{loop}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>"""
    return res

# Pattern to match the sections BEFORE my previous edits (i.e. with padding-right: 5%)
pattern = r'(<section class="play-section[^"]*">)\s*<div class="d-flex justify-content-between align-items-center mb-3 pr-5" style="padding-right: 5%;">\s*<h2 class="play-section-title mb-0">([^<]+)</h2>(?:.*?(href="[^"]+" class="play-btn-link"[^>]*>[^<]*<i[^>]*></i>\s*</a>))?\s*</div>\s*<div class="swiper playSwiper">\s*<div class="swiper-wrapper">\s*(.*?)\s*</div>\s*<div class="swiper-button-next"></div>\s*<div class="swiper-button-prev"></div>\s*</div>\s*</section>'

new_content = re.sub(pattern, replace_section, content, flags=re.DOTALL)

with open('cursovideoapp/templates/cursovideo/home.html', 'w') as f:
    f.write(new_content)

print("Replaced standard playSwiper sections")

