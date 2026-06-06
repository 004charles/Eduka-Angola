import os

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # If already applied, skip
    if 'unfold.admin' in content:
        print(f"Skipping {filepath} (already applied)")
        return

    # Check if this file uses admin classes
    if 'admin.ModelAdmin' not in content and 'admin.TabularInline' not in content and 'admin.StackedInline' not in content:
        return

    print(f"Updating {filepath}...")

    # Insert imports
    if 'from django.contrib import admin' in content:
        content = content.replace(
            'from django.contrib import admin',
            'from django.contrib import admin\nfrom unfold.admin import ModelAdmin as UnfoldModelAdmin\nfrom unfold.admin import TabularInline as UnfoldTabularInline\nfrom unfold.admin import StackedInline as UnfoldStackedInline'
        )
    elif 'import django.contrib.admin' in content:
        content = content.replace(
            'import django.contrib.admin',
            'import django.contrib.admin\nfrom unfold.admin import ModelAdmin as UnfoldModelAdmin\nfrom unfold.admin import TabularInline as UnfoldTabularInline\nfrom unfold.admin import StackedInline as UnfoldStackedInline'
        )
    else:
        # Fallback if admin is imported differently, just add to top
        content = 'from unfold.admin import ModelAdmin as UnfoldModelAdmin\nfrom unfold.admin import TabularInline as UnfoldTabularInline\nfrom unfold.admin import StackedInline as UnfoldStackedInline\n' + content

    # Replace classes
    content = content.replace('admin.ModelAdmin', 'UnfoldModelAdmin')
    content = content.replace('admin.TabularInline', 'UnfoldTabularInline')
    content = content.replace('admin.StackedInline', 'UnfoldStackedInline')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    base_dir = r"c:\Users\Muquissi\Documents\Eduka-Angola"
    for root, dirs, files in os.walk(base_dir):
        if '.venv' in root or '.git' in root or 'arquivos_scripts' in root:
            continue
        for file in files:
            if file == 'admin.py':
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
