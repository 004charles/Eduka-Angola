import os
import polib

def compile_translations():
    locale_dir = 'locale'
    for root, dirs, files in os.walk(locale_dir):
        for file in files:
            if file.endswith('.po'):
                po_path = os.path.join(root, file)
                mo_path = po_path.replace('.po', '.mo')
                try:
                    po = polib.pofile(po_path)
                    po.save_as_mofile(mo_path)
                    print(f'Compiled {po_path} -> {mo_path}')
                except Exception as e:
                    print(f'Error compiling {po_path}: {e}')

if __name__ == "__main__":
    compile_translations()
