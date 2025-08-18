import fitz  # PyMuPDF
import requests
import io

# PDF URL
pdf_url = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/389/434849072.pdf?request-content-type=application/force-download"

# Download PDF
response = requests.get(pdf_url)
if response.status_code != 200:
    raise Exception(f"❌ Failed to download {pdf_url}")

pdf_bytes = io.BytesIO(response.content)
doc = fitz.open(stream=pdf_bytes.getvalue(), filetype="pdf")
page = doc[0]

# Extract text blocks
blocks = page.get_text("blocks")

# Find TAX INVOICE block
tax_index = None
for i, block in enumerate(blocks):
    if "TAX INVOICE" in block[4].upper():
        tax_index = i
        break

if tax_index is not None:
    # Top of page
    top_y = page.mediabox.y0

    # Bottom = top of TAX INVOICE block (exclude it)
    # Subtract a small padding to fully remove its border/line
    padding = 3  # points (you can increase if needed)
    bottom_y = blocks[tax_index][1] - padding

    # Page width
    x0 = page.mediabox.x0
    x1 = page.mediabox.x1

    # Create crop area
    crop_area = fitz.Rect(x0, top_y, x1, bottom_y)
    crop_area = crop_area & page.mediabox  # ensure valid bounds

    # Apply crop
    page.set_cropbox(crop_area)

    # Save
    doc.save(r"D:\myProjects\ElitesecomTasks\Output PDFs\cropped_invoice.pdf")
    print("✅ Cropped PDF saved: from start until before TAX INVOICE.")
else:
    print("❌ TAX INVOICE block not found.")
