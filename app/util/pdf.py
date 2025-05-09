import os
from markdown_pdf import Section, MarkdownPdf

class MarkdownToPDF:
    def __init__(self, pdf_name='relatorio.pdf'):
        self.pdf_path = f'{os.getenv("TEMPORARY_FOLDER_PATH")}/pdf/' + pdf_name
        self.pdf = MarkdownPdf(toc_level=1, optimize=True)
        self.pdf.meta['title'] = 'Reporte'
        self.pdf.meta['author'] = 'Kersys API'
    
    def get_path(self):
        return self.pdf_path

    def add_page(self, text):
        self.pdf.add_section(Section(text))
    
    def save(self):
        self.pdf.save(self.pdf_path)
