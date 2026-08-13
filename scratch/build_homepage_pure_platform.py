import re

with open('scratch/extracted_homepage_all.html', 'r', encoding='utf-8') as f:
    raw_html = f.read()

# Locate main content container in the drawing HTML
body_content_match = re.search(r'(<div style="width: 1440px; margin: 0 auto; background: #F1EDE4">[\s\S]*?</div>\s*</div>)', raw_html)
if body_content_match:
    print("Found main container in drawing HTML!")
else:
    print("Main container search fallback...")
