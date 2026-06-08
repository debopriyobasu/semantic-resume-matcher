from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'John Doe Resume', border=False, ln=1, align='C')

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', border=False, ln=1, align='C')

pdf = PDF()
pdf.add_page()
pdf.set_font('helvetica', '', 12)
pdf.multi_cell(0, 10, txt="""
Skills:
- Python
- FastAPI
- Docker
- SQL
- Machine Learning

Experience:
- Senior Backend Engineer at TechCorp (2018 - Present)
  Built robust backend APIs with Python and FastAPI.
  Integrated LLMs and Vector Search using pgvector.
- Software Engineer at StartUp (2015 - 2018)
  Developed microservices and managed database schemas.

Education:
- B.S. Computer Science, State University, 2015

Location: New York, USA
Preferred Remote: True
""")
pdf.output('resume.pdf')
