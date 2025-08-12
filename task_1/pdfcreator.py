from fpdf import FPDF

# create FPDF object
# Pdf layout like (portrait or landscape)
# Unit for margins (mm, cm, inch)
# format (letter, A4 (default), A3, Legal)
pdf = FPDF('P', 'mm')

# add a page
pdf.add_page()

# specify font (eg. times, courier, helvetica, symbol etc.)
# bold, underline, italics
pdf.set_font('helvetica', '', 16)

# Add text with its width & height, text, newline
pdf.cell(40,10, "Hello World!", ln=True)
pdf.cell(40,10, "Good Bye World!", ln=True)
pdf.cell(40,10, "Hello Ganesh!")
pdf.cell(40,240, "Crop pdf")

pdf.output('sample.pdf')

