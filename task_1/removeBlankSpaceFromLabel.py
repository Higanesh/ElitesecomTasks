import fitz  # PyMuPDF library for PDF processing
import random  # Used for generating random numbers for sample text
import io
import requests  # For downloading the PDF from a URL

# -------------------------------------------------------
# Step 1: PDF URL (Change this to your desired PDF link)
# -------------------------------------------------------
pdf_url = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/437165474.pdf?request-content-type=application/force-download"

# -------------------------------------------------------
# Step 2: Download PDF from URL
# -------------------------------------------------------
response = requests.get(pdf_url)
if response.status_code != 200:
    raise Exception(f"❌ Failed to download {pdf_url}")

# Load PDF into PyMuPDF document object
pdf_bytes = io.BytesIO(response.content)
doc = fitz.open(stream=pdf_bytes.getvalue(), filetype="pdf")

# Output PDF path (where the processed file will be saved)
output_pdf = r"D:\myProjects\ElitesecomTasks\Output PDFs\cropped_with_text.pdf"

# ===== Step 1: Open the PDF =====
# doc = fitz.open(input_pdf)   # Load the PDF into memory
page = doc[0]                # Access the first (and only) page of the PDF

# ===== Step 2: Get all text blocks =====
# `get_text("blocks")` returns a list of tuples:
# (x0, y0, x1, y1, "text", block_no, block_type)
# Where:
#   x0, y0 → top-left coordinates of the block
#   x1, y1 → bottom-right coordinates of the block
#   text   → the actual text content in the block
blocks = page.get_text("blocks")

# If no text is found in the page, stop the script
if not blocks:
    raise Exception("❌ No text found in PDF.")

# Find the first (top-most) text block based on `y0` (smallest vertical value)
first_block = min(blocks, key=lambda b: b[1])

# Find the last (bottom-most) text block based on `y1` (largest vertical value)
last_block = max(blocks, key=lambda b: b[3])


# ===== Step 3: Insert random text at the TOP =====
# Create random top text
random_top_text = "Random Top Text: " + str(random.randint(1000, 9999))

# Position it 12 points from the left page border
top_insert_x = page.rect.x0 + 12

# Position it slightly above the first text block (-5 points from top of first block)
top_insert_y = first_block[1] - 5

# Insert the top text at calculated coordinates
page.insert_text(
    (top_insert_x, top_insert_y),  # Position (x, y)
    random_top_text,               # Text to insert
    fontsize=12,                   # Font size
    fontname="helv",                # Font type (Helvetica)
    fill=(0, 0, 0)                  # Font color (black)
)

# ===== Step 4: Insert random text at the BOTTOM =====
random_bottom_text = "Random Bottom Text: " + str(random.randint(1000, 9999))

# Left align with a 12-point margin
bottom_insert_x = page.rect.x0 + 12

# Place it slightly below the last existing block (+15 points)
bottom_insert_y = last_block[3] + 15

# Insert the bottom text
page.insert_text(
    (bottom_insert_x, bottom_insert_y),
    random_bottom_text,
    fontsize=12,
    fontname="helv",
    fill=(0, 0, 0)
)

# ===== Step 5: Crop only the bottom blank space =====
# Recalculate text blocks after adding the new bottom text
blocks_after = page.get_text("blocks")

# Find the bottom-most text position (largest y1)
last_y_after = max(b[3] for b in blocks_after)

# Create a new rectangle to define the visible page area:
#   Keep left, right, and top exactly the same
#   Set the bottom just slightly (5 points) after the last content
crop_rect = fitz.Rect(
    page.rect.x0,      # Left edge
    page.rect.y0,      # Top edge
    page.rect.x1,      # Right edge
    last_y_after + 5   # Bottom edge
)

# Apply cropping to the page
page.set_cropbox(crop_rect)

# ===== Step 6: Save the processed PDF =====
doc.save(output_pdf)
print(f"✅ Cropped PDF saved to: {output_pdf}")