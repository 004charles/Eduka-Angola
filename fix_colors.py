import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace shadow box wrapper
    content = content.replace(
        '<div class="rbt-shadow-box" style="background-color: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">',
        '<div class="bg-color-white rbt-shadow-box" style="padding: 40px; border-radius: 12px;">'
    )
    
    # Remove hardcoded color from play-section-title
    content = re.sub(
        r'class="play-section-title([^"]*)" style="([^"]*)color: #1e293b;([^"]*)"',
        r'class="play-section-title\1 title" style="\2\3"',
        content
    )
    
    # Replace custom navigation buttons with standard theme buttons
    content = content.replace(
        '<div class="d-flex justify-content-start gap-3 mt--30">\n                                <div class="play-custom-prev" style="width: 40px; height: 40px; background: rgba(0,0,0,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #1e293b;"><i class="feather-arrow-left"></i></div>\n                                <div class="play-custom-next" style="width: 40px; height: 40px; background: rgba(0,0,0,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #1e293b;"><i class="feather-arrow-right"></i></div>\n                            </div>',
        '<div class="d-flex justify-content-start gap-3 rbt-arrow-between mt--30">\n                                <div class="rbt-swiper-arrow style_2 play-custom-prev">\n                                    <div class="custom-overfolow">\n                                        <i class="rbt-icon feather-arrow-left"></i>\n                                        <i class="rbt-icon-top feather-arrow-left"></i>\n                                    </div>\n                                </div>\n                                <div class="rbt-swiper-arrow style_2 play-custom-next">\n                                    <div class="custom-overfolow">\n                                        <i class="rbt-icon feather-arrow-right"></i>\n                                        <i class="rbt-icon-top feather-arrow-right"></i>\n                                    </div>\n                                </div>\n                            </div>'
    )

    with open(filepath, 'w') as f:
        f.write(content)

process_file('cursovideoapp/templates/cursovideo/home.html')

