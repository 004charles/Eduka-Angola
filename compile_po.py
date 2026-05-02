
import os
import struct
import codecs

def unescape(s):
    # Handle basic escapes found in .po files
    return s.encode('utf-8').decode('unicode_escape')

def compile_po(po_file, mo_file):
    messages = {}
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('msgid "'):
            mid = line[7:-1]
            i += 1
            while i < len(lines) and lines[i].strip().startswith('"'):
                mid += lines[i].strip()[1:-1]
                i += 1
            
            # Now find msgstr
            while i < len(lines) and not lines[i].strip().startswith('msgstr "'):
                i += 1
            
            if i < len(lines):
                line = lines[i].strip()
                mstr = line[8:-1]
                i += 1
                while i < len(lines) and lines[i].strip().startswith('"'):
                    mstr += lines[i].strip()[1:-1]
                    i += 1
                
                # UNESCAPE BOTH
                try:
                    mid_un = unescape(mid)
                    mstr_un = unescape(mstr)
                    messages[mid_un] = mstr_un
                except:
                    messages[mid] = mstr
            else:
                break
        else:
            i += 1

    if not messages:
        return

    # Sort messages
    keys = sorted(messages.keys())
    offsets = []
    ids = b''
    strs = b''

    for key in keys:
        k_bytes = key.encode('utf-8')
        s_bytes = messages[key].encode('utf-8')
        offsets.append((len(ids), len(k_bytes), len(strs), len(s_bytes)))
        ids += k_bytes + b'\0'
        strs += s_bytes + b'\0'

    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    
    output = struct.pack('<Iiiiiii',
                         0x950412de,
                         0,
                         len(keys),
                         28,
                         28 + len(keys) * 8,
                         0, 0)

    for start, length, _, _ in offsets:
        output += struct.pack('<ii', length, keystart + start)
    for _, _, start, length in offsets:
        output += struct.pack('<ii', length, valuestart + start)
    
    output += ids
    output += strs

    with open(mo_file, 'wb') as f:
        f.write(output)

if __name__ == '__main__':
    base_locale = 'locale'
    for lang in os.listdir(base_locale):
        po_path = os.path.join(base_locale, lang, 'LC_MESSAGES', 'django.po')
        if os.path.exists(po_path):
            mo_path = os.path.join(base_locale, lang, 'LC_MESSAGES', 'django.mo')
            print(f"Compiling {po_path} -> {mo_path}")
            try:
                compile_po(po_path, mo_path)
            except Exception as e:
                print(f"Error compiling {lang}: {e}")
