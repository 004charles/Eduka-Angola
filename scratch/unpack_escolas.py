import json
import zlib
import base64
import re

with open(r'C:\Users\Muquissi\Downloads\edukangola-escolas-liceus.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

manifest_match = re.search(r'<script type="__bundler/manifest">\s*({.*?})\s*</script>', content, re.DOTALL)
if manifest_match:
    manifest_data = json.loads(manifest_match.group(1))
    print("Found manifest with keys:", len(manifest_data))
    
    html_snippets = []
    for key, val in manifest_data.items():
        data_b64 = val.get('data', '')
        compressed = val.get('compressed', False)
        if data_b64:
            try:
                raw = base64.b64decode(data_b64)
                if compressed:
                    # try zlib / gzip decompress
                    try:
                        decompressed = zlib.decompress(raw, 16 + zlib.MAX_WBITS)
                    except Exception:
                        decompressed = zlib.decompress(raw)
                    text = decompressed.decode('utf-8', errors='ignore')
                else:
                    text = raw.decode('utf-8', errors='ignore')
                
                html_snippets.append(f"<!-- KEY: {key} ({val.get('mime')}) -->\n" + text)
            except Exception as e:
                print(f"Error unpacking {key}:", e)
                
    full_unpacked = "\n".join(html_snippets)
    with open('scratch/extracted_escolas_all.html', 'w', encoding='utf-8') as out:
        out.write(full_unpacked)
    print("Successfully unpacked! Total size:", len(full_unpacked))
