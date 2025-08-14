import fitz  # PyMuPDF

input_pdf = "label-1.pdf"
output_pdf = "sample_out.pdf"

# Open PDF
doc = fitz.open(input_pdf)
page = doc[0]

# Define source rectangle (known coords)
src_rect = fitz.Rect(415.52, 426.66, 500.82, 445.53)

# Extract text from this rectangle
copied_text = page.get_textbox(src_rect)
print("Copied text:", repr(copied_text))

# Paste text at destination
dest_point = (20, 270.84)  # x=100, y=680
page.insert_text(dest_point, copied_text, fontsize=10, color=(0, 0, 0))

# Save PDF
doc.save(output_pdf)
doc.close()
print(f"Saved {output_pdf}")
