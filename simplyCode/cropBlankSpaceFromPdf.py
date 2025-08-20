import fitz
import random
import requests

pdf_urls = "https://ee-uploaded-files.s3.ap-south-1.amazonaws.com/Labels/388/437165474.pdf?request-content-type=application/force-download"
output_pdf = "cropped_output_self.pdf"

def download_and_crop_pdf(url):
    try:
        # Download the PDF
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
    except Exception as e:
        print(f"Failed to download PDF Internet Issue: {e}")
        return None  # or handle gracefully
    
    try:
        doc = fitz.open(stream=response.content, filetype="pdf")
    except Exception as e:
        raise Exception(f"Failed to open PDF: {e}")
    
    page = doc[0]  # Get the first page
    blocks = page.get_text("blocks")
    if not blocks:
        raise Exception("No text blocks found in the PDF.")
    try:
        first_block = min(blocks, key=lambda b: b[1])
        last_block  = max(blocks, key=lambda b: b[3])

        page.insert_text((page.rect.x0 + 12, first_block[1] - 5),
                        f"Random Top Text: {random.randint(1000,9999)}",
                        fontsize=12, fontname="helv", fill=(0,0,0))
        
        page.insert_text((page.rect.x0 + 12, last_block[3] + 15),
                        f"Random Bottom Text: {random.randint(1000,9999)}",
                        fontsize=12, fontname="helv", fill=(0,0,0))
    except Exception as e:
        raise Exception(f"Failed to insert text in PDF: {e}")
    
    try:
    # Crop the page to the area between the first and last blocks
        crop_rect = fitz.Rect(page.rect.x0, page.rect.y0, page.rect.x1, last_block[3] + 20)
        page.set_cropbox(crop_rect)
    except Exception as e:
        raise Exception(f"Failed to crop PDF: {e}")

    # Save the modified PDF to a new file
    doc.save(output_pdf)
download_and_crop_pdf(pdf_urls)