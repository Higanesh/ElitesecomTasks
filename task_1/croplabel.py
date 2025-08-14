from pypdf import PdfReader,PdfWriter
import requests
import io

# -------------------------------------------------------
# Step 1: PDF URL (Change this to your desired PDF link)
# -------------------------------------------------------
pdf_url = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/389/434849072.pdf?request-content-type=application/force-download"

# -------------------------------------------------------
# Step 2: Download PDF from URL
# -------------------------------------------------------
response = requests.get(pdf_url)
if response.status_code != 200:
    raise Exception(f"❌ Failed to download {pdf_url}")

# Store PDF in memory (so we don't have to save it to disk)
pdf_bytes = io.BytesIO(response.content)

reader = PdfReader(pdf_bytes)
writer = PdfWriter()

crop_x1, crop_y1 = 0.05, 485.20
crop_x2, crop_y2 = 590.57, 124.46

for page in reader.pages:
    page.mediabox.lower_left = (crop_x1, crop_y1)
    page.mediabox.upper_right = (crop_x2, crop_y2)
    writer.add_page(page)

# Save cropped PDF
with open("cropped_label_1.pdf", "wb") as f:
    writer.write(f)