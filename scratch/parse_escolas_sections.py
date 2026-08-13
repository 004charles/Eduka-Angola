import json
import zlib
import base64
import re

def unpack_escolas(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    manifest_match = re.search(r'<script type="__bundler/manifest">\s*({.*?})\s*</script>', content, re.DOTALL)
    if manifest_match:
        manifest_json = json.loads(manifest_match.group(1))
        all_html = []
        for file_info in manifest_json.get('files', []):
            fname = file_info.get('name', '')
            if fname.endswith('.html'):
                raw_b64 = file_info.get('content', '')
                try:
                    compressed = base64.b64decode(raw_b64)
                    decompressed = zlib.decompress(compressed)
                    all_html.append(f"<!-- FILE: {fname} -->\n" + decompressed.decode('utf-8', errors='ignore'))
                except Exception as e:
                    print(f"Decompress error on {fname}:", e)
        
        full_html = "\n".join(all_html)
        with open('scratch/extracted_escolas_all.html', 'w', encoding='utf-8') as out:
            out.write(full_html)
        print("Unpacked bundle! Total size:", len(full_html))
    else:
        print("No bundler manifest found, copying raw html...")
        with open('scratch/extracted_escolas_all.html', 'w', encoding='utf-8') as out:
            out.write(content)

unpack_escolas(r'C:\Users\Muquissi\Downloads\edukangola-escolas-liceus.html')
