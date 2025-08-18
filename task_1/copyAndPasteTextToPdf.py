"""
Script Name: update_order_date.py
Purpose:
    - Download a PDF from a given URL
    - Extract the "Order Date" section
    - Place it right after the "If undelivered, return to:" block in the PDF
"""

import fitz  # PyMuPDF - Library for PDF manipulation
import requests  # To download the PDF from a URL
import io  # For handling in-memory binary streams

# ------------------------------
# Step 1: Download PDF from URL
# ------------------------------
pdf_url = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/434861925.pdf?request-content-type=application/force-download"

response = requests.get(pdf_url)
if response.status_code != 200:
    raise Exception(f"❌ Failed to download PDF from: {pdf_url}")

# Store the downloaded file in memory (BytesIO object)
pdf_bytes = io.BytesIO(response.content)

# Open the PDF with PyMuPDF
doc = fitz.open(stream=pdf_bytes.getvalue(), filetype="pdf")

# ------------------------------
# Step 2: Extract all text from PDF
# ------------------------------
full_text = ""
for page_num in range(len(doc)):
    full_text += doc[page_num].get_text()  # Append text from each page

# Store PDF text in a tuple (optional)
pdf_text_tuple = (full_text,)

# ------------------------------
# Step 3: Extract "Order Date" block
# ------------------------------
text_str = pdf_text_tuple[0]  # Convert tuple → string
start_keyword = "Order Date"
end_keyword = "Invoice Date"

# Find indexes of keywords
start_index = text_str.find(start_keyword)
end_index = text_str.find(end_keyword)

if start_index != -1 and end_index != -1:
    extracted_order_date = text_str[start_index:end_index].strip()
    extracted_order_date = extracted_order_date.replace("\n", " ")  # Make it single line
else:
    raise Exception("❌ 'Order Date' section not found in PDF text.")

print("✅ Extracted Order Date block:", extracted_order_date)

# ------------------------------
# Step 4: Find "If undelivered" block position
# ------------------------------
page = doc[0]  # First page
blocks = page.get_text("blocks")  # List of (x0, y0, x1, y1, text, ...)

target_block_text = "If undelivered, return to:"
target_rect = None

# Search for the exact block
for b in blocks:
    if target_block_text in b[4]:  # b[4] contains the text
        target_rect = fitz.Rect(b[:4])  # Get coordinates
        break

if target_rect is None:
    raise Exception("❌ Target block not found in PDF.")

# ------------------------------
# Step 5: Insert extracted text after the block
# ------------------------------
insert_x = target_rect.x0
insert_y = target_rect.y1 + 10  # A little gap after block

page.insert_text(
    (insert_x, insert_y),
    extracted_order_date,
    fontsize=10,
    fontname="helv"
)

# ------------------------------
# Step 6: Save updated PDF
# ------------------------------
output_path = "final_updated_order_date.pdf"
doc.save(output_path)
doc.close()

print(f"✅ Updated PDF saved as: {output_path}")





"""
Mini Explanation Document for Presentation

Title: Automating Order Date Placement in PDF Labels

Objective:
The script automates reading a PDF from a URL, extracting the Order Date section, and placing it right after a specific text block inside the PDF.

Steps Overview:

Download the PDF

Uses requests to fetch the PDF directly from a given link.

Stores it in memory using io.BytesIO (no local temp file needed).

Extract Text

Loops through all PDF pages and combines the text into one string.

Stores text in a tuple for easy handling.

Find & Clean the Order Date

Locates "Order Date" and "Invoice Date" in the text.

Extracts the content between them.

Converts multi-line text into a single line.

Locate Target Block

Searches for "If undelivered, return to:" in the page's text blocks.

Gets the exact coordinates of the block.

Insert Order Date

Adds the extracted date just below the target block using PyMuPDF’s insert_text().

Save Updated PDF

Saves the modified file locally with the name final_updated_order_date.pdf.

Key Benefits:

Automated Process – No manual PDF editing.

Precise Placement – Uses actual block coordinates for accuracy.

Reusable – Works with any PDF having the same structure.

Lightweight – No heavy PDF editing tools required.
"""