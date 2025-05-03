from markdown_pdf import Section, MarkdownPdf

class MarkdownToPDF:
    def __init__(self, pdf_name='pdf_report.pdf'):
        self.pdf_path = '/app/.temp/pdf/' + pdf_name
        self.pdf = MarkdownPdf(toc_level=1, optimize=True)
        self.pdf.meta['title'] = 'Reporte'
        self.pdf.meta['author'] = 'Kersys API'

    def add_page(self, text):
        self.pdf.add_section(Section(text))
    
    def save(self):
        try:
            self.pdf.save(self.pdf_path)
        except Exception as e:
            print('ERROR: Erro ao tentar salvar o PDF no path: ', self.pdf_path)
            self.pdf.save('pdf_report.pdf')
