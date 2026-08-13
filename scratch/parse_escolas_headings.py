import re

with open('scratch/extracted_escolas_all.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Find headings h1, h2, h3, h4 and section titles
headings = re.findall(r'<(h[1-6]|div|span)[^>]*style="[^"]*font-(?:size|family)[^"]*"[^>]*>(.*?)</\1>', text, re.DOTALL)
print("Found headings/styled elements:", len(headings))

for tag, content in headings[:40]:
    clean = re.sub(r'<[^>]+>', '', content).strip()
    if clean and len(clean) < 100:
        print(f"[{tag}] {clean}")
