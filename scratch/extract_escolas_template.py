import re
import json

with open(r'C:\Users\Muquissi\Downloads\edukangola-escolas-liceus.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

template_match = re.search(r'<script type="__bundler/template">\s*(.*?)\s*</script>', content, re.DOTALL)
if template_match:
    raw_str = template_match.group(1).strip()
    try:
        html_content = json.loads(raw_str)
    except Exception:
        html_content = raw_str

    with open('scratch/extracted_escolas_drawing.html', 'w', encoding='utf-8') as out:
        out.write(html_content)
    print("SUCCESS! Saved template drawing HTML. Size:", len(html_content))
else:
    print("No bundler template found.")
