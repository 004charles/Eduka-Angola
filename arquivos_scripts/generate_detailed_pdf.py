import os
import re
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, 'Eduka-Angola: Plano de Desenvolvimento Detalhado', border=0, ln=1, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

def clean_text(text):
    # Replace special characters that might cause encoding issues with standard fonts
    replacements = {
        '→': '->',
        '•': '*',
        '—': '-',
        '–': '-',
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'",
        chr(149): '*',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Remove any other non-latin1 characters if necessary
    return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf(input_path, output_path):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = clean_text(content)
    lines = content.split('\n')

    pdf.set_font('helvetica', size=11)
    
    for line in lines:
        line = line.strip()
        
        # Heading 1
        if line.startswith('# '):
            pdf.ln(5)
            pdf.set_font('helvetica', 'B', 16)
            pdf.multi_cell(0, 10, line[2:])
            pdf.set_font('helvetica', size=11)
            pdf.ln(2)
        # Heading 2
        elif line.startswith('## '):
            pdf.ln(4)
            pdf.set_font('helvetica', 'B', 14)
            pdf.multi_cell(0, 10, line[3:])
            pdf.set_font('helvetica', size=11)
            pdf.ln(1)
        # Heading 3
        elif line.startswith('### '):
            pdf.ln(2)
            pdf.set_font('helvetica', 'B', 12)
            pdf.multi_cell(0, 10, line[4:])
            pdf.set_font('helvetica', size=11)
        # List items
        elif line.startswith('- ') or line.startswith('* '):
            pdf.set_x(15)
            pdf.multi_cell(0, 6, "* " + line[2:])
        # Tables (Very basic)
        elif line.startswith('|'):
            pdf.set_font('helvetica', 'B', 10)
            pdf.multi_cell(0, 6, line)
            pdf.set_font('helvetica', size=11)
        # Normal text
        elif line:
            # Handle markdown links [text](link) - just keep text
            line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
            # Handle bold **text**
            parts = re.split(r'(\*\*[^*]+\*\*)', line)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    pdf.set_font('helvetica', 'B', 11)
                    pdf.write(6, part[2:-2])
                    pdf.set_font('helvetica', size=11)
                else:
                    pdf.write(6, part)
            pdf.ln(6)
        else:
            pdf.ln(2)

    pdf.output(output_path)
    print(f"PDF criado em: {output_path}")

if __name__ == "__main__":
    input_file = "/home/ox4-ti/.gemini/antigravity/brain/920fb1b2-3b22-488d-acdb-4d1dc85a04ca/implementation_plan.md"
    output_file = "/home/ox4-ti/Eduka-Angola/Guia_Desenvolvimento_EdukaAngola.pdf"
    create_pdf(input_file, output_file)
