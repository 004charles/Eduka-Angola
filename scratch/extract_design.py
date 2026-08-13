import re
import json

html_path = r"c:\Users\Muquissi\Pictures\Eduka-Angola\scratch\edukangola_design\EdukAngola App do Aluno (offline).html"
output_path = r"c:\Users\Muquissi\Pictures\Eduka-Angola\scratch\extracted_code.txt"

print("Reading HTML file...")
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

print("Searching for __bundler/template...")
template_match = re.search(r'<script type="__bundler/template">(.*?)</script>', content, re.DOTALL)
if template_match:
    template_str = template_match.group(1).strip()
    try:
        template_data = json.loads(template_str)
        print("Template extracted! Saving to extracted_code.txt...")
        with open(output_path, "w", encoding="utf-8") as out:
            out.write(template_data)
        print("Done!")
    except Exception as e:
        print("Error parsing template JSON:", e)
else:
    print("Could not find template tag!")
