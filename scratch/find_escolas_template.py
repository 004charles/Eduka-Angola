import re

with open('scratch/extracted_escolas_all.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Find <x-dc> or template content
x_dc_matches = re.findall(r'<x-dc[^>]*>(.*?)</x-dc>', text, re.DOTALL)
print("x-dc matches:", len(x_dc_matches))

if x_dc_matches:
    with open('scratch/extracted_escolas_xdc.html', 'w', encoding='utf-8') as out:
        out.write(x_dc_matches[0])
    print("Saved x-dc content! Size:", len(x_dc_matches[0]))
else:
    # Search for any <div style= or html blocks
    div_matches = re.findall(r'<div[^>]*style="[^"]*background:[^"]*"[^>]*>.*', text)
    print("Div matches:", len(div_matches))
