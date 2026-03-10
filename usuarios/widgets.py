from django import forms
from django.utils.safestring import mark_safe

class ColorPickerWidget(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs, renderer)
        color_id = f"id_{name}_picker"
        return mark_safe(f'''
            <div style="display: flex; align-items: center; gap: 10px;">
                {output}
                <input type="color" id="{color_id}" 
                       value="{value if value else '#000000'}" 
                       style="width: 40px; height: 38px; border: 1px solid #ced4da; border-radius: 4px; padding: 2px;">
            </div>
            <script>
                document.getElementById("{color_id}").addEventListener("input", function(e) {{
                    document.getElementById("{attrs['id']}").value = e.target.value;
                }});
                document.getElementById("{attrs['id']}").addEventListener("input", function(e) {{
                    document.getElementById("{color_id}").value = e.target.value;
                }});
            </script>
        ''')
