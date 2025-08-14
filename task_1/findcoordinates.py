import fitz  # PyMuPDF

pdf_path = "label-1.pdf"  # or your PDF
doc = fitz.open(pdf_path)
page = doc[0]  # first page

# Get all text blocks
blocks = page.get_text("blocks")

print("\nAll text blocks with coordinates:")
for i, b in enumerate(blocks):
    x0, y0, x1, y1, text, block_no = b[0], b[1], b[2], b[3], b[4], b[5]
    print(f"Block {i}: Rect=({x0:.2f}, {y0:.2f}, {x1:.2f}, {y1:.2f})  Text={repr(text)}")

doc.close()
