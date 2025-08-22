from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

new_text = "New data added"

packet = BytesIO()
c = canvas.Canvas(packet,pagesize=A4)
c.drawString(100,300,new_text)
c.save()
packet.seek(0)

existing_pdf = PdfReader("sample.pdf")
overlay_pdf = PdfReader(packet)
output = PdfWriter()

page = existing_pdf.pages[0]
page.merge_page(overlay_pdf.pages[0])
output.add_page(page)

with open("updated.pdf","wb") as f:
    output.write(f)