from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

pdf_file = "sample.pdf"

c = canvas.Canvas(pdf_file, pagesize=A4)
c.setFont("Helvetica", 14)

# Top text at Y=780
c.drawString(100, 780, "This is the top text.")

# Bottom text at Y=730
c.drawString(100, 730, "This is the bottom text.")

c.save()
print(f"Created {pdf_file}")
