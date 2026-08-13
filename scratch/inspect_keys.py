import re

with open('scratch/extracted_escolas_all.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

parts = text.split('<!-- KEY:')
print("Total keys found in unpacked html:", len(parts))

for i, p in enumerate(parts[1:], 1):
    header = p.split('\n')[0]
    snippet = p[:300].replace('\n', ' ')
    print(f"\n--- PART {i}: {header} ---")
    print(snippet[:150])
