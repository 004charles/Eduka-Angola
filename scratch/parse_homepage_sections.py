import json
import zlib
import base64
import re

def unpack_bundle(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    manifest_match = re.search(r'<script type="__bundler/manifest">\s*({.*?})\s*</script>', content, re.DOTALL)
    template_match = re.search(r'<script type="__bundler/template">\s*("(?:[^"\\]|\\.)*")\s*</script>', content, re.DOTALL)

    if not manifest_match or not template_match:
        print("Erro: script tags do bundler nao encontradas via regex!")
        return

    manifest = json.loads(manifest_match.group(1))
    template = json.loads(template_match.group(1))

    decoded_manifest = {}
    for uuid, entry in manifest.items():
        data_bytes = base64.b64decode(entry['data'])
        if entry.get('compressed'):
            try:
                data_bytes = zlib.decompress(data_bytes, 15 + 32)
            except Exception:
                try:
                    data_bytes = zlib.decompress(data_bytes, -15)
                except Exception as e:
                    print(f"Failed to decompress {uuid}: {e}")

        try:
            decoded_manifest[uuid] = data_bytes.decode('utf-8')
        except Exception:
            decoded_manifest[uuid] = f"data:{entry.get('mime')};base64," + entry['data']

    final_html = template
    for uuid, val in decoded_manifest.items():
        if isinstance(val, str) and not val.startswith("data:"):
            if uuid in final_html:
                final_html = final_html.replace(uuid, val)

    with open('scratch/extracted_homepage_all.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

    headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', final_html, re.DOTALL)
    print("Found Headings in Homepage HTML:")
    for h in headings:
        clean_h = re.sub(r'<[^>]+>', '', h).strip()
        if clean_h:
            print(" -", clean_h)

if __name__ == "__main__":
    unpack_bundle(r"C:\Users\Muquissi\Downloads\edukangola-homepage.html")
