import fitz  # PyMuPDF for reading/editing PDFs
from pypdf import PdfReader, PdfWriter  # For cropping PDFs
import requests
import io

# -------------------------------------------------------
# Step 1: PDF URL (Change this to your desired PDF link)
# -------------------------------------------------------
pdf_url = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/389/434849072.pdf?request-content-type=application/force-download"

# -------------------------------------------------------
# Step 2: Download PDF from URL into memory
# -------------------------------------------------------
response = requests.get(pdf_url)
if response.status_code != 200:
    raise Exception(f"❌ Failed to download PDF from {pdf_url}")

# Store PDF in BytesIO (keeps it in memory, no temp file needed)
pdf_bytes = io.BytesIO(response.content)

# -------------------------------------------------------
# Step 3: Open the PDF in PyMuPDF
# -------------------------------------------------------
output_pdf = "copy_and_paste_cropped_label.pdf"
doc = fitz.open(stream=pdf_bytes.getvalue(), filetype="pdf")

# Get the first page (index starts from 0)
page = doc[0]

# -------------------------------------------------------
# Step 4: Define coordinates to COPY text from
# Coordinates format: (x1, y1, x2, y2) in points
# -------------------------------------------------------
src_rect = fitz.Rect(415.52, 426.66, 500.82, 445.53)

# Extract text from the source rectangle
copied_text = page.get_textbox(src_rect)
print("Copied text:", repr(copied_text))

# -------------------------------------------------------
# Step 5: PASTE copied text at the desired coordinates
# dest_point = (x, y)
# -------------------------------------------------------
dest_point = (20, 270.84)
page.insert_text(
    dest_point,
    copied_text,
    fontsize=10,         # Adjust font size if needed
    color=(0, 0, 0)      # Black color
)

# -------------------------------------------------------
# Step 6: Save the modified PDF
# -------------------------------------------------------
doc.save(output_pdf)
doc.close()
print(f"✅ Text copied & pasted. Saved as {output_pdf}")

# -------------------------------------------------------
# Step 7: CROP the PDF to the desired rectangle
# -------------------------------------------------------
reader = PdfReader(output_pdf)
writer = PdfWriter()

# Define crop box coordinates (x1, y1, x2, y2)
crop_x1, crop_y1 = 0.05, 485.20
crop_x2, crop_y2 = 590.57, 124.46

# Apply cropping to each page
for page in reader.pages:
    page.mediabox.lower_left = (crop_x1, crop_y1)
    page.mediabox.upper_right = (crop_x2, crop_y2)
    writer.add_page(page)

# -------------------------------------------------------
# Step 8: Save the cropped PDF
# -------------------------------------------------------
with open(output_pdf, "wb") as f:
    writer.write(f)

print(f"✅ Cropped PDF saved as {output_pdf}")
