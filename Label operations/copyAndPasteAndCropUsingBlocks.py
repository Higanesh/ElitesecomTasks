import fitz  # PyMuPDF - Library for reading and editing PDFs
import requests
import io

# ------------------------------
# Step 1: Download PDF from URL
# ------------------------------
pdf_url = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/434861925.pdf?request-content-type=application/force-download"

# Send GET request to download PDF
response = requests.get(pdf_url)
if response.status_code != 200:
    raise Exception(f"❌ Failed to download PDF from: {pdf_url}")

# Load PDF into PyMuPDF document object
pdf_bytes = io.BytesIO(response.content)
doc = fitz.open(stream=pdf_bytes.getvalue(), filetype="pdf")

# ------------------------------
# Step 2: Extract complete text from the PDF
# ------------------------------
full_text = ""
for page_num in range(len(doc)):
    full_text += doc[page_num].get_text()

# Store text as tuple for consistency
pdf_text_tuple = (full_text,)

# Define keywords to locate "Order Date" section
start_keyword = "Order Date"
end_keyword = "Invoice Date"

# Find positions of keywords in extracted text
text_str = pdf_text_tuple[0]
start_index = text_str.find(start_keyword)
end_index = text_str.find(end_keyword)

# Extract the text between keywords
if start_index != -1 and end_index != -1:
    extracted_order_date = text_str[start_index:end_index].strip()
    extracted_order_date = extracted_order_date.replace("\n", " ")  # Remove newlines
else:
    raise Exception("❌ 'Order Date' section not found in PDF text.")

print("✅ Extracted Order Date block:", extracted_order_date)

# ------------------------------
# Step 3: Insert extracted "Order Date" text after a specific label
# ------------------------------
page = doc[0]  # Working on first page only
blocks = page.get_text("blocks")  # Get all text blocks with positions

target_block_text = "If undelivered, return to:"
target_rect = None # will store the coordinates of this text once found

# Locate the coordinates of the target block
for b in blocks:
    if target_block_text in b[4]:
        target_rect = fitz.Rect(b[:4])  # Save rectangle position
        break

if target_rect is None:
    raise Exception("❌ Target block not found in PDF.")

# Decide where to insert new text (just below target block)
insert_x = target_rect.x0
insert_y = target_rect.y1 + 10  # 10 points padding below

# Insert extracted "Order Date" into PDF
page.insert_text(
    (insert_x, insert_y),
    extracted_order_date,
    fontsize=10,
    fontname="helv"
)

# ------------------------------
# Step 4: Crop PDF before the "TAX INVOICE" section
# ------------------------------
tax_index = None
for i, block in enumerate(blocks):
    if "TAX INVOICE" in block[4].upper():
        tax_index = i
        break

if tax_index is not None:
    # Top edge of the page
    top_y = page.mediabox.y0
    
    # Bottom edge: just above TAX INVOICE block
    padding = 3  # Small offset to avoid including border/line
    bottom_y = blocks[tax_index][1] - padding

    # Full page width
    x0 = page.mediabox.x0
    x1 = page.mediabox.x1

    # Define cropping rectangle
    crop_area = fitz.Rect(x0, top_y, x1, bottom_y)
    crop_area = crop_area & page.mediabox  # Ensure crop is within page bounds

    # Apply crop to page
    page.set_cropbox(crop_area)

    print("✅ Cropped PDF before TAX INVOICE.")
else:
    print("❌ TAX INVOICE block not found. No cropping applied.")

# ------------------------------
# Step 5: Save Final Modified PDF
# ------------------------------
output_path = r"D:\myProjects\ElitesecomTasks\Output PDFs\cropped_invoice.pdf"
doc.save(output_path)
doc.close()

print(f"✅ Final PDF saved as: {output_path}")



"""
PDF Processing Script – Explanation
Purpose

This Python script:

Downloads a PDF from a given URL.

Extracts the "Order Date" section from the PDF text.

Inserts this extracted date below a specific label ("If undelivered, return to:") in the PDF.

Crops the PDF to remove everything after the "TAX INVOICE" section.

Saves the modified PDF to a local file.

Libraries Used

fitz (PyMuPDF): Read, edit, and manipulate PDF files.

requests: Download PDF from the internet.

io: Handle PDF data in memory without saving to disk.

Step-by-Step Flow
1. Download PDF
response = requests.get(pdf_url)
doc = fitz.open(stream=response.content, filetype="pdf")


Fetches the PDF from the given URL.

Loads it directly into memory without saving it first.

2. Extract Complete PDF Text
full_text = ""
for page_num in range(len(doc)):
    full_text += doc[page_num].get_text()


Reads all text from the PDF pages.

Stores it in a single string for searching.

3. Find “Order Date” Section
start_index = text_str.find("Order Date")
end_index = text_str.find("Invoice Date")
extracted_order_date = text_str[start_index:end_index].strip()


Locates the text starting from “Order Date” up to “Invoice Date”.

Cleans the text by removing unwanted newlines.

4. Insert “Order Date” in PDF
for b in blocks:
    if "If undelivered, return to:" in b[4]:
        target_rect = fitz.Rect(b[:4])
insert_x = target_rect.x0
insert_y = target_rect.y1 + 10
page.insert_text((insert_x, insert_y), extracted_order_date)


Finds the position of “If undelivered, return to:” block.

Inserts the extracted Order Date just below it.

5. Crop Before “TAX INVOICE”
for i, block in enumerate(blocks):
    if "TAX INVOICE" in block[4].upper():
        bottom_y = blocks[i][1] - 3
        crop_area = fitz.Rect(x0, top_y, x1, bottom_y)
        page.set_cropbox(crop_area)


Searches for the “TAX INVOICE” block.

Crops the page so that everything below it is removed.

6. Save Final PDF
doc.save(output_path)
doc.close()


Saves the modified PDF locally.

Example Output

Original PDF: Full document including invoice section.

Modified PDF:

"Order Date" inserted under “If undelivered, return to:”

Invoice section completely removed.

Benefits

Fully automated: No manual PDF editing.

Works directly from an online PDF link.

Easy to adapt for other keyword-based extractions and insertions.
"""